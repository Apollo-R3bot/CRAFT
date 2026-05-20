import sqlite3
from services.utils.utils import convert_webkit_time, safe_copy

def extract_search_terms(browser, files, user_profile):
    results = []

    for db_file in files:
        try:
            safe_db = safe_copy(db_file)
            if not safe_db:
                continue

            conn = sqlite3.connect(f"file:{safe_db}?mode=ro", uri=True)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT url, term, last_visit_time
                FROM keyword_search_terms
                JOIN urls ON keyword_search_terms.url_id = urls.id
            """)

            for url, term, time in cursor.fetchall():
                results.append([
                    term,
                    # url,
                    convert_webkit_time(time)
                ])

            conn.close()

        except Exception as e:
            print(f"Search terms error: {e}")

    return results