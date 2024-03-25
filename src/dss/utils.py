import os
import time
from typing import Optional

from lightkube import ApiError, Client, KubeConfig
from lightkube.resources.apps_v1 import Deployment
from lightkube.resources.core_v1 import Service

from dss.config import DSS_NAMESPACE, MLFLOW_DEPLOYMENT_NAME
from dss.logger import setup_logger

# Set up logger
logger = setup_logger("logs/dss.log")

# Resource types used for a DSS Notebook
NOTEBOOK_RESOURCES = (Service, Deployment)

# Name for the environment variable storing kubeconfig
KUBECONFIG_ENV_VAR = "DSS_KUBECONFIG"
KUBECONFIG_DEFAULT = "./kubeconfig"


def wait_for_deployment_ready(
    client: Client,
    namespace: str,
    deployment_name: str,
    timeout_seconds: int = 60,
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


def get_notebook_url(name: str, namespace: str, lightkube_client: Client) -> str:
    """
    Returns the URL of the notebook server given the name of the server.

    Assumes the following conventions:
    * the notebook server is exposed by a service of the same name
    * the notebook service exposes the notebook on the first port in the service
    """
    service = lightkube_client.get(Service, namespace=DSS_NAMESPACE, name=name)
    ip = service.spec.clusterIP
    port = service.spec.ports[0].port
    return f"http://{ip}:{port}/notebook/{namespace}/{name}/lab"


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
