import os

from charmed_kubeflow_chisme.kubernetes import KubernetesResourceHandler
from lightkube import Client
from lightkube.resources.apps_v1 import Deployment
from lightkube.resources.core_v1 import Namespace, PersistentVolumeClaim, Service

from dss.logger import setup_logger
from dss.utils import wait_for_deployment_ready

# Set up logger
logger = setup_logger("logs/dss.log")


DSS_CLI_MANAGER_LABELS = {"app.kubernetes.io/managed-by": "dss-cli"}


def initialize(lightkube_client: Client) -> None:
    """
    Initializes the Kubernetes cluster by applying manifests from a YAML file.

    Args:
        lightkube_client (Client): The Kubernetes client.

    Returns:
        None
    """
    # Path to the manifests YAML file
    manifests_file = os.path.join(os.path.dirname(__file__), "manifests.yaml")

    # Initialize KubernetesResourceHandler
    k8s_resource_handler = KubernetesResourceHandler(
        field_manager="dss",
        labels=DSS_CLI_MANAGER_LABELS,
        template_files=[manifests_file],
        context={},
        resource_types={Deployment, Service, PersistentVolumeClaim, Namespace},
        lightkube_client=lightkube_client,
    )

    try:
        # Apply resources using KubernetesResourceHandler
        k8s_resource_handler.apply()

        # Wait for mlflow deployment to be ready
        wait_for_deployment_ready(lightkube_client, namespace="dss", deployment_name="mlflow")

        logger.info(
            "DSS initialized. To create your first notebook run the command:\n\ndss create-notebook"  # noqa E501
        )

    except TimeoutError:
        logger.error(
            "Timeout waiting for deployment 'mlflow-deployment' in namespace 'dss' to be ready. "  # noqa E501
            "Deleting resources..."
        )
        k8s_resource_handler.delete()
