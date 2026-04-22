import os
from PySide6.QtWidgets import (QApplication, QFileDialog, QGroupBox, QHBoxLayout, QLabel, QMessageBox, QPushButton, QTableWidget, QVBoxLayout, QDialog, QLayout, QFrame)
from PySide6.QtCore import QDir, QStandardPaths
from PySide6.QtGui import QAction


class MainController:
    def get_all_users(self):
        # Set the path to the user profiles directory
        users_dir = QDir("C:/Users")
        filters = QDir.Dirs | QDir.NoDotAndDotDot
        exclude = ["Public", "Default", "All Users", "Default User"]
        all_profiles = users_dir.entryList(filters)
        # all_profiles = users_dir.entryList(filters) # Include Default, Public
        user_folders = [p for p in all_profiles if p not in exclude]
        # return [user_folders]
        # return [current_profile]
        return [QDir.toNativeSeparators(users_dir.absoluteFilePath(p)) for p in user_folders]
    

    def quit_app(self):
        QApplication.quit()
        



