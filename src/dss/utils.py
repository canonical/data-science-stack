import os
import time
from pathlib import Path
from typing import Optional, Union

import lightkube
from lightkube import ApiError, Client, KubeConfig
from lightkube.resources.apps_v1 import Deployment
from lightkube.resources.core_v1 import Namespace, Node, PersistentVolumeClaim, Pod, Service

from dss.config import (
    DSS_NAMESPACE,
    MLFLOW_DEPLOYMENT_NAME,
    NOTEBOOK_LABEL,
    NOTEBOOK_PVC_NAME,
    DeploymentState,
)
from dss.logger import setup_logger

# Set up logger
logger = setup_logger("logs/dss.log")

# Resource types used for a DSS Notebook
NOTEBOOK_RESOURCES = (Service, Deployment)

# Name for the environment variable storing kubeconfig
KUBECONFIG_ENV_VAR = "DSS_KUBECONFIG"
KUBECONFIG_DEFAULT = Path.home() / ".dss/config"


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
                    labels={NOTEBOOK_LABEL: deployment_name},
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
            logger.info(
                f"Waiting for deployment {deployment_name} in namespace {namespace} to be ready..."
            )


def get_kubeconfig_path(
    env_var: str = KUBECONFIG_ENV_VAR,
    default_kubeconfig_location: Union[Path, str] = KUBECONFIG_DEFAULT,
) -> Path:
    """
    Returns the path to the kubeconfig used by DSS

    This will return:
    * the kubeconfig file at the path specified by the given environment variable, if set
    * otherwise, the kubeconfig file at the default path given

    Args:
        env_var (str): The name of the environment variable to check for the kubeconfig path.
        default_kubeconfig_location (Path or str): The default path to the kubeconfig file if not
                                                   specified by the environment variable.

    Returns:
        Path: the path to the kubeconfig file
    """
    # use expanduser() to handle '~' in the path
    return Path(os.environ.get(env_var, default_kubeconfig_location)).expanduser()


def get_kubeconfig(
    env_var: str = KUBECONFIG_ENV_VAR,
    default_kubeconfig_location: Union[Path, str] = KUBECONFIG_DEFAULT,
) -> lightkube.KubeConfig:
    """Returns the kubeconfig used by DSS as a lightkube.KubeConfig object or fails if it not found.

    This will return:
    * the kubeconfig file at the path specified by the given environment variable, if set
    * otherwise, the kubeconfig file at the default path given

    Args:
        env_var (str): The name of the environment variable to check for the kubeconfig path.
        default_kubeconfig_location (Path or str): The default path to the kubeconfig file if not
                                                   specified by the environment variable.

    Returns:
        lightkube.KubeConfig: the value of kubeconfig
    """
    kubeconfig_path = get_kubeconfig_path(env_var, default_kubeconfig_location)
    return KubeConfig.from_file(kubeconfig_path)


def save_kubeconfig(
    kubeconfig: str,
    env_var: str = KUBECONFIG_ENV_VAR,
    default_kubeconfig_location: Union[Path, str] = KUBECONFIG_DEFAULT,
) -> None:
    """
    Save the kubeconfig file to the specified location.

    This will create the parent directory if it does not exist.

    Args:
        kubeconfig (str): The kubeconfig file contents.
        env_var (str): The name of the environment variable to check for the kubeconfig path.
        default_kubeconfig_location (str): The default path to the kubeconfig file if not
                                           specified by the environment variable.

    Returns:
        None
    """
    save_location = get_kubeconfig_path(env_var, default_kubeconfig_location)
    logger.info(f"Storing provided kubeconfig to {save_location}")

    # Create the parent directory, if it does not exist
    save_location.parent.mkdir(exist_ok=True)

    with open(save_location, "w") as f:
        f.write(kubeconfig)


def get_lightkube_client() -> lightkube.Client:
    """Returns a lightkube client configured with the kubeconfig used by DSS."""
    kubeconfig = get_kubeconfig()
    lightkube_client = Client(config=kubeconfig)
    return lightkube_client


def get_mlflow_tracking_uri() -> str:
    """Returns the MLflow tracking URI for the DSS deployment."""
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


def intel_is_present_in_node(lightkube_client: Client) -> bool:
    """Return True if the Node has the intel GPU label, False otherwise.

    Args:
        lightkube_client (Client): The Kubernetes client.
    """
    try:
        node_labels = get_labels_for_node(lightkube_client)
    except ValueError as e:
        logger.debug(f"Failed to get labels for nodes: {e}.", exc_info=True)
        logger.error(f"Failed to retrieve status: {e}.")
        raise RuntimeError()
    if "intel.feature.node.kubernetes.io/gpu" in node_labels:
        return True
    return False


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
                    "ContainerCreating",
                ]:
                    return DeploymentState.DOWNLOADING
                elif container_status.state.waiting.reason in [
                    "ImagePullBackOff",
                    "ErrImagePull",
                ]:
                    return DeploymentState.ERRIMAGE

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
