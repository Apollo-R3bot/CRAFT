from datetime import datetime
import os
import shutil
from PySide6.QtWidgets import QMessageBox
import pandas as pd

from services.parsing.preferences import extract_browser_info, extract_signed_in_accounts
from services.parsing.autofills import extract_autofill
from services.parsing.history import extract_history
from services.parsing.logins import  extract_logins
from services.parsing.downloads import extract_downloads
from services.parsing.cookies import extract_cookies
from services.parsing.bookmarks import extract_bookmarks
from services.parsing.top_sites import extract_top_sites
from services.parsing.firefox import extract_firefox_bookmarks, extract_firefox_cookies, extract_firefox_downloads, extract_firefox_logins
from services.utils.utils import hash_file_multi, write_to_csv, zip_folder


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
    
    def generate_hash(self, user_name, browser, archive_folder):
        zip_output = os.path.join(
            self.output_folder,
            f"{user_name}_{browser}_{self.timestamp}.zip"
        )

        # Step 1: Hash all files inside archive folder
        hash_output = os.path.join(
            self.output_folder,
            f"hash_{user_name}_{browser}.txt"
        )

        with open(hash_output, "w", encoding="utf-8") as f:
            f.write("HASH VERIFICATION\n")
            f.write("=" * 60 + "\n\n")

            f.write("INDIVIDUAL FILE HASHES\n")
            f.write("-" * 60 + "\n")

            for root, _, files in os.walk(archive_folder):
                for file in files:
                    file_path = os.path.join(root, file)

                    try:
                        md5, sha1, sha256 = hash_file_multi(file_path)
                        relative_path = os.path.relpath(file_path,archive_folder)

                        f.write(f"FILE: {relative_path}\n")
                        f.write(f"MD5: {md5}\n")
                        f.write(f"SHA1: {sha1}\n")
                        f.write(f"SHA256: {sha256}\n")
                        f.write("-" * 60 + "\n")

                    except Exception as e:
                        f.write(f"FAILED: {file_path}\n")
                        f.write(f"ERROR: {str(e)}\n")
                        f.write("-" * 60 + "\n")

        # Step 2: Create ZIP after hashing files
        zip_folder(archive_folder, zip_output)

        # Step 3: Hash ZIP file
        zip_md5, zip_sha1, zip_sha256 = hash_file_multi(zip_output)

        with open(hash_output, "a", encoding="utf-8") as f:
            f.write("\nZIP ARCHIVE HASH\n")
            f.write("=" * 60 + "\n")
            f.write(f"ZIP FILE: {os.path.basename(zip_output)}\n")
            f.write(f"MD5: {zip_md5}\n")
            f.write(f"SHA1: {zip_sha1}\n")
            f.write(f"SHA256: {zip_sha256}\n")
            f.write("=" * 60 + "\n")

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
                autofill_path = os.path.join(base_path, "Web Data")
                top_sites_path = os.path.join(base_path, "Top Sites")

            elif browser == "opera":
                base_path = os.path.dirname(browser_path)
                history_path = browser_path
                cookies_path = os.path.join(base_path, "Network","Cookies")
                logins_path = os.path.join(base_path, "Login Data")
                bookmarks_path = os.path.join(base_path, "Bookmarks")
                autofill_path = os.path.join(base_path, "Web Data")
                top_sites_path = os.path.join(base_path, "Top Sites")

            elif browser == "firefox":
                base_path = os.path.dirname(browser_path)
                history_path = browser_path
                cookies_path = os.path.join(base_path, "cookies.sqlite")
                logins_path = os.path.join(base_path, "logins.json")
                bookmarks_path = browser_path  # bookmarks ipo ndani ya places.sqlite
                autofill_path = os.path.join(base_path, "formhistory.sqlite")
                top_sites_path = browser_path
            
            profile_files = {
                "history": [history_path],
                "search_terms": [history_path],
                "cookies": [cookies_path],
                "logins": [logins_path],
                "bookmarks": [bookmarks_path],
                "autofill": [autofill_path],
                "top_sites": [top_sites_path]
            }

            user_name = os.path.basename(root_folder)
            archive_folder = os.path.join(self.output_folder, f"{user_name}_{browser}_{self.timestamp}")
            os.makedirs(archive_folder, exist_ok=True)

            # Parse History Files
            history_data, search_data = extract_history(browser, profile_files["history"], user_name, logger=self.logger)
            history_output = os.path.join(archive_folder, "history.csv")
            write_to_csv(history_data, ["Status","Visit Time", "URL", "Title", "Visit Count", "Comment/Type"], history_output)
            if self.logger:
                self.logger.info(f"History extracted: {len(history_data)} records")

            # Parse Search Terms
            search_output = os.path.join(archive_folder, "search_terms.csv")
            write_to_csv(search_data, ["Time", "Domain", "Search Term"], search_output)
            if self.logger:
                self.logger.info(f"Search terms extracted: {len(history_data)} records")

            # Parse Downloads
            if browser == "firefox":
                downloads_data = extract_firefox_downloads(profile_files["history"], user_name)
                downloads_output = os.path.join(archive_folder, "downloads.csv")
                write_to_csv(downloads_data, ["Start Time", "File Name", "Size", "URL", "Comment"], downloads_output)
            else:
                downloads_data = extract_downloads(browser, profile_files["history"], user_name)
                downloads_output = os.path.join(archive_folder, "downloads.csv")
                write_to_csv(downloads_data, ["Start Time", "File Name", "Size", "URL", "Interrupt Reason", "Status", "Comment"], downloads_output)
            if self.logger:
                self.logger.info(f"Downloads extracted: {len(downloads_data)} records")

            # Parse Cookies
            if browser == "firefox":
                cookies_data = extract_firefox_cookies(profile_files["cookies"], user_name)
                cookies_output = os.path.join(archive_folder, "cookies.csv")
                write_to_csv(cookies_data, ["Creation Time", "Host", "Name", "Value", "Last Access Time", "Comment"], cookies_output)
            else:
                cookies_data = extract_cookies(browser, profile_files["cookies"], user_name)
                cookies_output = os.path.join(archive_folder, "cookies.csv")
                write_to_csv(cookies_data, [ "Creation Time", "Host", "Name", "Last Access Time", "Comment"], cookies_output)
            if self.logger:
                self.logger.info(f"Cookies extracted: {len(cookies_data)} records")

            #Parse Login Data
            if browser == "firefox":
                logins_data = extract_firefox_logins(profile_files["logins"], user_name)
            else:
                logins_data = extract_logins(browser, profile_files["logins"], user_name)
            logins_output = os.path.join(archive_folder, "logins.csv")
            write_to_csv(logins_data, ["Created Time","Username","Password","URL"], logins_output)
            if self.logger:
                self.logger.info(f"Logins data extracted: {len(logins_data)} records")

            #Parse Bookmarks
            if browser == "firefox":
                bookmarks_data = extract_firefox_bookmarks(profile_files["bookmarks"], user_name)
            else:
                bookmarks_data = extract_bookmarks(browser, profile_files["bookmarks"], user_name, logger=self.logger)
            bookmarks_output = os.path.join(archive_folder, "bookmarks.csv")
            write_to_csv(bookmarks_data, [ "Date Added","Name","URL"], bookmarks_output)
            if self.logger:
                self.logger.info(f"Bookmarks extracted: {len(bookmarks_data)} records")
            
            # Parse Autofill
            autofill_data = extract_autofill(browser, profile_files["autofill"], user_name, logger=self.logger)
            autofill_output = os.path.join(archive_folder, "autofill.csv")
            write_to_csv(autofill_data, [ "Created", "Field Name", "Value", "Comment"], autofill_output)
            if self.logger:
                self.logger.info(f"Autofills data extracted: {len(autofill_data)} records")

            # Parse Top Sites
            top_sites_data = extract_top_sites(browser, profile_files["history"], user_name)
            top_sites_output = os.path.join(archive_folder, "top_sites.csv")
            write_to_csv(top_sites_data,["Last Visit", "Visit Count", "Domain"], top_sites_output)


            # Parse Signed-in Accounts
            accounts_data = extract_signed_in_accounts(base_path, user_name, archive_folder)
            if self.logger:
                self.logger.info(f"Signed-in accounts extracted: {len(accounts_data)} records")

            extract_browser_info(
                browser_type=browser,
                profile_path=base_path,
                output_folder=archive_folder, 
                username=user_name, 
                accounts_data=accounts_data
            )
            

            if self.enable_hashing:
                self.generate_hash(user_name, browser, archive_folder)
                if self.logger:
                    self.logger.info(f"Hash verification started.. saved in {archive_folder}")

            return archive_folder
        
        except Exception as e:
            if self.logger:
                self.logger.error(f"Acquisition not completed.!: {e}")
            QMessageBox.critical(self, "Error", f"Acquisition not completed.!: {e}")
