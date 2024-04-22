from unittest.mock import MagicMock, patch

import pytest
from lightkube import ApiError
from lightkube.resources.apps_v1 import Deployment

from dss.config import NOTEBOOK_LABEL, DeploymentState
from dss.list import list_notebooks

TEST_IMAGE = "deployment_image"
TEST_DEPLOYMENT_NAME = "notebook_name"
TEST_SVC = "http://example.com"


@pytest.fixture
def mock_client() -> MagicMock:
    """Mock Kubernetes Client."""
    with patch("dss.list.Client") as mock:
        yield mock.return_value


@pytest.fixture
def mock_deployment() -> MagicMock:
    """Mock Deployment with predefined attributes and correct labels."""
    deployment = MagicMock(spec=Deployment)
    deployment.metadata.name = TEST_DEPLOYMENT_NAME
    deployment.metadata.labels = {NOTEBOOK_LABEL: TEST_DEPLOYMENT_NAME}
    deployment.spec.template.spec.containers = [MagicMock(image=TEST_IMAGE)]
    deployment.spec.replicas = 1
    deployment.status.replicas = 1
    deployment.status.availableReplicas = 1
    return deployment


@pytest.fixture
def mock_get_deployment_state() -> MagicMock:
    """Mock the deployment state retrieval function."""
    with patch("dss.list.get_deployment_state") as mock:
        yield mock


@pytest.fixture
def mock_get_service_url() -> MagicMock:
    """Mock the service URL retrieval function."""
    with patch("dss.list.get_service_url") as mock:
        yield mock


@pytest.fixture
def mock_logger() -> MagicMock:
    """Mock the logger for capturing log outputs."""
    with patch("dss.list.logger") as mock:
        yield mock


@pytest.fixture
def mock_pretty_table() -> MagicMock:
    """Mock the PrettyTable class."""
    with patch("dss.list.PrettyTable") as mock:
        yield mock.return_value


def test_successful_notebook_listing(
    mock_client: MagicMock,
    mock_deployment: MagicMock,
    mock_get_service_url: MagicMock,
    mock_get_deployment_state: MagicMock,
    mock_pretty_table: MagicMock,
) -> None:
    """Test successful listing of notebooks and correct function calls."""
    mock_client.list.return_value = [mock_deployment]
    mock_get_deployment_state.return_value = DeploymentState.ACTIVE
    mock_get_service_url.return_value = TEST_SVC

    list_notebooks(mock_client, wide=False)

    mock_get_service_url.assert_called_once_with(TEST_DEPLOYMENT_NAME, "dss", mock_client)
    mock_pretty_table.add_row.assert_called_once_with([TEST_DEPLOYMENT_NAME, TEST_IMAGE, TEST_SVC])


def test_listing_failure_due_to_api_error(mock_client: MagicMock) -> None:
    """
    Verify that a RuntimeError is raised when an API error occurs during the listing of deployments.
    """
    mock_client.list.side_effect = ApiError(response=MagicMock())

    with pytest.raises(RuntimeError):
        list_notebooks(mock_client)


def test_no_notebooks_found(mock_client: MagicMock, mock_logger: MagicMock) -> None:
    """
    Test that the appropriate message is displayed when no deployments are found.
    """
    mock_client.list.return_value = []

    list_notebooks(mock_client, wide=False)

    mock_logger.info.assert_called_with("No notebooks found.")


@pytest.mark.parametrize(
    "state, expected_url",
    [
        (DeploymentState.DOWNLOADING, "(Downloading)"),
        (DeploymentState.STOPPING, "(Stopping)"),
        (DeploymentState.STOPPED, "(Stopped)"),
        (DeploymentState.REMOVING, "(Removing)"),
        (DeploymentState.UNKNOWN, "(Unknown)"),
    ],
)
def test_non_active_deployment_url_representation(
    state: DeploymentState,
    expected_url: str,
    mock_client: MagicMock,
    mock_deployment: MagicMock,
    mock_get_deployment_state: MagicMock,
    mock_pretty_table: MagicMock,
) -> None:
    """Ensure that non-active deployment states are correctly shown in the URL field."""
    mock_client.list.return_value = [mock_deployment]
    mock_get_deployment_state.return_value = state

    list_notebooks(mock_client, wide=False)

    mock_pretty_table.add_row.assert_called_once_with(
        [TEST_DEPLOYMENT_NAME, TEST_IMAGE, expected_url]
    )


def test_no_service_url_returned(
    mock_client: MagicMock,
    mock_deployment: MagicMock,
    mock_get_deployment_state: MagicMock,
    mock_get_service_url: MagicMock,
    mock_pretty_table: MagicMock,
) -> None:
    """Test behavior when no service URL is found and a default message is displayed."""
    mock_client.list.return_value = [mock_deployment]
    mock_get_deployment_state.return_value = DeploymentState.ACTIVE
    mock_get_service_url.return_value = None

    list_notebooks(mock_client, wide=False)

    mock_pretty_table.add_row.assert_called_once_with(
        [TEST_DEPLOYMENT_NAME, TEST_IMAGE, "(No service)"]
    )
