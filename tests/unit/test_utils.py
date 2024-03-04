from unittest.mock import MagicMock, patch

import pytest
from lightkube.resources.apps_v1 import Deployment
from lightkube.models.core_v1 import Service, ServicePort, ServiceSpec

from dss.config import MLFLOW_DEPLOYMENT_NAME, DSS_NAMESPACE
from dss.utils import (
    KUBECONFIG_DEFAULT,
    get_default_kubeconfig,
    get_lightkube_client,
    get_notebook_url,
    wait_for_deployment_ready, get_mlflow_tracking_uri,
)


@pytest.fixture
def mock_client() -> MagicMock:
    """
    Fixture to mock the Client class.
    """
    with patch("dss.utils.Client") as mock_client:
        yield mock_client


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
def mock_logger() -> MagicMock:
    """
    Fixture to mock the logger object.
    """
    with patch("dss.initialize.logger") as mock_logger:
        yield mock_logger


@pytest.mark.parametrize(
    "kubeconfig, kubeconfig_env_var, expected",
    [
        ("some_file", "", "some_file"),
        (None, "some_file", "some_file"),
        (None, "", KUBECONFIG_DEFAULT),
    ],
)
def test_get_default_kubeconfig_successful(
    kubeconfig: str,
    kubeconfig_env_var: str,
    expected: str,
    mock_environ_get: MagicMock,
) -> None:
    """
    Test case to verify missing kubeconfig environment variable.

    Args:
        kubeconfig: path to a kubeconfig file, passed to get_lightkube_client by arg
        kubeconfig_env_var: environment variable for kubeconfig
        expected: expected returned value for kubeconfig
    """
    mock_environ_get.return_value = kubeconfig_env_var

    returned = get_default_kubeconfig(kubeconfig)
    assert returned == expected


def test_get_lightkube_client_successful(
    mock_kubeconfig: MagicMock,
    mock_client: MagicMock,
) -> None:
    """
    Tests that we successfully try to create a lightkube client, given a kubeconfig.
    """
    kubeconfig = "some_file"
    mock_kubeconfig_instance = "kubeconfig-returned"
    mock_kubeconfig.from_file.return_value = mock_kubeconfig_instance

    returned_client = get_lightkube_client(kubeconfig)

    mock_kubeconfig.from_file.assert_called_with(kubeconfig)
    mock_client.assert_called_with(config=mock_kubeconfig_instance)
    assert returned_client is not None


def test_get_mlflow_tracking_uri() -> None:
    """
    Tests whether get_mlflow_tracking_uri returns the expected value.
    """
    expected = f"http://{MLFLOW_DEPLOYMENT_NAME}.{DSS_NAMESPACE}.svc.cluster.local:5000"
    assert get_mlflow_tracking_uri() == expected


def test_get_notebook_url() -> None:
    """
    Test the get_notebook_url helper.
    """
    name = "name"
    namespace = "namespace"
    ip = "1.1.1.1"
    port = 8765
    expected_url = f"http://{ip}:{port}/notebook/{namespace}/{name}/lab"

    mock_service = Service(spec=ServiceSpec(clusterIP=ip, ports=[ServicePort(port=port)]))
    mock_client = MagicMock()
    mock_client.get.return_value = mock_service

    actual_url = get_notebook_url(name=name, namespace=namespace, lightkube_client=mock_client)

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

    # Call the function to test
    with pytest.raises(TimeoutError) as exc_info:
        wait_for_deployment_ready(
            mock_client_instance,
            namespace="test-namespace",
            deployment_name="test-deployment",
            timeout_seconds=5,
            interval_seconds=1,
        )

    # Assertions
    assert (
        str(exc_info.value)
        == "Timeout waiting for deployment test-deployment in namespace test-namespace to be ready"
    )
    assert mock_client_instance.get.call_count == 6  # 5 attempts, 1 final attempt after timeout
