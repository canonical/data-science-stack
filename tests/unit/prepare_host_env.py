from dss.prepare_host_env import generate_prepare_host_script


def test_generate_prepare_host_script_auto():
    gpu_driver_version = "auto"
    result = generate_prepare_host_script(gpu_driver_version)

    assert "sudo microk8s enable gpu --driver auto" in result
    assert "sudo microk8s enable gpu --set driver.version" not in result


def test_generate_prepare_host_script_none():
    gpu_driver_version = "none"
    result = generate_prepare_host_script(gpu_driver_version)

    assert "sudo microk8s enable gpu --driver auto" not in result
    assert "sudo microk8s enable gpu --set driver.version" not in result


def test_generate_prepare_host_script_specific_version():
    gpu_driver_version = "535.129.03"
    result = generate_prepare_host_script(gpu_driver_version)

    assert f"sudo microk8s enable gpu --set driver.version='{gpu_driver_version}'" in result
    assert "sudo microk8s enable gpu --driver auto" not in result
