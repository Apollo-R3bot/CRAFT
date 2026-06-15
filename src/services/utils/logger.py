import logging
import os
import platform
import socket
import getpass
import sys
from datetime import datetime
import winreg

APP_VERSION = "v1.0.0 (Portable)"

def get_windows_version_string():
    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
        )

        product_name = winreg.QueryValueEx(key,"ProductName")[0]
        current_build = winreg.QueryValueEx(key,"CurrentBuild")[0]
        ubr = winreg.QueryValueEx(key,"UBR")[0]
        architecture = ("x64"if platform.machine().endswith("64")else "x86")

        return (
            f"{product_name} "
            f"{architecture} "
            f"(Build {current_build}.{ubr})"
        )

    except Exception:
        return "Unknown Windows Version"

def log_system_info(log_file):
    windows_version = get_windows_version_string()
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(f"Craft               : {APP_VERSION}\n")
        f.write(f"Hostname            : {socket.gethostname()}\n")
        f.write(f"Username            : {getpass.getuser()}\n")
        f.write(
            f"OS Release          : {platform.system()} {platform.release()}\n"
        )
        f.write(
            f"Windows Version     : {windows_version}\n"
        )
        f.write("=" * 60 + "\n")

def setup_logger(log_folder, name="CRAFT"):
    os.makedirs(log_folder, exist_ok=True)

    log_file = os.path.join(
        log_folder,
        f"craft.log"
    )

    log_system_info(log_file)

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