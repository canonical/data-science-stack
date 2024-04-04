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
    NOTEBOOK_PVC_NAME,
)
from dss.logger import setup_logger
from dss.utils import (
    ImagePullBackOffError,
    does_dss_pvc_exist,
    does_notebook_exist,
    get_mlflow_tracking_uri,
    get_notebook_url,
    wait_for_deployment_ready,
)

NOTEBOOK_IMAGES_ALIASES = {
    "pytorch": "charmedkubeflow/jupyter-pytorch-full:1.8.0-3058193",
    # TODO: add the rest of the rocks once updated in https://github.com/canonical/kubeflow-rocks
    # "pytorch-cuda": "charmedkubeflow/jupyter-pytorch-cuda-full:1.8.0-xxxxx",
    # "tensorflow-cuda": "charmedkubeflow/jupyter-tensorflow-cuda-full:1.8.0-xxxx",
    # "tensorflow": "charmedkubeflow/jupyter-tensorflow-full:1.8.0-xxxx"
}

# Set up logger
logger = setup_logger("logs/dss.log")


def create_notebook(name: str, image: str, lightkube_client: Client) -> None:
    """
    Creates a Notebook server on the Kubernetes cluster.

    Args:
        name (str): The name of the notebook server.
        image (str): The image used for the notebook server.
        lightkube_client (Client): The Kubernetes client.
    """
    if not does_dss_pvc_exist(lightkube_client):
        logger.error(
            "Failed to create notebook. DSS was not correctly initialized."
            "   You might want to run"
            "   dss status      to check the current status"
            "   dss logs --all  to review all logs"
            "   dss initialize  to install dss"
        )
        return
    if does_notebook_exist(name, DSS_NAMESPACE, lightkube_client):
        url = get_notebook_url(name, DSS_NAMESPACE, lightkube_client)
        logger.error(
            f"Failed to create Notebook. Notebook with name '{name}' already exists."
            f"  Please specify a different name."
            f"  To connect to the existing notebook, go to {url}."
        )
        return

    manifests_file = Path(
        Path(__file__).parent, MANIFEST_TEMPLATES_LOCATION, "notebook_deployment.yaml.j2"
    )

    config = _get_notebook_config(image, name)

    # Initialize KubernetesResourceHandler
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
        logger.error(
            f"Failed to create Notebook with error code {err.status.code}"
            "   Check the debug logs for more details."
        )
        logger.debug(f"Failed to create Notebook {name} with error {err}")
    except TimeoutError as err:
        logger.error(str(err))
        logger.warn(f"Notebook {name} might be in the cluster. Check the status with `dss list`.")
        return
    except ImagePullBackOffError:
        logger.error(
            f"Failed to create Notebook {name}. Image {image} does not exist or is not accessible."
        )
        return
    notebook_url = get_notebook_url(name, DSS_NAMESPACE, lightkube_client)
    logger.info(f"Access the notebook at {notebook_url}.")


def _get_notebook_config(image, name):
    mlflow_tracking_uri = get_mlflow_tracking_uri()
    full_image = _get_notebook_image_name(image)
    context = {
        "mlflow_tracking_uri": mlflow_tracking_uri,
        "notebook_name": name,
        "namespace": DSS_NAMESPACE,
        "notebook_image": full_image,
        "pvc_name": NOTEBOOK_PVC_NAME,
    }
    return context


def _get_notebook_image_name(image) -> str:
    """
    Returns the image's full name if the input is a key in `NOTEBOOK_IMAGES_ALIASES`
    else it returns the input.
    """
    return NOTEBOOK_IMAGES_ALIASES.get(image, image)
