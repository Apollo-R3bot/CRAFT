from datetime import datetime
import os
import sqlite3
from services.utils.utils import convert_firefox_time, convert_webkit_date, safe_copy

def extract_autofill(browser, files, user_profile, logger=None):
    autofill = []

    for db_file in files:
        try:
            safe_db = safe_copy(db_file)
            if not safe_db:
                continue

            conn = sqlite3.connect(f"file:{safe_db}?mode=ro", uri=True)
            cursor = conn.cursor()

            # CHROMIUM (Chrome, Edge, Opera)
            if browser in ["chrome", "edge", "opera"]:
                cursor.execute("""
                    SELECT name, value, date_created, date_last_used, count
                    FROM autofill
                """)

                for row in cursor.fetchall():
                    count = str(row[4])
                    comment = f'Used={count} times, Last time used {convert_webkit_date(row[3])}'
                    autofill.append([
                        convert_webkit_date(row[2]),
                        row[0],
                        row[1],
                        comment
                    ])

            # FIREFOX
            elif browser == "firefox":
                cursor.execute("""
                    SELECT fieldname, value, timesUsed, firstUsed, lastUsed
                    FROM moz_formhistory
                """)

                for row in cursor.fetchall():
                    count = str(row[2])
                    comment = f'Used={count} times, Last time used {convert_firefox_time(row[4])}'
                    autofill.append([
                        convert_firefox_time(row[3]), 
                        row[0],
                        row[1],
                        comment
                    ])

            conn.close()

        except Exception as e:
            if logger:
                logger.error(f"History extraction failed from {db_file} : {e}")

    return autofill