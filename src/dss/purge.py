from lightkube import Client
from lightkube.resources.core_v1 import Namespace

from dss.config import DSS_NAMESPACE
from dss.logger import setup_logger
from dss.utils import does_namespace_exist, wait_for_namespace_to_be_deleted

# Set up logger
logger = setup_logger("logs/dss.log")


def purge(lightkube_client: Client) -> None:
    """
    Removes all notebooks and DSS components. This is done by removing the
    `dss` namespace, and thus all resources living in that namespace.

    Args:
        lightkube_client (Client): The Kubernetes client.
    """
    if not does_namespace_exist(lightkube_client, DSS_NAMESPACE):
        logger.warn(f"Cannot purge DSS components. Namespace `{DSS_NAMESPACE}` does not exist.")
        logger.info("You might want to run")
        logger.info("  dss status      to check the current status")
        logger.info("  dss logs --all  to review all logs")
        logger.info("  dss initialize  to install dss")
        return
    else:
        lightkube_client.delete(Namespace, DSS_NAMESPACE)
        # need to wait on namespace deletion to be completed
        wait_for_namespace_to_be_deleted(lightkube_client, DSS_NAMESPACE)
        logger.info(
            "Success: All DSS components and notebooks purged successfully from the Kubernetes cluster."  # noqa E501
        )
