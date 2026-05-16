from datetime import datetime
import os
import shutil
from PySide6.QtWidgets import QMessageBox

from services.parsing.autofills import extract_autofill
from services.parsing.caches import extract_caches
from services.parsing.history import extract_history
from services.parsing.logins import  extract_logins
from services.parsing.downloads import extract_downloads
from services.parsing.cookies import extract_cookies
from services.parsing.bookmarks import extract_bookmarks
from services.parsing.firefox import extract_firefox_bookmarks, extract_firefox_cookies, extract_firefox_downloads, extract_firefox_logins
from services.parsing.sessions import extract_session_and_tabs
from services.utils.utils import hash_all_csv_to_txt, hash_file_multi, write_to_csv, zip_folder


class AcquireEvidenceController:
    def __init__(self, logger=None):
        self.output_folder  = None
        self.enable_hashing = False
        self.logger = logger
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")

    def set_output_folder(self, folder):
        self.output_folder = folder

    def set_hashing(self, enabled: bool):
        self.enable_hashing = enabled
    
    def generate_hash(self, user_name, browser):
        zip_output = os.path.join(self.output_folder, f"{user_name}_{browser}_{self.timestamp}.zip")
        zip_folder(self.output_folder, zip_output)
        md5, sha1, sha256 = hash_file_multi(zip_output)
        
        hash_output = os.path.join(self.output_folder, f"hash_report_{user_name}_{browser}.txt")
        hash_all_csv_to_txt(self.output_folder, hash_output, zip_path=zip_output)

    def copy_session_folder(self, session_source, output_folder):
        session_output = os.path.join(output_folder, "sessions")
        os.makedirs(session_output, exist_ok=True)

        if os.path.exists(session_source):
            for file in os.listdir(session_source):
                full_path = os.path.join(session_source, file)

                if os.path.isfile(full_path):
                    try:
                        shutil.copy2(
                            full_path,
                            os.path.join(session_output, file)
                        )
                    except Exception as e:
                        print(f"Session copy error: {e}")

    def start_parsing(self, root_folder, browser_path):
        try:
            if self.logger:
                self.logger.info(f"Acquisition started | User: {root_folder} | Path: {browser_path}")

            if not browser_path or not os.path.exists(browser_path):
                raise Exception("Invalid browser path")
            
            if "Chrome" in browser_path:
                browser = "chrome"
            elif "Edge" in browser_path:
                browser = "edge"
            elif "Opera" in browser_path:
                browser = "opera"
            elif "Firefox" in browser_path:
                browser = "firefox"
            else:
                raise Exception("Unsupported browser")
    
            if browser in ["chrome", "edge"]:
                base_path = os.path.dirname(browser_path)
                history_path = browser_path
                cookies_path = os.path.join(base_path, "Network", "Cookies")
                logins_path = os.path.join(base_path, "Login Data")
                bookmarks_path = os.path.join(base_path, "Bookmarks")
                cache_path = os.path.join(base_path, "Cache")
                session_path = os.path.join(base_path, "Sessions")
                autofill_path = os.path.join(base_path, "Web Data")
                # top_sites_path = os.path.join(base_path, "Top Sites")

            elif browser == "opera":
                base_path = os.path.dirname(browser_path)
                history_path = browser_path
                cookies_path = os.path.join(base_path, "Cookies")
                logins_path = os.path.join(base_path, "Login Data")
                bookmarks_path = os.path.join(base_path, "Bookmarks")
                cache_path = os.path.join(base_path, "Cache")
                session_path = os.path.join(base_path, "Sessions")
                autofill_path = os.path.join(base_path, "Web Data")
                # top_sites_path = os.path.join(base_path, "Top Sites")

            elif browser == "firefox":
                base_path = os.path.dirname(browser_path)
                history_path = browser_path
                cookies_path = os.path.join(base_path, "cookies.sqlite")
                logins_path = os.path.join(base_path, "logins.json")
                bookmarks_path = browser_path  # bookmarks ipo ndani ya places.sqlite
                cache_path =  os.path.join(base_path, "cache2")
                session_path = os.path.join(base_path, "sessionstore-backups")
                autofill_path = os.path.join(base_path, "formhistory.sqlite")

                if os.path.exists(cache_path):
                    profiles = os.listdir(cache_path)
                    if profiles:
                        return os.path.join(cache_path, profiles[0], "cache2")
            
            profile_files = {
                "history": [history_path],
                "search_terms": [history_path],
                "cookies": [cookies_path],
                "logins": [logins_path],
                "bookmarks": [bookmarks_path],
                "cache": [cache_path],
                "sessions": [session_path],
                "autofill": [autofill_path]
                # "top_sites": [top_sites_path]
            }

            user_name = os.path.basename(root_folder)

            # Parse History Files
            history_data, search_data = extract_history(browser, profile_files["history"], user_name, logger=self.logger)
            history_output = os.path.join(self.output_folder, "history.csv")
            write_to_csv(history_data, ["Visit Time", "URL", "Title", "Visit Count", "Visit Type", "Duration", "Browser", "User Profile", "Source"], history_output)
            self.logger.info(f"History extracted: {len(history_data)} records")

            # Parse Search Terms
            search_output = os.path.join(self.output_folder, "search_terms.csv")
            write_to_csv(search_data, ["Search Term", "URL", "Time", "Browser", "User", "Source"], search_output)
            self.logger.info(f"Search terms extracted: {len(history_data)} records")

            # Parse Caches
            cache_data = extract_caches(browser, profile_files["cache"], user_name)
            cache_output = os.path.join(self.output_folder, "caches.csv")
            write_to_csv(cache_data, ["Field", "Value", "Created", "Last Used","Browser", "User", "Source"], cache_output)
            self.logger.info(f"Caches extracted: {len(cache_data)} records")

            # Parse Downloads
            if browser == "firefox":
                downloads_data = extract_firefox_downloads(profile_files["history"], user_name)
            else:
                downloads_data = extract_downloads(browser, profile_files["history"], user_name)
            downloads_output = os.path.join(self.output_folder, "downloads.csv")
            write_to_csv(downloads_data, ["Start Time", "End Time", "File Path", "Total Bytes", "Received Bytes", "Danger Type", "Interrupt Reason", "Opened", "Browser", "User Profile", "Source"], downloads_output)
            self.logger.info(f"Downloads extracted: {len(downloads_data)} records")

            # Parse Cookies
            if browser == "firefox":
                cookies_data = extract_firefox_cookies(profile_files["cookies"], user_name)
            else:
                cookies_data = extract_cookies(browser, profile_files["cookies"], user_name)
            cookies_output = os.path.join(self.output_folder, "cookies.csv")
            write_to_csv(cookies_data, ["Host", "Name", "Value", "Creation Time", "Last Access Time", "Expiry Time", "Secure", "HTTP Only", "Browser", "User Profile", "Source"], cookies_output)
            self.logger.info(f"Cookies extracted: {len(cookies_data)} records")

            #Parse Login Data
            if browser == "firefox":
                logins_data = extract_firefox_logins(profile_files["logins"], user_name)
            else:
                logins_data = extract_logins(browser, profile_files["logins"], user_name)
            logins_output = os.path.join(self.output_folder, "logins.csv")
            write_to_csv(logins_data, ["URL","Username","Password","Created Time","Browser", "User Profile", "Source"], logins_output)
            self.logger.info(f"Logins data extracted: {len(logins_data)} records")

            #Parse Bookmarks
            if browser == "firefox":
                bookmarks_data = extract_firefox_bookmarks(profile_files["bookmarks"], user_name)
            else:
                bookmarks_data = extract_bookmarks(browser, profile_files["bookmarks"], user_name, logger=self.logger)
            bookmarks_output = os.path.join(self.output_folder, "bookmarks.csv")
            write_to_csv(bookmarks_data, ["Name","URL","Browser","User Profile"], bookmarks_output)
            self.logger.info(f"Bookmarks extracted: {len(bookmarks_data)} records")

            # Parse Sessions and Tabs
            sessions_data = extract_session_and_tabs(browser, profile_files["sessions"], user_name)
            sessions_output = os.path.join(self.output_folder, "sessions.csv")
            write_to_csv(sessions_data, ["Session/Tab Info", "Browser", "User", "Source"], sessions_output)
            self.logger.info(f"Sessions data extracted: {len(sessions_data)} records")

            self.copy_session_folder(session_path, self.output_folder)
            
            # Parse Autofill
            autofill_data = extract_autofill(browser, profile_files["autofill"], user_name, logger=self.logger)
            autofill_output = os.path.join(self.output_folder, "autofill.csv")
            write_to_csv(autofill_data, ["Field Name", "Value", "First Used", "Last Used", "Count", "Browser", "User", "Source"], autofill_output)
            self.logger.info(f"Autofills data extracted: {len(autofill_data)} records")

            # Parse Top Sites
            # top_sites_data = extract_top_sites(browser, profile_files["top_sites"], user_name)
            # top_sites_output = os.path.join(self.output_folder, "top_sites.csv")
            # write_to_csv(top_sites_data,["URL", "Rank/VisitCount", "Browser", "User", "Source"], top_sites_output)

            if self.enable_hashing:
                self.generate_hash(user_name, browser)

            archive_folder = os.path.join(self.output_folder, f"{user_name}_{browser}_{self.timestamp}")
            os.makedirs(archive_folder, exist_ok=True)

            for item in os.listdir(self.output_folder):
                item_path = os.path.join(self.output_folder, item)

                if item.endswith(".zip"):
                    continue

                if item.endswith(".txt"):
                    continue

                if item == os.path.basename(archive_folder):
                    continue

                try:
                    shutil.move(
                        item_path,
                        os.path.join(archive_folder, item)
                    )
                except Exception as e:
                    if self.logger:
                        self.logger.exception(
                            f"Failed to move {item}: {str(e)}"
                        )

            for file in os.listdir(self.output_folder):
                if file.endswith(".csv"):
                    shutil.move(
                        os.path.join(self.output_folder, file),
                        os.path.join(archive_folder, file)
                    )
        except Exception as e:
            QMessageBox.critical(self, "Error", "Acquisition not completed.!")

       