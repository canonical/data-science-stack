from unittest.mock import MagicMock, patch

import pytest
from charmed_kubeflow_chisme.lightkube.mocking import FakeApiError

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


@pytest.fixture
def mock_does_notebook_exist() -> MagicMock:
    """
    Fixture to mock the `does_notebook_exist` function.
    """
    with patch("dss.remove_notebook.does_notebook_exist") as mock_does_notebook_exist:
        yield mock_does_notebook_exist


def test_remove_notebook_success(
    mock_client: MagicMock,
    mock_logger: MagicMock,
) -> None:
    """
    Test case to verify successful remove call.
    """
    notebook_name = "test-notebook"

    # Call the function to test
    remove_notebook(name=notebook_name, lightkube_client=mock_client)

    # Assertions
    mock_client.delete.call_count == 2
    mock_logger.info.assert_called_with(
        f"Removing the notebook {notebook_name}. Check `dss list` for the status of the notebook."
    )


def test_remove_notebook_not_found(
    mock_client: MagicMock, mock_logger: MagicMock, mock_does_notebook_exist: MagicMock
) -> None:
    """
    Tests case to verify failed remove call when all Notebook resources don't exist.
    """
    notebook_name = "test-notebook"

    mock_does_notebook_exist.return_value = False

    with pytest.raises(RuntimeError):
        remove_notebook(notebook_name, mock_client)

    # Assertions
    mock_logger.debug.assert_called_once_with(
        f"Failed to remove Notebook. Notebook {notebook_name} does not exist."
    )
    mock_logger.error.assert_called_once_with(
        f"Failed to remove Notebook. Notebook {notebook_name} does not exist."
    )
    mock_logger.info.assert_called_once_with("Run 'dss list' to check all notebooks.")


@pytest.mark.parametrize(
    "lightkube_client_side_effects, missing_resource_type",
    [([FakeApiError(404), None], "Deployment"), ([None, FakeApiError(404)], "Service")],
)
def test_remove_notebook_one_resource_not_exist(
    mock_client: MagicMock,
    mock_logger: MagicMock,
    mock_does_notebook_exist: MagicMock,
    lightkube_client_side_effects,
    missing_resource_type,
):
    """
    Tests case to verify failed remove call when one of the Notebook resources doesn't exist.
    """
    notebook_name = "test-notebook"

    mock_does_notebook_exist.return_value = True
    mock_client.delete.side_effect = lightkube_client_side_effects

    remove_notebook(notebook_name, mock_client)

    mock_logger.warn.assert_called_once_with(
        f"Failed to remove {missing_resource_type} {notebook_name}. {missing_resource_type} {notebook_name} does not exist. Ignoring."  # noqa E501
    )
    mock_logger.info.assert_called_once_with(
        f"Removing the notebook {notebook_name}. Check `dss list` for the status of the notebook."
    )


@pytest.mark.parametrize(
    "lightkube_client_side_effects, debug_log_calls",
    [
        # Removing the Deployment error
        ([FakeApiError(400), None], 2),
        # Removing the Service error
        ([None, FakeApiError(400)], 2),
        # Removing both the Deployment and Service error
        ([FakeApiError(400), FakeApiError(400)], 3),
    ],
)
def test_remove_notebook_unexpected_error(
    mock_client: MagicMock,
    mock_logger: MagicMock,
    mock_does_notebook_exist: MagicMock,
    lightkube_client_side_effects,
    debug_log_calls,
):
    """
    Tests case to verify failed remove call on an unexpected ApiError (not 404).
    """
    notebook_name = "test-notebook"

    mock_does_notebook_exist.return_value = True
    mock_client.delete.side_effect = lightkube_client_side_effects

    with pytest.raises(RuntimeError):
        remove_notebook(notebook_name, mock_client)

    assert mock_logger.debug.call_count == debug_log_calls
    mock_logger.info.assert_any_call("Note: You might want to run")
    mock_logger.info.assert_any_call("  dss status      to check the current status")
    mock_logger.info.assert_any_call(f"  dss logs {notebook_name} to review the notebook logs")
