from lightkube import Client
from lightkube.core.exceptions import ApiError
from lightkube.resources.apps_v1 import Deployment
from lightkube.resources.core_v1 import Service

from dss.config import DSS_NAMESPACE
from dss.logger import setup_logger

# Set up logger
logger = setup_logger("logs/dss.log")


def remove_notebook(name: str, lightkube_client: Client) -> None:
    """
    Removes a Notebook server from the Kubernetes cluster.

    Args:
        name (str): The name of the notebook server.
        lightkube_client (Client): The Kubernetes client.
    """

    try:
        lightkube_client.delete(res=Deployment, name=name, namespace=DSS_NAMESPACE)
        lightkube_client.delete(res=Service, name=name, namespace=DSS_NAMESPACE)
    except ApiError as err:
        if err.status.code == 404:
            logger.warn("Failed to delete K8s resources not found. Ignoring remove-notebook.")
            return
        else:
            logger.error(f"Failed to delete K8S resources, with error: {err}")
            return
    logger.info(f"Notebook {name} removed.")
