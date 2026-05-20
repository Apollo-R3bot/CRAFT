from PySide6.QtWidgets import QDialog, QFrame, QHBoxLayout, QPushButton, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

from gui.evidence_acquisition_dialog import EvidenceAcquisition
from gui.evidence_analysis_dialog import EvidenceAnalysis

class ModeSelectionDialog(QDialog):
    def __init__(self, logger):
        super().__init__()

        self.setWindowTitle("CRAFT - Cross Browser Artifact Forensics Tool v1.0.0")
        # self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint)
        self.resize(400, 300)

        self.selected_mode = None
        self.logger = logger

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        heading = QLabel("Welcome to CRAFT")
        heading.setStyleSheet("""font-size: 25px; font-weight: bold;""")
        layout.addWidget(heading)
        heading.setAlignment(Qt.AlignCenter)
        label = QLabel("By continuing, you agree to the CRAFT Terms of Use and our Privacy Notice. Choose what you want to do.")
        label.setWordWrap(True)
        layout.addWidget(label)
        label.setAlignment(Qt.AlignCenter)

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
            QDialog {
                padding: 40px;
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
        self.logger.info("User selected: Acquire Evidence")
        self.selected_mode = "analyze"
        self.accept()
