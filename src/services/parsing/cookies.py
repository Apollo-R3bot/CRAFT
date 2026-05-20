import sqlite3
from services.utils.utils import convert_webkit_time, safe_copy

def extract_cookies(browser, files, user_profile):
    cookies = []
    for db_file in files:
        try:
            safe_db = safe_copy(db_file)
            if not safe_db:
                continue

            conn = sqlite3.connect(f"file:{safe_db}?mode=ro", uri=True)
            cursor = conn.cursor()

            query = '''
            SELECT host_key, name, creation_utc, last_access_utc, expires_utc, is_secure, is_httponly
            FROM cookies
            '''
            cursor.execute(query)
            for row in cursor.fetchall():
                host_key, name, creation_utc, last_access_utc, expires_utc, is_secure, is_httponly = row
                creation_time_utc = convert_webkit_time(creation_utc)
                last_access_time_utc = convert_webkit_time(last_access_utc)
                expiry_time_utc = convert_webkit_time(expires_utc)
                cookies.append([host_key, name, creation_time_utc, last_access_time_utc, expiry_time_utc, "Yes" if is_secure else "No", "Yes" if is_httponly else "No"])
            conn.close()
        except sqlite3.Error as e:
            print(f"Error extracting cookies from {db_file}: {e}")
    return cookies