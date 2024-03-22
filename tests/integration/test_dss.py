import subprocess
from pathlib import Path

import lightkube
import pytest
import yaml
from charmed_kubeflow_chisme.kubernetes import KubernetesResourceHandler
from lightkube.core.exceptions import ApiError
from lightkube.resources.apps_v1 import Deployment
from lightkube.resources.core_v1 import Namespace, PersistentVolumeClaim, Service

from dss.config import DSS_CLI_MANAGER_LABELS, DSS_NAMESPACE
from dss.utils import wait_for_deployment_ready

NOTEBOOK_RESOURCES_FILE = "./tests/integration/deploy.yaml"
DEPLOYMENT_NAME = yaml.safe_load_all(Path(NOTEBOOK_RESOURCES_FILE).read_text()).__next__()[
    "metadata"
]["name"]


def test_initialize_creates_dss(cleanup_after_initialize) -> None:
    """
    Integration test to verify if the initialize command creates the 'dss' namespace and
    the 'mlflow' deployment is active in the 'dss' namespace.
    """
    # TODO: is there a better way to initialize this?  Maybe an optional argument to the test?
    kubeconfig = "~/.kube/config"

    result = subprocess.run(
        ["dss", "initialize", "--kubeconfig", kubeconfig],
        capture_output=True,
        text=True,
    )

    # Check if the command executed successfully
    print(result.stdout)
    assert result.returncode == 0

    # Check if the dss namespace exists using kubectl
    kubectl_result = subprocess.run(
        ["kubectl", "get", "namespace", "dss"], capture_output=True, text=True
    )
    assert "dss" in kubectl_result.stdout

    # Check if the mlflow-deployment deployment is active in the dss namespace
    kubectl_result = subprocess.run(
        ["kubectl", "get", "deployment", "mlflow", "-n", "dss"],
        capture_output=True,
        text=True,
    )
    assert "mlflow" in kubectl_result.stdout
    assert (
        "1/1" in kubectl_result.stdout
    )  # Assuming it should have 1 replica and all are available

    # Check if the dss notebook pvc exists using kubectl
    kubectl_result = subprocess.run(
        ["kubectl", "get", "pvc", "notebooks", "-n", "dss"], capture_output=True, text=True
    )
    assert "notebooks" in kubectl_result.stdout


def test_remove_notebook(cleanup_after_initialize) -> None:
    """
    Tests that `dss remove-notebook` successfully removes a notebook as expected.
    Must be run after `dss initialize`
    """
    # FIXME: remove the `--kubeconfig`` option after fixing https://github.com/canonical/data-science-stack/issues/37
    kubeconfig_file = "~/.kube/config"
    kubeconfig = lightkube.KubeConfig.from_file(kubeconfig_file)
    lightkube_client = lightkube.Client(kubeconfig)

    # FIXME: remove this line when https://github.com/canonical/data-science-stack/pull/43 is merged
    # and set the name of the notebook to be the same as in the create notebook test
    create_deployment_and_service()

    result = subprocess.run(
        [
            DSS_NAMESPACE,
            "remove-notebook",
            "--name",
            DEPLOYMENT_NAME,
            "--kubeconfig",
            kubeconfig_file,
        ]
    )
    assert result.returncode == 0

    # Check if the notebook deployment is not found in the namespace
    with pytest.raises(ApiError):
        lightkube_client.get(Deployment, name=DEPLOYMENT_NAME, namespace=DSS_NAMESPACE)

    # Check if the notebook Service is not found in the namespace
    with pytest.raises(ApiError):
        lightkube_client.get(Service, name=DEPLOYMENT_NAME, namespace=DSS_NAMESPACE)


@pytest.fixture(scope="module")
def cleanup_after_initialize():
    """Cleans up resources that might have been deployed by dss initialize.

    Note that this is a white-box implementation - it depends on knowing what could be deployed and
    explicitly removing those objects, rather than truly restoring the cluster to a previous state.
    This could be leaky, depending on how `dss initialize` is changed in future.
    """
    yield

    k8s_resource_handler = KubernetesResourceHandler(
        field_manager="dss",
        labels=DSS_CLI_MANAGER_LABELS,
        template_files=[],
        context={},
        resource_types={Deployment, Service, PersistentVolumeClaim, Namespace},
    )

    # Attempt to clean up anything that initialize might create
    # Note that .delete() does not wait on the objects to be successfully deleted, so repeating
    # the tests quickly can still cause an issue
    k8s_resource_handler.delete()


# FIXME: remove this function when https://github.com/canonical/data-science-stack/pull/43 is merged
def create_deployment_and_service():
    """
    Helper to mimic the creation of a Notebook.
    """
    output = subprocess.run(
        ["kubectl", "apply", "-f", NOTEBOOK_RESOURCES_FILE], capture_output=True, text=True
    )
    print(output)

    k8s_resource_handler = KubernetesResourceHandler(
        field_manager="dss",
        labels=DSS_CLI_MANAGER_LABELS,
        template_files=[],
        context={},
        resource_types={Deployment, Service, PersistentVolumeClaim, Namespace},
    )

    wait_for_deployment_ready(
        k8s_resource_handler.lightkube_client,
        namespace=DSS_NAMESPACE,
        deployment_name=DEPLOYMENT_NAME,
    )
