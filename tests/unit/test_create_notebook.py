from unittest.mock import MagicMock, patch

import pytest
from test_utils import FakeApiError

from dss.config import DSS_NAMESPACE, NOTEBOOK_PVC_NAME, RECOMMENDED_IMAGES_MESSAGE
from dss.create_notebook import _get_notebook_config, create_notebook
from dss.utils import ImagePullBackOffError


@pytest.fixture
def mock_get_service_url() -> MagicMock:
    """
    Fixture to mock the get_service_url function.
    """
    with patch("dss.create_notebook.get_service_url") as mock_get_service_url:
        yield mock_get_service_url


@pytest.fixture
def mock_resource_handler() -> MagicMock:
    """
    Fixture to mock the KubernetesResourceHandler class.
    """
    with patch("dss.create_notebook.KubernetesResourceHandler") as mock_handler:
        yield mock_handler


@pytest.fixture
def mock_wait_for_deployment_ready() -> MagicMock:
    """
    Fixture to mock the KubernetesResourceHandler class.
    """
    with patch("dss.create_notebook.wait_for_deployment_ready") as mock_wait_for_deployment_ready:
        yield mock_wait_for_deployment_ready


@pytest.fixture
def mock_logger() -> MagicMock:
    """
    Fixture to mock the logger object.
    """
    with patch("dss.create_notebook.logger") as mock_logger:
        yield mock_logger


