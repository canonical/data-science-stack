import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logger(log_file_path, log_level=logging.DEBUG):
    logger = logging.getLogger(__name__)

    # Check if the logger already has handlers to avoid duplication
    if not logger.handlers:
        logger.setLevel(log_level)

        # Create log formatter
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] [%(module)s] [%(funcName)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        if not os.path.exists(os.path.dirname(log_file_path)):
            os.makedirs(os.path.dirname(log_file_path))

        file_handler = RotatingFileHandler(log_file_path, maxBytes=5 * 1024 * 1024, backupCount=5)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
