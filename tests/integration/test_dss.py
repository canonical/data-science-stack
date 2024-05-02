import os
import subprocess
from pathlib import Path

import lightkube
import pytest
from charmed_kubeflow_chisme.kubernetes import KubernetesResourceHandler
from lightkube.core.exceptions import ApiError
from lightkube.resources.apps_v1 import Deployment
from lightkube.resources.core_v1 import Namespace, PersistentVolumeClaim, Service

from dss.config import DSS_CLI_MANAGER_LABELS, DSS_NAMESPACE, FIELD_MANAGER
from dss.utils import KUBECONFIG_DEFAULT, KUBECONFIG_ENV_VAR

# TODO: is there a better way to initialize this?  Maybe an optional argument to the test?
NOTEBOOK_RESOURCES_FILE = "./tests/integration/notebook-resources.yaml"
NOTEBOOK_NAME = "test-nb"
NOTEBOOK_IMAGE = "kubeflownotebookswg/jupyter-scipy:v1.8.0"
# Path to the kubeconfig for the host's kubernetes cluster used for testing
KUBECONFIG_PATH_FOR_TEST = Path("~/.kube/config").expanduser()


@pytest.fixture()
def set_dss_kubeconfig_environment_variable(monkeypatch):
    """Sets the DSS_KUBECONFIG environment variable to ~/.kube/config unless it is already set.

    Yields the value of the environment variable, for convenience."""
    if not os.environ.get(KUBECONFIG_ENV_VAR):
        with pytest.MonkeyPatch.context() as mp:
            mp.setenv(KUBECONFIG_ENV_VAR, str(KUBECONFIG_PATH_FOR_TEST))
            yield os.environ.get(KUBECONFIG_ENV_VAR)
    else:
        yield os.environ.get(KUBECONFIG_ENV_VAR)


def test_status_before_initialize(
    set_dss_kubeconfig_environment_variable, cleanup_after_initialize
) -> None:
    """
    Integration test to verify 'dss status' command before initialization.

    Unlike other tests below, this test gets its kubeconfig from a path specified by an environment
    variable.  This is both by necessity (bevcause initialize has not run yet) and also to test
    whether the environment variable mechanism works.
    """

    # Run the status command
    result = subprocess.run(["dss", "status"], capture_output=True, text=True)

    # Check if the command executed successfully
    assert result.returncode == 0

    # Check if the output indicates MLflow deployment is not ready
    assert "MLflow deployment: Not ready" in result.stderr

    # Check if the output indicates GPU acceleration is disabled
    assert "GPU acceleration: Disabled" in result.stderr


def test_initialize_creates_dss(cleanup_after_initialize) -> None:
    """
    Integration test to verify if the initialize command creates the 'dss' namespace and
    the 'mlflow' deployment is active in the 'dss' namespace.

    Note that this test requires an existing kubeconfig file exist at ~/.kube/config, and it stores
    this kubeconfig for all other tests below.
    """
    kubeconfig_text = KUBECONFIG_PATH_FOR_TEST.read_text()

    result = subprocess.run(
        ["dss", "initialize", "--kubeconfig", kubeconfig_text],
        capture_output=True,
        text=True,
    )

    # Check if the command executed successfully
    print(result.stdout)
    assert result.returncode == 0

    # Check if the dss namespace exists using kubectl
    kubectl_result = subprocess.run(
        ["kubectl", "get", "namespace", DSS_NAMESPACE], capture_output=True, text=True
    )
    assert DSS_NAMESPACE in kubectl_result.stdout

    # Check if the mlflow-deployment deployment is active in the dss namespace
    kubectl_result = subprocess.run(
        ["kubectl", "get", "deployment", "mlflow", "-n", DSS_NAMESPACE],
        capture_output=True,
        text=True,
    )
    assert "mlflow" in kubectl_result.stdout
    assert (
        "1/1" in kubectl_result.stdout
    )  # Assuming it should have 1 replica and all are available

    # Check if the dss notebook pvc exists using kubectl
    kubectl_result = subprocess.run(
        ["kubectl", "get", "pvc", "notebooks", "-n", DSS_NAMESPACE], capture_output=True, text=True
    )
    assert "notebooks" in kubectl_result.stdout


def test_create_notebook(cleanup_after_initialize) -> None:
    """
    Tests that `dss create` successfully creates a notebook as expected.

    Must be run after `dss initialize`
    """
    lightkube_client = get_lightkube_client()

    result = subprocess.run(
        [
            DSS_NAMESPACE,
            "create",
            NOTEBOOK_NAME,
            "--image",
            NOTEBOOK_IMAGE,
        ],
        capture_output=True,
        text=True,
        timeout=60 * 4,
    )

    # Check if the command executed successfully
    print(result.stdout)
    assert result.returncode == 0

    # Check if the notebook deployment is active in the dss namespace
    deployment = lightkube_client.get(Deployment, name=NOTEBOOK_NAME, namespace=DSS_NAMESPACE)
    assert deployment.status.availableReplicas == deployment.spec.replicas


