import subprocess

import lightkube
import pytest
from charmed_kubeflow_chisme.kubernetes import KubernetesResourceHandler
from lightkube.resources.apps_v1 import Deployment
from lightkube.resources.core_v1 import Namespace, PersistentVolumeClaim, Service

from dss.config import DSS_CLI_MANAGER_LABELS, DSS_NAMESPACE, FIELD_MANAGER


def test_initialize_creates_dss(cleanup_after_tests) -> None:
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


def test_create_notebook(cleanup_after_tests) -> None:
    """
    Tests that `dss create-notebook` successfully creates a notebook as expected.

    Must be run after `dss initialize`
    """
    # TODO: is there a better way to initialize this?  Maybe an optional argument to the test?
    kubeconfig_file = "~/.kube/config"
    kubeconfig = lightkube.KubeConfig.from_file(kubeconfig_file)
    lightkube_client = lightkube.Client(kubeconfig)

    notebook_name = "test-notebook"
    notebook_image = "kubeflownotebookswg/jupyter-scipy:v1.8.0"

    result = subprocess.run(
        [
            DSS_NAMESPACE,
            "create-notebook",
            notebook_name,
            "--image",
            notebook_image,
            "--kubeconfig",
            kubeconfig_file,
        ],
        capture_output=True,
        text=True,
        timeout=60 * 4,
    )

    # Check if the command executed successfully
    print(result.stdout)
    assert result.returncode == 0

    # Check if the notebook deployment is active in the dss namespace
    deployment = lightkube_client.get(Deployment, name=notebook_name, namespace=DSS_NAMESPACE)
    assert deployment.status.availableReplicas == deployment.spec.replicas


@pytest.fixture(scope="module")
def cleanup_after_tests():
    """Cleans up resources that might have been deployed by the tests.

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
