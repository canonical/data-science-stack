from typing import Dict, List
from unittest.mock import MagicMock

import pytest

from dss.status import get_status


@pytest.mark.parametrize(
    "mlflow_exist, mlflow_url, gpu_labels, expected_logs",
    [
        (
            True,
            "<Mocked MLflow URL>",
            {
                "nvidia.com/gpu.present": "true",
                "nvidia.com/gpu.deploy.container-toolkit": "true",
                "nvidia.com/gpu.deploy.device-plugin": "true",
                "nvidia.com/gpu.product": "Test-GPU",
            },
            [
                "MLflow deployment: Ready",
                "MLflow URL: <Mocked MLflow URL>",
                "NVIDIA GPU acceleration: Enabled (Test-GPU)",
                "Intel GPU acceleration: Disabled",
            ],
        ),
        (
            True,
            "<Mocked MLflow URL>",
            {
                "intel.feature.node.kubernetes.io/gpu": "true",
            },
            [
                "MLflow deployment: Ready",
                "MLflow URL: <Mocked MLflow URL>",
                "NVIDIA GPU acceleration: Disabled",
                "Intel GPU acceleration: Enabled",
            ],
        ),
        (
            True,
            "<Mocked MLflow URL>",
            {
                "nvidia.com/gpu.present": "true",
                "nvidia.com/gpu.deploy.container-toolkit": "true",
                "nvidia.com/gpu.deploy.device-plugin": "true",
                "nvidia.com/gpu.product": "Test-GPU",
                "intel.feature.node.kubernetes.io/gpu": "true",
            },
            [
                "MLflow deployment: Ready",
                "MLflow URL: <Mocked MLflow URL>",
                "NVIDIA GPU acceleration: Enabled (Test-GPU)",
                "Intel GPU acceleration: Enabled",
            ],
        ),
        (
            True,
            "<Mocked MLflow URL>",
            {},
            [
                "MLflow deployment: Ready",
                "MLflow URL: <Mocked MLflow URL>",
                "NVIDIA GPU acceleration: Disabled",
                "Intel GPU acceleration: Disabled",
            ],
        ),
        (
            False,
            None,
            {},
            [
                "MLflow deployment: Not ready",
                "NVIDIA GPU acceleration: Disabled",
                "Intel GPU acceleration: Disabled",
            ],
        ),
    ],
)
def test_get_status_with_different_scenarios(
    mocker: MagicMock,
    mlflow_exist: bool,
    mlflow_url: str,
    gpu_labels: Dict[str, str],
    expected_logs: List[str],
):
    """
    Test case to verify different scenarios of MLflow deployment and GPU acceleration status.
    """
    # Mock the functions
    mocker.patch("dss.status.does_mlflow_deployment_exist", return_value=mlflow_exist)
    mocker.patch("dss.status.get_service_url", return_value=mlflow_url)
    mocker.patch("dss.status.get_labels_for_node", return_value=gpu_labels)
    mocker.patch("dss.utils.get_labels_for_node", return_value=gpu_labels)

    # Mock the logger
    mock_logger = mocker.patch("dss.status.logger")

    # Call the function to test
    get_status(None)  # Pass None as the client argument since it's not used in this test case

    # Assertions
    for log_message in expected_logs:
        mock_logger.info.assert_any_call(log_message)
