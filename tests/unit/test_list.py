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
    """Provides a mock for the Kubernetes Client."""
    with patch("dss.list.Client") as mock:
        yield mock.return_value


@pytest.fixture
def mock_deployment() -> MagicMock:
    """Creates a mock Deployment object with correct labels and predefined attributes."""
    deployment = MagicMock(spec=Deployment)
    deployment.metadata.name = TEST_DEPLOYMENT_NAME
    deployment.metadata.labels = {NOTEBOOK_LABEL: TEST_DEPLOYMENT_NAME}
    deployment.spec.template.spec.containers = [MagicMock(image=TEST_IMAGE)]
    deployment.spec.replicas = 1
    deployment.status.replicas = 1
    deployment.status.availableReplicas = 1
    return deployment


@pytest.fixture
def mock_deployment_with_incorrect_labels() -> MagicMock:
    """Creates a mock Deployment object with incorrect labels to test label filtering."""
    deployment = MagicMock(spec=Deployment)
    deployment.metadata.labels = {}
    return deployment


@pytest.fixture
def mock_get_deployment_state() -> MagicMock:
    """Mocks the get_deployment_state function."""
    with patch("dss.list.get_deployment_state") as mock:
        yield mock


@pytest.fixture
def mock_get_service_url() -> MagicMock:
    """Mocks the get_service_url function."""
    with patch("dss.list.get_service_url") as mock:
        yield mock


@pytest.fixture
def mock_truncate_row() -> MagicMock:
    """Mocks the truncate_row function."""
    with patch("dss.list.truncate_row") as mock:
        yield mock


@pytest.fixture
def mock_logger() -> MagicMock:
    """Mocks the logger used in list_notebooks."""
    with patch("dss.list.logger") as mock:
        yield mock


def test_list_notebooks_success(
    mock_client: MagicMock,
    mock_deployment: MagicMock,
    mock_truncate_row: MagicMock,
    mock_get_service_url: MagicMock,
    mock_get_deployment_state: MagicMock,
) -> None:
    """
    Ensures that listing notebooks with correct labels proceeds without errors and
    that all dependent functions are called with expected parameters.
    """
    # Arrange
    mock_client.list.return_value = [mock_deployment]
    mock_get_deployment_state.return_value = DeploymentState.ACTIVE
    mock_get_service_url.return_value = TEST_SVC
    mock_truncate_row.return_value = (TEST_DEPLOYMENT_NAME, TEST_IMAGE, TEST_SVC)

    # Act
    list_notebooks(mock_client, wide=False)

    # Assert
    mock_get_service_url.assert_called_once_with(TEST_DEPLOYMENT_NAME, "dss", mock_client)
    mock_truncate_row.assert_called_once_with(TEST_DEPLOYMENT_NAME, TEST_IMAGE, TEST_SVC)


def test_list_notebooks_failure_listing_deployments(
    mock_client: MagicMock, mock_logger: MagicMock
) -> None:
    """
    Checks that errors during the listing of deployments are logged correctly.
    """
    # Arrange
    mock_client.list.side_effect = ApiError(response=MagicMock())

    # Act
    list_notebooks(mock_client)

    # Assert
    mock_logger.error.assert_called_with("Failed to list notebooks: None")


@pytest.mark.parametrize(
    "state",
    [
        DeploymentState.DOWNLOADING,
        DeploymentState.STOPPING,
        DeploymentState.STOPPED,
        DeploymentState.REMOVING,
        DeploymentState.UNKNOWN,
    ],
)
def test_non_active_deployment_states(
    state: DeploymentState,
    mock_client: MagicMock,
    mock_deployment: MagicMock,
    mock_get_deployment_state: MagicMock,
    mock_truncate_row: MagicMock,
) -> None:
    """
    Ensures that non-active deployment states are correctly reflected in the URL field.
    """
    # Arrange
    mock_client.list.return_value = [mock_deployment]
    mock_get_deployment_state.return_value = state
    expected_url = f"({state.value})"
    mock_truncate_row.return_value = (TEST_DEPLOYMENT_NAME, TEST_IMAGE, expected_url)

    # Act
    list_notebooks(mock_client, wide=False)

    # Assert
    mock_truncate_row.assert_called_with(TEST_DEPLOYMENT_NAME, TEST_IMAGE, expected_url)


def test_list_notebooks_no_truncate_when_wide(
    mock_client: MagicMock, mock_truncate_row: MagicMock, mock_deployment: MagicMock
) -> None:
    """
    Confirms that no truncation occurs when the 'wide' option is enabled.
    """
    # Arrange
    mock_client.list.return_value = [mock_deployment]

    # Act
    list_notebooks(mock_client, wide=True)

    # Assert
    mock_truncate_row.assert_not_called()
