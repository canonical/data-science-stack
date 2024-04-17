from lightkube import Client
from lightkube.core.exceptions import ApiError
from lightkube.resources.apps_v1 import Deployment
from tabulate import tabulate

from dss.config import DSS_NAMESPACE, NOTEBOOK_LABEL
from dss.logger import setup_logger
from dss.utils import get_service_url, truncate_row

# Set up logger
logger = setup_logger("logs/dss.log")


def list_notebooks(lightkube_client: Client, wide: bool = False) -> None:
    """
    List the available notebooks in the DSS namespace.

    Args:
        lightkube_client (Client): The Kubernetes client.
        wide (bool, optional): Whether to display the full information without truncation.
                               Defaults to False.
    """
    try:
        # Get the list of deployments in the dss namespace
        deployments = lightkube_client.list(Deployment, namespace=DSS_NAMESPACE)
    except ApiError as e:
        logger.error(f"Failed to list notebooks: {e}")
        return

    notebook_list = []
    for deployment in deployments:
        # Check if the deployment has the required label
        labels = deployment.metadata.labels
        if NOTEBOOK_LABEL in labels:
            name = deployment.metadata.name
            image = deployment.spec.template.spec.containers[0].image

            # Check if the deployment is available (scaled to at least 1 replica)
            available_replicas = deployment.status.availableReplicas
            url = (
                get_service_url(name, DSS_NAMESPACE, lightkube_client)
                if available_replicas
                else "(stopped)"
            )

            print([name, image, url])
            if wide:
                notebook_list.append([name, image, url])
            else:
                name, image, url = truncate_row(name, image, url)
                notebook_list.append((name, image, url))

    # Print the information in a tabular format
    headers = ["Name", "Image", "URL"]
    logger.info("\n" + tabulate(notebook_list, headers=headers, tablefmt="grid"))
