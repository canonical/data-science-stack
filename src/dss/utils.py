import os
import time
from typing import Optional

from lightkube import ApiError, Client, KubeConfig
from lightkube.resources.apps_v1 import Deployment
from lightkube.resources.core_v1 import Node, PersistentVolumeClaim, Pod, Service

from dss.config import DSS_NAMESPACE, MLFLOW_DEPLOYMENT_NAME, NOTEBOOK_PVC_NAME
from dss.logger import setup_logger

# Set up logger
logger = setup_logger("logs/dss.log")

# Resource types used for a DSS Notebook
NOTEBOOK_RESOURCES = (Service, Deployment)

# Name for the environment variable storing kubeconfig
KUBECONFIG_ENV_VAR = "DSS_KUBECONFIG"
KUBECONFIG_DEFAULT = "./kubeconfig"


class ImagePullBackOffError(Exception):
    """
    Raised when the Notebook Pod is unable to pull the image.
    """

    __module__ = None

    def __init__(self, msg: str, *args):
        super().__init__(str(msg), *args)
        self.msg = str(msg)


def wait_for_deployment_ready(
    client: Client,
    namespace: str,
    deployment_name: str,
    timeout_seconds: int = 180,
    interval_seconds: int = 10,
) -> None:
    """
    Waits for a Kubernetes deployment to be ready.

    Args:
        client (Client): The Kubernetes client.
        namespace (str): The namespace of the deployment.
        deployment_name (str): The name of the deployment.
        timeout_seconds (int): Timeout in seconds. Defaults to 600.
        interval_seconds (int): Interval between checks in seconds. Defaults to 10.

    Returns:
        None
    """
    logger.info(
        f"Waiting for deployment {deployment_name} in namespace {namespace} to be ready..."
    )
    start_time = time.time()
    while True:
        deployment: Deployment = client.get(Deployment, namespace=namespace, name=deployment_name)
        if deployment.status.availableReplicas == deployment.spec.replicas:
            logger.info(f"Deployment {deployment_name} in namespace {namespace} is ready")
            break
        elif time.time() - start_time >= timeout_seconds:
            # Surround the following block with try-except?
            # ----Block-start----
            pod: Pod = list(
                client.list(
                    Pod,
                    namespace=namespace,
                    labels={"canonical.com/dss-notebook": deployment_name},
                )
            )[0]
            reason = pod.status.containerStatuses[0].state.waiting.reason
            if reason in ["ImagePullBackOff", "ErrImagePull"]:
                raise ImagePullBackOffError(
                    f"Failed to create Deployment {deployment_name} with {reason}"
                )
            # ----Block-end----
            raise TimeoutError(
                f"Timeout waiting for deployment {deployment_name} in namespace {namespace} to be ready"  # noqa E501
            )
        else:
            time.sleep(interval_seconds)
            logger.info(
                f"Waiting for deployment {deployment_name} in namespace {namespace} to be ready..."
            )


def get_default_kubeconfig(kubeconfig: Optional[str] = None) -> str:
    """
    Get the kubeconfig file path, from input, environment variable, or default.

    Args:
        kubeconfig (str): Path to a kubeconfig file. Defaults to None.

    Returns:
        str: the value of kubeconfig if it is not None, else:
             the value of the DSS_KUBECONFIG environment variable if it is set, else:
             the default value of "./kubeconfig"

    """
    if kubeconfig:
        return kubeconfig
    elif os.environ.get(KUBECONFIG_ENV_VAR, ""):
        return os.environ.get(KUBECONFIG_ENV_VAR, "")
    else:
        return KUBECONFIG_DEFAULT


def get_lightkube_client(kubeconfig: Optional[str] = None):
    # Compute the default kubeconfig, if not specified
    kubeconfig = KubeConfig.from_file(kubeconfig)
    lightkube_client = Client(config=kubeconfig)
    return lightkube_client


def get_mlflow_tracking_uri() -> str:
    return f"http://{MLFLOW_DEPLOYMENT_NAME}.{DSS_NAMESPACE}.svc.cluster.local:5000"


def get_service_url(name: str, namespace: str, lightkube_client: Client) -> str:
    """
    Returns the URL of the service given the name of the service and None if the service is not
    found. Assumes that the service is exposed on its first port.
    """
    try:
        service = lightkube_client.get(Service, namespace=namespace, name=name)
    except ApiError as err:
        logger.error(
            f"Failed to get the url of notebook {name} with error code {err.status.code}.\n"
            "  Check the debug logs for more details."
        )
        logger.debug(f"Failed to get the url of notebook {name} with error: {err}")
        return
    ip = service.spec.clusterIP
    port = service.spec.ports[0].port
    return f"http://{ip}:{port}"


def does_notebook_exist(name: str, namespace: str, lightkube_client: Client) -> bool:
    """
    Returns True if a notebook server with the given name exists in the given namespace.

    This function returns true if either a Service or Deployment of the standard naming convention
    exists.
    """
    for resource in NOTEBOOK_RESOURCES:
        try:
            lightkube_client.get(resource, namespace=namespace, name=name)
            return True
        except ApiError as e:
            if e.response.status_code == 404:
                # Request succeeded but resource does not exist.  Continue searching
                continue
            else:
                # Something went wrong
                raise e

    # No resources found
    return False


def does_dss_pvc_exist(lightkube_client: Client) -> bool:
    """
    Returns True if the Notebooks PVC created during `dss initialize` exists in the DSS namespace.
    """
    try:
        lightkube_client.get(
            PersistentVolumeClaim, namespace=DSS_NAMESPACE, name=NOTEBOOK_PVC_NAME
        )
        return True
    except ApiError as e:
        if e.response.status_code == 404:
            # PVC not found
            return False
        else:
            # Something went wrong
            raise e


def does_mlflow_deployment_exist(lightkube_client: Client) -> bool:
    """
    Returns True if the `mlflow` Deployment created during `dss initialize`
    exists in the DSS namespace.
    """
    try:
        lightkube_client.get(Deployment, namespace=DSS_NAMESPACE, name=MLFLOW_DEPLOYMENT_NAME)
        return True
    except ApiError as e:
        if e.response.status_code == 404:
            # Deployment not found
            return False
        else:
            # Something went wrong
            raise e


def get_labels_for_node(lightkube_client: Client) -> dict:
    """
    Get the labels of the only node in the cluster.

    Args:
        lightkube_client (Client): The Kubernetes client.

    Returns:
        dict: A dictionary containing labels of the node matching the gpu_type.
    """
    nodes = list(lightkube_client.list(Node))
    if len(nodes) != 1:
        raise ValueError("Expected exactly one node in the cluster")

    return nodes[0].metadata.labels

def truncate_row(name: str, image: str, url: str, max_length: int = 80) -> tuple[str, str, str]:
    """
    Truncate the row components if the total length exceeds the maximum length.

    Args:
        name (str): The name component of the row.
        image (str): The image component of the row.
        url (str): The URL component of the row.
        max_length (int, optional): The maximum total length allowed for the row. Defaults to 80.

    Returns:
        tuple[str, str, str]: The truncated components of the row (name, image, url).
    """
    table_chars = 10  # Extra chars needed for table
    total_length = len(name) + len(image) + len(url) + table_chars
    if total_length <= max_length:
        return name, image, url
    else:
        available_space = max_length - len(name) - len(url)
        if available_space <= 0:
            return name[:max_length], "", ""
        else:
            truncated_image = image[: available_space - 3] + "..."  # Leave space for "..."
            return name, truncated_image, url
