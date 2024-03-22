from unittest.mock import MagicMock, patch

import pytest
from charmed_kubeflow_chisme.lightkube.mocking import FakeApiError

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

    # Call the function to test
    remove_notebook(name=notebook_name, lightkube_client=mock_client)

    # Assertions
    mock_client.delete.call_count == 2
    mock_logger.info.assert_called_with(f"Notebook {notebook_name} removed.")


def test_remove_notebook_not_found(
    mock_client: MagicMock,
    mock_logger: MagicMock,
) -> None:
    """
    Tests case to verify failed remove-notebook call with 404 error.
    """
    notebook_name = "test-notebook"

    mock_client.delete.side_effect = FakeApiError(404)

    # Call the function to test
    remove_notebook(name=notebook_name, lightkube_client=mock_client)

    mock_logger.warn.assert_called_with(
        "Failed to delete K8s resources not found. Ignoring remove-notebook."
    )
