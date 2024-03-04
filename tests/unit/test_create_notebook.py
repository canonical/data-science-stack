from unittest.mock import MagicMock, patch

import pytest
from lightkube.models.core_v1 import Service, ServicePort, ServiceSpec

from dss.config import DSS_NAMESPACE
from dss.create_notebook import _get_notebook_url, create_notebook


@pytest.fixture
def mock_client() -> MagicMock:
    """
    Fixture to mock the Client class.
    """
    with patch("dss.create_notebook.Client") as mock_client:
        yield mock_client


@pytest.fixture
def mock_resource_handler() -> MagicMock:
    """
    Fixture to mock the KubernetesResourceHandler class.
    """
    with patch("dss.create_notebook.KubernetesResourceHandler") as mock_handler:
        yield mock_handler


@pytest.fixture
def mock_logger() -> MagicMock:
    """
    Fixture to mock the logger object.
    """
    with patch("dss.create_notebook.logger") as mock_logger:
        yield mock_logger


def test_create_notebook_success(
    mock_client: MagicMock,
    mock_resource_handler: MagicMock,
    mock_logger: MagicMock,
) -> None:
    """
    Test case to verify successful create-notebook call.
    """
    notebook_name = "test-notebook"
    notebook_image = "test-image"

    # Mock the behavior of Client
    mock_client_instance = MagicMock()

    # Mock the behavior of KubernetesResourceHandler
    mock_resource_handler_instance = MagicMock()
    mock_resource_handler.return_value = mock_resource_handler_instance

    # Mock wait_for_deployment_ready
    with patch("dss.create_notebook.wait_for_deployment_ready") as mock_wait_for_deployment_ready:
        # Call the function to test
        create_notebook(
            name=notebook_name, image=notebook_image, lightkube_client=mock_client_instance
        )

        # Assertions
        mock_resource_handler_instance.apply.assert_called_once()
        mock_wait_for_deployment_ready.assert_called_once_with(
            mock_client_instance, namespace=DSS_NAMESPACE, deployment_name=notebook_name
        )
        mock_logger.info.assert_called_with("Notebook created.")


def test_get_notebook_url() -> None:
    """
    Test the get_notebook_url helper.
    """
    name = "name"
    namespace = "namespace"
    ip = "1.1.1.1"
    port = 8765
    expected_url = f"http://{ip}:{port}/notebook/{namespace}/{name}/lab"

    mock_service = Service(spec=ServiceSpec(clusterIP=ip, ports=[ServicePort(port=port)]))
    mock_client = MagicMock()
    mock_client.get.return_value = mock_service

    actual_url = _get_notebook_url(name=name, namespace=namespace, lightkube_client=mock_client)

    assert actual_url == expected_url
