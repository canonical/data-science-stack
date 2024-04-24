import os
import time
from typing import List, Optional

from lightkube import ApiError, Client, KubeConfig
from lightkube.resources.apps_v1 import Deployment
from lightkube.resources.core_v1 import Namespace, Node, PersistentVolumeClaim, Pod, Service

from dss.config import DSS_NAMESPACE, MLFLOW_DEPLOYMENT_NAME, NOTEBOOK_PVC_NAME, DeploymentState
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


def node_has_gpu_labels(lightkube_client: Client, labels: List[str]) -> bool:
    """
    Check if at least one node in the Kubernetes cluster has all the specified labels.

    Args:
        lightkube_client (Client): The Kubernetes client.
        labels (List[str]): A list of label keys that must be present on the node.

    Returns:
        bool: True if at least one node has all the specified labels, False otherwise.
    """
    nodes = lightkube_client.list(Node)
    for node in nodes:
        node_labels = node.metadata.labels
        if all(label in node_labels for label in labels):
            return True
    return False


def wait_for_deployment_ready(
    client: Client,
    namespace: str,
    deployment_name: str,
    timeout_seconds: Optional[int] = 180,
    interval_seconds: int = 10,
) -> None:
    """
    Waits for a Kubernetes deployment to be ready. Can wait indefinitely if timeout_seconds is None.

    Args:
        client (Client): The Kubernetes client.
        namespace (str): The namespace of the deployment.
        deployment_name (str): The name of the deployment.
        timeout_seconds (Optional[int]): Timeout in seconds, or None for no timeout.
                                         Defaults to 180.
        interval_seconds (int): Interval between checks in seconds. Defaults to 10.

    Raises:
        ImagePullBackOffError: If there is an issue pulling the deployment image.
        TimeoutError: If the timeout is reached before the deployment is ready.
    """
    logger.info(
        f"Waiting for deployment {deployment_name} in namespace {namespace} to be ready..."
    )
    start_time = time.time()
    while True:
        deployment: Deployment = client.get(Deployment, namespace=namespace, name=deployment_name)
        if deployment.status and deployment.status.availableReplicas == deployment.spec.replicas:
            logger.info(f"Deployment {deployment_name} in namespace {namespace} is ready")
            break
        try:
            pods = list(
                client.list(
                    Pod,
                    namespace=namespace,
                    labels={"canonical.com/dss-notebook": deployment_name},
                )
            )
        except ApiError as e:
            if e.response.status_code == 404:
                pods = []

        if pods:
            reason = (
                pods[0].status.containerStatuses[0].state.waiting.reason
                if pods[0].status.containerStatuses
                and pods[0].status.containerStatuses[0].state.waiting
                else "Unknown"
            )
            if reason in ["ImagePullBackOff", "ErrImagePull"]:
                raise ImagePullBackOffError(
                    f"Failed to create Deployment {deployment_name} with {reason}"
                )

        if timeout_seconds is not None and time.time() - start_time >= timeout_seconds:
            raise TimeoutError(
                f"Timeout waiting for deployment {deployment_name} in namespace {namespace} to be ready"  # noqa E501
            )
        else:
            time.sleep(interval_seconds)
            logger.debug(
                f"Still waiting for deployment {deployment_name} in namespace {namespace} to be ready..."  # noqa E501
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
    Returns the URL of the service given the name of the service.
    Assumes that the service is exposed on its first port.
    Returns None if the service is not found or if an error occurs,
    logging the issue as an error.

    Args:
        name (str): The name of the service.
        namespace (str): The namespace where the service is located.
        lightkube_client (Client): The Kubernetes client.

    Returns:
        str or None: The URL of the service if found and has at least one port, otherwise None.
    """
    try:
        service = lightkube_client.get(Service, namespace=namespace, name=name)
    except ApiError as err:
        logger.error(
            f"Failed to get the URL of notebook {name} with error code {err.status.code}.\n"
            "Check the debug logs for more details."
        )
        logger.debug(f"Failed to get the URL of notebook {name} with error: {err}")
        return None

    if not service.spec.ports:
        logger.error(f"No ports defined for the service {name} in namespace {namespace}.")
        return None

    ip = service.spec.clusterIP
    port = service.spec.ports[
        0
    ].port  # Consider parameterizing or handling multiple ports if needed
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


def get_deployment_state(deployment: Deployment, lightkube_client: Client) -> DeploymentState:
    """
    Determine the state of a Kubernetes deployment, which is constrained to 0 or 1 replicas.

    Args:
        deployment (Deployment): The deployment object.
        lightkube_client (Client): The Kubernetes client.

    Returns:
        DeploymentState: The state of the deployment as an enumeration.
    """
    # Extract replica counts and deletion timestamp from deployment
    desired_replicas = deployment.spec.replicas if deployment.spec.replicas is not None else 0
    current_replicas = deployment.status.replicas if deployment.status.replicas is not None else 0
    deletion_timestamp = deployment.metadata.deletionTimestamp

    # Check for deployment deletion
    if deletion_timestamp:
        return DeploymentState.REMOVING

    # Check pod statuses for image pulling issues and container creation
    pods = lightkube_client.list(
        Pod, namespace=deployment.metadata.namespace, labels=deployment.spec.selector.matchLabels
    )
    for pod in pods:
        container_statuses = (
            pod.status.containerStatuses if pod.status.containerStatuses is not None else []
        )
        for container_status in container_statuses:
            if container_status.state.waiting:
                if container_status.state.waiting.reason in [
                    "ImagePullBackOff",
                    "ErrImagePull",
                    "ContainerCreating",
                ]:
                    return DeploymentState.DOWNLOADING

    # Determine the state based on replica counts
    if desired_replicas == 0:
        if current_replicas == 0:
            return DeploymentState.STOPPED
        else:
            return DeploymentState.STOPPING
    elif desired_replicas == 1:
        if current_replicas == 0:
            return DeploymentState.STARTING
        else:
            # Check if all replicas are available
            available_replicas = (
                deployment.status.availableReplicas
                if deployment.status.availableReplicas is not None
                else 0
            )
            if available_replicas < 1:
                return DeploymentState.STARTING
            return DeploymentState.ACTIVE
    else:
        DeploymentState.UNKNOWN


def does_namespace_exist(lightkube_client: Client, namespace: str) -> bool:
    """
    Returns:
        True if the given namespace exists and False if the request returns a 404.

    Raises:
        ApiError if the request raises an error that is not a 404.
    """
    try:
        lightkube_client.get(Namespace, name=namespace)
        return True
    except ApiError as err:
        if err.response.status_code == 404:
            # Namespace was not found
            return False
        else:
            raise err


def wait_for_namespace_to_be_deleted(
    lightkube_client: Client,
    namespace: str,
    interval_seconds: int = 10,
) -> None:
    """
    Waits for a namespace to be deleted.

    Args:
        lightkube_client (Client): The Kubernetes client.
        namespace (str): The namespace being deleted.
        interval_seconds (int): Interval between checks in seconds. Defaults to 10.

    Returns:
        None

    Raises:
        ApiError if helper does_namespace_exist() raises an ApiError.
    """
    while True:
        logger.info(f"Waiting for namespace {namespace} to be deleted...")
        if does_namespace_exist(lightkube_client, DSS_NAMESPACE):
            time.sleep(interval_seconds)
        else:
            break
