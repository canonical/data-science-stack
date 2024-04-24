from lightkube import Client
from lightkube.core.exceptions import ApiError
from lightkube.resources.apps_v1 import Deployment
from lightkube.resources.core_v1 import Service

from dss.config import DSS_NAMESPACE
from dss.logger import setup_logger
from dss.utils import does_notebook_exist

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

    if not does_notebook_exist(
        name=name, namespace=DSS_NAMESPACE, lightkube_client=lightkube_client
    ):
        logger.debug(f"Failed to remove Notebook. Notebook {name} does not exist.")
        logger.error(f"Failed to remove Notebook. Notebook {name} does not exist.")  # noqa E501
        logger.info("Run 'dss list' to check all notebooks.")
        raise RuntimeError()

    # From this point forward we know either one or both
    # resources (Deployment, Service) exist for the Notebook.
    exceptions = []
    notebook_resources = [Deployment, Service]
    for resource in notebook_resources:
        try:
            lightkube_client.delete(res=resource, name=name, namespace=DSS_NAMESPACE)
        except ApiError as err:
            if err.status.code == 404:
                logger.warn(
                    f"Failed to remove {resource.__name__} {name}. {resource.__name__} {name} does not exist. Ignoring."  # noqa E501
                )
            else:
                logger.debug(
                    f"Failed to delete {resource.__name__} for notebook {name}, with error: {err}"
                )
                exceptions.append(err)

    if exceptions:
        logger.debug(f"Failed to remove notebook {name}: {exceptions}")
        logger.error(f"Failed to remove notebook {name}. Please try again.")
        logger.info("Note: You might want to run")
        logger.info("  dss status      to check the current status")
        logger.info(f"  dss logs {name} to review the notebook logs")
        raise RuntimeError()
    else:
        logger.info(
            f"Removing the notebook {name}. Check `dss list` for the status of the notebook."
        )
