import os
from pathlib import Path
from PySide6.QtCore import QDir
from PySide6.QtWidgets import QComboBox, QDialog, QFileDialog, QFrame, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QRadioButton, QVBoxLayout
from controllers.acquire_controller import AcquireEvidenceController
from controllers.browser_controller import BrowserSelectionController
from controllers.main_controller import MainController

class EvidenceSourceAndDestination(QDialog):
    def __init__(self):
        super().__init__()

        # Controllers
        self.acquire = AcquireEvidenceController()
        self.select_browser = BrowserSelectionController()
        self.user_profile = MainController()

        self.selected_browser_path = None
        self.selected_user = None

        self.setWindowTitle("Select Evidence Source")
        self.resize(450, 500)
        layout = QVBoxLayout()

        # Select User Profile
        target_profile = QGroupBox("Select User Profile")
        layout.addWidget(target_profile)
        user = QVBoxLayout()
        target_profile.setStyleSheet("QGroupBox { margin: 10px; padding: 10px; }")
        target_profile.setLayout(user)

        self.user_combo = QComboBox()
        self.user_list = self.user_profile.get_all_users()
        self.user_combo.addItems(self.user_list)
        self.selected_user = self.user_combo.currentText()
        self.user_combo.currentTextChanged.connect(self.set_user)
        user.addWidget(self.user_combo)

        # Select Browser
        target_browser = QGroupBox("Select Browser")
        layout.addWidget(target_browser)
        self.browser_layout = QVBoxLayout()
        target_browser.setStyleSheet("QGroupBox { margin: 10px; padding: 10px; }")
        locations = self.select_browser.get_browser_history_locations(self.selected_user)

        for browser, path in locations.items():
            select_browser_btn = QRadioButton(browser)

            if os.path.exists(path):
                select_browser_btn.toggled.connect(
                    lambda checked, p=path: self.set_browser(p) if checked else None
                )
            else:
                select_browser_btn.setEnabled(False)
            self.browser_layout.addWidget(select_browser_btn)
        target_browser.setLayout(self.browser_layout)

        # Select Destination Folder
        destination_folder = QGroupBox("Select Destination Folder")
        layout.addWidget(destination_folder)
        destination = QHBoxLayout()

        # Line Edit for Path Input
        self.path_input = QLineEdit()
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_output_folder)
        destination_folder.setStyleSheet("QGroupBox { margin: 10px; padding: 10px; }")
        destination.addWidget(self.path_input)
        destination.addWidget(browse_btn)
        destination_folder.setLayout(destination)

        # Footer - Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

        footer = QHBoxLayout()
        start_btn = QPushButton("Start")
        cancel_btn = QPushButton("Cancel")

        start_btn.clicked.connect(self.handle_start)
        cancel_btn.clicked.connect(self.accept)

        footer.addWidget(start_btn)
        footer.addWidget(cancel_btn)
        
        layout.addLayout(footer) 
        self.setLayout(layout)

    def set_user(self, user):
        self.selected_user = user
        self.update_browsers()

    def update_browsers(self):
        for i in reversed(range(self.browser_layout.count())):
            widget = self.browser_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        self.selected_browser_path = None

        locations = self.select_browser.get_browser_history_locations(self.selected_user)

        for browser, path in locations.items():
            select_browser_btn = QRadioButton(browser)

            if os.path.exists(path):
                select_browser_btn.toggled.connect(
                    lambda checked, p=path: self.set_browser(p) if checked else None
                )
            else:
                select_browser_btn.setEnabled(False)
            self.browser_layout.addWidget(select_browser_btn)

    def set_browser(self, path):
        self.selected_browser_path = path

    def browse_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.path_input.setText(QDir.toNativeSeparators(folder))
            self.acquire.set_output_folder(QDir.toNativeSeparators(folder))

    def handle_start(self):
        if not self.selected_browser_path:
            QMessageBox.warning(self, "Error", "Select a browser")
            return

        data = self.acquire.start_parsing(
            self.selected_user,
            self.selected_browser_path
        )
        QMessageBox.information(self, "Done", "Parsing Complete")

    
    