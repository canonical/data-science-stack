import os
from typing import Optional

from lightkube import Client, KubeConfig

# Name for the environment variable storing kubeconfig
KUBECONFIG_ENV_VAR = "DSS_KUBECONFIG"
KUBECONFIG_DEFAULT = "./kubeconfig"


def get_default_kubeconfig(kubeconfig: Optional[str] = None) -> str:
    """
    Get the kubeconfig file path, from input, environment variable, or default.

    Args:
        kubeconfig (str): Path to a kubeconfig file. Defaults to None.

    Returns:
        str: the value of kubeconfig if it is not None, else:
             the value of the DSS_KUBECONFIG environment variable if it is set, else:
             the default value of "./kubeconfig"

    """
    if kubeconfig:
        return kubeconfig
    elif os.environ.get(KUBECONFIG_ENV_VAR, ""):
        return os.environ.get(KUBECONFIG_ENV_VAR, "")
    else:
        return KUBECONFIG_DEFAULT


def get_lightkube_client(kubeconfig: Optional[str] = None):
    # Compute the default kubeconfig, if not specified
    kubeconfig = KubeConfig.from_file(kubeconfig)
    lightkube_client = Client(config=kubeconfig)
    return lightkube_client
