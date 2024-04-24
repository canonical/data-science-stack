from lightkube import Client
from lightkube.core.exceptions import ApiError
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
        parts (str): Specify which part's logs to retrieve: 'notebooks', 'mlflow', or 'all'.
        name (str): Name of the notebook or deployment to retrieve logs from.
            This parameter is required for 'notebooks' logs but not for 'mlflow' or 'all'.
        lightkube_client (Client): The Kubernetes client.

    Returns:
        None
    """
    try:
        if parts == "notebooks":
            notebook_deployments = list(lightkube_client.list(Deployment, namespace=DSS_NAMESPACE))
            for deployment in notebook_deployments:
                if deployment.metadata.name == name:
                    break
            else:
                logger.debug(
                    f"Failed to retrieve logs. Deployment '{name}' does not exist in {DSS_NAMESPACE} namespace."  # noqa E501
                )
                logger.error(f"Failed to retrieve logs. Notebook '{name}' does not exist.")
                logger.info("Run 'dss list' to check all notebooks.")
                raise RuntimeError()
            pods = lightkube_client.list(
                Pod, namespace=DSS_NAMESPACE, labels=deployment.spec.selector.matchLabels
            )
        elif parts == "mlflow":
            try:
                mlflow_deployment = lightkube_client.get(
                    Deployment, name=MLFLOW_DEPLOYMENT_NAME, namespace=DSS_NAMESPACE
                )
                pods = lightkube_client.list(
                    Pod,
                    namespace=DSS_NAMESPACE,
                    labels=mlflow_deployment.spec.selector.matchLabels,
                )
            except ApiError as e:
                logger.debug(f"Failed to retrieve logs for MLflow: {e}", exc_info=True)
                logger.error(
                    "Failed to retrieve logs. MLflow seems to be not present. Make sure DSS is correctly initialized."  # noqa: E501
                )
                logger.info("Note: You might want to run")
                logger.info("  dss status      to check the current status")
                logger.info("  dss logs --all  to view all logs")
                logger.info("  dss initialize  to install dss")
                raise RuntimeError()
        elif parts == "all":
            deployments = list(lightkube_client.list(Deployment, namespace=DSS_NAMESPACE))
            pods = []
            for deployment in deployments:
                pods += list(
                    lightkube_client.list(
                        Pod, namespace=DSS_NAMESPACE, labels=deployment.spec.selector.matchLabels
                    )
                )
    except ApiError as e:
        logger.debug(f"Failed to retrieve logs for {parts} {name}: {e}", exc_info=True)
        logger.error(
            f"Failed to retrieve logs for {parts} {name}. Make sure DSS is correctly initialized."  # noqa: E501
        )
        logger.info("Note: You might want to run")
        logger.info("  dss status      to check the current status")
        logger.info("  dss initialize  to install dss")
        raise RuntimeError()

    if not pods:
        logger.debug(f"Failed to retrieve logs. No pods found for {parts} {name}.")
        logger.error(f"Failed to retrieve logs. No pods found for {parts} {name}.")
        raise RuntimeError()

    for pod in pods:
        # Retrieve logs from the pod
        logger.info(f"Logs for {pod.metadata.name}:")
        try:
            for line in lightkube_client.log(pod.metadata.name, namespace=DSS_NAMESPACE):
                # Remove the newline character from the end of the log message
                line = line.rstrip("\n")
                logger.info(line)
        except ApiError as e:
            logger.debug(
                f"Failed to retrieve logs for pod {pod.metadata.name}: {e}", exc_info=True
            )
            logger.error(
                f"Failed to retrieve logs. There was a problem while getting the logs for {pod.metadata.name}"  # noqa: E501
            )
            raise RuntimeError()
