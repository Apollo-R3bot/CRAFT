import logging
import os
from datetime import datetime

def setup_logger(log_folder, name="CRAFT"):
    os.makedirs(log_folder, exist_ok=True)

    log_file = os.path.join(
        log_folder,
        f"logs.log"
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

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger