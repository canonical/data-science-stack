import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logger(
    log_file_path: str, file_log_level: int = logging.DEBUG, console_log_level: int = logging.INFO
) -> logging.Logger:
    """
    Set up a logger with a file handler and console handler.

    Args:
        log_file_path (str): Path to the log file.
        file_log_level (int, optional): Logging level for file logs. Defaults to logging.DEBUG.
        console_log_level (int, optional): Logging level for console logs. Defaults to logging.INFO.

    Returns:
        logging.Logger: Configured logger object.
    """
    logger = logging.getLogger(__name__)

    # Check if the logger already has handlers to avoid duplication
    if not logger.handlers:
        logger.setLevel(file_log_level)

        # Create console formatter
        console_formatter = logging.Formatter(
            "[%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Create file formatter
        file_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] [%(module)s] [%(funcName)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Create the log directory if it doesn't exist
        if not os.path.exists(os.path.dirname(log_file_path)):
            os.makedirs(os.path.dirname(log_file_path))

        # Create file handler
        file_handler = RotatingFileHandler(log_file_path, maxBytes=5 * 1024 * 1024, backupCount=5)
        file_handler.setLevel(file_log_level)
        file_handler.setFormatter(file_formatter)

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(console_log_level)
        console_handler.setFormatter(console_formatter)

        # Add handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
