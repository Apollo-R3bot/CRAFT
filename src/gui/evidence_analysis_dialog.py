import json
import os
from PySide6.QtCore import QDir
from PySide6.QtWidgets import QDialog, QFileDialog, QFrame, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QTextEdit, QVBoxLayout
from controllers.browser_and_user_profile_controller import BrowserSelectionController
from gui.case_information_dialog import CaseInformationDialog

class EvidenceAnalysis(QDialog):
    def __init__(self, logger, parent=None):
        super().__init__(parent)

        # Controllers
        self.user_profile = BrowserSelectionController()
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

        # Case Information
        case_information = QGroupBox("Case Information")
        case_information.setStyleSheet("QGroupBox { margin: 10px; padding: 10px; }")
        layout.addWidget(case_information)
        case = QVBoxLayout()

        case.addWidget(QLabel("Case Number"))
        self.case_number = QLineEdit()
        case.addWidget(self.case_number)

        case.addWidget(QLabel("Evidence Number"))
        self.evidence_number = QLineEdit()
        case.addWidget(self.evidence_number)

        case.addWidget(QLabel("Examiner Name"))
        self.examiner_name = QLineEdit()
        case.addWidget(self.examiner_name)

        case.addWidget(QLabel("Description"))
        self.desc = QTextEdit()
        self.desc.setFixedHeight(130)
        case.addWidget(self.desc)
        case_information.setLayout(case)


        # Footer - Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

        footer = QHBoxLayout()
        back_btn = QPushButton("< Back")
        start_btn = QPushButton("Open")
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

    def load_case_information(self):
        prefs_file = os.path.join(
            self.evidence_path,
            "preferences.json"
        )

        if not os.path.exists(prefs_file):
            return

        try:
            with open(prefs_file, "r", encoding="utf-8") as f:
                prefs = json.load(f)

            case_info = prefs.get("case_information")
            if not case_info:
                return

            self.case_number.setText(case_info.get("case_number", ""))
            self.evidence_number.setText(case_info.get("evidence_number", ""))
            self.examiner_name.setText(case_info.get("examiner_name", ""))
            self.desc.setPlainText(case_info.get("notes", ""))

        except Exception as e:
            print(f"Load case information error: {e}")

    def browse_evidence_file(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Evidence Folder")

        if folder:
            self.path_input.setText(QDir.toNativeSeparators(folder))
            self.evidence_path = folder

            self.load_case_information()

    def go_back(self):
        self.reject()


    def save_case_information(self):
        prefs_file = os.path.join(
            self.evidence_path,
            "preferences.json"
        )

        if not os.path.exists(prefs_file):
            QMessageBox.warning(
                self,
                "Error",
                "Preferences file not found"
            )
            return

        try:
            with open(prefs_file,"r",encoding="utf-8") as f:
                prefs = json.load(f)

            case_exists = "case_information" in prefs

            prefs["case_information"] = {
                "case_number": self.case_number.text(),
                "evidence_number": self.evidence_number.text(),
                "examiner_name": self.examiner_name.text(),
                "notes": self.desc.toPlainText()
            }

            with open(prefs_file,"w",encoding="utf-8") as f:
                json.dump(
                    prefs,
                    f,
                    indent=4,
                    ensure_ascii=False
                )

            if not case_exists:
                QMessageBox.information(
                    self,
                    "Success",
                    "Case information saved successful."
                )

        except Exception as e:
            QMessageBox.critical(self,"Error",str(e))

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

        self.save_case_information()

        self.accept() 

    
    