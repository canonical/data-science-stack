import click

from dss.initialize import initialize
from dss.logger import setup_logger
from dss.remove_notebook import remove_notebook
from dss.utils import KUBECONFIG_DEFAULT, get_default_kubeconfig, get_lightkube_client

# Set up logger
logger = setup_logger("logs/dss.log")


@click.group()
def main():
    """Command line interface for managing the DSS application."""


@main.command(name="initialize")
@click.option(
    "--kubeconfig",
    help=f"Path to a Kubernetes config file. Defaults to the value of the KUBECONFIG environment variable, else to '{KUBECONFIG_DEFAULT}'.",  # noqa E501
)
def initialize_command(kubeconfig: str) -> None:
    """
    Initialize DSS on the given Kubernetes cluster.
    """
    logger.info("Executing initialize command")

    kubeconfig = get_default_kubeconfig(kubeconfig)
    lightkube_client = get_lightkube_client(kubeconfig)

    initialize(lightkube_client=lightkube_client)


# FIXME: remove the `--kubeconfig`` option
# after fixing https://github.com/canonical/data-science-stack/issues/37
@main.command(name="remove-notebook")
@click.option(
    "--name",
    help="Name of the Notebook to removed.",
)
@click.option(
    "--kubeconfig",
    help=f"Path to a Kubernetes config file. Defaults to the value of the KUBECONFIG environment variable, else to '{KUBECONFIG_DEFAULT}'.",  # noqa E501
)
def remove_notebook_command(name: str, kubeconfig: str):
    """
    Remove a Notebook server.
    """
    logger.info("Executing remove-notebook command")

    kubeconfig = get_default_kubeconfig(kubeconfig)
    lightkube_client = get_lightkube_client(kubeconfig)

    remove_notebook(name=name, lightkube_client=lightkube_client)


if __name__ == "__main__":
    main()
