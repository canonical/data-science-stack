import click

from dss.initialize import initialize
from dss.logger import setup_logger
from dss.logs import get_logs
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


@main.command(name="logs")
@click.option(
    "--parts",
    type=click.Choice(["notebooks", "mlflow"]),
    required=True,
    help="Specify which part's logs you want to retrieve: 'notebooks' or 'mlflow'.",
)
@click.option(
    "--name",
    help="Specify the name of the notebook or deployment to retrieve logs from.",
)
@click.option(
    "--kubeconfig",
    help=f"Path to a Kubernetes config file. Defaults to the value of the KUBECONFIG environment variable, else to '{KUBECONFIG_DEFAULT}'.",  # noqa E501
)
def logs_command(parts: str, name: str, kubeconfig: str) -> None:
    """
    Retrieve logs from specified parts of the DSS application.
    """
    logger.info(f"Retrieving logs for {parts} - {name}")

    if parts == "mlflow" and name is not None:
        click.echo("Warning: The 'name' parameter will be ignored for 'mlflow' logs.")
    elif parts == "notebooks" and name is None:
        click.echo("Error: The 'name' parameter is required for 'notebooks' logs.")
        return

    kubeconfig = get_default_kubeconfig(kubeconfig)
    lightkube_client = get_lightkube_client(kubeconfig)
    get_logs(parts, name, lightkube_client)


if __name__ == "__main__":
    main()
