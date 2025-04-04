from pathlib import Path

from charmed_kubeflow_chisme.kubernetes import KubernetesResourceHandler
from lightkube import Client
from lightkube.resources.apps_v1 import Deployment
from lightkube.resources.core_v1 import Namespace, PersistentVolumeClaim, Service

from dss.config import (
    DEFAULT_NOTEBOOK_IMAGE,
    DSS_CLI_MANAGER_LABELS,
    DSS_NAMESPACE,
    FIELD_MANAGER,
    MANIFEST_TEMPLATES_LOCATION,
    MLFLOW_DEPLOYMENT_NAME,
    NOTEBOOK_PVC_NAME,
)
from dss.logger import setup_logger
from dss.utils import wait_for_deployment_ready

# Set up logger
logger = setup_logger()


def initialize(lightkube_client: Client) -> None:
    """
    Initializes the Kubernetes cluster by applying manifests from a YAML file.

    Args:
        lightkube_client (Client): The Kubernetes client.

    Returns:
        None
    """
    # Path to the manifests YAML file
    manifests_files = [
        Path(Path(__file__).parent, MANIFEST_TEMPLATES_LOCATION, "dss_core.yaml.j2"),
        Path(Path(__file__).parent, MANIFEST_TEMPLATES_LOCATION, "mlflow_deployment.yaml.j2"),
    ]

    config = {
        "mlflow_name": MLFLOW_DEPLOYMENT_NAME,
        "namespace": DSS_NAMESPACE,
        "notebook_pvc_name": NOTEBOOK_PVC_NAME,
    }

    k8s_resource_handler = KubernetesResourceHandler(
        field_manager=FIELD_MANAGER,
        labels=DSS_CLI_MANAGER_LABELS,
        template_files=manifests_files,
        context=config,
        resource_types={Deployment, Service, PersistentVolumeClaim, Namespace},
        lightkube_client=lightkube_client,
    )

    try:
        # Apply resources using KubernetesResourceHandler
        k8s_resource_handler.apply()

        # Wait for mlflow deployment to be ready
        wait_for_deployment_ready(lightkube_client, namespace="dss", deployment_name="mlflow")

        logger.info(
            "DSS initialized. To create your first notebook run the command:\n\ndss create\n\n"  # noqa E501
            "Examples:\n"
            "  dss create my-notebook --image=pytorch\n"
            f"  dss create my-notebook --image={DEFAULT_NOTEBOOK_IMAGE}\n"
        )

    except TimeoutError:
        logger.error(
            "Timeout waiting for deployment 'mlflow-deployment' in namespace 'dss' to be ready. "  # noqa E501
            "Deleting resources..."
        )
        k8s_resource_handler.delete()
