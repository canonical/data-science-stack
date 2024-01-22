import getpass
import unittest
from unittest.mock import patch

from dss.setup_microk8s import CommandExecutionError, install_microk8s


class TestInstallMicrok8s(unittest.TestCase):
    @patch("dss.setup_microk8s.run_commands", return_value=True)
    def test_install_microk8s_success_without_gpu(self, mock_run_commands):
        # Get the current user dynamically
        current_user = getpass.getuser()

        # Call the function with allow_gpu set to False
        install_microk8s(allow_gpu=False)

        # Assert that run_commands was called with the expected commands
        expected_commands = [
            "sudo snap install microk8s --channel=1.28/stable --classic",
            f"sudo usermod -a -G microk8s {current_user}",
            "sudo microk8s enable dns storage metallb:'10.64.140.43-10.64.140.49,192.168.0.105-192.168.0.111'",  # noqa: E501
            "sudo microk8s.kubectl wait --for=condition=available -nkube-system deployment/coredns deployment/hostpath-provisioner",  # noqa: E501
            "sudo microk8s.kubectl -n kube-system rollout status ds/calico-node",
        ]
        mock_run_commands.assert_called_once_with(expected_commands)

    @patch("dss.setup_microk8s.run_commands", return_value=True)
    def test_install_microk8s_success_with_gpu(self, mock_run_commands):
        # Get the current user dynamically
        current_user = getpass.getuser()

        # Call the function with allow_gpu set to True
        install_microk8s(allow_gpu=True)

        # Assert that run_commands was called with the expected commands, including the GPU command
        expected_commands = [
            "sudo snap install microk8s --channel=1.28/stable --classic",
            f"sudo usermod -a -G microk8s {current_user}",
            "sudo microk8s enable dns storage metallb:'10.64.140.43-10.64.140.49,192.168.0.105-192.168.0.111'",  # noqa: E501
            "sudo microk8s enable gpu --driver auto",
            "sudo microk8s.kubectl wait --for=condition=available -nkube-system deployment/coredns deployment/hostpath-provisioner",  # noqa: E501
            "sudo microk8s.kubectl -n kube-system rollout status ds/calico-node",
        ]
        mock_run_commands.assert_called_once_with(expected_commands)

    @patch("dss.setup_microk8s.run_commands")
    def test_install_microk8s_failure(self, mock_run_commands):
        # Simulate a CommandExecutionError during the execution of commands
        mock_run_commands.side_effect = CommandExecutionError("Fake error")

        install_microk8s(allow_gpu=True)

        # Assert that the function handles the CommandExecutionError and reverts changes
        expected_remove_commands = [
            "sudo snap remove microk8s --purge",
        ]
        mock_run_commands.assert_called_with(expected_remove_commands)


if __name__ == "__main__":
    unittest.main()
