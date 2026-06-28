import os
import json
import sqlite3
from services.utils.utils import convert_firefox_expiry, convert_firefox_time, format_size, safe_copy

def extract_firefox_downloads(files, user_profile, logger=None):
    downloads = []

    for db_file in files:
        try:
            safe_db = safe_copy(db_file)
            if not safe_db:
                continue

            conn = sqlite3.connect(f"file:{safe_db}?mode=ro",uri=True)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    p.url, dest.content AS download_path, meta.content AS metadata, dest.dateAdded
                FROM moz_annos dest
                LEFT JOIN moz_annos meta
                    ON dest.place_id = meta.place_id
                JOIN moz_places p
                    ON dest.place_id = p.id
                WHERE dest.anno_attribute_id = (
                    SELECT id
                    FROM moz_anno_attributes
                    WHERE name='downloads/destinationFileURI'
                )
                AND meta.anno_attribute_id = (
                    SELECT id
                    FROM moz_anno_attributes
                    WHERE name='downloads/metaData'
                )
            """)

            rows = cursor.fetchall()

            for row in rows:
                url, download_path, metadata_json, date_added = row
                size = ""
                end_time = ""

                try:
                    metadata = json.loads(metadata_json)
                    size = metadata.get("fileSize", "")
                    end_time_raw = metadata.get("endTime","")

                    if end_time_raw:
                        end_time = convert_firefox_time(
                            int(end_time_raw)
                        )

                except Exception:
                    pass
                
                total_size = format_size(size) if size else "0 B"
                file_name = os.path.basename(download_path)
                downloads.append([
                    convert_firefox_time(date_added),                         
                    file_name,                  
                    total_size,                           
                    url,
                    download_path                              
                ])

            conn.close()

        except Exception as e:
            if logger:
                logger.exception(
                    f"Firefox downloads extraction failed: {e}"
                )

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
                url = 'https://' + row[0].strip('.')
                comment = f'expires in {convert_firefox_expiry(row[5])} ' + f"| {'secure' if row[6] else ''} " + f", {'httponly' if row[7] else ''}"
                cookies.append([
                    convert_firefox_time(row[3]),
                    url,
                    row[1],
                    row[2],
                    convert_firefox_time(row[4]),
                    comment
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
                    entry.get("timeCreated"),
                    entry.get("encryptedUsername"),
                    entry.get("encryptedPassword"),
                    entry.get("hostname")
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
                    convert_firefox_time(date_added)
                ])

            conn.close()

        except Exception as e:
            print(f"Error extracting Firefox bookmarks from {db_file}: {e}")

    return bookmarks