import pytest

from dss.config import DEFAULT_NOTEBOOK_IMAGE


def pytest_addoption(parser):
    """
    Add a command-line option to pytest for specifying the notebook image.
    """
    parser.addoption(
        "--notebook-image",
        action="store",
        default=DEFAULT_NOTEBOOK_IMAGE,
        help="Docker image to use for the notebook tests",
    )


@pytest.fixture(scope="session")
def notebook_image(pytestconfig):
    """
    A pytest fixture to access the notebook image command-line option.
    """
    return pytestconfig.getoption("notebook_image")
