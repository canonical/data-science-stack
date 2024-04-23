from pathlib import Path

from charmed_kubeflow_chisme.kubernetes import KubernetesResourceHandler
from lightkube import Client
from lightkube.core.exceptions import ApiError
from lightkube.resources.apps_v1 import Deployment
from lightkube.resources.core_v1 import Service

from dss.config import (
    DSS_CLI_MANAGER_LABELS,
    DSS_NAMESPACE,
    FIELD_MANAGER,
    MANIFEST_TEMPLATES_LOCATION,
    NOTEBOOK_IMAGES_ALIASES,
    NOTEBOOK_PVC_NAME,
    RECOMMENDED_IMAGES_MESSAGE,
    NODE_LABELS,
    GPU_DEPLOYMENT_LABEL
)
from dss.logger import setup_logger
from dss.utils import (
    ImagePullBackOffError,
    does_dss_pvc_exist,
    does_mlflow_deployment_exist,
    does_notebook_exist,
    get_mlflow_tracking_uri,
    get_service_url,
    wait_for_deployment_ready,
    node_has_gpu_labels
)

# Set up logger
logger = setup_logger("logs/dss.log")


def create_notebook(name: str, image: str, lightkube_client: Client, gpu: Optional[str] = None) -> None:
    """
    Creates a Notebook server on the Kubernetes cluster with optional GPU support.

    Args:
        name (str): The name of the notebook server.
        image (str): The Docker image used for the notebook server.
        lightkube_client (Client): The Kubernetes client used for server creation.
        gpu (Optional[str]): Specifies the GPU type for the notebook if required. Supported: 'nvidia'.
    
    Raises:
        RuntimeError: If there is a failure in notebook creation or GPU label checking.
    """
    if gpu and not node_has_gpu_labels(lightkube_client, NODE_LABELS[gpu]):
        logger.error(f"Failed to create notebook with {gpu} GPU acceleration.")
        logger.info("You are trying to setup notebook backed by GPU but the GPU devices were not properly set up in the Kubernetes cluster. Please refer to this guide http://<data-science-stack-docs>/setup-gpu for more information on the setup.")
        raise RuntimeError()

    if not does_dss_pvc_exist(lightkube_client) or not does_mlflow_deployment_exist(lightkube_client):
        logger.error("Failed to create notebook. DSS was not correctly initialized.")
        logger.info("You might want to run 'dss status' to check the current status, 'dss logs --all' to review all logs, or 'dss initialize' to install DSS.")
        raise RuntimeError()

    if does_notebook_exist(name, DSS_NAMESPACE, lightkube_client):
        logger.error(f"Notebook with name '{name}' already exists. Please specify a different name.")
        url = get_service_url(name, DSS_NAMESPACE, lightkube_client)
        if url:
            logger.info(f"To connect to the existing notebook, go to {url}.")
        return

    manifests_file = Path(__file__).parent / MANIFEST_TEMPLATES_LOCATION / "notebook_deployment.yaml.j2"
    image_full_name = _get_notebook_image_name(image)
    config = _get_notebook_config(image_full_name, name, GPU_DEPLOYMENT_LABEL[gpu] if gpu else None)

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
        wait_for_deployment_ready(lightkube_client, namespace=DSS_NAMESPACE, deployment_name=name)
        logger.info(f"Success: Notebook {name} created successfully.")
    except ApiError as err:
        logger.error(f"Failed to create Notebook with error code {err.status.code}. Check the debug logs for more details.")
        logger.debug(f"Failed to create Notebook {name} with error {err}")
        raise RuntimeError()
    except TimeoutError as err:
        logger.error(str(err))
        logger.warn(f"Timed out while trying to create Notebook {name}. Some resources might be left in the cluster. Check the status with `dss list`.")
        raise RuntimeError()
    except ImagePullBackOffError as err:
        logger.error(f"Image {image_full_name} does not exist or is not accessible.")
        logger.info("Note: You might want to use some of these recommended images:\n" + RECOMMENDED_IMAGES_MESSAGE)
        logger.debug(f"Image pull back off error while creating Notebook {name} with error {err}.")
        raise RuntimeError()

    url = get_service_url(name, DSS_NAMESPACE, lightkube_client)
    if url:
        logger.info(f"Access the notebook at {url}.")


def _get_notebook_config(image: str, name: str, gpu: str = None) -> dict:
    """
    Generates the configuration dictionary for creating a notebook deployment.

    Args:
        image (str): The Docker image to use for the notebook.
        name (str): The name of the notebook.
        gpu (str, optional): The type of GPU acceleration ('nvidia'), if applicable.

    Returns:
        dict: A dictionary with configuration values for the notebook.
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
        context["gpu"] = gpu

    return context


def _get_notebook_image_name(image: str) -> str:
    """
    Returns the image's full name if the input is a key in `NOTEBOOK_IMAGES_ALIASES`
    else it returns the input.
    """
    return NOTEBOOK_IMAGES_ALIASES.get(image, image)
