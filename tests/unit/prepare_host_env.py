import pytest
from dss.prepare_host_env import generate_prepare_host_script

@pytest.mark.parametrize("gpu_driver_version, expected_line", [
    ("auto", "sudo microk8s enable gpu --driver auto"),
    ("none", ""),
    ("535.129.03", "sudo microk8s enable gpu --set driver.version='535.129.03'"),
])
def test_generate_prepare_host_script(gpu_driver_version, expected_line):
    result = generate_prepare_host_script(gpu_driver_version)

    if expected_line:
        assert expected_line in result
    else:
        assert expected_line not in result
