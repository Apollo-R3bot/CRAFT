import os
import json
from pandas import DataFrame
from PySide6.QtCore import QDir
from PySide6.QtWidgets import QFileDialog, QMessageBox, QTableWidget  

from services.parsing import extract_firefox_bookmarks, extract_firefox_logins, find_browser_profile_files, extract_history, extract_downloads, extract_cookies, extract_logins, extract_bookmarks
from services.utils import write_to_csv

class AcquireEvidenceController:
    
    def __init__(self):
        self.output_folder  = None

    def set_output_folder(self, folder):
        self.output_folder = folder

    
    def start_parsing(self, root_folder, browser_path):
        try:
            # Profile files
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
                history_path = browser_path
                cookies_path = browser_path.replace("History", r"Network\Cookies")
                logins_path = browser_path.replace("History", "Login Data")
                bookmarks_path = browser_path.replace("History", "Bookmarks")
            elif browser == "opera":
                history_path = browser_path
                cookies_path = browser_path.replace("History", "Cookies")
                logins_path = browser_path.replace("History", "Login Data")
                bookmarks_path = browser_path.replace("History", "Bookmarks")
            elif browser == "firefox":
                history_path = browser_path
                cookies_path = browser_path.replace("places.sqlite", "cookies.sqlite")
                logins_path = browser_path.replace("places.sqlite", "logins.json")
                bookmarks_path = browser_path  # bookmarks ipo ndani ya places.sqlite
            
            profile_files = {
                "history": [history_path],
                "cookies": [cookies_path],
                "logins": [logins_path],
                "bookmarks": [bookmarks_path]
            }

            user_name = os.path.basename(root_folder)

            # Parse History Files
            history_data = extract_history(browser, profile_files["history"], user_name)
            history_output = os.path.join(self.output_folder, "history.csv")
            write_to_csv(history_data, ["Visit Time", "URL", "Title", "Visit Count", "Visit Type", "Duration", "Browser", "User Profile", "Source"], history_output)

            # Parse Downloads
            downloads_data = extract_downloads(browser, profile_files["history"], user_name)
            downloads_output = os.path.join(self.output_folder, "downloads.csv")
            write_to_csv(downloads_data, ["Start Time", "End Time", "File Path", "Total Bytes", "Received Bytes", "Danger Type", "Interrupt Reason", "Opened", "Browser", "User Profile", "Source"], downloads_output)

            # Parse Cookies
            cookies_data = extract_cookies(browser, profile_files["cookies"], user_name)
            cookies_output = os.path.join(self.output_folder, "cookies.csv")
            write_to_csv(cookies_data, ["Host", "Name", "Value", "Creation Time", "Last Access Time", "Expiry Time", "Secure", "HTTP Only", "Browser", "User Profile", "Source"], cookies_output)

            #Parse Login Data
            if browser == "firefox":
                logins_data = extract_firefox_logins(profile_files["logins"], user_name)
            else:
                logins_data = extract_logins(browser, profile_files["logins"], user_name)
            logins_output = os.path.join(self.output_folder, "logins.csv")
            write_to_csv(logins_data, ["URL","Username","Password","Created Time","Browser", "User Profile", "Source"], logins_output)

            #Parse Bookmarks
            if browser == "firefox":
                bookmarks_data = extract_firefox_bookmarks(profile_files["bookmarks"], user_name)
            else:
                bookmarks_data = extract_bookmarks(browser, profile_files["bookmarks"], user_name)
            bookmarks_output = os.path.join(self.output_folder, "bookmarks.csv")
            write_to_csv(bookmarks_data, ["Name","URL","Browser","User Profile"], bookmarks_output)

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            # self.status_label.setText("Parsing failed!")

       