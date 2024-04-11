from lightkube import Client

from dss.config import DSS_NAMESPACE, MLFLOW_DEPLOYMENT_NAME
from dss.logger import setup_logger
from dss.utils import does_mlflow_deployment_exist, get_labels_for_node, get_service_url

# Set up logger
logger = setup_logger("logs/dss.log")


def get_status(lightkube_client: Client):
    """
    Checks the status of key components within the DSS environment.

    Args:
        lightkube_client (Client): The Kubernetes client.
    """
    try:
        # Check MLflow deployment
        mlflow_ready = does_mlflow_deployment_exist(lightkube_client)

        # Log MLflow deployment status and URL
        if mlflow_ready:
            mlflow_url = get_service_url(MLFLOW_DEPLOYMENT_NAME, DSS_NAMESPACE, lightkube_client)
            logger.info("MLflow deployment: Ready")
            logger.info(f"MLflow URL: {mlflow_url}")
        else:
            logger.info("MLflow deployment: Not ready")

        # Check NVIDIA GPU acceleration
        gpu_acceleration = False
        node_labels = get_labels_for_node(lightkube_client)
        if (
            "nvidia.com/gpu.present" in node_labels
            and "nvidia.com/gpu.deploy.container-toolkit" in node_labels
            and "nvidia.com/gpu.deploy.device-plugin" in node_labels
        ):
            gpu_acceleration = True

        # Log GPU status
        if gpu_acceleration:
            logger.info("GPU acceleration: Enabled (NVIDIA GPU)")
        else:
            logger.info("GPU acceleration: Disabled")
    except Exception as e:
        logger.error(f"Failed to retrieve status: {e}")
        return
