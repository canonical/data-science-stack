from dss.logger import setup_logger

# Set up logger
logger = setup_logger("logs/dss.log")


def generate_prepare_host_script(gpu_driver_version: str) -> str:
    """
    Generate a script for setting up microk8s on the host machine.

    Args:
        gpu_driver_version (str): GPU driver version or 'auto' for automatic detection.

    Returns:
        str: Generated script content.
    """
    script_lines = [
        "#!/bin/bash",
        "sudo snap install microk8s --classic --channel=1.28/stable",
        "sudo usermod -a -G microk8s ubuntu",
        "sudo mkdir /home/ubuntu/.kube",
        "sudo mkdir -p /home/ubuntu/.local/share",
        "sudo chown -f -R ubuntu /home/ubuntu/.kube",
        "sudo chown -f -R ubuntu /home/ubuntu/.local/share",
        "sudo microk8s enable dns storage metallb:'10.64.140.43-10.64.140.49,192.168.0.105-192.168.0.111'",  # noqa: E501
    ]

    if gpu_driver_version.lower() != "none":
        if gpu_driver_version.lower() == "auto":
            script_lines.append("sudo microk8s enable gpu --driver auto")
        else:
            script_lines.append(
                f"sudo microk8s enable gpu --set driver.version='{gpu_driver_version}'"
            )

    script_lines.extend(
        [
            "sudo microk8s.kubectl wait --for=condition=available -nkube-system deployment/coredns deployment/hostpath-provisioner",  # noqa: E501
            "sudo microk8s.kubectl -n kube-system rollout status ds/calico-node",
        ]
    )

    return "\n".join(script_lines)
