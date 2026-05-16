import os
from pathlib import Path
from PySide6.QtCore import QDir
from PySide6.QtWidgets import QCheckBox, QComboBox, QDialog, QFileDialog, QFrame, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QRadioButton, QVBoxLayout
from controllers.acquire_controller import AcquireEvidenceController
from controllers.analysis_controller import AnalyzeEvidenceController
from controllers.browser_controller import BrowserSelectionController
from controllers.user_profile_controller import UserProfileController
from gui.main_window import MainWindow

class EvidenceAnalysis(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Controllers
        self.user_profile = UserProfileController()
        self.evidence_path = None

        self.setWindowTitle("Select Evidence Source")
        self.resize(450, 200)
        layout = QVBoxLayout()

        # Select File
        destination_folder = QGroupBox("Select Evidence Folder")
        destination_folder.setStyleSheet("QGroupBox { margin: 10px; padding: 10px; }")
        layout.addWidget(destination_folder)
        destination = QHBoxLayout()

        # Line Edit for Path Input
        self.path_input = QLineEdit()
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_evidence_file)
        destination.addWidget(self.path_input)
        destination.addWidget(browse_btn)
        destination_folder.setLayout(destination)

        # Footer - Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

        footer = QHBoxLayout()
        back_btn = QPushButton("< Back")
        start_btn = QPushButton("Finish")
        cancel_btn = QPushButton("Cancel")

        back_btn.clicked.connect(self.go_back)
        start_btn.clicked.connect(self.open_analysis)
        cancel_btn.clicked.connect(self.reject)
        start_btn.setEnabled(False)
        self.path_input.textChanged.connect(
            lambda text: start_btn.setEnabled(bool(text.strip()))
        )

        footer.addWidget(back_btn)
        footer.addWidget(start_btn)
        footer.addWidget(cancel_btn)
        self.setStyleSheet("""
            QPushButton {
                padding: 5px;
                font-size: 12px;
            }
            QDialog {
                padding: 40px;
            }
            """)
        layout.addLayout(footer) 
        self.setLayout(layout)

    def browse_evidence_file(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Evidence Folder")
        if folder:
            self.path_input.setText(QDir.toNativeSeparators(folder))

    def go_back(self):
        self.reject()

    def open_analysis(self):
        input_path = self.path_input.text().strip()

        if not input_path:
            QMessageBox.warning(
                self,
                "Warning",
                "Please select a evidence source before starting."
            )
            return

        # Required forensic artifact files
        required_files = [
            "history.csv",
            "downloads.csv",
            "cookies.csv",
            "caches.csv",
            "autofill.csv",
            "logins.csv",
            "bookmarks.csv",
            "sessions.csv",
            "search_terms.csv"
        ]

        missing_files = []

        for file_name in required_files:
            file_path = os.path.join(input_path, file_name)

            if not os.path.exists(file_path):
                missing_files.append(file_name)

        # If evidence is invalid
        if missing_files:
            QMessageBox.critical(
                self,
                "Invalid Evidence",
                "Invalid evidence folder. Please try another evidence source."
            )
            return
    
        self.evidence_path = input_path
        self.accept() 

    
    