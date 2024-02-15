import subprocess


def test_initialize_creates_dss_namespace() -> None:
    """
    Integration test to verify if the initialize command creates the 'dss' namespace and
    the 'mlflow-deployment' deployment is active in the 'dss' namespace.
    """
    # Run the initialize command with the provided kubeconfig
    microk8s_config = subprocess.run(["microk8s", "config"], capture_output=True, text=True)
    kubeconfig_content: str = microk8s_config.stdout.strip()

    result = subprocess.run(
        ["dss", "initialize", "--kubeconfig", kubeconfig_content],
        capture_output=True,
        text=True,
    )

    # Check if the command executed successfully
    print(result.stdout)
    assert result.returncode == 0

    # Check if the dss namespace exists using kubectl
    kubectl_result = subprocess.run(
        ["kubectl", "get", "namespace", "dss"], capture_output=True, text=True
    )

    # Check if the namespace exists
    assert "dss" in kubectl_result.stdout

    # Check if the mlflow-deployment deployment is active in the dss namespace
    kubectl_result = subprocess.run(
        ["kubectl", "get", "deployment", "mlflow-deployment", "-n", "dss"],
        capture_output=True,
        text=True,
    )

    # Check if the deployment exists and is active
    assert "mlflow-deployment" in kubectl_result.stdout
    assert (
        "1/1" in kubectl_result.stdout
    )  # Assuming it should have 1 replica and all are available
