import lightkube
from lightkube import Client
from lightkube.core.exceptions import ApiError
from lightkube.resources.apps_v1 import Deployment
from tabulate import tabulate

from dss.config import DSS_NAMESPACE, NOTEBOOK_LABEL, DeploymentState
from dss.logger import setup_logger
from dss.utils import get_deployment_state, get_service_url, truncate_row

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
        deployments = lightkube_client.list(
            Deployment,
            namespace=DSS_NAMESPACE,
            labels={NOTEBOOK_LABEL: lightkube.operators.exists()},
        )
    except ApiError as e:
        logger.error(f"Failed to list notebooks: {e}")
        return

    notebook_list = []
    for deployment in deployments:
        name = deployment.metadata.name
        image = deployment.spec.template.spec.containers[0].image
        state = get_deployment_state(deployment, lightkube_client)

        # Use state to decide what to display in the URL column
        if state == DeploymentState.ACTIVE:
            available_replicas = deployment.status.availableReplicas
            url = (
                get_service_url(name, DSS_NAMESPACE, lightkube_client)
                if available_replicas
                else f"({DeploymentState.STOPPED})"
            )
        else:
            url = f"({state.value})"

        if not wide:
            name, image, url = truncate_row(name, image, url)

        notebook_list.append([name, image, url])

    headers = ["Name", "Image", "URL"]
    logger.info("\n" + tabulate(notebook_list, headers=headers, tablefmt="grid"))
