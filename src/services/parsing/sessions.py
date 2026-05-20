import os
import json
import re

def extract_session_and_tabs(browser, session_paths, user_profile):
    sessions = []

    for session_dir in session_paths:
        if not os.path.exists(session_dir):
            continue

        try:
            # CHROMIUM (Chrome, Edge, Opera)
            if browser in ["chrome", "edge", "opera"]:
                for file in os.listdir(session_dir):
                    if file.endswith(".json"):
                        full_path = os.path.join(session_dir, file)

                        try:
                            with open(full_path, "r", encoding="utf-8") as f:
                                data = json.load(f)

                            for window in data.get("windows", []):
                                for tab in window.get("tabs", []):
                                    url = tab.get("url")
                                    if url:
                                        sessions.append([
                                            url
                                        ])
                        except:
                            pass

                    else:
                        sessions.append([
                            file
                        ])

            # FIREFOX
            elif browser == "firefox":
                for file in os.listdir(session_dir):
                    if file.endswith(".jsonlz4"):
                        full_path = os.path.join(session_dir, file)

                        sessions.append([
                            file
                        ])

        except Exception as e:
            print(f"Error extracting sessions from {session_dir}: {e}")

    return sessions

def extract_urls_from_tabs_file(file_path):
    urls = []

    try:
        with open(file_path, "rb") as f:
            content = f.read()

        found_urls = re.findall(
            rb'https?://[^\s"\']+',
            content
        )

        for url in found_urls:
            try:
                decoded = url.decode("utf-8", errors="ignore")
                urls.append(decoded)
            except:
                pass

    except Exception as e:
        print(f"Tabs parse error: {e}")

    return list(set(urls))