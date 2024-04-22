from unittest.mock import MagicMock, patch

import pytest

from dss.config import DSS_NAMESPACE
from dss.purge import purge


@pytest.fixture
def mock_does_namespace_exist() -> MagicMock:
    """
    Fixture to mock the get_service_url function.
    """
    with patch("dss.purge.does_namespace_exist") as mock_does_namespace_exist:
        yield mock_does_namespace_exist


@pytest.fixture
def mock_wait_for_namespace_to_be_deleted() -> MagicMock:
    """
    Fixture to mock the KubernetesResourceHandler class.
    """
    with patch(
        "dss.purge.wait_for_namespace_to_be_deleted"
    ) as mock_wait_for_namespace_to_be_deleted:
        yield mock_wait_for_namespace_to_be_deleted


@pytest.fixture
def mock_logger() -> MagicMock:
    """
    Fixture to mock the logger object.
    """
    with patch("dss.purge.logger") as mock_logger:
        yield mock_logger


def test_purge_success(
    mock_logger: MagicMock,
    mock_does_namespace_exist: MagicMock,
    mock_wait_for_namespace_to_be_deleted: MagicMock,
) -> None:
    """
    Test case to verify behavior on success.
    """
    mock_does_namespace_exist.return_value = True
    mock_client_instance = MagicMock()
    purge(mock_client_instance)

    # Assertions
    mock_logger.info.assert_called_with(
        "Success: All DSS components and notebooks purged successfully from the Kubernetes cluster."  # noqa E501
    )
    mock_logger.error.assert_not_called()
    mock_logger.warn.assert_not_called()
    mock_logger.debug.assert_not_called()


def test_purge_failure_namespace_does_not_exist(
    mock_logger: MagicMock, mock_does_namespace_exist: MagicMock
) -> None:
    """
    Test case to verify behavior when `dss` namespace does not exist.
    """
    mock_does_namespace_exist.return_value = False
    mock_client_instance = MagicMock()
    with pytest.raises(RuntimeError):
        purge(mock_client_instance)

    # Assertions
    mock_logger.warn.assert_called_with(
        f"Cannot purge DSS components. Namespace `{DSS_NAMESPACE}` does not exist."
    )
    mock_logger.info.assert_any_call("You might want to run")
    mock_logger.info.assert_any_call("  dss status      to check the current status")
    mock_logger.info.assert_any_call("  dss logs --all  to review all logs")
    mock_logger.info.assert_called_with("  dss initialize  to install dss")
    mock_logger.error.assert_not_called()
    mock_logger.debug.assert_not_called()


def test_purge_failure_runtime_error(mock_does_namespace_exist: MagicMock) -> None:
    """
    Test case to verify that ApiError is handled.
    """
    mock_does_namespace_exist.return_value = True
    mock_client_instance = MagicMock()
    mock_client_instance.delete.side_effect = RuntimeError()
    with pytest.raises(RuntimeError):
        purge(mock_client_instance)


def test_purge_failure_not_runtime_error(mock_does_namespace_exist: MagicMock) -> None:
    """
    Test case to verify that ApiError is handled.
    """
    mock_does_namespace_exist.return_value = True
    mock_client_instance = MagicMock()
    error_code = 400
    mock_client_instance.delete.side_effect = Exception(error_code)
    with pytest.raises(Exception) as exc_info:
        purge(mock_client_instance)

    # Assertions
    assert str(exc_info.value) == "400"
