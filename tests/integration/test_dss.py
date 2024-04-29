import subprocess

import lightkube
import pytest
from charmed_kubeflow_chisme.kubernetes import KubernetesResourceHandler
from lightkube.core.exceptions import ApiError
from lightkube.resources.apps_v1 import Deployment
from lightkube.resources.core_v1 import Namespace, PersistentVolumeClaim, Pod, Service

from dss.config import DSS_CLI_MANAGER_LABELS, DSS_NAMESPACE, FIELD_MANAGER, NOTEBOOK_LABEL

# TODO: is there a better way to initialize this?  Maybe an optional argument to the test?
KUBECONFIG = "~/.kube/config"
NOTEBOOK_RESOURCES_FILE = "./tests/integration/notebook-resources.yaml"
NOTEBOOK_NAME = "test-nb"


def get_pod_name_from_deployment(client, deployment_name, namespace):
    pods = list(client.list(Pod, namespace=namespace, labels={NOTEBOOK_LABEL: deployment_name}))
    return pods[0].metadata.name if pods else None


@pytest.mark.cpu_run
def test_status_before_initialize(cleanup_after_initialize) -> None:
    """
    Integration test to verify 'dss status' command before initialization.
    """

    # Run the status command
    result = subprocess.run(
        ["dss", "status", "--kubeconfig", KUBECONFIG], capture_output=True, text=True
    )

    # Check if the command executed successfully
    assert result.returncode == 0

    # Check if the output indicates MLflow deployment is not ready
    assert "MLflow deployment: Not ready" in result.stderr

    # Check if the output indicates GPU acceleration is disabled
    assert "GPU acceleration: Disabled" in result.stderr


@pytest.mark.gpu_run
def test_status_before_initialize_gpu(cleanup_after_initialize) -> None:
    """
    Integration test to verify 'dss status' command before initialization on a GPU-enabled system.
    """

    # Run the status command
    result = subprocess.run(
        ["dss", "status", "--kubeconfig", KUBECONFIG], capture_output=True, text=True
    )

    # Check if the command executed successfully
    assert result.returncode == 0

    # Check if the output indicates MLflow deployment is not ready
    assert "MLflow deployment: Not ready" in result.stderr

    # Check if the output indicates GPU acceleration is enabled and captures a GPU model
    assert "GPU acceleration: Enabled" in result.stderr
    assert (
        "NVIDIA" in result.stderr
    )  # This checks for the presence of NVIDIA in the log, assuming only NVIDIA GPUs are used.


