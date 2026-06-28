import os
from PySide6.QtWidgets import QApplication

class MainController:
    def __init__(self, logger=None):
        super().__init__()
        self.logger = logger

    def load_evidence(self, path):
        return path

    def quit_app(self):
        if self.logger:
            self.logger.info("CRAFT application exited.")
        QApplication.quit()
        



