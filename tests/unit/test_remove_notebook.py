from unittest.mock import MagicMock, patch

import pytest

from dss.config import DSS_NAMESPACE
from dss.remove_notebook import remove_notebook


@pytest.fixture
def mock_client() -> MagicMock:
    """
    Fixture to mock the Client class.
    """
    with patch("dss.utils.Client") as mock_client:
        yield mock_client


@pytest.fixture
def mock_logger() -> MagicMock:
    """
    Fixture to mock the logger object.
    """
    with patch("dss.remove_notebook.logger") as mock_logger:
        yield mock_logger


def test_remove_notebook_success(
    mock_client: MagicMock,
    mock_logger: MagicMock,
) -> None:
    """
    Test case to verify successful remove-notebook call.
    """
    notebook_name = "test-notebook"

    # Mock wait_for_deployment_ready
    with patch(
        "dss.remove_notebook.wait_for_deployment_deleted"
    ) as mock_wait_for_deployment_deleted:
        # Call the function to test
        remove_notebook(name=notebook_name, lightkube_client=mock_client)

        # Assertions
        mock_client.delete.call_count == 2
        mock_wait_for_deployment_deleted.assert_called_once_with(
            mock_client, namespace=DSS_NAMESPACE, deployment_name=notebook_name
        )
        mock_logger.info.assert_called_with(f"Notebook {notebook_name} removed.")
