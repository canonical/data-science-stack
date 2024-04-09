import click

from dss.config import RECOMMENDED_IMAGES_MESSAGE
from dss.create_notebook import create_notebook
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


IMAGE_OPTION_HELP = "\b\nThe image used for the notebook server.\n" + RECOMMENDED_IMAGES_MESSAGE


@main.command(name="create")
@click.argument(
    "name",
    required=True,
)
@click.option(
    "--image",
    default="kubeflownotebookswg/jupyter-scipy:v1.8.0",
    help=IMAGE_OPTION_HELP,
)
# FIXME: Remove the kubeconfig param from the create command (and any tests) after
#  https://github.com/canonical/data-science-stack/issues/37
@click.option(
    "--kubeconfig",
    help=f"Path to a Kubernetes config file. Defaults to the value of the KUBECONFIG environment variable, else to '{KUBECONFIG_DEFAULT}'.",  # noqa E501
)
def create_notebook_command(name: str, image: str, kubeconfig: str) -> None:
    """Create a Jupyter notebook in DSS and connect it to MLflow.
    This command also outputs the URL to access the notebook on success.

    \b
    Examples:
        dss create my-notebook --image=pytorch
        dss create my-notebook --image=kubeflownotebookswg/jupyter-scipy:v1.8.0
    """
    logger.info("Executing create command")

    kubeconfig = get_default_kubeconfig(kubeconfig)
    lightkube_client = get_lightkube_client(kubeconfig)

    create_notebook(name=name, image=image, lightkube_client=lightkube_client)


@main.command(name="logs")
@click.option(
    "--kubeconfig",
    help=f"Path to a Kubernetes config file. Defaults to the value of the KUBECONFIG environment variable, else to '{KUBECONFIG_DEFAULT}'.",  # noqa E501
)
@click.argument("notebook_name", required=False)
@click.option(
    "--all", "print_all", is_flag=True, help="Print the logs for all notebooks and MLflow."
)
@click.option("--mlflow", is_flag=True, help="Print the logs for the MLflow deployment.")
def logs_command(kubeconfig: str, notebook_name: str, print_all: bool, mlflow: bool) -> None:
    """Prints the logs for the specified notebook or DSS component.

    \b
    Examples:
      dss logs my-notebook
      dss logs --mlflow
      dss logs --all
    """
    if not notebook_name and not mlflow and not print_all:
        click.echo(
            "Failed to retrieve logs. Missing notebook name. Run the logs command with desired notebook name."  # noqa E501
        )
        return

    kubeconfig = get_default_kubeconfig(kubeconfig)
    lightkube_client = get_lightkube_client(kubeconfig)

    if print_all:
        get_logs("all", None, lightkube_client)
    elif mlflow:
        get_logs("mlflow", None, lightkube_client)
    elif notebook_name:
        get_logs("notebooks", notebook_name, lightkube_client)


if __name__ == "__main__":
    main()