@pytest.mark.gpu_run
@pytest.mark.cpu_run
def test_initialize_creates_dss(cleanup_after_initialize) -> None:
    """
    Integration test to verify if the initialize command creates the 'dss' namespace and
    the 'mlflow' deployment is active in the 'dss' namespace.
    """
    result = subprocess.run(
        ["dss", "initialize", "--kubeconfig", KUBECONFIG],
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


@pytest.mark.gpu_run
@pytest.mark.cpu_run
def test_create_notebook(cleanup_after_initialize, notebook_image) -> None:
    """
    Tests that `dss create` successfully creates a notebook as expected.

    Must be run after `dss initialize`
    """
    kubeconfig = lightkube.KubeConfig.from_file(KUBECONFIG)
    lightkube_client = lightkube.Client(kubeconfig)

    result = subprocess.run(
        [
            DSS_NAMESPACE,
            "create",
            NOTEBOOK_NAME,
            "--image",
            notebook_image,
            "--kubeconfig",
            KUBECONFIG,
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


@pytest.mark.gpu_run
def test_notebook_gpu_availability(notebook_image, cleanup_after_initialize):
    """
    Test to ensure that the GPU is available in the deployed Jupyter notebook.

    Args:
        kubeconfig (str): Path to the Kubernetes configuration file.
        notebook_image (str): Docker image used for the notebook deployment.
    """
    kubeconfig = lightkube.KubeConfig.from_file(KUBECONFIG)
    lightkube_client = lightkube.Client(kubeconfig)

    deployment = lightkube_client.get(Deployment, name=NOTEBOOK_NAME, namespace=DSS_NAMESPACE)
    assert deployment.status.availableReplicas == deployment.spec.replicas

    # Execute the Python command to check GPU availability
    pod_name = get_pod_name_from_deployment(lightkube_client, NOTEBOOK_NAME, DSS_NAMESPACE)
    gpu_check_command = [
        "kubectl",
        "exec",
        pod_name,
        "--namespace",
        DSS_NAMESPACE,
        "--",
        "python",
        "-c",
        "import torch; print('CUDA Available:', torch.cuda.is_available())",
    ]
    print("Executing command:", " ".join(gpu_check_command))
    gpu_result = subprocess.run(gpu_check_command, capture_output=True, text=True)
    assert "CUDA Available: True" in gpu_result.stdout, "GPU is not available in the notebook pod"


@pytest.mark.gpu_run
@pytest.mark.cpu_run
def test_list_after_create(cleanup_after_initialize) -> None:
    """
    Tests that `dss list` lists notebooks as expected.
    """
    result = subprocess.run(
        [
            "dss",
            "list",
            "--kubeconfig",
            KUBECONFIG,
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


@pytest.mark.cpu_run
def test_status_after_initialize(cleanup_after_initialize) -> None:
    """
    Integration test to verify 'dss status' command before initialization.
    """
    # Run the status command
    result = subprocess.run(
        ["dss", "status", "--kubeconfig", KUBECONFIG], capture_output=True, text=True
    )

    # Check if the command executed successfully
    assert result.returncode == 0

    # Check if the output indicates MLflow deployment is ready
    assert "MLflow deployment: Ready" in result.stderr

    # Check if the output indicates GPU acceleration is enabled
    assert "GPU acceleration: Disabled" in result.stderr


@pytest.mark.gpu_run
def test_status_after_initialize_gpu(cleanup_after_initialize) -> None:
    """
    Integration test to verify 'dss status' command after initialization on a GPU-enabled system.
    """
    # Run the status command
    result = subprocess.run(
        ["dss", "status", "--kubeconfig", KUBECONFIG], capture_output=True, text=True
    )

    # Check if the command executed successfully
    assert result.returncode == 0

    # Check if the output indicates MLflow deployment is ready
    assert "MLflow deployment: Ready" in result.stderr

    # Check for MLflow URL presence in the output
    assert "MLflow URL: http://" in result.stderr

    # Check if the output indicates GPU acceleration is enabled and captures any GPU model
    assert "GPU acceleration: Enabled" in result.stderr
    assert (
        "NVIDIA" in result.stderr
    )  # This checks for the presence of NVIDIA, assuming NVIDIA GPUs are used.


@pytest.mark.gpu_run
@pytest.mark.cpu_run
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
            "--kubeconfig",
            KUBECONFIG,
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
        ["dss", "logs", "--mlflow", "--kubeconfig", KUBECONFIG],
        capture_output=True,
        text=True,
    )

    # Check if the command executed successfully
    assert result.returncode == 0

    # Check if the expected logs are present in the output
    assert "Starting gunicorn" in result.stderr


@pytest.mark.gpu_run
@pytest.mark.cpu_run
def test_stop_notebook(cleanup_after_initialize) -> None:
    """
    Tests that `dss stop` successfully stops a notebook as expected.

    Must be run after `dss create`.
    """
    kubeconfig = lightkube.KubeConfig.from_file(KUBECONFIG)
    lightkube_client = lightkube.Client(kubeconfig)

    # Run the stop command with the notebook name and kubeconfig file
    result = subprocess.run(
        [
            "dss",
            "stop",
            NOTEBOOK_NAME,
            "--kubeconfig",
            KUBECONFIG,
        ],
        capture_output=True,
        text=True,
    )

    # Check the command executed successfully
    assert result.returncode == 0

    # Check the notebook deployment was scaled down to 0
    deployment = lightkube_client.get(Deployment, name=NOTEBOOK_NAME, namespace=DSS_NAMESPACE)
    assert deployment.spec.replicas == 0


@pytest.mark.gpu_run
@pytest.mark.cpu_run
def test_start_notebook(cleanup_after_initialize) -> None:
    """
    Tests that `dss start` successfully starts a notebook as expected.

    Must be run after `dss create` and `dss stop`.
    """
    kubeconfig = lightkube.KubeConfig.from_file(KUBECONFIG)
    lightkube_client = lightkube.Client(kubeconfig)

    # Run the start command with the notebook name and kubeconfig file
    result = subprocess.run(
        [
            "dss",
            "start",
            NOTEBOOK_NAME,
            "--kubeconfig",
            KUBECONFIG,
        ],
        capture_output=True,
        text=True,
    )

    # Check the command executed successfully
    assert result.returncode == 0

    # Check the notebook deployment was scaled up to 1
    deployment = lightkube_client.get(Deployment, name=NOTEBOOK_NAME, namespace=DSS_NAMESPACE)
    assert deployment.spec.replicas == 1


@pytest.mark.gpu_run
@pytest.mark.cpu_run
def test_remove_notebook(cleanup_after_initialize) -> None:
    """
    Tests that `dss remove` successfully removes a notebook as expected.
    Must be run after `dss initialize`
    """
    # FIXME: remove the `--kubeconfig`` option
    # after fixing https://github.com/canonical/data-science-stack/issues/37
    kubeconfig = lightkube.KubeConfig.from_file(KUBECONFIG)
    lightkube_client = lightkube.Client(kubeconfig)

    result = subprocess.run(
        [
            DSS_NAMESPACE,
            "remove",
            NOTEBOOK_NAME,
            "--kubeconfig",
            KUBECONFIG,
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


@pytest.mark.gpu_run
@pytest.mark.cpu_run
def test_purge(cleanup_after_initialize) -> None:
    """
    Tests that `purge` command removes all notebooks and DSS components.
    """

    # Run the purge command with the notebook name and kubeconfig file
    result = subprocess.run(
        [
            "dss",
            "purge",
            "--kubeconfig",
            KUBECONFIG,
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
    kubeconfig = lightkube.KubeConfig.from_file(KUBECONFIG)
    lightkube_client = lightkube.Client(kubeconfig)
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
