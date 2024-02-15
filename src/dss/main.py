import os

import click

from dss.initialize import initialize
from dss.logger import setup_logger

# Set up logger
logger = setup_logger("logs/dss.log")

# Name for the environment variable storing kubeconfig
KUBECONFIG_ENV_VAR = "DSS_KUBECONFIG"


@click.group()
def main():
    """Command line interface for managing the DSS application."""


@main.command(name="initialize")
@click.option(
    "--kubeconfig",
    help="Specify the kubeconfig content. Defaults to the value of file at path on the KUBECONFIG environment variable.",  # noqa E501
)
def initialize_command(kubeconfig: str) -> None:
    """
    Initialize the Kubernetes cluster and deploy charms.
    """
    logger.info("Executing initialize command")

    # If kubeconfig is provided, set it as an environment variable
    if kubeconfig:
        os.environ[KUBECONFIG_ENV_VAR] = kubeconfig

    # If kubeconfig is not provided, check environment variable
    elif KUBECONFIG_ENV_VAR not in os.environ:
        kubeconfig_path = os.environ.get("KUBECONFIG", "")
        if not kubeconfig_path:
            logger.error(
                "Missing required argument: --kubeconfig or environment variable KUBECONFIG"
            )
            exit(1)
        with open(kubeconfig_path, "r") as file:
            os.environ[KUBECONFIG_ENV_VAR] = file.read()

    initialize()


if __name__ == "__main__":
    main()
