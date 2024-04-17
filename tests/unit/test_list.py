from unittest.mock import MagicMock, patch

import pytest
from lightkube import ApiError

from dss.config import NOTEBOOK_LABEL
from dss.list import list_notebooks

TEST_IMAGE = "deployment_image"
TEST_DEPLOYMENT_NAME = "notebook_name"
TEST_SVC = "http://example.com"


@pytest.fixture
def mock_client() -> MagicMock:
    """
    Fixture to mock the Client class.
    """
    with patch("dss.list.Client") as mock_client:
        yield mock_client


@pytest.fixture
def mock_deployment() -> MagicMock:
    """
    Fixture to mock the Deployment class.
    """
    with patch("dss.list.Deployment") as mock_deployment:
        yield mock_deployment


@pytest.fixture
def mock_truncate_row() -> MagicMock:
    """
    Fixture to mock the truncate_row function.
    """
    with patch("dss.list.truncate_row") as mock_truncate_row:
        yield mock_truncate_row


@pytest.fixture
def mock_logger() -> MagicMock:
    """
    Fixture to mock the logger object.
    """
    with patch("dss.list.logger") as mock_logger:
        yield mock_logger


@pytest.fixture
def mock_get_service_url() -> MagicMock:
    """
    Fixture to mock the get_service_url function.
    """
    with patch("dss.list.get_service_url") as mock_get_service_url:
        yield mock_get_service_url


def test_list_notebooks_success(
    mock_client: MagicMock, mock_truncate_row: MagicMock, mock_get_service_url: MagicMock
) -> None:
    """
    Test case to verify behavior when listing notebooks succeeds.
    """

    # Mock the behavior of Client
    mock_client_instance = MagicMock()

    # Mock the deployment object
    mock_deployment_instance = MagicMock()
    mock_deployment_instance.metadata.name = TEST_DEPLOYMENT_NAME
    mock_deployment_instance.metadata.labels = {NOTEBOOK_LABEL: TEST_DEPLOYMENT_NAME}
    mock_deployment_instance.spec.template.spec.containers[0].image = TEST_IMAGE

    # Set up mock return value for truncate_row as we are mocking the function
    mock_truncate_row.return_value = ("", "", "")

    # Ensure list() returns the mock deployment object
    mock_client_instance.list.return_value = [mock_deployment_instance]
    mock_client.return_value = mock_client_instance

    # Mock the behavior of get_service_url
    mock_get_service_url.return_value = TEST_SVC

    # Call the function to test
    list_notebooks(mock_client_instance)

    # Assertions
    mock_truncate_row.assert_called_once_with(
        TEST_DEPLOYMENT_NAME,
        TEST_IMAGE,
        TEST_SVC,
    )


def test_list_notebooks_ignore_incorrect_labels(
    mock_client: MagicMock, mock_truncate_row: MagicMock, mock_get_service_url: MagicMock
) -> None:
    """
    Test case to verify behavior when deployments with incorrect labels are ignored.
    """

    # Mock the behavior of Client
    mock_client_instance = MagicMock()

    # Mock a deployment with incorrect labels
    incorrect_labels = {}
    mock_deployment_instance = MagicMock()
    mock_deployment_instance.metadata.labels = incorrect_labels

    # Ensure list() returns the mock deployment object
    mock_client_instance.list.return_value = [mock_deployment_instance]
    mock_client.return_value = mock_client_instance

    # Call the function to test
    list_notebooks(mock_client_instance)

    # Assertions
    mock_truncate_row.assert_not_called()


def test_list_notebooks_failure_listing_deployments(
    mock_client: MagicMock, mock_logger: MagicMock
) -> None:
    """
    Test case to verify behavior when listing notebooks fails due to an error listing deployments.
    """

    # Mock the behavior of Client to raise an ApiError when listing deployments
    mock_client_instance = MagicMock()
    mock_client_instance.list.side_effect = ApiError(response=MagicMock())
    mock_client.return_value = mock_client_instance

    # Call the function to test
    list_notebooks(mock_client_instance)

    # Assertions
    mock_logger.error.assert_called_once_with("Failed to list notebooks: None")


def test_list_notebooks_no_truncate_when_wide(
    mock_client: MagicMock, mock_truncate_row: MagicMock
) -> None:
    """
    Test case to verify behavior when truncate_row is not called when wide is False.
    """

    # Mock the behavior of Client
    mock_client_instance = MagicMock()

    # Mock the deployment object
    mock_deployment_instance = MagicMock()
    mock_deployment_instance.metadata.labels = {NOTEBOOK_LABEL: "notebook_name"}

    # Set up mock return value for truncate_row as we are mocking the function
    mock_truncate_row.return_value = ("", "", "")

    # Ensure list() returns the mock deployment object
    mock_client_instance.list.return_value = [mock_deployment_instance]
    mock_client.return_value = mock_client_instance

    # Call the function to test with wide=False
    list_notebooks(mock_client_instance, wide=True)

    # Assertions
    mock_truncate_row.assert_not_called()
