import sys, os
from PySide6.QtWidgets import QApplication, QDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon, Qt
from gui.evidence_acquisition_dialog import EvidenceAcquisition
from gui.evidence_analysis_dialog import EvidenceAnalysis
from gui.main_window import MainWindow
from gui.mode_selection_dialog import ModeSelectionDialog
from services.utils.logger import log_system_info, setup_logger


def main():
    app = QApplication(sys.argv)

    app.setWindowIcon(QIcon("./resources/craft.png"))

    log_folder = os.path.join(os.getcwd(), "Logs")
    logger = setup_logger(log_folder)

    logger.info("=== CRAFT Application Started ===")
    
    
    while True:
        dialog = ModeSelectionDialog(logger=logger)
        result = dialog.exec()

        if result != QDialog.Accepted:
            break 

        if dialog.selected_mode == "acquire":
            acquire_dialog = EvidenceAcquisition(logger=logger)
            acquire_dialog.exec()
            continue  

        elif dialog.selected_mode == "analyze":
            analysis_dialog = EvidenceAnalysis(logger=logger)
            result = analysis_dialog.exec()
            if result == QDialog.Accepted:
                evidence_path = analysis_dialog.evidence_path
                window = MainWindow(evidence_path)
                window.showMaximized() 
                sys.exit(app.exec())

            elif result == QDialog.Rejected:
                continue

    sys.exit()


if __name__ == "__main__":
    main()