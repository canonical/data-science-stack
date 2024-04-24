from unittest.mock import MagicMock, patch

import pytest
from lightkube import ApiError

from dss.config import DSS_NAMESPACE
from dss.logs import get_logs


@pytest.fixture
def mock_client() -> MagicMock:
    """
    Fixture to mock the Client class.
    """
    with patch("dss.logs.Client") as mock_client:
        yield mock_client


@pytest.fixture
def mock_deployment() -> MagicMock:
    """
    Fixture to mock the Deployment class.
    """
    with patch("dss.logs.Deployment") as mock_deployment:
        yield mock_deployment


@pytest.fixture
def mock_pod() -> MagicMock:
    """
    Fixture to mock the Pod class.
    """
    with patch("dss.logs.Pod") as mock_pod:
        yield mock_pod


@pytest.fixture
def mock_logger() -> MagicMock:
    """
    Fixture to mock the logger object.
    """
    with patch("dss.logs.logger") as mock_logger:
        yield mock_logger


def test_get_logs_failure_notebook_not_exist(
    mock_client: MagicMock, mock_logger: MagicMock
) -> None:
    """
    Test case to verify behavior when the specified notebook does not exist.
    """
    notebook_name = "test_notebook"

    # Mock the behavior of Client
    mock_client_instance = MagicMock()
    mock_client_instance.get.return_value = None

    with pytest.raises(RuntimeError):
        # Call the function to test
        get_logs("notebooks", notebook_name, mock_client_instance)

    # Assertions
    mock_logger.debug.assert_called_with(
        f"Failed to retrieve logs. Deployment '{notebook_name}' does not exist in {DSS_NAMESPACE} namespace."  # noqa E501
    )
    mock_logger.error.assert_called_with(
        f"Failed to retrieve logs. Notebook '{notebook_name}' does not exist."
    )
    mock_logger.info.assert_called_with("Run 'dss list' to check all notebooks.")


def test_get_logs_failure_retrieve_mlflow(mock_client: MagicMock, mock_logger: MagicMock) -> None:
    """
    Test case to verify behavior when failed to retrieve MLflow logs.
    """

    # Create an ApiError instance with the Status object
    api_error = ApiError("Test exception", response=MagicMock())

    # Mock the behavior of Client
    mock_client_instance = MagicMock()
    mock_client_instance.get.side_effect = api_error
    mock_client.return_value = mock_client_instance

    # Call the function to test
    with pytest.raises(RuntimeError):
        get_logs("mlflow", None, mock_client_instance)

    # Assertions
    mock_logger.debug.assert_called_with(
        f"Failed to retrieve logs for MLflow: {api_error}", exc_info=True
    )
    mock_logger.error.assert_called_with(
        "Failed to retrieve logs. MLflow seems to be not present. Make sure DSS is correctly initialized."  # noqa: E501
    )
    mock_logger.info.assert_any_call("Note: You might want to run")
    mock_logger.info.assert_any_call("  dss status      to check the current status")
    mock_logger.info.assert_any_call("  dss logs --all  to view all logs")
    mock_logger.info.assert_any_call("  dss initialize  to install dss")


def test_get_logs_failure_retrieve_pod(
    mock_client: MagicMock, mock_deployment: MagicMock, mock_pod: MagicMock, mock_logger: MagicMock
) -> None:
    """
    Test case to verify behavior when retrieval of pods fails.
    """
    notebook_name = "test_notebook"

    # Mock the behavior of Client and Deployment
    mock_client_instance = MagicMock()
    mock_deployment_instance = MagicMock()
    mock_deployment_instance.spec.selector.matchLabels = {"app": "test_app"}
    mock_deployment_instance.spec = MagicMock()
    mock_client_instance.get.return_value = mock_deployment_instance

    # Mock the behavior of Pod with an ApiError
    api_error = ApiError(response=MagicMock())
    mock_client_instance.list.side_effect = api_error

    with pytest.raises(RuntimeError):
        # Call the function to test
        get_logs("notebooks", notebook_name, mock_client_instance)

    # Assertions
    mock_logger.debug.assert_called_with(
        f"Failed to retrieve logs for notebooks {notebook_name}: {api_error}", exc_info=True
    )
    mock_logger.error.assert_called_with(
        "Failed to retrieve logs for notebooks test_notebook. Make sure DSS is correctly initialized."  # noqa: E501
    )


def test_get_logs_success_retrieve_notebook(
    mock_client: MagicMock, mock_logger: MagicMock
) -> None:
    """
    Test case to verify successful retrieval of logs for a notebook.
    """

    # Mock the behavior of Client
    mock_client_instance = MagicMock()

    # Mock the behavior of Deployment
    mock_deployment_instance = MagicMock()
    mock_deployment_instance.metadata.name = "test_notebook"
    mock_deployment_instance.spec.selector.matchLabels = {"app": "test_app"}
    mock_deployment_instance.spec = MagicMock()

    # Mock the behavior of Pod
    mock_pod_instance = MagicMock()
    mock_pod_instance.metadata.name = "test_pod"

    # Set the return values for list method calls
    mock_client_instance.list.side_effect = [[mock_deployment_instance], [mock_pod_instance]]

    # Mock the log method of Client
    mock_client_instance.log.return_value = iter(["Log line 1", "Log line 2"])

    # Call the function to test
    get_logs("notebooks", "test_notebook", mock_client_instance)

    mock_client_instance.log.assert_called_once_with("test_pod", namespace="dss")
    mock_logger.info.assert_any_call("Logs for test_pod:")
    mock_logger.info.assert_any_call("Log line 1")
    mock_logger.info.assert_any_call("Log line 2")