def test_list_after_create(cleanup_after_initialize) -> None:
    """
    Tests that `dss list` lists notebooks as expected.
    """
    result = subprocess.run(
        [
            "dss",
            "list",
            "--wide",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )

    # Check if the command executed successfully
    assert result.returncode == 0

    # Check if the notebook name is presented in the output
    assert NOTEBOOK_NAME in result.stderr


def test_status_after_initialize(cleanup_after_initialize) -> None:
    """
    Integration test to verify 'dss status' command before initialization.
    """
    # Run the status command
    result = subprocess.run(["dss", "status"], capture_output=True, text=True)

    # Check if the command executed successfully
    assert result.returncode == 0

    # Check if the output indicates MLflow deployment is ready
    assert "MLflow deployment: Ready" in result.stderr

    # Check if the output indicates GPU acceleration is enabled
    assert "GPU acceleration: Disabled" in result.stderr


def test_log_command(cleanup_after_initialize) -> None:
    """
    Integration test for the 'logs' command.
    """
    # Run the logs command with the notebook name and kubeconfig file
    result = subprocess.run(
        [
            "dss",
            "logs",
            NOTEBOOK_NAME,
        ],
        capture_output=True,
        text=True,
    )

    # Check if the command executed successfully
    assert result.returncode == 0

    # Check if the expected logs are present in the output
    assert "Jupyter Server" in result.stderr

    # Run the logs command for MLflow with the kubeconfig file
    result = subprocess.run(
        ["dss", "logs", "--mlflow"],
        capture_output=True,
        text=True,
    )

    # Check if the command executed successfully
    assert result.returncode == 0

    # Check if the expected logs are present in the output
    assert "Starting gunicorn" in result.stderr


def test_stop_notebook(cleanup_after_initialize) -> None:
    """
    Tests that `dss stop` successfully stops a notebook as expected.

    Must be run after `dss create`.
    """
    lightkube_client = get_lightkube_client()

    # Run the stop command with the notebook name and kubeconfig file
    result = subprocess.run(
        [
            "dss",
            "stop",
            NOTEBOOK_NAME,
        ],
        capture_output=True,
        text=True,
    )

    # Check the command executed successfully
    assert result.returncode == 0

    # Check the notebook deployment was scaled down to 0
    deployment = lightkube_client.get(Deployment, name=NOTEBOOK_NAME, namespace=DSS_NAMESPACE)
    assert deployment.spec.replicas == 0


def test_start_notebook(cleanup_after_initialize) -> None:
    """
    Tests that `dss start` successfully starts a notebook as expected.

    Must be run after `dss create` and `dss stop`.
    """
    lightkube_client = get_lightkube_client()

    # Run the start command with the notebook name and kubeconfig file
    result = subprocess.run(
        [
            "dss",
            "start",
            NOTEBOOK_NAME,
        ],
        capture_output=True,
        text=True,
    )

    # Check the command executed successfully
    assert result.returncode == 0

    # Check the notebook deployment was scaled up to 1
    deployment = lightkube_client.get(Deployment, name=NOTEBOOK_NAME, namespace=DSS_NAMESPACE)
    assert deployment.spec.replicas == 1


def test_remove_notebook(cleanup_after_initialize) -> None:
    """
    Tests that `dss remove` successfully removes a notebook as expected.
    Must be run after `dss initialize`
    """
    lightkube_client = get_lightkube_client()

    result = subprocess.run(
        [
            DSS_NAMESPACE,
            "remove",
            NOTEBOOK_NAME,
        ]
    )
    assert result.returncode == 0

    # Check if the notebook Deployment is not found in the namespace
    with pytest.raises(ApiError) as err:
        lightkube_client.get(Deployment, name=NOTEBOOK_NAME, namespace=DSS_NAMESPACE)
    assert err.value.response.status_code == 404

    # Check if the notebook Service is not found in the namespace
    with pytest.raises(ApiError) as err:
        lightkube_client.get(Service, name=NOTEBOOK_NAME, namespace=DSS_NAMESPACE)
    assert err.value.response.status_code == 404


def test_purge(cleanup_after_initialize) -> None:
    """
    Tests that `purge` command removes all notebooks and DSS components.
    """

    # Run the purge command with the notebook name and kubeconfig file
    result = subprocess.run(
        [
            "dss",
            "purge",
        ],
        capture_output=True,
        text=True,
    )

    # Check if the command executed successfully
    assert result.returncode == 0
    assert (
        "Success: All DSS components and notebooks purged successfully from the Kubernetes cluster."
        in result.stderr
    )

    # Check that namespace has been deleted
    lightkube_client = get_lightkube_client()
    with pytest.raises(ApiError) as err:
        lightkube_client.get(Namespace, name=DSS_NAMESPACE)
    assert str(err.value) == 'namespaces "dss" not found'


@pytest.fixture(scope="module")
def cleanup_after_initialize():
    """Cleans up resources that might have been deployed by dss initialize.

    Note that this is a white-box implementation - it depends on knowing what could be deployed and
    explicitly removing those objects, rather than truly restoring the cluster to a previous state.
    This could be leaky, depending on how `dss` is changed in future.  Hopefully though, by cleaning
    up the Namespace, anything that might leak through will still be caught.
    """
    yield

    k8s_resource_handler = KubernetesResourceHandler(
        field_manager=FIELD_MANAGER,
        labels=DSS_CLI_MANAGER_LABELS,
        template_files=[],
        context={},
        resource_types={Deployment, Service, PersistentVolumeClaim, Namespace},
    )

    # Attempt to clean up anything that initialize might create
    # Note that .delete() does not wait on the objects to be successfully deleted, so repeating
    # the tests quickly can still cause an issue
    k8s_resource_handler.delete()

    # Clean up our kubeconfig cache file
    if os.path.exists(KUBECONFIG_DEFAULT):
        os.remove(KUBECONFIG_DEFAULT)


def get_lightkube_client(kubeconfig_path: str = KUBECONFIG_DEFAULT) -> lightkube.Client:
    """Returns a lightkube.Client using a kubeconfig from the specified location."""
    kubeconfig = lightkube.KubeConfig.from_file(kubeconfig_path)
    return lightkube.Client(kubeconfig)
