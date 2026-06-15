import os
from PySide6.QtWidgets import (QApplication, QGroupBox, QHBoxLayout, QLabel, QMessageBox, QPushButton, QTableWidget, QVBoxLayout, QDialog, QLayout, QFrame)
from PySide6.QtCore import QDir

class MainController:
    def __init__(self):
        super().__init__()

    def load_evidence(self, path):
        return path

    def quit_app(self):
        QApplication.quit()
        



