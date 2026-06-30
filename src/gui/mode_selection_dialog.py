import os

from PySide6.QtWidgets import QDialog, QPushButton, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap

from services.utils.utils import resource_path

class ModeSelectionDialog(QDialog):
    def __init__(self, logger):
        super().__init__()

        self.setWindowTitle("CRAFT - Cross Browser Artifact Forensics Tool v1.0.0")
        self.resize(400, 300)

        self.selected_mode = None
        self.logger = logger

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        logo = QLabel()
        pixmap = QPixmap(
            resource_path("resources/icons/craft.png")
        )
        pixmap = pixmap.scaled(120,120,Qt.KeepAspectRatio,Qt.SmoothTransformation)
        logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignCenter)
        layout.insertWidget(0, logo)

        heading = QLabel("Welcome to CRAFT")
        heading.setStyleSheet("""font-size: 25px; font-weight: bold;""")
        layout.addWidget(heading)
        heading.setAlignment(Qt.AlignCenter)
        label2 = QLabel("Choose what you want to do.")
        label2.setWordWrap(True)
        layout.addWidget(label2)
        label2.setAlignment(Qt.AlignCenter)

        acquire_btn = QPushButton("Acquire Evidence")
        analyze_btn = QPushButton("Analyze Evidence")
        self.setStyleSheet("""
            QPushButton {
                padding: 10px;
                font-size: 15px;
            }
            QLabel {
                text-align: center;
                font-size: 15px;
            }
            
            """)

        acquire_btn.clicked.connect(self.select_acquire)
        analyze_btn.clicked.connect(self.select_analyze)

        layout.addWidget(acquire_btn)
        layout.addWidget(analyze_btn)
        self.setLayout(layout)

    def select_acquire(self):
        self.logger.info("User selected: Acquire Evidence")
        self.selected_mode = "acquire"
        self.accept()
        
    def select_analyze(self):
        self.logger.info("User selected: Analyze Evidence")
        self.selected_mode = "analyze"
        self.accept()
