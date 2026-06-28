from collections import defaultdict
import sqlite3
import os
from urllib.parse import urlparse
from services.utils.utils import convert_firefox_time, convert_webkit_time, safe_copy

def extract_top_sites(browser, files, user_profile):
    top_sites = []

    domain_counts = defaultdict(int)
    domain_last_visit = {}

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
                    SELECT url, visit_count, last_visit_time
                    FROM urls
                    WHERE visit_count > 0
                    ORDER BY last_visit_time DESC
                """)
                
                for url, visit_count, last_visit_time in cursor.fetchall():
                    domain = urlparse(url).netloc.lower()
                    if domain.startswith("www."):
                        domain = domain[4:]

                    domain_counts[domain] += visit_count
                    last_visit = convert_webkit_time(last_visit_time)

                    if domain not in domain_last_visit or last_visit > domain_last_visit[domain]:
                        domain_last_visit[domain] = last_visit

            # FIREFOX (approximation)
            elif browser == "firefox":
                cursor.execute("""
                    SELECT url, visit_count, last_visit_date
                    FROM moz_places
                    WHERE visit_count > 0
                    ORDER BY last_visit_date DESC
                """)

                for url, visit_count, last_visit_date  in cursor.fetchall():
                    domain = urlparse(url).netloc.lower()
                    if domain.startswith("www."):
                        domain = domain[4:]

                    domain_counts[domain] += visit_count
                    last_visit = convert_firefox_time(last_visit_date)

                    if domain not in domain_last_visit or last_visit > domain_last_visit[domain]:
                        domain_last_visit[domain] = last_visit

            conn.close()

        except Exception as e:
            print(f"Error extracting top sites from {db_file}: {e}")

    top_sites = sorted(
        domain_counts.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return [
        [
            domain_last_visit.get(domain, ""),
            count,
            domain
        ]
        for domain, count in top_sites[:20]
    ]
    # return top_sites