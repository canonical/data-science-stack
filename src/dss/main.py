from argparse import RawTextHelpFormatter
import click

from dss.create_notebook import create_notebook
from dss.initialize import initialize
from dss.logger import setup_logger
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


CREATE_NOTEBOOK_IMAGE_HELP = """
\b\nThe image used for the notebook server.  Suggested images:
- kubeflownotebookswg/jupyter-scipy:v1.8.0
- kubeflownotebookswg/jupyter-pytorch-full:v1.8.0
- kubeflownotebookswg/jupyter-pytorch-cuda-full:v1.8.0
- kubeflownotebookswg/jupyter-tensorflow-full:v1.8.0
- kubeflownotebookswg/jupyter-tensorflow-cuda-full:v1.8.0
"""


@main.command(name="create-notebook")
@click.option(
    "--name",
    help="Name given to the notebook being created.",
)
@click.option(
    "--image",
    help=CREATE_NOTEBOOK_IMAGE_HELP,
)
@click.option(
    "--kubeconfig",
    help=f"Path to a Kubernetes config file. Defaults to the value of the KUBECONFIG environment variable, else to '{KUBECONFIG_DEFAULT}'.",  # noqa E501
)
def create_notebook_command(name: str, image: str, kubeconfig: str) -> None:
    """
    Create a Notebook server.
    """
    logger.info("Executing create-notebook command")

    kubeconfig = get_default_kubeconfig(kubeconfig)
    lightkube_client = get_lightkube_client(kubeconfig)

    create_notebook(name=name, image=image, lightkube_client=lightkube_client)


if __name__ == "__main__":
    main()
