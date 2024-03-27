from lightkube import ApiError, Client
from lightkube.resources.apps_v1 import Deployment
from lightkube.resources.core_v1 import Pod

from dss.config import DSS_NAMESPACE, MLFLOW_DEPLOYMENT_NAME
from dss.logger import setup_logger

# Set up logger
logger = setup_logger("logs/dss.log")


def get_logs(parts: str, name: str, lightkube_client: Client) -> None:
    """
    Retrieve logs from specified parts of the DSS application.

    Args:
        parts (str): Specify which part's logs to retrieve: 'notebooks' or 'mlflow'.
        name (str): Name of the notebook or deployment to retrieve logs from.
        lightkube_client (Client): The Kubernetes client.

    Returns:
        None
    """
    try:
        if parts == "notebooks":
            deployment = lightkube_client.get(Deployment, name=name, namespace=DSS_NAMESPACE)
        elif parts == "mlflow":
            deployment = lightkube_client.get(
                Deployment, name=MLFLOW_DEPLOYMENT_NAME, namespace=DSS_NAMESPACE
            )
        else:
            logger.error("Invalid value for 'parts'. Use 'notebooks' or 'mlflow'.")
            return
    except ApiError:
        deployment = None

    # The get command can return empty DeploymentList object with empty spec field
    if deployment is None or deployment.spec is None:
        if parts == "notebooks":
            logger.error(f"No notebook found with the name '{name}'.")
            logger.info(
                "Please wait a moment or recreate the notebook with 'dss create-notebook'."
            )
        elif parts == "mlflow":
            logger.error("MLflow is not initialized properly.")
            logger.info("Please run 'dss initialize' first.")
        return

    selector_labels = deployment.spec.selector.matchLabels
    pods = lightkube_client.list(Pod, namespace=DSS_NAMESPACE, labels=selector_labels)

    if not pods:
        if parts == "notebooks":
            logger.error(f"No pods found for notebook - {name}.")
            logger.info(
                "Please wait a moment or recreate the notebook with 'dss create-notebook'."
            )
        elif parts == "mlflow":
            logger.error("No pods found for MLflow.")
            logger.info("Please wait a moment or run 'dss initialize' first.")
        return

    for pod in pods:
        # Retrieve logs from the pod
        logger.info(f"Logs for {pod.metadata.name}:")
        try:
            for line in lightkube_client.log(pod.metadata.name, namespace=DSS_NAMESPACE):
                logger.info(line)
        except ApiError as e:
            logger.error(f"Failed to retrieve logs for pod {pod.metadata.name}: {e}")
            if parts == "notebooks":
                logger.info(
                    "Please wait a moment or recreate the notebook with 'dss create-notebook'."
                )
            elif parts == "mlflow":
                logger.info("Please wait a moment or run 'dss initialize' first.")
