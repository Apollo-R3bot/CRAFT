import os
from PySide6.QtCore import QDir

class BrowserSelectionController:
    def __init__(self, logger=None):
        self.logger = logger

    def get_browser_history_locations(self, user_path):
        locations = {
            'Google Chrome': os.path.join(user_path, r'AppData\Local\Google\Chrome\User Data\Default\History'),
            'Microsoft Edge': os.path.join(user_path, r'AppData\Local\Microsoft\Edge\User Data\Default\History'),
            'Opera': os.path.join(user_path, r'AppData\Roaming\Opera Software\Opera Stable\Default\History'),
            'Mozilla Firefox': os.path.join(user_path, r'AppData\Roaming\Mozilla\Firefox\Profiles'), 
        }

        if os.path.exists(locations['Mozilla Firefox']):
            profiles = os.listdir(locations['Mozilla Firefox'])
            if profiles:
                locations['Mozilla Firefox'] = os.path.join(locations['Mozilla Firefox'], profiles[0], 'places.sqlite')
        return locations
    
    def get_all_users(self):
        # Set the path to the user profiles directory
        users_dir = QDir("C:/Users")
        filters = QDir.Dirs | QDir.NoDotAndDotDot
        exclude = ["Public", "Default", "All Users", "Default User"]
        all_profiles = users_dir.entryList(filters)
        user_folders = [p for p in all_profiles if p not in exclude]
        return [QDir.toNativeSeparators(users_dir.absoluteFilePath(p)) for p in user_folders]



