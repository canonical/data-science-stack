import click

from dss.config import DEFAULT_NOTEBOOK_IMAGE, RECOMMENDED_IMAGES_MESSAGE
from dss.create_notebook import create_notebook
from dss.initialize import initialize
from dss.list import list_notebooks
from dss.logger import setup_logger
from dss.logs import get_logs
from dss.purge import purge
from dss.remove_notebook import remove_notebook
from dss.start import start_notebook
from dss.status import get_status
from dss.stop import stop_notebook
from dss.utils import KUBECONFIG_DEFAULT, get_lightkube_client, save_kubeconfig

# Set up logger
logger = setup_logger()


@click.group()
def main():
    """Command line interface for managing the DSS application."""


@main.command(name="initialize")
@click.option(
    "--kubeconfig",
    help=f"Content of a Kubernetes config file defining the cluster to use.  The kubeconfig will be saved to {KUBECONFIG_DEFAULT} and overwrite any kubeconfig previously stored there.  Future `dss` commands will reuse this kubeconfig by default.",  # noqa E501
)
def initialize_command(kubeconfig: str) -> None:
    """
    Initialize DSS on the given Kubernetes cluster.
    """
    logger.info("Executing initialize command")

    try:
        if kubeconfig:
            save_kubeconfig(kubeconfig=kubeconfig)
    except Exception as e:
        logger.debug(f"Failed to save kubeconfig: {e}.", exc_info=True)
        logger.error(f"Failed to save kubeconfig: {str(e)}.")
        click.get_current_context().exit(1)

    try:
        lightkube_client = get_lightkube_client()
        initialize(lightkube_client=lightkube_client)
    except RuntimeError:
        click.get_current_context().exit(1)
    except Exception as e:
        logger.debug(f"Failed to initialize dss: {e}.", exc_info=True)
        logger.error(f"Failed to initialize dss: {str(e)}.")
        click.get_current_context().exit(1)


initialize_command.help += """

\b
Examples
  # To initialize DSS with microk8s's kubeconfig
  dss initialize --kubeconfig "$(microk8s config)"

"""


IMAGE_OPTION_HELP = "\b\nThe image used for the notebook server.\n"


@main.command(name="create")
@click.argument(
    "name",
    required=True,
)
@click.option(
    "--image",
    default=DEFAULT_NOTEBOOK_IMAGE,
    help=IMAGE_OPTION_HELP,
)
def create_notebook_command(name: str, image: str) -> None:
    """Create a Jupyter notebook in DSS and connect it to MLflow. This command also
    outputs the URL to access the notebook on success.

    \b
    """
    logger.info("Executing create command")
    if image == DEFAULT_NOTEBOOK_IMAGE:
        logger.info(
            f"No image is specified. Using default value {DEFAULT_NOTEBOOK_IMAGE}."
            " For more information on using a specific image, see dss create --help."
        )

    try:
        lightkube_client = get_lightkube_client()

        create_notebook(name=name, image=image, lightkube_client=lightkube_client)
    except RuntimeError:
        click.get_current_context().exit(1)
    except Exception as e:
        logger.debug(f"Failed to create notebook {name}: {e}.", exc_info=True)
        logger.error(f"Failed to create notebook {name}: {str(e)}.")
        click.get_current_context().exit(1)


create_notebook_command.help += f"""
Examples
  dss create my-notebook --image=pytorch
  dss create my-notebook --image={DEFAULT_NOTEBOOK_IMAGE}

    \b\n{RECOMMENDED_IMAGES_MESSAGE}
"""


@main.command(name="logs")
@click.argument("notebook_name", required=False)
@click.option(
    "--all", "print_all", is_flag=True, help="Print the logs for all notebooks and MLflow."
)
@click.option("--mlflow", is_flag=True, help="Print the logs for the MLflow deployment.")
def logs_command(notebook_name: str, print_all: bool, mlflow: bool) -> None:
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

    try:
        lightkube_client = get_lightkube_client()

        if print_all:
            get_logs("all", None, lightkube_client)
        elif mlflow:
            get_logs("mlflow", None, lightkube_client)
        elif notebook_name:
            get_logs("notebooks", notebook_name, lightkube_client)
    except RuntimeError:
        click.get_current_context().exit(1)
    except Exception as e:
        logger.debug(f"Failed to retrieve logs: {e}.", exc_info=True)
        logger.error(f"Failed to retrieve logs: {str(e)}.")
        click.get_current_context().exit(1)


