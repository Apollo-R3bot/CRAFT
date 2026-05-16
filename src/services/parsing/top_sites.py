import sqlite3
import os
from services.utils.utils import safe_copy

def extract_top_sites(browser, files, user_profile):
    top_sites = []

    for db_file in files:
        try:
            if not os.path.exists(db_file):
                continue

            safe_db = safe_copy(db_file)
            if not safe_db:
                continue

            conn = sqlite3.connect(f"file:{safe_db}?mode=ro", uri=True)
            cursor = conn.cursor()

            # CHROMIUM (Chrome, Edge, Opera)
            if browser in ["chrome", "edge", "opera"]:
                cursor.execute("""
                    SELECT url, url_rank
                    FROM top_sites
                    ORDER BY url_rank ASC
                """)

                for row in cursor.fetchall():
                    url, rank = row

                    top_sites.append([
                        url,
                        rank,
                        browser,
                        user_profile,
                        db_file
                    ])

            # FIREFOX (approximation)
            elif browser == "firefox":
                cursor.execute("""
                    SELECT url, visit_count
                    FROM moz_places
                    ORDER BY visit_count DESC
                    LIMIT 20
                """)

                for row in cursor.fetchall():
                    url, count = row

                    top_sites.append([
                        url,
                        count,
                        browser,
                        user_profile,
                        db_file
                    ])

            conn.close()

        except Exception as e:
            print(f"Error extracting top sites from {db_file}: {e}")

    return top_sites