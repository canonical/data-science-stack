import subprocess

import pytest


@pytest.mark.integration
def test_prepare_host_env_integration():
    # Run the dss prepare-host-env command and capture the script
    result = subprocess.run(
        ["dss", "prepare-host-env", "--gpu-driver-version=none"],
        stdout=subprocess.PIPE,
        text=True,
        check=True,
    )
    script = result.stdout

    # Run the generated script
    subprocess.run(script, shell=True, check=True)

    # Check the status of microk8s
    microk8s_status = subprocess.run(
        ["sudo", "microk8s", "status"], stdout=subprocess.PIPE, text=True, check=True
    )
    assert "microk8s is running" in microk8s_status.stdout
