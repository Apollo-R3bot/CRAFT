import sqlite3

import urllib
from urllib.parse import parse_qs, urlparse
from services.utils.utils import convert_webkit_time, convert_firefox_time, safe_copy

TRANSITION_TYPES = {
    0: 'Link',
    1: 'Typed URL',
    2: 'Auto Bookmark',
    3: 'Auto Subframe',
    4: 'Manual Subframe',
    5: 'Generated',
    6: 'Start Page',
    7: 'Form Submit',
    8: 'Reload',
    9: 'Keyword',
    10: 'Keyword Generated'
}

FIREFOX_TRANSITION_TYPES = {
    1: 'Link',
    2: 'Typed',
    3: 'Bookmark',
    4: 'Embed',
    5: 'Redirect Permanent',
    6: 'Redirect Temporary',
    7: 'Download',
    8: 'Framed Link'
}

def extract_search_term_from_url(url):
    try:
        parsed = urlparse(url)
        query = parse_qs(parsed.query)

        for key in ["q", "query", "search", "search_query"]:  # supports Google, Bing, Yahoo, Youtube
            if key in query:
                return query[key][0]
    except:
        pass

    return None

def extract_history(browser, files, user_profile, logger=None):
    history = []
    search_terms = []
    seen = set()

    for db_file in files:
        try:
            safe_db = safe_copy(db_file)
            if not safe_db:
                continue

            conn = sqlite3.connect(f"file:{safe_db}?mode=ro", uri=True)
            cursor = conn.cursor()

            # Check tables in database
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [table[0] for table in cursor.fetchall()]

            if 'urls' in tables:
                # Chromium-based history
                query = '''
                SELECT urls.url, urls.title, urls.visit_count, urls.last_visit_time, visits.visit_time, visits.visit_duration, visits.from_visit, visits.transition
                FROM urls
                JOIN visits ON urls.id = visits.url
                '''
                cursor.execute(query)

                for row in cursor.fetchall():
                    url, title, visit_count, last_visit_time, visit_time, visit_duration, from_visit, transition = row
                    visit_time_utc = convert_webkit_time(visit_time)
                    visit_duration_sec = visit_duration / 1000000 if visit_duration else 0
                    visit_type = TRANSITION_TYPES.get(transition & 0xFF, 'Unknown')
                    history.append([visit_time_utc, url, title, visit_count, visit_type, visit_duration_sec, browser, user_profile, db_file])
                    term = extract_search_term_from_url(url)

                    if term:
                        term = term.replace("+", " ").strip()
                        key = term.lower()
                        if key not in seen:
                            seen.add(key)
                            search_terms.append([term,url,visit_time_utc,browser,user_profile,db_file])

            elif 'moz_places' in tables and 'moz_historyvisits' in tables:
                # Firefox history
                query = '''
                SELECT 
                    moz_places.url, 
                    moz_places.title, 
                    moz_places.visit_count, 
                    moz_historyvisits.visit_date,
                    moz_historyvisits.visit_type
                FROM moz_places
                JOIN moz_historyvisits ON moz_places.id = moz_historyvisits.place_id
                '''
                cursor.execute(query)
                for row in cursor.fetchall():
                    url, title, visit_count, visit_time, url_visit_type = row
                    visit_time_utc = convert_firefox_time(visit_time)
                    visit_type = FIREFOX_TRANSITION_TYPES.get(url_visit_type, 'Unknown')
                    history.append([visit_time_utc, url, title, visit_count, visit_type, None, browser, user_profile, db_file])
                    term = extract_search_term_from_url(url)
                    if term:
                        term = term.replace("+", " ").strip()
                        key = term.lower()
                        if key not in seen:
                            seen.add(key)
                        search_terms.append([term,url,visit_time_utc,browser,user_profile,db_file])

            conn.close()
        except sqlite3.Error as e:
            if logger:
                logger.error(f"History extraction failed from {db_file}: {e}")
    return history, search_terms