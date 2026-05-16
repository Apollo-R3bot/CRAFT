import sys, os
from PySide6.QtWidgets import QApplication, QDialog
from PySide6.QtCore import Qt
from gui.evidence_acquisition_dialog import EvidenceAcquisition
from gui.evidence_analysis_dialog import EvidenceAnalysis
from gui.main_window import MainWindow
from gui.mode_selection_dialog import ModeSelectionDialog
from services.utils.logger import setup_logger


def main():
    app = QApplication(sys.argv)
    # app.setStyleSheet("""
    #     QWidget {
    #         background-color: #f5f7fa;
    #         color: #222222;
    #         font-size: 14px;
    #     }

    #     QMainWindow {
    #         background-color: #f5f7fa;
    #     }

    #     QDialog {
    #         background-color: white;
    #     }

    #     QLabel {
    #         color: #222222;
    #     }

    #     QPushButton {
    #         background-color: white;
    #         color: #222222;
    #         border: 1px solid #cccccc;
    #         border-radius: 6px;
    #         padding: 6px;
    #     }

    #     QPushButton:hover {
    #         background-color: #f0f0f0;
    #     }

    #     QLineEdit, QComboBox, QListWidget, QTableWidget {
    #         background-color: white;
    #         color: #222222;
    #         border: 1px solid #dcdcdc;
    #         border-radius: 5px;
    #     }

    #     QHeaderView::section {
    #         background-color: #eeeeee;
    #         color: #111111;
    #         padding: 5px;
    #         border: none;
    #     }
    # """)

    log_folder = os.path.join(os.getcwd(), "Log")
    logger = setup_logger(log_folder)

    logger.info("=== APPLICATION STARTED ===")
    
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
            analysis_dialog = EvidenceAnalysis()
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