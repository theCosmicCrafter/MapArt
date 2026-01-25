import logging
import os
from datetime import datetime


def setup_logger():
    """
    Setup a logger that prints to both file and console.
    """
    if not os.path.exists("logs"):
        os.makedirs("logs")

    log_filename = os.path.join("logs", f"app_{datetime.now().strftime('%Y%m%d')}.log")

    logger = logging.getLogger("map_art_generator")
    logger.setLevel(logging.DEBUG)

    # Create handlers
    file_handler = logging.FileHandler(log_filename)
    console_handler = logging.StreamHandler()

    # Create formatters and add them to handlers
    log_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(log_format)
    console_handler.setFormatter(log_format)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


logger = setup_logger()
