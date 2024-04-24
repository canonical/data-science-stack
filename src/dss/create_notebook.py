from pathlib import Path
from typing import Dict, Optional

from charmed_kubeflow_chisme.kubernetes import KubernetesResourceHandler
from lightkube import Client
from lightkube.core.exceptions import ApiError
from lightkube.resources.apps_v1 import Deployment
from lightkube.resources.core_v1 import Service

from dss.config import (
    DSS_CLI_MANAGER_LABELS,
    DSS_NAMESPACE,
    FIELD_MANAGER,
    GPU_DEPLOYMENT_LABEL,
    MANIFEST_TEMPLATES_LOCATION,
    NODE_LABELS,
    NOTEBOOK_IMAGES_ALIASES,
    NOTEBOOK_PVC_NAME,
    RECOMMENDED_IMAGES_MESSAGE,
)
from dss.logger import setup_logger
from dss.utils import (
    ImagePullBackOffError,
    does_dss_pvc_exist,
    does_mlflow_deployment_exist,
    does_notebook_exist,
    get_mlflow_tracking_uri,
    get_service_url,
    node_has_gpu_labels,
    wait_for_deployment_ready,
)

# Set up logger
logger = setup_logger("logs/dss.log")


def create_notebook(
    name: str, image: str, lightkube_client: Client, gpu: Optional[str] = None
) -> None:
    """
    Creates a Notebook server on the Kubernetes cluster with optional GPU support.

    Args:
        name (str): The name of the notebook server.
        image (str): The Docker image used for the notebook server.
        lightkube_client (Client): The Kubernetes client used for server creation.
        gpu (Optional[str]): Specifies the GPU type for the notebook if required.

    Raises:
        RuntimeError: If there is a failure in notebook creation or GPU label checking.
    """
    if gpu and not node_has_gpu_labels(lightkube_client, NODE_LABELS[gpu]):
        logger.error(f"Failed to create notebook with {gpu} GPU acceleration.\n")
        logger.info(
            "You are trying to setup notebook backed by GPU but the GPU devices were not properly set up in the Kubernetes cluster. Please refer to this guide http://<data-science-stack-docs>/setup-gpu for more information on the setup."  # noqa E501
        )
        raise RuntimeError()

    if not does_dss_pvc_exist(lightkube_client) or not does_mlflow_deployment_exist(
        lightkube_client
    ):
        logger.error("Failed to create notebook. DSS was not correctly initialized.\n")
        logger.info(
            "You might want to run\n"
            "  dss status      to check the current status\n"
            "  dss logs --all  to review all logs\n"
            "  dss initialize  to install dss\n"
        )
        raise RuntimeError()

    if does_notebook_exist(name, DSS_NAMESPACE, lightkube_client):
        logger.error(
            f"Failed to create Notebook. Notebook with name '{name}' already exists.\n"
            f"Please specify a different name."
        )
        url = get_service_url(name, DSS_NAMESPACE, lightkube_client)
        if url:
            logger.info(f"To connect to the existing notebook, go to {url}.")
        raise RuntimeError()

    manifests_file = (
        Path(__file__).parent / MANIFEST_TEMPLATES_LOCATION / "notebook_deployment.yaml.j2"
    )
    image_full_name = _get_notebook_image_name(image)
    config = _get_notebook_config(image_full_name, name, gpu)

    k8s_resource_handler = KubernetesResourceHandler(
        field_manager=FIELD_MANAGER,
        labels=DSS_CLI_MANAGER_LABELS,
        template_files=[manifests_file],
        context=config,
        resource_types={Deployment, Service},
        lightkube_client=lightkube_client,
    )

    try:
        k8s_resource_handler.apply()
        wait_for_deployment_ready(
            lightkube_client, namespace=DSS_NAMESPACE, deployment_name=name, timeout_seconds=None
        )
        logger.info(f"Success: Notebook {name} created successfully.")
        if gpu:
            logger.info(f"{gpu.title()} GPU attached to notebook.")
    except ApiError as err:
        logger.error(
            f"Failed to create Notebook with error code {err.status.code}."
            " Check the debug logs for more details."
        )
        logger.debug(f"Failed to create Notebook {name} with error {err}")
        raise RuntimeError()
    except ImagePullBackOffError as err:
        logger.error(f"Image {image_full_name} does not exist or is not accessible.\n")
        logger.info(
            "Note: You might want to use some of these recommended images:\n"
            + RECOMMENDED_IMAGES_MESSAGE
        )
        logger.debug(f"Image pull back off error while creating Notebook {name} with error {err}.")
        raise RuntimeError()

    url = get_service_url(name, DSS_NAMESPACE, lightkube_client)
    if url:
        logger.info(f"Access the notebook at {url}.")


def _get_notebook_config(image: str, name: str, gpu: Optional[str] = None) -> Dict[str, str]:
    """
    Generates the configuration dictionary for creating a notebook deployment.

    Args:
        image (str): The Docker image to use for the notebook.
        name (str): The name of the notebook.
        gpu (Optional[str]): GPU label for the notebook deployment, if GPU support is enabled.

    Returns:
        Dict[str, str]: A dictionary with configuration values for the notebook deployment.
    """
    # Base configuration for the notebook
    context = {
        "mlflow_tracking_uri": get_mlflow_tracking_uri(),
        "notebook_name": name,
        "namespace": DSS_NAMESPACE,
        "notebook_image": image,
        "pvc_name": NOTEBOOK_PVC_NAME,
    }

    # Conditionally add GPU configuration if specified
    if gpu:
        context["gpu"] = GPU_DEPLOYMENT_LABEL[gpu]

    return context


def _get_notebook_image_name(image: str) -> str:
    """
    Resolves the full Docker image name from an alias or returns the image if not an alias.

    Args:
        image (str): An alias for a notebook image or a full Docker image name.

    Returns:
        str: The resolved full Docker image name.
    """
    return NOTEBOOK_IMAGES_ALIASES.get(image, image)
