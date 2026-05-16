from datetime import datetime
import os
import shutil
from PySide6.QtWidgets import QMessageBox

class AnalyzeEvidenceController:
    def __init__(self):
        self.output_folder  = None
        self.enable_hashing = False

    def set_input_folder(self, folder):
        self.input_folder = folder

    def set_hashing(self, enabled: bool):
        self.enable_hashing = enabled
    

    def start_analysis(self, evidence_path):
        try:
            pass
        except Exception as e:
            QMessageBox.critical(self, "Error", "Acquisition not completed.!")

       