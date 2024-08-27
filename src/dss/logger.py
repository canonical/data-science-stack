import logging
import os
import sys
from logging.handlers import RotatingFileHandler

class InfoFilter(logging.Filter):
    """Filter to remove [INFO] level name in console output."""
    
    def filter(self, record: logging.LogRecord) -> bool:
        if record.levelno == logging.INFO:
            record.levelname = ''  # Remove level name for INFO
        return True

class CustomFormatter(logging.Formatter):
    """Custom formatter to adjust format based on log level."""
    
    def format(self, record: logging.LogRecord) -> str:
        if not record.levelname:  # Skip brackets if levelname is empty
            self._style._fmt = "%(message)s"
        else:
            self._style._fmt = "[%(levelname)s] %(message)s"
        return super().format(record)

def setup_logger(
    log_file_path: str, 
    file_log_level: int = logging.DEBUG, 
    console_log_level: int = logging.INFO
) -> logging.Logger:
    """
    Set up a logger with both file and console handlers.
    
    Args:
        log_file_path (str): Path to the log file.
        file_log_level (int, optional): Logging level for file logs. Defaults to logging.DEBUG.
        console_log_level (int, optional): Logging level for console logs. Defaults to logging.INFO.
        
    Returns:
        logging.Logger: Configured logger object.
    """
    logger = logging.getLogger(__name__)

    if not logger.handlers:
        logger.setLevel(file_log_level)

        # Formatter for console - omits [INFO]
        console_formatter = CustomFormatter(
            "[%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Formatter for file - includes [INFO]
        file_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] [%(module)s] [%(funcName)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Ensure the log directory exists
        if not os.path.exists(os.path.dirname(log_file_path)):
            os.makedirs(os.path.dirname(log_file_path))

        # File handler setup
        file_handler = RotatingFileHandler(log_file_path, maxBytes=5 * 1024 * 1024, backupCount=5)
        file_handler.setLevel(file_log_level)
        file_handler.setFormatter(file_formatter)

        # Console handler setup
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(console_log_level)
        console_handler.setFormatter(console_formatter)
        console_handler.addFilter(InfoFilter())  # Apply filter to remove [INFO]

        # Add handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
