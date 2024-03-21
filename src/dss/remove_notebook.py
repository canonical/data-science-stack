from lightkube import Client
from lightkube.resources.apps_v1 import Deployment
from lightkube.resources.core_v1 import Service

from dss.config import DSS_NAMESPACE
from dss.logger import setup_logger
from dss.utils import wait_for_deployment_deleted

# Set up logger
logger = setup_logger("logs/dss.log")


def remove_notebook(name: str, lightkube_client: Client) -> None:
    """
    Removes a Notebook server from the Kubernetes cluster.

    Args:
        name (str): The name of the notebook server.
        lightkube_client (Client): The Kubernetes client.
    """

    lightkube_client.delete(res=Deployment, name=name, namespace=DSS_NAMESPACE)
    lightkube_client.delete(res=Service, name=name, namespace=DSS_NAMESPACE)

    try:
        wait_for_deployment_deleted(
            lightkube_client, namespace=DSS_NAMESPACE, deployment_name=name
        )

    except TimeoutError as err:
        logger.error(str(err))

    logger.info(f"Notebook {name} deleted.")
