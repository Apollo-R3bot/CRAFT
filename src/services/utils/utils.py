import json
import csv
import psutil
from datetime import datetime, timedelta
import hashlib
import os
from os import path
import shutil
import sys
import tempfile
import zipfile

BROWSER_PROCESS_NAMES = {
    "chrome.exe":        "Google Chrome",
    "msedge.exe":        "Microsoft Edge",
    "opera.exe":         "Opera",
    "opera_gx.exe":       "Opera GX",
    "firefox.exe":       "Firefox",
}

BROWSER_KEY_TO_PROCESSES = {
    "chrome":  ["chrome.exe"],
    "edge":    ["msedge.exe"],
    "opera":   ["opera.exe", "opera_gx.exe"],
    "firefox": ["firefox.exe"],
}

         
def convert_webkit_date(microseconds):
    return datetime.fromtimestamp(microseconds).strftime("%Y-%m-%d %H:%M:%S")

def convert_webkit_time(microseconds):
    epoch_start = datetime(1601, 1, 1)
    delta = timedelta(microseconds=microseconds)
    return (epoch_start + delta).strftime('%Y-%m-%d %H:%M:%S')

def convert_firefox_time(milliseconds):
    return datetime.utcfromtimestamp(milliseconds / 1000000).strftime('%Y-%m-%d %H:%M:%S')

def convert_firefox_expiry(expiry):
    try:
        if not expiry or expiry == 0:
            return "Session Cookie"
        expiry = int(expiry)

        # milliseconds
        if expiry > 9999999999:
            expiry = expiry / 1000
        return datetime.utcfromtimestamp(expiry).strftime("%Y-%m-%d %H:%M:%S")

    except Exception as e:
        return "Unknown"
    
def format_size(bytes_size):
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024**2:
        return f"{bytes_size / 1024:.2f} KB"
    elif bytes_size < 1024**3:
        return f"{bytes_size / (1024**2):.2f} MB"
    else:
        return f"{bytes_size / (1024**3):.2f} GB"
    
def write_to_csv(data, headers, output_file):
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(data)    

def safe_copy(db_path, logger=None):
    try:
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, os.path.basename(db_path))

        shutil.copy2(db_path, temp_path)
        return temp_path

    except Exception as e:
        if logger:
            logger.error(f"Safe copy failed for {db_path}: {e}")
        return None
    
def zip_folder(folder_path, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)

                if file_path == zip_path:
                    continue

                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)
    return zip_path

def hash_file_multi(file_path):
    md5 = hashlib.md5()
    sha1 = hashlib.sha1()
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            md5.update(chunk)
            sha1.update(chunk)
            sha256.update(chunk)

    return md5.hexdigest(), sha1.hexdigest(), sha256.hexdigest()

def hash_all_csv_to_txt(folder_path, output_file, zip_path=None):
    lines = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines.append(f"=== HASH REPORT ===")
    lines.append(f"Generated: {timestamp}")
    lines.append(f"Folder: {folder_path}")
    lines.append("-" * 80)

    for file in os.listdir(folder_path):
        if file.endswith(".csv"):
            full_path = os.path.join(folder_path, file)
            try:
                md5, sha1, sha256 = hash_file_multi(full_path)
                lines.append(f"File: {file}")
                lines.append(f"Path: {full_path}")
                lines.append(f"MD5   : {md5}")
                lines.append(f"SHA1  : {sha1}")
                lines.append(f"SHA256: {sha256}")
                lines.append("-" * 80)

            except Exception as e:
                lines.append(f"Error hashing {file}: {e}")
                lines.append("-" * 80)

    # Append ZIP hash
    if zip_path and os.path.exists(zip_path):
        try:
            md5, sha1, sha256 = hash_file_multi(zip_path)

            lines.append("=== ZIP FILE HASH ===")
            lines.append(f"File: {os.path.basename(zip_path)}")
            lines.append(f"Path: {zip_path}")
            lines.append(f"MD5   : {md5}")
            lines.append(f"SHA1  : {sha1}")
            lines.append(f"SHA256: {sha256}")
            lines.append("-" * 80)

        except Exception as e:
            lines.append(f"Error hashing ZIP: {e}")
            lines.append("-" * 80)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        
    return output_file

def write_json(data, output_file):
    with open(output_file,"w",encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )

def get_icon(name: str) -> str:
    base = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "resources", "icons")
    )
    return os.path.join(base, name)

def resource_path(relative_path):
    if getattr(sys, "frozen", False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    return os.path.join(base_path, relative_path)


def get_running_browsers() -> list:
    running = set()
    for proc in psutil.process_iter(attrs=["name"]):
        try:
            proc_name = (proc.info.get("name") or "").lower()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

        for exe_name, display_name in BROWSER_PROCESS_NAMES.items():
            if proc_name == exe_name:
                running.add(display_name)

    return sorted(running)


def is_browser_running(browser_key: str) -> bool:
    target_processes = BROWSER_KEY_TO_PROCESSES.get(browser_key.lower(), [])
    if not target_processes:
        return False

    for proc in psutil.process_iter(attrs=["name"]):
        try:
            proc_name = (proc.info.get("name") or "").lower()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

        if proc_name in target_processes:
            return True

    return False


def detect_browser_from_path(browser_path: str) -> str:
    if not browser_path:
        return ""
    path_lower = browser_path.lower()
    if "chrome" in path_lower:
        return "chrome"
    if "edge" in path_lower:
        return f"edge"
    if "opera" in path_lower:
        return "opera"
    if "firefox" in path_lower:
        return "firefox"
    return ""