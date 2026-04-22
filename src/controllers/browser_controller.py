import os
from PySide6.QtWidgets import (QApplication, QFileDialog, QGroupBox, QHBoxLayout, QLabel, QMessageBox, QPushButton, QTableWidget, QVBoxLayout, QDialog, QLayout, QFrame)
from PySide6.QtCore import QDir

from controllers.main_controller import MainController


class BrowserSelectionController:
    def get_browser_history_locations(self, user_path):

        locations = {
            'Google Chrome': os.path.join(user_path, r'AppData\Local\Google\Chrome\User Data\Default\History'),
            'Microsoft Edge': os.path.join(user_path, r'AppData\Local\Microsoft\Edge\User Data\Default\History'),
            'Opera': os.path.join(user_path, r'AppData\Local\Opera Software\Opera Stable\History'),
            'Mozilla Firefox': os.path.join(user_path, r'AppData\Roaming\Mozilla\Firefox\Profiles'), 
        }
        
        # Special handling for Firefox to find the specific profile folder
        if os.path.exists(locations['Mozilla Firefox']):
            profiles = os.listdir(locations['Mozilla Firefox'])
            if profiles:
                locations['Mozilla Firefox'] = os.path.join(locations['Mozilla Firefox'], profiles[0], 'places.sqlite')
        return locations



