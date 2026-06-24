import logging
import os
import platform
import socket
import getpass
import sys
from datetime import datetime

APP_VERSION = "v1.0.0 (Portable)"


def setup_logger(log_folder, name="CRAFT"):
    os.makedirs(log_folder, exist_ok=True)

    log_file = os.path.join(
        log_folder,
        f"craft.log"
    )

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )

    file_handler = logging.FileHandler(
        log_file, 
        encoding="utf-8",
        mode="a"
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger