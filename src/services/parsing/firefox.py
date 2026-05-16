import os
import json
import sqlite3
from services.utils.utils import convert_firefox_time, safe_copy

def extract_firefox_downloads(files, user_profile):
    downloads = []

    for db_file in files:
        try:
            safe_db = safe_copy(db_file)
            if not safe_db:
                continue

            conn = sqlite3.connect(f"file:{safe_db}?mode=ro", uri=True)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT 
                    moz_places.url,
                    moz_annos.content,
                    moz_annos.dateAdded
                FROM moz_annos
                JOIN moz_places ON moz_annos.place_id = moz_places.id
                WHERE moz_annos.anno_attribute_id IN (
                    SELECT id FROM moz_anno_attributes 
                    WHERE name = 'downloads/destinationFileURI'
                )
            """)

            for url, file_path, date_added in cursor.fetchall():
                downloads.append([
                    convert_firefox_time(date_added),
                    None,
                    file_path,
                    None,
                    None,
                    None,
                    None,
                    None,
                    "firefox",
                    user_profile,
                    db_file
                ])

            conn.close()

        except Exception as e:
            print(f"Firefox downloads error: {e}")

    return downloads


def extract_firefox_cookies(files, user_profile):
    cookies = []

    for db_file in files:
        try:
            safe_db = safe_copy(db_file)
            if not safe_db:
                continue

            conn = sqlite3.connect(f"file:{safe_db}?mode=ro", uri=True)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT host, name, value, creationTime, lastAccessed, expiry, isSecure, isHttpOnly
                FROM moz_cookies
            """)

            for row in cursor.fetchall():
                cookies.append([
                    row[0],
                    row[1],
                    row[2],
                    convert_firefox_time(row[3]),
                    convert_firefox_time(row[4]),
                    convert_firefox_time(row[5]),
                    "Yes" if row[6] else "No",
                    "Yes" if row[7] else "No",
                    "firefox",
                    user_profile,
                    db_file
                ])

            conn.close()

        except Exception as e:
            print(f"Firefox cookies error: {e}")

    return cookies


def extract_firefox_logins(files, user_profile):
    logins = []

    for file in files:
        try:
            if not os.path.exists(file):
                continue

            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)

            for entry in data.get("logins", []):
                logins.append([
                    entry.get("hostname"),
                    entry.get("encryptedUsername"),
                    entry.get("encryptedPassword"),
                    entry.get("timeCreated"),
                    "firefox",
                    user_profile,
                    file
                ])

        except Exception as e:
            print(f"Error extracting Firefox logins from {file}: {e}")

    return logins

def extract_firefox_bookmarks(files, user_profile):
    bookmarks = []

    for db_file in files:
        try:
            safe_db = safe_copy(db_file)
            if not safe_db:
                continue

            conn = sqlite3.connect(f"file:{safe_db}?mode=ro", uri=True)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT moz_bookmarks.title, moz_places.url, moz_bookmarks.dateAdded
                FROM moz_bookmarks
                JOIN moz_places ON moz_bookmarks.fk = moz_places.id
                WHERE moz_bookmarks.type = 1
            """)

            for title, url, date_added in cursor.fetchall():
                bookmarks.append([
                    title,
                    url,
                    convert_firefox_time(date_added),
                    "firefox",
                    user_profile,
                    db_file
                ])

            conn.close()

        except Exception as e:
            print(f"Error extracting Firefox bookmarks from {db_file}: {e}")

    return bookmarks