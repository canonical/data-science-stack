import pytest


def pytest_addoption(parser):
    """
    Add a command-line option to pytest for specifying the notebook image.
    """
    parser.addoption(
        "--notebook-image",
        action="store",
        default="kubeflownotebookswg/jupyter-scipy:v1.8.0",
        help="Docker image to use for the notebook tests",
    )


@pytest.fixture(scope="session")
def notebook_image(pytestconfig):
    """
    A pytest fixture to access the notebook image command-line option.
    """
    return pytestconfig.getoption("notebook_image")
