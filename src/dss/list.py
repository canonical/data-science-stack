import sys

import lightkube
from lightkube import Client
from lightkube.core.exceptions import ApiError
from lightkube.resources.apps_v1 import Deployment
from prettytable import PrettyTable

from dss.config import DSS_NAMESPACE, NOTEBOOK_LABEL, DeploymentState
from dss.logger import setup_logger
from dss.utils import get_deployment_state, get_service_url

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
        deployments = list(
            lightkube_client.list(
                Deployment,
                namespace=DSS_NAMESPACE,
                labels={NOTEBOOK_LABEL: lightkube.operators.exists()},
            )
        )
    except ApiError as e:
        logger.error(f"Failed to list notebooks: {e}")
        return

    if not deployments:
        # Use stdout for table so the output can be piped properly
        print("No notebooks found")
        return

    # Create a PrettyTable object
    table = PrettyTable()
    table.field_names = ["Name", "Image", "URL"]
    table.border = False
    table.align = "l"  # Align the text to left

    # Adjust column widths based on the output destination
    if sys.stdout.isatty() and not wide:
        # Output is to a terminal and not in wide mode
        table._max_width = {"Name": 26, "Image": 30, "URL": 24}

    for deployment in deployments:
        name = deployment.metadata.name
        image = deployment.spec.template.spec.containers[0].image
        state = get_deployment_state(deployment, lightkube_client)

        # Use state to decide what to display in the URL column
        if state == DeploymentState.ACTIVE:
            available_replicas = deployment.status.availableReplicas
            url = get_service_url(name, DSS_NAMESPACE, lightkube_client)
            if not url:
                # TODO: Add documentation link
                logger.warning(
                    f"No service found for the notebook {name}. Please refer to our documentation."
                )
                url = f"({DeploymentState.NO_SERVICE.value})"
            elif not available_replicas:
                url = f"({DeploymentState.STOPPED.value})"
        else:
            url = f"({state.value})"

        table.add_row([name, image, url])

    # Use stdout for table so the output can be piped properly
    print(table)
