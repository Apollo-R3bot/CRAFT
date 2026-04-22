
import csv
from datetime import datetime, timedelta
import os
import shutil
import tempfile

def convert_webkit_time(microseconds):
    epoch_start = datetime(1601, 1, 1)
    delta = timedelta(microseconds=microseconds)
    return (epoch_start + delta).strftime('%Y-%m-%d %H:%M:%S')

def convert_firefox_time(milliseconds):
    return datetime.utcfromtimestamp(milliseconds / 1000000).strftime('%Y-%m-%d %H:%M:%S')

def write_to_csv(data, headers, output_file):
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(data)    

def safe_copy(db_path):
    try:
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, os.path.basename(db_path))

        shutil.copy2(db_path, temp_path)
        return temp_path

    except Exception as e:
        print(f"Safe copy failed for {db_path}: {e}")
        return None