def test_get_logs_success_retrieve_mlflow(mock_client: MagicMock, mock_logger: MagicMock) -> None:
    """
    Test case to verify successful retrieval of MLflow logs.
    """

    # Mock the behavior of Client and Deployment
    mock_client_instance = MagicMock()
    mock_deployment_instance = MagicMock()
    mock_deployment_instance.metadata.name = "mlflow-deployment"
    mock_deployment_instance.spec.selector.matchLabels = {"app": "mlflow"}
    mock_deployment_instance.spec = MagicMock()
    mock_client_instance.get.return_value = mock_deployment_instance

    # Mock the behavior of Pod
    mock_pod_instance = MagicMock()
    mock_pod_instance.metadata.name = "mlflow-pod"

    # Set the return values for list method calls
    mock_client_instance.list.return_value = [mock_pod_instance]

    # Mock the log method of Client
    mock_client_instance.log.return_value = iter(["Log line 1", "Log line 2"])

    # Call the function to test
    get_logs("mlflow", None, mock_client_instance)

    # Assertions
    mock_client_instance.log.assert_called_once_with("mlflow-pod", namespace="dss")
    mock_logger.info.assert_any_call("Logs for mlflow-pod:")
    mock_logger.info.assert_any_call("Log line 1")
    mock_logger.info.assert_any_call("Log line 2")


def test_get_logs_success_retrieve_all(mock_client: MagicMock, mock_logger: MagicMock) -> None:
    """
    Test case to verify successful retrieval of logs for all deployments.
    """

    # Mock the behavior of Client and Deployments
    mock_client_instance = MagicMock()

    # Mock deployments
    mock_notebook_deployment = MagicMock()
    mock_notebook_deployment.metadata.name = "notebook-deployment"
    mock_notebook_deployment.spec.selector.matchLabels = {"app": "notebook"}
    mock_notebook_deployment.spec = MagicMock()

    mock_mlflow_deployment = MagicMock()
    mock_mlflow_deployment.metadata.name = "mlflow"
    mock_mlflow_deployment.spec.selector.matchLabels = {"app": "mlflow"}
    mock_mlflow_deployment.spec = MagicMock()

    # Mock the behavior of Pods
    mock_notebook_pod = MagicMock()
    mock_notebook_pod.metadata.name = "notebook-pod"

    mock_mlflow_pod = MagicMock()
    mock_mlflow_pod.metadata.name = "mlflow-pod"

    # Set the return values for list method calls
    mock_client_instance.list.side_effect = [
        [mock_notebook_deployment, mock_mlflow_deployment],
        [mock_notebook_pod],
        [mock_mlflow_pod],
    ]

    # Mock the log method of Client
    mock_client_instance.log.side_effect = [
        iter(["Log line 1 for notebook-pod", "Log line 2 for notebook-pod"]),
        iter(["Log line 1 for mlflow-pod", "Log line 2 for mlflow-pod"]),
    ]

    # Call the function to test
    get_logs("all", None, mock_client_instance)

    # Assertions
    assert mock_client_instance.list.call_count == 3
    mock_client_instance.log.assert_any_call("notebook-pod", namespace="dss")
    mock_client_instance.log.assert_called_with("mlflow-pod", namespace="dss")
    mock_logger.info.assert_any_call("Logs for notebook-pod:")
    mock_logger.info.assert_any_call("Log line 1 for notebook-pod")
    mock_logger.info.assert_any_call("Log line 2 for notebook-pod")
    mock_logger.info.assert_any_call("Logs for mlflow-pod:")
    mock_logger.info.assert_any_call("Log line 1 for mlflow-pod")
    mock_logger.info.assert_any_call("Log line 2 for mlflow-pod")


def test_get_logs_failure_retrieve_pod_logs(
    mock_client: MagicMock, mock_logger: MagicMock
) -> None:
    """
    Test case to verify behavior when there is a failure retrieving logs from a pod.
    """

    # Mock the behavior of Client
    mock_client_instance = MagicMock()

    # Mock the behavior of Deployment
    mock_deployment_instance = MagicMock()
    mock_deployment_instance.metadata.name = "test_notebook"
    mock_deployment_instance.spec.selector.matchLabels = {"app": "test_app"}
    mock_deployment_instance.spec = MagicMock()

    # Mock the behavior of Pod
    mock_pod_instance = MagicMock()
    pod_name = "test_pod"
    mock_pod_instance.metadata.name = pod_name

    # Set the return values for list method calls
    mock_client_instance.list.side_effect = [[mock_deployment_instance], [mock_pod_instance]]

    # Mock the log method of Client to raise an exception
    api_error = ApiError("Test error", response=MagicMock())
    mock_client_instance.log.side_effect = api_error

    # Call the function to test
    with pytest.raises(RuntimeError):
        get_logs("notebooks", "test_notebook", mock_client_instance)

    # Assertions
    mock_logger.debug.assert_called_with(
        f"Failed to retrieve logs for pod {pod_name}: {api_error}", exc_info=True
    )
    mock_logger.error.assert_any_call(
        f"Failed to retrieve logs. There was a problem while getting the logs for {pod_name}"
    )
