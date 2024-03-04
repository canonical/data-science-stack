from pathlib import Path

from charmed_kubeflow_chisme.kubernetes import KubernetesResourceHandler
from lightkube import Client
from lightkube.resources.apps_v1 import Deployment
from lightkube.resources.core_v1 import Service

from dss.config import (
    DSS_CLI_MANAGER_LABELS,
    DSS_NAMESPACE,
    FIELD_MANAGER,
    MANIFEST_TEMPLATES_LOCATION,
    NOTEBOOK_PVC_NAME,
)
from dss.logger import setup_logger
from dss.utils import wait_for_deployment_ready, _get_notebook_url

# Set up logger
logger = setup_logger("logs/dss.log")


def create_notebook(name: str, image: str, lightkube_client: Client) -> None:
    """
    Creates a Notebook server on the Kubernetes cluster.

    Args:
        name (str): The name of the notebook server.
        image (str): The image used for the notebook server.
        lightkube_client (Client): The Kubernetes client.

    Returns:
        None
    """
    manifests_file = Path(
        Path(__file__).parent, MANIFEST_TEMPLATES_LOCATION, "notebook_deployment.yaml.j2"
    )

    context = {
        "notebook_name": name,
        "namespace": DSS_NAMESPACE,
        "notebook_image": image,
        "pvc_name": NOTEBOOK_PVC_NAME,
    }

    # Initialize KubernetesResourceHandler
    k8s_resource_handler = KubernetesResourceHandler(
        field_manager=FIELD_MANAGER,
        labels=DSS_CLI_MANAGER_LABELS,
        template_files=[manifests_file],
        context=context,
        resource_types={Deployment, Service},
        lightkube_client=lightkube_client,
    )

    try:
        k8s_resource_handler.apply()

        wait_for_deployment_ready(lightkube_client, namespace=DSS_NAMESPACE, deployment_name=name)

        logger.info("Notebook created.")
    except TimeoutError as err:
        logger.error(f"{str(err)}\nCleaning up the resources just created.")
        k8s_resource_handler.delete()
        return

    notebook_url = _get_notebook_url(name, DSS_NAMESPACE, lightkube_client)
    logger.info(f"Access the notebook at {notebook_url}.")
