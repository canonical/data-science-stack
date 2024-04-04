import subprocess
from pathlib import Path

import pytest
import yaml
from charmed_kubeflow_chisme.kubernetes import KubernetesResourceHandler
from lightkube.resources.apps_v1 import Deployment
from lightkube.resources.core_v1 import Namespace, PersistentVolumeClaim, Service

from dss.config import DSS_CLI_MANAGER_LABELS, DSS_NAMESPACE
from dss.utils import wait_for_deployment_ready

NOTEBOOK_RESOURCES_FILE = "./tests/integration/notebook-resources.yaml"
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


def test_log_command(cleanup_after_initialize) -> None:
    """
    Integration test for the 'logs' command.
    """
    kubeconfig_file = "~/.kube/config"

    # FIXME: remove this line when https://github.com/canonical/data-science-stack/pull/43 is
    # merged and set the name of the notebook to be the same as in the create notebook test
    create_deployment_and_service()

    # Run the logs command with the notebook name and kubeconfig file
    result = subprocess.run(
        [
            "dss",
            "logs",
            DEPLOYMENT_NAME,
            "--kubeconfig",
            kubeconfig_file,
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
        ["dss", "logs", "--mlflow", "--kubeconfig", kubeconfig_file],
        capture_output=True,
        text=True,
    )

    # Check if the command executed successfully
    assert result.returncode == 0

    # Check if the expected logs are present in the output
    assert "Starting gunicorn" in result.stderr


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


# FIXME: remove function when https://github.com/canonical/data-science-stack/pull/43 is merged
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
