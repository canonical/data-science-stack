from unittest.mock import MagicMock, patch

import pytest

from dss.config import DSS_NAMESPACE
from dss.create_notebook import create_notebook


@pytest.fixture
def mock_get_notebook_url() -> MagicMock:
    """
    Fixture to mock the get_notebook_url function.
    """
    with patch("dss.create_notebook.get_notebook_url") as mock_get_notebook_url:
        yield mock_get_notebook_url


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
    mock_get_notebook_url: MagicMock,
    mock_resource_handler: MagicMock,
    mock_logger: MagicMock,
) -> None:
    """
    Test case to verify successful create_notebook call.
    """
    notebook_name = "test-notebook"
    notebook_image = "test-image"
    notebook_url = "http://somewhere.com:1234/notebook/namespace/name/lab"

    # Mock the behavior of Client
    mock_client_instance = MagicMock()

    mock_get_notebook_url.return_value = notebook_url

    # Mock the behavior of KubernetesResourceHandler
    mock_resource_handler_instance = MagicMock()
    mock_resource_handler.return_value = mock_resource_handler_instance

    with patch("dss.create_notebook.does_dss_pvc_exist", return_value=True), patch(
        "dss.create_notebook.does_notebook_exist", return_value=False
    ), patch("dss.create_notebook.wait_for_deployment_ready") as mock_wait_for_deployment_ready:
        # Call the function to test
        create_notebook(
            name=notebook_name, image=notebook_image, lightkube_client=mock_client_instance
        )

        # Assertions
        mock_resource_handler_instance.apply.assert_called_once()
        mock_wait_for_deployment_ready.assert_called_once_with(
            mock_client_instance, namespace=DSS_NAMESPACE, deployment_name=notebook_name
        )
        mock_logger.info.assert_called_with(f"Access the notebook at {notebook_url}.")
