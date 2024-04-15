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
    Removes the Notebook of name `name` from the Kubernetes cluster.

    To remove the Notebook, this function Removes the Deployment and Service of name `name`.

    Args:
        name (str): The name of the notebook server.
        lightkube_client (Client): The Kubernetes client.
    """

    try:
        lightkube_client.delete(res=Deployment, name=name, namespace=DSS_NAMESPACE)
        lightkube_client.delete(res=Service, name=name, namespace=DSS_NAMESPACE)
    except ApiError as err:
        if err.status.code == 404:
            logger.warn(
                f"Failed to remove notebook. Notebook {name} does not exist. Run 'dss list' to check all notebooks."  # noqa E501
            )
            return
        else:
            logger.error(f"Failed to remove notebook {name}. Please try again.")
            logger.info(
                "You might want to run\n"
                "  dss status      to check the current status\n"
                f"  dss logs {name}  to review the notebook logs\n"
            )
            logger.debug(f"Failed to delete K8S resources for notebook {name}, with error: {err}")
            return
    logger.info(f"Notebook {name} removed successfully.")
