import logging
import os
import sys
from logging.handlers import RotatingFileHandler


class CustomFormatter(logging.Formatter):
    """Custom formatter to adjust format based on log level."""

    def format(self, record: logging.LogRecord) -> str:  # noqa: A003
        # Check if the log level is INFO and remove the brackets if so
        if record.levelname == "INFO":
            self._style._fmt = "%(message)s"
        else:
            self._style._fmt = "[%(levelname)s] %(message)s"
        return super().format(record)


def setup_logger(
    log_file_path: str = None,
    file_log_level: int = logging.DEBUG,
    console_log_level: int = logging.INFO,
) -> logging.Logger:
    """
    Set up a logger with optional file and console arguments.

    Args:
        log_file_path (str, optional): Path to the log file. Defaults to $SNAP_COMMON/logs/dss.log.
        file_log_level (int, optional): Logging level for file logs. Defaults to logging.DEBUG.
        console_log_level (int, optional): Logging level for console logs. Defaults to logging.INFO.

    Returns:
        logging.Logger: Configured logger.
    """
    logger = logging.getLogger(__name__)

    if not logger.handlers:
        logger.setLevel(min(file_log_level, console_log_level))

        # Console formatter
        console_formatter = CustomFormatter(
            "[%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(console_log_level)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # Setup file handler if path is provided or fallback to SNAP_COMMON
        if log_file_path is None:
            snap_common = os.environ.get("SNAP_COMMON", "/tmp")
            log_dir = os.path.join(snap_common, "logs")
            os.makedirs(log_dir, exist_ok=True)
            log_file_path = os.path.join(log_dir, "dss.log")

        # File formatter
        file_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] [%(module)s] [%(funcName)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler = RotatingFileHandler(log_file_path, maxBytes=5 * 1024 * 1024, backupCount=5)
        file_handler.setLevel(file_log_level)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger
