from unittest.mock import MagicMock, patch

import pytest

from dss.initialize import initialize


@pytest.fixture
def mock_client() -> MagicMock:
    """
    Fixture to mock the Client class.
    """
    with patch("dss.initialize.Client") as mock_client:
        yield mock_client


@pytest.fixture
def mock_resource_handler() -> MagicMock:
    """
    Fixture to mock the KubernetesResourceHandler class.
    """
    with patch("dss.initialize.KubernetesResourceHandler") as mock_handler:
        yield mock_handler


@pytest.fixture
def mock_logger() -> MagicMock:
    """
    Fixture to mock the logger object.
    """
    with patch("dss.initialize.logger") as mock_logger:
        yield mock_logger


def test_initialize_success(
    mock_client: MagicMock,
    mock_resource_handler: MagicMock,
    mock_logger: MagicMock,
) -> None:
    """
    Test case to verify successful initialization.
    """
    # Mock the behavior of Client
    mock_client_instance = MagicMock()
    mock_client.return_value = mock_client_instance

    # Mock the behavior of KubernetesResourceHandler
    mock_resource_handler_instance = MagicMock()
    mock_resource_handler.return_value = mock_resource_handler_instance

    # Mock wait_for_deployment_ready
    with patch("dss.initialize.wait_for_deployment_ready") as mock_wait_for_deployment_ready:
        # Call the function to test
        initialize(lightkube_client=mock_client_instance)

        # Assertions
        mock_resource_handler_instance.apply.assert_called_once()
        mock_wait_for_deployment_ready.assert_called_once_with(
            mock_client_instance, namespace="dss", deployment_name="mlflow"
        )
        mock_logger.info.assert_called_with(
            "DSS initialized. To create your first notebook run the command:\n\ndss create-notebook"
        )
