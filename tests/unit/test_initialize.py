from unittest.mock import MagicMock, patch

import pytest
from lightkube.resources.apps_v1 import Deployment

from dss.initialize import initialize, wait_for_deployment_ready


@pytest.fixture
def mock_environ_get() -> MagicMock:
    """
    Fixture to mock the os.environ.get function.
    """
    with patch("dss.initialize.os.environ.get") as mock_env_get:
        yield mock_env_get


@pytest.fixture
def mock_kubeconfig_from_dict() -> MagicMock:
    """
    Fixture to mock the KubeConfig.from_dict function.
    """
    with patch("dss.initialize.KubeConfig.from_dict") as mock_kubeconfig:
        yield mock_kubeconfig


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
def mock_load_generic_resources() -> MagicMock:
    """
    Fixture to mock the load_in_cluster_generic_resources function.
    """
    with patch("dss.initialize.load_in_cluster_generic_resources") as mock_load:
        yield mock_load


@pytest.fixture
def mock_logger() -> MagicMock:
    """
    Fixture to mock the logger object.
    """
    with patch("dss.initialize.logger") as mock_logger:
        yield mock_logger


def test_initialize_success(
    mock_environ_get: MagicMock,
    mock_kubeconfig_from_dict: MagicMock,
    mock_client: MagicMock,
    mock_resource_handler: MagicMock,
    mock_load_generic_resources: MagicMock,
    mock_logger: MagicMock,
) -> None:
    """
    Test case to verify successful initialization.
    """
    # Mock the return value of os.environ.get
    mock_environ_get.return_value = "dummy_kubeconfig_content"

    # Mock the behavior of KubeConfig.from_dict
    mock_kubeconfig = MagicMock()
    mock_kubeconfig_from_dict.return_value = mock_kubeconfig

    # Mock the behavior of Client
    mock_client_instance = MagicMock()
    mock_client.return_value = mock_client_instance

    # Mock the behavior of KubernetesResourceHandler
    mock_resource_handler_instance = MagicMock()
    mock_resource_handler.return_value = mock_resource_handler_instance

    # Mock wait_for_deployment_ready
    with patch("dss.initialize.wait_for_deployment_ready") as mock_wait_for_deployment_ready:
        # Call the function to test
        initialize()

        # Assertions
        mock_environ_get.assert_called_once_with("DSS_KUBECONFIG", "")
        mock_kubeconfig_from_dict.assert_called_once_with("dummy_kubeconfig_content")
        mock_client.assert_called_once_with(mock_kubeconfig)
        mock_load_generic_resources.assert_called_once_with(mock_client_instance)
        mock_resource_handler_instance.apply.assert_called_once()
        mock_wait_for_deployment_ready.assert_called_once_with(
            mock_client_instance, namespace="dss", deployment_name="mlflow-deployment"
        )
        mock_logger.info.assert_called_with(
            "DSS initialized. To create your first notebook run the command:\n\ndss create-notebook"
        )


def test_initialize_missing_kubeconfig_env_var(
    mock_environ_get: MagicMock,
    mock_kubeconfig_from_dict: MagicMock,
    mock_client: MagicMock,
    mock_load_generic_resources: MagicMock,
) -> None:
    """
    Test case to verify missing kubeconfig environment variable.
    """
    # Mock the absence of the DSS_KUBECONFIG environment variable
    mock_environ_get.return_value = ""

    # Call the function to test
    with pytest.raises(ValueError) as exc_info:
        initialize()

    # Assertions
    assert (
        str(exc_info.value)
        == "Kubeconfig content not found in environment variable DSS_KUBECONFIG"
    )
    mock_environ_get.assert_called_once_with("DSS_KUBECONFIG", "")
    mock_kubeconfig_from_dict.assert_not_called()
    mock_client.assert_not_called()
    mock_load_generic_resources.assert_not_called()


def test_wait_for_deployment_ready_timeout(mock_client: MagicMock, mock_logger: MagicMock) -> None:
    """
    Test case to verify timeout while waiting for deployment to be ready.
    """
    # Mock the behavior of the client.get method to return a deployment with available replicas = 0
    mock_client_instance = MagicMock()
    mock_client_instance.get.return_value = MagicMock(
        spec=Deployment, status=MagicMock(availableReplicas=0), spec_replicas=1
    )

    # Call the function to test
    with pytest.raises(TimeoutError) as exc_info:
        wait_for_deployment_ready(
            mock_client_instance,
            namespace="test-namespace",
            deployment_name="test-deployment",
            timeout_seconds=5,
            interval_seconds=1,
        )

    # Assertions
    assert (
        str(exc_info.value)
        == "Timeout waiting for deployment test-deployment in namespace test-namespace to be ready"
    )
    assert mock_client_instance.get.call_count == 6  # 5 attempts, 1 final attempt after timeout
