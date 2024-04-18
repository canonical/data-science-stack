from lightkube import Client
from lightkube.core.exceptions import ApiError
from lightkube.models.autoscaling_v1 import ScaleSpec
from lightkube.models.meta_v1 import ObjectMeta
from lightkube.resources.apps_v1 import Deployment

from dss.config import DSS_NAMESPACE
from dss.logger import setup_logger
from dss.utils import does_notebook_exist

# Set up logger
logger = setup_logger("logs/dss.log")


def stop_notebook(name: str, lightkube_client: Client) -> None:
    """
    Stops a Notebook server on the Kubernetes cluster by scaling down the Notebook's Deployment.

    Args:
        name (str): The name of the notebook server.
        lightkube_client (Client): The Kubernetes client.
    """

    if not does_notebook_exist(
        name=name, namespace=DSS_NAMESPACE, lightkube_client=lightkube_client
    ):
        logger.error(f"Failed to stop Notebook. Notebook {name} does not exist.")
        logger.info("Run 'dss list' to check all notebooks.")
        raise RuntimeError(f"Failed to stop Notebook. Notebook {name} does not exist.")

    obj = Deployment.Scale(
        metadata=ObjectMeta(name=name, namespace=DSS_NAMESPACE), spec=ScaleSpec(replicas=0)
    )

    try:
        lightkube_client.replace(obj)
        logger.info(
            f"Stopping the notebook {name}. Check `dss list` for the status of the notebook."
        )
        return
    except ApiError as e:
        logger.error(f"Failed to stop Notebook {name}")
        logger.debug(f"Failed to scale down Deployment {name} with error: {e}")
        raise e
