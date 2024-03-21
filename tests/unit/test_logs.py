from unittest.mock import MagicMock, patch

import pytest
from lightkube import ApiError

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


def test_get_logs_no_deployment(mock_client: MagicMock, mock_logger: MagicMock) -> None:
    """
    Test case to verify behavior when no deployment is found.
    """

    # Create an ApiError instance with the Status object
    api_error = ApiError("Test exception", response=MagicMock())

    # Mock the behavior of Client
    mock_client_instance = MagicMock()
    mock_client_instance.get.side_effect = api_error
    mock_client.return_value = mock_client_instance

    # Call the function to test
    get_logs("notebooks", "test_notebook", mock_client_instance)

    # Assertions
    mock_logger.error.assert_called_with("No notebook found with the name 'test_notebook'.")


def test_get_logs_no_pods(
    mock_client: MagicMock, mock_deployment: MagicMock, mock_pod: MagicMock, mock_logger: MagicMock
) -> None:
    """
    Test case to verify behavior when no pods are found.
    """
    mock_client_instance = MagicMock()
    mock_deployment_instance = MagicMock()
    mock_deployment_instance.spec.selector.matchLabels = {"app": "test_app"}
    mock_deployment_instance.spec = MagicMock()
    mock_client_instance.get.return_value = mock_deployment_instance

    mock_pod_instance = MagicMock()
    mock_pod_instance.metadata.name = "test_pod"
    mock_client_instance.list.return_value = []
    mock_pod.return_value = mock_pod_instance

    get_logs("notebooks", "test_notebook", mock_client_instance)

    mock_logger.error.assert_called_with("No pods found for notebook - test_notebook.")


def test_get_logs_success(
    mock_client: MagicMock, mock_deployment: MagicMock, mock_pod: MagicMock, mock_logger: MagicMock
) -> None:
    """
    Test case to verify successful retrieval of logs.
    """
    # Mock deployment and pod instances
    mock_client_instance = MagicMock()
    mock_deployment_instance = MagicMock()
    mock_deployment_instance.spec.selector.matchLabels = {"app": "test_app"}
    mock_deployment_instance.spec = MagicMock()
    mock_client_instance.get.return_value = mock_deployment_instance

    mock_pod_instance = MagicMock()
    mock_pod_instance.metadata.name = "test_pod"
    mock_pod_instance.status.containerStatuses[0].state.waiting = None
    mock_client_instance.list.return_value = [mock_pod_instance]

    # Call the function to test
    get_logs("notebooks", "test_notebook", mock_client_instance)

    # Assertions
    mock_logger.info.assert_called_with("Logs for test_pod:")
    mock_client_instance.log.assert_called_once_with("test_pod", namespace="dss")
    mock_logger.error.assert_not_called()
