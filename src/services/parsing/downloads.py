import os
import sqlite3
from services.utils.utils import convert_webkit_time, format_size, safe_copy

DANGER_TYPE_MAP = {
    0: "Safe",
    1: "Dangerous File",
    2: "Dangerous URL",
    3: "Dangerous Content",
    4: "Uncommon Content",
    5: "User Validation Required",
    6: "Dangerous Host",
    7: "Potentially Unwanted Program (PUP)"
}

INTERRUPT_REASON_MAP = {
    0: "No Interrupt",
    1: "File Error",
    2: "Access Denied",
    3: "Disk Full",
    5: "Network Error",
    7: "Virus Detected",
    10: "Timeout",
    11: "Canceled",
    12: "Browser Shutdown"
}

def extract_downloads(browser, files, user_profile):
    downloads = []
    for db_file in files:
        try:
            safe_db = safe_copy(db_file)
            if not safe_db:
                continue

            conn = sqlite3.connect(f"file:{safe_db}?mode=ro", uri=True)
            cursor = conn.cursor()

            query = '''
            SELECT target_path, start_time, total_bytes, danger_type, interrupt_reason, end_time, opened
            FROM downloads
            '''
            cursor.execute(query)
            
            for row in cursor.fetchall():
                target_path, start_time, total_bytes, danger_type, interrupt_reason, end_time, opened = row
                start_time_utc = convert_webkit_time(start_time)
                end_time_utc = convert_webkit_time(end_time) if end_time else None
                danger_description = DANGER_TYPE_MAP.get(danger_type, "Unknown")
                interrupt_description = INTERRUPT_REASON_MAP.get(interrupt_reason, "Unknown")
                opened_description = "Yes" if opened == 1 else "No"
                total_size = format_size(total_bytes) if total_bytes else "0 B"
                downloads.append([start_time_utc, end_time_utc, target_path, total_size, danger_description, interrupt_description, opened_description])
            conn.close()
        except sqlite3.Error as e:
            print(f"Error extracting downloads from {db_file}: {e}")
    return downloads