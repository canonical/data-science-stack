import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional


def setup_logger(log_file_path: str, log_level: int = logging.DEBUG) -> logging.Logger:
    """
    Set up a logger with a file handler and console handler.

    Args:
        log_file_path (str): Path to the log file.
        log_level (int, optional): Logging level. Defaults to logging.DEBUG.

    Returns:
        logging.Logger: Configured logger object.
    """
    logger = logging.getLogger(__name__)

    # Check if the logger already has handlers to avoid duplication
    if not logger.handlers:
        logger.setLevel(log_level)

        # Create log formatter
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] [%(module)s] [%(funcName)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Create the log directory if it doesn't exist
        if not os.path.exists(os.path.dirname(log_file_path)):
            os.makedirs(os.path.dirname(log_file_path))

        # Create file handler
        file_handler = RotatingFileHandler(log_file_path, maxBytes=5 * 1024 * 1024, backupCount=5)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)

        # Add handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
