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
    11: "Blocked",
    12: "Browser Shutdown",
    20: "Network Error",
    21: "Operation Timed Out",
    22: "Connection Lost",
    23: "Server Down",
    30: "Server Error",
    31: "Range Request Error",
    32: "Server Precondition Error",
    33: "Unable to get file",
    34: "Server Unauthorized",
    35: "Server Certificate Problem",
    36: "Server Access Forbidden",
    37: "Server Unreachable",
    38: "Content Length Mismatch",
    39: "Cross Origin Redirect",
    40: "Cancelled",
    41: "Browser Shutdown",
    50: "Browser Crashed"
}

DOWNLOAD_STATE = {
    0: 'In Progress', 
    1: 'Complete', 
    2: 'Cancelled', 
    3: 'Interrupted',
    4: 'Interrupted'
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

            previous_id = None
            previous_time = None

            query = '''
            SELECT id, target_path, tab_url, start_time, total_bytes, interrupt_reason, state
            FROM downloads
            ORDER BY id ASC
            '''
            cursor.execute(query)

            for row in cursor.fetchall():
                download_id, target_path, tab_url, start_time, total_bytes, interrupt_reason, state = row
                start_time_utc = convert_webkit_time(start_time)
                interrupt_description = INTERRUPT_REASON_MAP.get(interrupt_reason, "Unknown")
                total_size = format_size(total_bytes) if total_bytes else "0 B"
                status = DOWNLOAD_STATE.get(state, f'state={state}')
                file_name = os.path.basename(target_path)

                comment = ""

                if previous_id is not None:
                    gap = download_id - previous_id - 1
                    comment = (
                        f"Possible deletion occurred: {gap} download record(s) "
                        f"missing between between "
                        f"{previous_time} and {start_time_utc}"
                    )
                    if gap > 0:
                        downloads.append([start_time_utc, f"GAP of {gap} deleted downloads", "", "", "Unknown", "Deleted", comment])
                downloads.append([start_time_utc, file_name, total_size, tab_url, interrupt_description, status, f"Saved in {target_path}"])
                previous_id = download_id
                previous_time = start_time_utc
                
            conn.close()
        except sqlite3.Error as e:
            print(f"Error extracting downloads from {db_file}: {e}")
    return downloads