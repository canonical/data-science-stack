from unittest.mock import MagicMock, patch

import pytest

from dss.utils import KUBECONFIG_DEFAULT, get_default_kubeconfig, get_lightkube_client


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
def mock_client() -> MagicMock:
    """
    Fixture to mock the Client class.
    """
    with patch("dss.utils.Client") as mock_client:
        yield mock_client


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