def test_create_notebook_success(
    mock_get_service_url: MagicMock,
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

    mock_get_service_url.return_value = notebook_url

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


def test_create_notebook_failure_pvc_does_not_exist(
    mock_logger: MagicMock,
) -> None:
    """
    Test case to verify behavior when DSS pvc does not exist.
    """
    notebook_name = "test-notebook"
    notebook_image = "test-image"

    # Mock the behavior of Client
    mock_client_instance = MagicMock()

    with patch("dss.create_notebook.does_dss_pvc_exist", return_value=False), patch(
        "dss.create_notebook.does_notebook_exist", return_value=False
    ):
        with pytest.raises(RuntimeError):
            # Call the function to test
            create_notebook(
                name=notebook_name, image=notebook_image, lightkube_client=mock_client_instance
            )

        # Assertions
        mock_logger.debug.assert_called_with(
            "Failed to create notebook. DSS was not correctly initialized."
        )
        mock_logger.error.assert_called_with(
            "Failed to create notebook. DSS was not correctly initialized."
        )
        mock_logger.info.assert_any_call("Note: You might want to run")
        mock_logger.info.assert_any_call("  dss status      to check the current status")
        mock_logger.info.assert_any_call("  dss logs --all  to view all logs")
        mock_logger.info.assert_called_with("  dss initialize  to install dss")


def test_create_notebook_failure_mlflow_does_not_exist(
    mock_logger: MagicMock,
) -> None:
    """
    Test case to verify behavior when MLflow deployment does not exist.
    """
    notebook_name = "test-notebook"
    notebook_image = "test-image"

    # Mock the behavior of Client
    mock_client_instance = MagicMock()

    with patch("dss.create_notebook.does_mlflow_deployment_exist", return_value=False), patch(
        "dss.create_notebook.does_notebook_exist", return_value=False
    ):
        with pytest.raises(RuntimeError):
            # Call the function to test
            create_notebook(
                name=notebook_name, image=notebook_image, lightkube_client=mock_client_instance
            )

        # Assertions
        mock_logger.debug.assert_called_with(
            "Failed to create notebook. DSS was not correctly initialized."
        )
        mock_logger.error.assert_called_with(
            "Failed to create notebook. DSS was not correctly initialized."
        )
        mock_logger.info.assert_any_call("Note: You might want to run")
        mock_logger.info.assert_any_call("  dss status      to check the current status")
        mock_logger.info.assert_any_call("  dss logs --all  to view all logs")
        mock_logger.info.assert_called_with("  dss initialize  to install dss")


def test_create_notebook_failure_notebook_exists(
    mock_get_service_url: MagicMock,
    mock_logger: MagicMock,
) -> None:
    """
    Test case to verify behavior when a Notebook with the same name exists.
    """
    notebook_name = "test-notebook"
    notebook_image = "test-image"
    notebook_url = "http://somewhere.com:1234/notebook/namespace/name/lab"

    # Mock the behavior of Client
    mock_client_instance = MagicMock()

    mock_get_service_url.return_value = notebook_url
    with patch("dss.create_notebook.does_dss_pvc_exist", return_value=True), patch(
        "dss.create_notebook.does_notebook_exist", return_value=True
    ):
        with pytest.raises(RuntimeError):
            # Call the function to test
            create_notebook(
                name=notebook_name, image=notebook_image, lightkube_client=mock_client_instance
            )

        # Assertions
        mock_logger.debug.assert_called_with(
            f"Failed to create Notebook. Notebook with name '{notebook_name}' already exists."
        )
        mock_logger.error.assert_called_with(
            f"Failed to create Notebook. Notebook with name '{notebook_name}' already exists."
        )
        mock_logger.info.assert_any_call("Please specify a different name.")
        mock_logger.info.assert_called_with(
            f"To connect to the existing notebook, go to {notebook_url}."
        )


def test_create_notebook_failure_api(
    mock_logger: MagicMock, mock_wait_for_deployment_ready: MagicMock
) -> None:
    """
    Test case to verify behavior when an ApiError is raised.
    """
    notebook_name = "test-notebook"
    notebook_image = "test-image"

    # Mock the behavior of Client
    mock_client_instance = MagicMock()

    # Mock the behavior of wait_for_deployment_ready
    error_code = 400
    mock_wait_for_deployment_ready.side_effect = FakeApiError(error_code)

    with patch("dss.create_notebook.does_dss_pvc_exist", return_value=True), patch(
        "dss.create_notebook.does_notebook_exist", return_value=False
    ):
        with pytest.raises(RuntimeError):
            # Call the function to test
            create_notebook(
                name=notebook_name, image=notebook_image, lightkube_client=mock_client_instance
            )

        # Assertions
        mock_logger.debug.assert_called_with(
            f"Failed to create Notebook {notebook_name}: broken.", exc_info=True
        )
        mock_logger.error.assert_called_with(
            f"Failed to create Notebook with error code {error_code}."
        )
        mock_logger.info.assert_called_with(" Check the debug logs for more details.")


def test_create_notebook_failure_time_out(
    mock_logger: MagicMock, mock_wait_for_deployment_ready: MagicMock
) -> None:
    """
    Test case to verify behavior when a TimeoutError is raised.
    """
    notebook_name = "test-notebook"
    notebook_image = "test-image"
    exception_message = "test-exception-message"

    # Mock the behavior of Client
    mock_client_instance = MagicMock()

    # Mock the behavior of wait_for_deployment_ready
    mock_wait_for_deployment_ready.side_effect = TimeoutError(exception_message)

    with patch("dss.create_notebook.does_dss_pvc_exist", return_value=True), patch(
        "dss.create_notebook.does_notebook_exist", return_value=False
    ):
        with pytest.raises(RuntimeError):
            # Call the function to test
            create_notebook(
                name=notebook_name, image=notebook_image, lightkube_client=mock_client_instance
            )

        # Assertions
        mock_logger.debug.assert_called_with(
            f"Failed to create Notebook {notebook_name}: {exception_message}", exc_info=True
        )
        mock_logger.error.assert_called_with(
            f"Timed out while trying to create Notebook {notebook_name}."
        )
        mock_logger.warn.assert_called_with(" Some resources might be left in the cluster.")
        mock_logger.info.assert_called_with(" Check the status with `dss list`.")


def test_create_notebook_failure_image_pull(
    mock_logger: MagicMock, mock_wait_for_deployment_ready: MagicMock
) -> None:
    """
    Test case to verify behavior when an ImagePullBackOffError is raised.
    """
    notebook_name = "test-notebook"
    notebook_image = "test-image"
    exception_message = "test-exception-message"

    # Mock the behavior of Client
    mock_client_instance = MagicMock()

    # Mock the behavior of wait_for_deployment_ready
    mock_wait_for_deployment_ready.side_effect = ImagePullBackOffError(exception_message)

    with patch("dss.create_notebook.does_dss_pvc_exist", return_value=True), patch(
        "dss.create_notebook.does_notebook_exist", return_value=False
    ), patch("dss.create_notebook._get_notebook_image_name", return_value=notebook_image):
        # Call the function to test
        with pytest.raises(RuntimeError):
            create_notebook(
                name=notebook_name, image=notebook_image, lightkube_client=mock_client_instance
            )

        # Assertions
        mock_logger.debug.assert_called_with(
            f"Timed out while trying to create Notebook {notebook_name}: {exception_message}.",
            exc_info=True,
        )
        mock_logger.error.assert_any_call(
            f"Timed out while trying to create Notebook {notebook_name}."
        )
        mock_logger.error.assert_called_with(
            f"Image {notebook_image} does not exist or is not accessible."
        )
        mock_logger.info.assert_called_with(
            "Note: You might want to use some of these recommended images:\n"
            f"{RECOMMENDED_IMAGES_MESSAGE}"
        )


def test_get_notebook_config() -> None:
    """
    Test case to verify behavior when an ImagePullBackOffError is raised.
    """
    notebook_name = "test-notebook"
    notebook_image = "test-image"
    mlflow_tracking_uri = "http://mlflow.dss.svc.cluster.local:5000"
    expected_context = {
        "mlflow_tracking_uri": mlflow_tracking_uri,
        "notebook_name": notebook_name,
        "namespace": DSS_NAMESPACE,
        "notebook_image": notebook_image,
        "pvc_name": NOTEBOOK_PVC_NAME,
    }
    with patch("dss.create_notebook.get_mlflow_tracking_uri", return_value=mlflow_tracking_uri):
        actual_context = _get_notebook_config(notebook_image, notebook_name)
        assert actual_context == expected_context
