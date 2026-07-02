import os
from pathlib import Path
from PySide6.QtCore import QDir, QTimer
from PySide6.QtWidgets import QCheckBox, QComboBox, QDialog, QFileDialog, QFrame, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QProgressBar, QPushButton, QRadioButton, QVBoxLayout
from controllers.acquire_controller import AcquireEvidenceController
from controllers.browser_and_user_profile_controller import BrowserSelectionController

from services.utils.utils import detect_browser_from_path, get_running_browsers, is_browser_running
from version import APP_TITLE

class EvidenceAcquisition(QDialog):
    def __init__(self, logger, parent=None):
        super().__init__(parent)

        # Controllers
        self.logger = logger
        self.acquire = AcquireEvidenceController(logger=self.logger)
        self.select_browser = BrowserSelectionController()
        self.user_profile = BrowserSelectionController()

        self.selected_browser_path = None
        self.selected_user = None
        self.parent_dialog = parent 
        self.generated_evidence_path = None

        self.setWindowTitle(f"{APP_TITLE} - Select Profile and Browser Source")
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
        destination_folder.setStyleSheet("QGroupBox { margin: 10px; padding: 10px; }")
        layout.addWidget(destination_folder)
        destination = QHBoxLayout()

        # Line Edit for Path Input
        self.path_input = QLineEdit()
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_output_folder)
        destination.addWidget(self.path_input)
        destination.addWidget(browse_btn)
        destination_folder.setLayout(destination)

        # if Hashing required
        hash_checkbox = QCheckBox("Verify evidence after they are created")
        hash_checkbox.stateChanged.connect(self.toggle_hashing)
        hash_checkbox.setChecked(True)
        hash_checkbox.setStyleSheet("QCheckBox { padding: 10px; }")
        layout.addWidget(hash_checkbox)

        # Footer - Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

        footer = QHBoxLayout()
        back_btn = QPushButton("< Back")
        start_btn = QPushButton("Start")
        cancel_btn = QPushButton("Cancel")

        back_btn.clicked.connect(self.go_back)
        start_btn.clicked.connect(self.start_acquire)
        cancel_btn.clicked.connect(self.accept)

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

    def toggle_hashing(self, state):
        self.acquire.set_hashing(state == 2)

    def go_back(self):
        self.reject()

    # ── Browser running check ──────────────────────────────────────────
    def _check_browser_not_running(self) -> bool:
        browser_key = detect_browser_from_path(self.selected_browser_path)

        if browser_key and is_browser_running(browser_key):
            if self.logger:
                self.logger.warning(
                    f"[ACQUIRE] Selected browser '{browser_key}' is currently running"
                )

            response = QMessageBox.warning(
                self,
                "Browser Is Running",
                f"The selected browser ({browser_key.title()}) is currently open.\n\n"
                "Please close all browser windows and try again.\n\n"
                "Do you want to continue anyway? (Not recommended)",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )

            if response == QMessageBox.No:
                if self.logger:
                    self.logger.info(
                        "[ACQUIRE] User cancelled acquisition — browser still running"
                    )
                return False

            if self.logger:
                self.logger.warning(
                    "[ACQUIRE] User chose to proceed despite browser being open"
                )

        # Also warn about other browsers running, even if not the selected one,
        # since some shared system resources (e.g. Network/Cookies on Windows)
        # can still be affected by other Chromium-based browsers.
        all_running = get_running_browsers()
        if all_running and self.logger:
            self.logger.info(f"[ACQUIRE] Browsers currently running: {', '.join(all_running)}")

        return True

    def start_acquire(self):
        output_path = self.path_input.text().strip()
        if not output_path or not self.selected_browser_path:
            QMessageBox.warning(
                self,
                "Warning",
                "Please select both browser and destination folder"
            )
            return

        # ── Pre-flight check: is the selected browser currently running? ──
        if not self._check_browser_not_running():
            return

        try:
            evidence_folder = self.acquire.start_parsing(
                self.selected_user,
                self.selected_browser_path
            )

            self.generated_evidence_path = evidence_folder

            QMessageBox.information(
                self,
                "Success",
                "Acquisition Completed Successfully"
            )

        except Exception as e:
            if self.logger:
                self.logger.error(f"Acquisition failed: {str(e)}")
            raise Exception(str(e))

    
    