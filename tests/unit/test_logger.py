import logging
import os
import uuid
from typing import Generator, Optional

import pytest

from dss.logger import setup_logger  # Adjust with your actual module name


@pytest.fixture(scope="function")
def logger_setup(
    tmp_path_factory: pytest.TempPathFactory,
) -> Generator[logging.Logger, None, None]:
    """Fixture to set up a unique logger with a log file for the test."""
    # Generate a random and unique logger name to avoid conflicts
    unique_logger_name = f"test_logger_{uuid.uuid4().hex}"

    # Set a static log file name, unique to each test
    log_file_name = "test_log.log"
    log_file_path = tmp_path_factory.mktemp("logs") / log_file_name

    # Create a unique logger instance
    logger = logging.getLogger(unique_logger_name)

    # Clear any existing handlers (if reusing logger names between tests)
    logger.handlers.clear()

    logger = setup_logger(
        log_file_path=str(log_file_path),
    )

    # Force creation of the log file by logging an empty message
    logger.debug("Logger initialized")

    yield logger

    # Cleanup: remove the log file after the test is done
    if log_file_path.exists():
        os.remove(log_file_path)


def get_log_file_path(logger: logging.Logger) -> Optional[str]:
    """Helper function to get the file path of the log file used by the logger."""
    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
            return handler.baseFilename
    return None


@pytest.mark.parametrize(
    "log_level, log_message, expected_prefix",
    [
        (logging.INFO, "This is an info message", "[INFO]"),
        (logging.WARNING, "This is a warning message", "[WARNING]"),
        (logging.DEBUG, "This is a debug message", "[DEBUG]"),
        (logging.ERROR, "This is an error message", "[ERROR]"),
    ],
)
def test_file_logs(
    logger_setup: logging.Logger, log_level: int, log_message: str, expected_prefix: str
) -> None:
    """Test that logs include the correct prefix in the file output."""
    logger = logger_setup

    logger.log(log_level, log_message)

    log_file_path = get_log_file_path(logger)
    assert log_file_path is not None, "Log file path could not be determined."

    with open(log_file_path, "r") as f:
        log_contents = f.read().strip()

    assert expected_prefix in log_contents
    assert log_message in log_contents


@pytest.mark.parametrize(
    "log_level, log_message, expected_prefix",
    [
        (logging.INFO, "This is an info message", ""),  # No prefix for INFO in console
        (logging.WARNING, "This is a warning message", "[WARNING]"),
        (logging.ERROR, "This is an error message", "[ERROR]"),
    ],
)
def test_console_logs(
    logger_setup: logging.Logger,
    capfd: pytest.CaptureFixture,
    log_level: int,
    log_message: str,
    expected_prefix: str,
) -> None:
    """Test that logs include the correct prefix in the console output."""
    logger = logger_setup

    logger.log(log_level, log_message)

    # Capture stdout output
    captured = capfd.readouterr()

    # Assert that the output includes the correct prefix (or lack of it for INFO)
    if expected_prefix:
        assert expected_prefix in captured.out
    else:
        assert "[INFO]" not in captured.out  # Ensure no [INFO] prefix

    assert log_message in captured.out
