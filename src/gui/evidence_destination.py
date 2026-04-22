import os

from PySide6.QtWidgets import QComboBox, QDialog, QFrame, QGroupBox, QHBoxLayout, QLabel, QPushButton, QRadioButton, QVBoxLayout
from controllers.browser_controller import BrowserSelectionController
from controllers.main_controller import MainController

class DestinationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Destination")
        self.resize(500, 350)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("This is the second modal self!"))
        self.setLayout(layout)
