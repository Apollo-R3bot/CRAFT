import sys
import os
from PySide6.QtWidgets import QApplication, QDialog
from PySide6.QtGui import QIcon
from gui.evidence_acquisition_dialog import EvidenceAcquisition
from gui.evidence_analysis_dialog import EvidenceAnalysis
from gui.main_window import MainWindow
from gui.mode_selection_dialog import ModeSelectionDialog
from services.utils.logger import setup_logger
from services.utils.utils import get_icon, resource_path
from version import APP_TITLE

MENUBAR_BG    = "#06080f"
TEXT_PRIMARY  = "#e2e8f0"
PRIMARY_CL   = "#1e3a5f"
SECONDARY_CL   = "#2a4569"

def main():
    app = QApplication(sys.argv)

    path = resource_path("resources/icons/craft.ico")
    app.setWindowIcon(QIcon(path))

    app.setStyleSheet(f"""
        QMessageBox {{
            background: {MENUBAR_BG};
            color: {TEXT_PRIMARY};
            padding: 5px;
        }}
        QDialog {{
            padding: 30px;
            background: {MENUBAR_BG};
            color: {TEXT_PRIMARY};
        }}
        QLineEdit, QTextEdit {{
            background: {MENUBAR_BG};
            color: #e2e8f0;
            border: 1px solid {PRIMARY_CL};
            border-radius: 6px;
            padding: 4px;
        }}
        QPushButton {{border: 1px solid {PRIMARY_CL};border-radius: 6px;padding: 5px;}}
        QPushButton:hover {{background: {SECONDARY_CL};border-color: {SECONDARY_CL};}}
    """)

    # ── Logger setup ───────────────────────────────────────────────────
    log_folder = os.path.join(os.getcwd(), "Logs")
    logger     = setup_logger(log_folder)

    logger.info(f"{APP_TITLE} application initialised")
    logger.info(f"Log folder: {log_folder}")

    # ── Global exception handler ───────────────────────────────────────
    def _handle_exception(exc_type, exc_value, exc_tb):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_tb)
            return
        logger.critical(
            "Unhandled exception", exc_info=(exc_type, exc_value, exc_tb)
        )

    sys.excepthook = _handle_exception

    # ── Main loop ──────────────────────────────────────────────────────
    while True:
        logger.user("[NAV] Mode selection dialog opened")
        dialog = ModeSelectionDialog(logger=logger)
        result = dialog.exec()

        if result != QDialog.Accepted:
            logger.user("[NAV] Mode selection cancelled — exiting")
            break

        # ── Acquire mode ───────────────────────────────────────────────
        if dialog.selected_mode == "acquire":
            logger.user("[NAV] Mode selected: Acquire Evidence")
            acquire_dialog = EvidenceAcquisition(logger=logger)
            acq_result     = acquire_dialog.exec()

            if acq_result == QDialog.Accepted:
                evidence = getattr(acquire_dialog, "generated_evidence_path", None)
                if evidence:
                    logger.info(f"[ACQUIRE] Evidence saved to: {evidence}")
                else:
                    logger.warning("[ACQUIRE] Dialog accepted but no evidence path returned")
            else:
                logger.user("[ACQUIRE] Acquisition cancelled")

            continue

        # ── Analyse mode ───────────────────────────────────────────────
        elif dialog.selected_mode == "analyze":
            logger.user("[NAV] Mode selected: Analyze Evidence")
            analysis_dialog = EvidenceAnalysis(logger=logger)
            ana_result      = analysis_dialog.exec()

            if ana_result == QDialog.Accepted:
                evidence_path = analysis_dialog.evidence_path
                logger.user(f"[ANALYZE] Evidence folder selected: {evidence_path}")

                logger.info("[WINDOW] Opening main analysis window")
                window = MainWindow(evidence_path, logger=logger)
                window.showMaximized()

                exit_code = app.exec()
                logger.info(f"[WINDOW] Main window closed (exit code {exit_code})")
                logger.info("=== CRAFT session ended ===")
                sys.exit(exit_code)

            else:
                logger.user("[ANALYZE] Evidence selection cancelled")
                continue

    logger.info(f"=== {APP_TITLE} session ended ===")
    sys.exit(0)


if __name__ == "__main__":
    main()