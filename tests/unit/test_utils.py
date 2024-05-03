from contextlib import nullcontext as does_not_raise
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest
from lightkube import ApiError
from lightkube.models.core_v1 import Service, ServicePort, ServiceSpec
from lightkube.resources.apps_v1 import Deployment
from lightkube.resources.core_v1 import Node, Pod

from dss.config import DSS_NAMESPACE, MLFLOW_DEPLOYMENT_NAME, DeploymentState
from dss.utils import (
    ImagePullBackOffError,
    does_dss_pvc_exist,
    does_namespace_exist,
    does_notebook_exist,
    get_deployment_state,
    get_kubeconfig,
    get_kubeconfig_path,
    get_labels_for_node,
    get_lightkube_client,
    get_mlflow_tracking_uri,
    get_service_url,
    save_kubeconfig,
    wait_for_deployment_ready,
    wait_for_namespace_to_be_deleted,
)


@pytest.fixture
def mock_client() -> MagicMock:
    """
    Fixture to mock the Client class.
    """
    with patch("dss.utils.Client") as mock_client:
        yield mock_client


@pytest.fixture
def mock_deployment():
    """Fixture to create a mock Deployment object with variable attributes."""
    return MagicMock(spec=Deployment)


@pytest.fixture
def mock_environ_get() -> MagicMock:
    """
    Fixture to mock the os.environ.get function.
    """
    with patch("dss.utils.os.environ.get") as mock_env_get:
        yield mock_env_get


@pytest.fixture
def mock_kubeconfig() -> MagicMock:
    """
    Fixture to mock the KubeConfig.from_dict function.
    """
    with patch("dss.utils.KubeConfig") as mock_kubeconfig:
        yield mock_kubeconfig


@pytest.fixture
def mock_get_kubeconfig() -> MagicMock:
    """
    Fixture to mock the KubeConfig.from_dict function.
    """
    with patch("dss.utils.get_kubeconfig") as mock_get_kubeconfig:
        yield mock_get_kubeconfig


@pytest.fixture
def mock_logger() -> MagicMock:
    """
    Fixture to mock the logger object.
    """
    with patch("dss.utils.logger") as mock_logger:
        yield mock_logger


@pytest.fixture
def mock_does_namespace_exist() -> MagicMock:
    """
    Fixture to mock the does_namespace_exist function.
    """
    with patch("dss.utils.does_namespace_exist") as mock_does_namespace_exist:
        yield mock_does_namespace_exist


class _FakeResponse:
    """Used to fake an httpx response during testing only."""

    def __init__(self, code):
        self.status_code = code
        self.name = ""

    def json(self):
        reason = ""
        if self.status_code == 409:
            reason = "AlreadyExists"
        return {
            "apiVersion": 1,
            "code": self.status_code,
            "message": "broken",
            "reason": reason,
        }


class FakeApiError(ApiError):
    """Used to simulate an ApiError during testing."""

    def __init__(self, code=400):
        super().__init__(response=_FakeResponse(code))


@patch("dss.utils.get_kubeconfig_path")
def test_get_kubeconfig(
    mock_get_kubeconfig_path,
    mock_kubeconfig,
    monkeypatch,
):
    """Tests that get_kubeconfig succeeds as expected."""
    # Arrange
    mock_get_kubeconfig_path.return_value = Path("kubeconfig-path")

    # Act
    _ = get_kubeconfig()

    # Assert
    mock_kubeconfig.from_file.assert_called_once_with(mock_get_kubeconfig_path.return_value)


@pytest.mark.parametrize(
    "env_var_content, kubeconfig_default, expected_kubeconfig_path_used",
    [
        ("env_var_path", "default_path", Path("env_var_path")),
        (None, "default_path", Path("default_path")),
    ],
)
def test_get_kubeconfig_path(
    env_var_content: str,
    kubeconfig_default: str,
    expected_kubeconfig_path_used: Path,
    monkeypatch,
):
    """Test that get_kubeconfig_path correctly returns the default path and one from an env var."""
    # Arrange
    env_var = "test-env-var"

    with pytest.MonkeyPatch.context() as mp:
        if env_var_content is None:
            mp.delenv(env_var, raising=False)
        else:
            mp.setenv(env_var, env_var_content)

        # Act
        actual = get_kubeconfig_path(
            env_var=env_var, default_kubeconfig_location=kubeconfig_default
        )

    # Assert
    assert actual == expected_kubeconfig_path_used


@patch("dss.utils.get_kubeconfig_path")
def test_save_kubeconfig(
    mock_get_kubeconfig_path: MagicMock,
    monkeypatch,
):
    """Test that save_kubeconfig succeeds as expected."""
    # Arrange
    kubeconfig = "kubeconfig-text"

    # Act
    mocked_open = mock_open()
    with patch("dss.utils.open", mocked_open):
        save_kubeconfig(kubeconfig)

    # Assert
    mock_get_kubeconfig_path.return_value.parent.mkdir.assert_called_once()
    mocked_open.assert_called_once_with(mock_get_kubeconfig_path.return_value, "w")
    mocked_open().write.assert_called_once_with(kubeconfig)


