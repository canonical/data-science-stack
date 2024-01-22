import click

from dss.logger import setup_logger
from dss.prepare_host_env import generate_prepare_host_script

# Set up logger
logger = setup_logger("logs/dss.log")


@click.group()
def main():
    """Command line interface for managing the DSS application."""


@main.command(name="prepare-host-env")
@click.option(
    "--gpu-driver-version",
    default="auto",
    help="Specify GPU driver version or use 'auto' for automatic detection.",
)
def prepare_host_env_command(gpu_driver_version: str) -> None:
    """
    Prints script for setting up microk8s on the host machine.
    Args:
        gpu_driver_version (str): GPU driver version 'auto' for auto or 'none' for no driver.
    """
    logger.info("Executing prepare_host_env command")
    content = generate_prepare_host_script(gpu_driver_version)
    click.echo(content)


if __name__ == "__main__":
    main()