@main.command(name="status")
def status_command() -> None:
    """Checks the status of key components within the DSS environment. Verifies if the MLflow deployment is ready and checks if GPU acceleration is enabled on the Kubernetes cluster by examining the labels of Kubernetes nodes for NVIDIA or Intel GPU devices."""  # noqa E501
    try:
        lightkube_client = get_lightkube_client()

        get_status(lightkube_client)
    except RuntimeError:
        click.get_current_context().exit(1)
    except Exception as e:
        logger.debug(f"Failed to retrieve status: {e}.", exc_info=True)
        logger.error(f"Failed to retrieve status: {str(e)}.")
        click.get_current_context().exit(1)


@main.command(name="list")
@click.option(
    "--wide",
    default=False,
    is_flag=True,
    help="Display full information without truncation.",
)
def list_command(wide: bool):
    """
    Lists all created notebooks in the DSS environment.

    The output is truncated to 80 characters. Use the --wide flag to display full information.
    """
    try:
        lightkube_client = get_lightkube_client()
        list_notebooks(lightkube_client, wide)
    except RuntimeError:
        click.get_current_context().exit(1)
    except Exception as e:
        logger.debug(f"Failed to list notebooks: {e}.", exc_info=True)
        logger.error(f"Failed to list notebooks: {str(e)}.")
        click.get_current_context().exit(1)


@main.command(name="stop")
@click.argument("notebook_name", required=True)
def stop_notebook_command(notebook_name: str):
    """
    Stops a running notebook in the DSS environment.
    \b
    Example:
        dss stop my-notebook
    """
    try:
        lightkube_client = get_lightkube_client()
        stop_notebook(name=notebook_name, lightkube_client=lightkube_client)
    except RuntimeError:
        click.get_current_context().exit(1)
    except Exception as e:
        logger.debug(f"Failed to stop notebook: {e}.", exc_info=True)
        logger.error(f"Failed to stop notebook: {str(e)}.")
        click.get_current_context().exit(1)


@main.command(name="start")
@click.argument(
    "name",
    required=True,
)
def start_notebook_command(name: str):
    """
    Starts a stopped notebook in the DSS environment.
    \b
    Example:
        dss start my-notebook
    """
    logger.info("Executing start command")

    try:
        lightkube_client = get_lightkube_client()
        start_notebook(name=name, lightkube_client=lightkube_client)
    except RuntimeError:
        click.get_current_context().exit(1)
    except Exception as e:
        logger.debug(f"Failed to start notebook: {e}.", exc_info=True)
        logger.error("Failed to start notebook.")
        logger.info("Run 'dss list' to check all notebooks.")
        click.get_current_context().exit(1)


@main.command(name="remove")
@click.argument(
    "name",
    required=True,
)
def remove_notebook_command(name: str):
    """
    Remove a Jupter Notebook in DSS with the name NAME.
    """
    logger.info("Executing remove command")

    try:
        lightkube_client = get_lightkube_client()

        remove_notebook(name=name, lightkube_client=lightkube_client)
    except RuntimeError:
        click.get_current_context().exit(1)
    except Exception as e:
        logger.debug(f"Failed to remove notebook: {e}.", exc_info=True)
        logger.error(f"Failed to remove notebook: {str(e)}.")
        click.get_current_context().exit(1)


@main.command(name="purge")
def purge_command() -> None:
    """
    Removes all notebooks and DSS components.
    """
    try:
        lightkube_client = get_lightkube_client()
        purge(lightkube_client=lightkube_client)
    except RuntimeError:
        click.get_current_context().exit(1)
    except Exception as e:
        logger.debug(f"Failed to purge DSS components: {e}.", exc_info=True)
        logger.error(f"Failed to purge DSS components: {str(e)}.")
        click.get_current_context().exit(1)


if __name__ == "__main__":
    main()