def test_get_lightkube_client_successful(
    mock_get_kubeconfig: MagicMock,
    mock_client: MagicMock,
) -> None:
    """
    Tests that we successfully try to create a lightkube client, given a kubeconfig.
    """
    returned_client = get_lightkube_client()
    assert returned_client is not None


def test_get_mlflow_tracking_uri() -> None:
    """
    Tests whether get_mlflow_tracking_uri returns the expected value.
    """
    expected = f"http://{MLFLOW_DEPLOYMENT_NAME}.{DSS_NAMESPACE}.svc.cluster.local:5000"
    assert get_mlflow_tracking_uri() == expected


def test_get_service_url() -> None:
    """
    Test the get_service_url helper.
    """
    name = "name"
    namespace = "namespace"
    ip = "1.1.1.1"
    port = 8765
    expected_url = f"http://{ip}:{port}"

    mock_service = Service(spec=ServiceSpec(clusterIP=ip, ports=[ServicePort(port=port)]))
    mock_client = MagicMock()
    mock_client.get.return_value = mock_service

    actual_url = get_service_url(name=name, namespace=namespace, lightkube_client=mock_client)

    assert actual_url == expected_url


def test_wait_for_deployment_ready_timeout(mock_client: MagicMock, mock_logger: MagicMock) -> None:
    """
    Test case to verify timeout while waiting for deployment to be ready.
    """
    # Mock the behavior of the client.get method to return a deployment with available replicas = 0
    mock_client_instance = MagicMock()
    mock_client_instance.get.return_value = MagicMock(
        spec=Deployment, status=MagicMock(availableReplicas=0), spec_replicas=1
    )

    # Mock the behavior of the client.list method to return an iterable of one Pod
    pod = MagicMock()
    mock_client_instance.list.return_value = iter([pod])

    # Call the function to test
    with pytest.raises(TimeoutError) as exc_info:
        wait_for_deployment_ready(
            mock_client_instance,
            namespace="test-namespace",
            deployment_name="test-deployment",
            timeout_seconds=2,
            interval_seconds=1,
        )

    # Assertions
    assert (
        str(exc_info.value)
        == "Timeout waiting for deployment test-deployment in namespace test-namespace to be ready"
    )
    assert mock_client_instance.get.call_count == 3  # 2 attempts, 1 final attempt after timeout


def test_wait_for_deployment_ready_image_pull_backoff(
    mock_client: MagicMock, mock_logger: MagicMock
) -> None:
    """
    Test case to verify that ImagePullBackOffError is raised when the pod status indicates that.
    """
    # Mock the behavior of the client.get method to return a deployment with available replicas = 0
    mock_client_instance = MagicMock()
    mock_client_instance.get.return_value = MagicMock(
        spec=Deployment, status=MagicMock(availableReplicas=0), spec_replicas=1
    )

    # Mock the behavior of the client.list method to return a pod with `ImagePullBackOff` reason
    pod = MagicMock()
    pod.status.containerStatuses[0].state.waiting.reason = "ImagePullBackOff"
    mock_client_instance.list.return_value = iter([pod])

    # Call the function to test
    with pytest.raises(ImagePullBackOffError) as exc_info:
        wait_for_deployment_ready(
            mock_client_instance,
            namespace="test-namespace",
            deployment_name="test-deployment",
            timeout_seconds=2,
            interval_seconds=1,
        )

    # Assertions
    assert (
        str(exc_info.value) == "Failed to create Deployment test-deployment with ImagePullBackOff"
    )


@pytest.mark.parametrize(
    "lightkube_client_side_effect, context_raised, expected_return",
    [
        # A resource is found (lightkube_client.get() does not fail)
        (None, does_not_raise(), True),
        # The first resource is missing (ApiError with 404 status code), but the second is found
        ([FakeApiError(404), None], does_not_raise(), True),
        # No resources are found
        ([FakeApiError(404), FakeApiError(404)], does_not_raise(), False),
        # Some other ApiError is raised, which we don't know how to handle
        ([FakeApiError(999)], pytest.raises(ApiError), None),
    ],
)
def test_does_notebook_exist(lightkube_client_side_effect, context_raised, expected_return):
    """Test the does_notebook_exist helper."""
    mock_client = MagicMock()
    mock_client.get.side_effect = lightkube_client_side_effect

    with context_raised:
        assert does_notebook_exist("notebook", "namespace", mock_client) == expected_return


@pytest.mark.parametrize(
    "lightkube_client_side_effect, context_raised, expected_return",
    [
        # The PVC is found (lightkube_client.get() does not fail)
        (None, does_not_raise(), True),
        # The PVC is missing
        ([FakeApiError(404)], does_not_raise(), False),
        # Some other ApiError is raised, which we don't know how to handle
        ([FakeApiError(999)], pytest.raises(ApiError), None),
    ],
)
def test_does_dss_pvc_exist(lightkube_client_side_effect, context_raised, expected_return):
    """Test the does_dss_pvc_exist helper."""
    mock_client = MagicMock()
    mock_client.get.side_effect = lightkube_client_side_effect

    with context_raised:
        assert does_dss_pvc_exist(mock_client) == expected_return


def test_get_labels_for_node_with_single_node(mock_client: MagicMock):
    """
    Test to verify the behavior of get_labels_for_node when there is only one node in the cluster.
    """
    # Mock the list method of lightkube_client to return a list with a single node
    mock_client.list.return_value = [MagicMock(metadata=MagicMock(labels={"gpu_type": "NVIDIA"}))]

    # Call the function to test
    labels = get_labels_for_node(mock_client)

    # Assertions
    assert labels == {"gpu_type": "NVIDIA"}
    mock_client.list.assert_called_once_with(Node)


def test_get_labels_for_node_with_multiple_nodes(mock_client: MagicMock):
    """
    Test to verify the behavior of get_labels_for_node when there are multiple nodes in the cluster.
    """
    # Mock the list method of lightkube_client to return a list with two nodes
    mock_client.list.return_value = [MagicMock(), MagicMock()]

    # Verify that the function raises a ValueError
    with pytest.raises(ValueError):
        get_labels_for_node(mock_client)

    # Verify that lightkube_client.list was called once with Node
    mock_client.list.assert_called_once_with(Node)


@pytest.mark.parametrize(
    "desired_replicas, current_replicas, available_replicas, deletion_timestamp, waiting_reason, expected_state",  # noqa E501
    [
        (1, 1, 1, None, None, DeploymentState.ACTIVE),
        (1, 0, 0, None, None, DeploymentState.STARTING),
        (0, 1, 1, None, None, DeploymentState.STOPPING),
        (0, 0, 0, None, None, DeploymentState.STOPPED),
        (None, None, None, True, None, DeploymentState.REMOVING),
        (1, 1, 0, None, "ImagePullBackOff", DeploymentState.DOWNLOADING),
        (1, 1, 0, None, "ErrImagePull", DeploymentState.DOWNLOADING),
        (1, 1, 0, None, "ContainerCreating", DeploymentState.DOWNLOADING),
        (1, 1, 0, None, None, DeploymentState.STARTING),
    ],
)
def test_get_deployment_state(
    mock_deployment,
    mock_client,
    desired_replicas,
    current_replicas,
    available_replicas,
    deletion_timestamp,
    waiting_reason,
    expected_state,
):
    # Arrange
    mock_deployment.spec.replicas = desired_replicas
    mock_deployment.status.replicas = current_replicas
    mock_deployment.status.availableReplicas = available_replicas
    mock_deployment.metadata.deletionTimestamp = deletion_timestamp

    pod = MagicMock(spec=Pod)
    container_status = MagicMock()
    if waiting_reason:
        container_status.state.waiting = MagicMock(reason=waiting_reason)
    else:
        container_status.state.waiting = None
    pod.status.containerStatuses = [container_status]
    mock_client.list.return_value = [pod]

    # Act
    state = get_deployment_state(mock_deployment, mock_client)

    # Assert
    assert state == expected_state, f"Expected {expected_state}, but got {state}"


@pytest.mark.parametrize(
    "lightkube_client_side_effect, context_raised, expected_return",
    [
        # The namespace is found (lightkube_client.get() does not fail)
        (None, does_not_raise(), True),
        # The namespace is not found
        (FakeApiError(404), does_not_raise(), False),
        # Some other ApiError is raised, which we don't know how to handle
        (FakeApiError(999), pytest.raises(ApiError), None),
    ],
)
def test_does_namespace_exist(lightkube_client_side_effect, context_raised, expected_return):
    """Test the does_namespace_exist function."""
    mock_client = MagicMock()
    mock_client.get.side_effect = lightkube_client_side_effect

    with context_raised:
        assert does_namespace_exist(mock_client, "namespace") == expected_return


@pytest.mark.parametrize(
    "return_value, context_raised, side_effect, error_message, logger_info_call_count",
    [
        # Namespace has been deleted when the function is called
        (False, does_not_raise(), None, None, 1),
        # Raises an unexpected error.
        (False, pytest.raises(FakeApiError), FakeApiError(999), "broken", 1),
    ],
)
def test_wait_for_namespace_to_be_deleted(
    mock_does_namespace_exist: MagicMock,
    mock_logger: MagicMock,
    return_value: bool,
    context_raised,
    side_effect: Exception,
    error_message: str,
    logger_info_call_count: int,
) -> None:
    """
    Test the three cases for wait_for_namespace_to_be_deleted function.
    """
    mock_client_instance = MagicMock()
    namespace = "test-namespace"
    mock_does_namespace_exist.return_value = return_value
    mock_does_namespace_exist.side_effect = side_effect

    # Call the function to test
    with context_raised as exc_info:
        wait_for_namespace_to_be_deleted(
            mock_client_instance,
            namespace=namespace,
            interval_seconds=1,
        )

    # Assertions
    mock_logger.info.assert_called_with(f"Waiting for namespace {namespace} to be deleted...")
    assert mock_logger.info.call_count == logger_info_call_count
    if error_message:
        assert str(exc_info.value) == error_message
