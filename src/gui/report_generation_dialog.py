
import datetime
import json
import os
import re

from PySide6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QFrame,
    QRadioButton,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QFileDialog,
    QMessageBox,
    QHBoxLayout
)
from PySide6.QtGui import QIcon
from services.utils.utils import resource_path

def get_case_number(evidence_path):
    prefs = os.path.join(evidence_path, "preferences.json")

    if os.path.exists(prefs):
        with open(prefs, "r", encoding="utf-8") as f:
            data = json.load(f)

        return (
            data.get("case_information", {})
                .get("case_number", "")
        )

    return ""

class ReportGenerationDialog(QDialog):
    def __init__(self, report_controller, report_mode="full", parent=None, logger=None):
        super().__init__(parent)
        self.report_controller = report_controller
        self.report_mode = report_mode
        self.logger = logger

        self.evidence_path = report_controller.evidence_path

        self.setWindowTitle("Generate Report")
        self.resize(350, 150)

        layout = QVBoxLayout(self)

        # Format Selection
        format_layout = QVBoxLayout()
        format_layout.addWidget(QLabel("Select Report Format:"))

        # Radio Buttons
        self.pdf_radio = QRadioButton("PDF")
        self.csv_radio = QRadioButton("CSV")
        self.json_radio = QRadioButton("JSON")

        # Default selected
        self.pdf_radio.setChecked(True)

        # Group buttons
        self.format_group = QButtonGroup(self)
        self.format_group.addButton(self.pdf_radio)
        self.format_group.addButton(self.csv_radio)
        self.format_group.addButton(self.json_radio)

        format_layout.addWidget(self.pdf_radio)
        format_layout.addWidget(self.csv_radio)
        format_layout.addWidget(self.json_radio)

        layout.addLayout(format_layout)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

        # Buttons
        button_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        export_btn = QPushButton("Generate")
        cancel_btn.clicked.connect(self.reject)
        export_btn.clicked.connect(self.generate_report)
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(export_btn)

        layout.addLayout(button_layout)
    
    def generate_report(self):
        if self.pdf_radio.isChecked():
            selected_format = "pdf"
        elif self.csv_radio.isChecked():
            selected_format = "csv"
        elif self.json_radio.isChecked():
            selected_format = "json"

        case_number = get_case_number(self.evidence_path)

        if not case_number:
            case_number = "NO_CASE"

        # Make filename safe
        case_number = re.sub(r'[^A-Za-z0-9_-]', "_", case_number)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        default_name = f"report_{case_number}_{timestamp}.{selected_format}"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Report",
            default_name,
            f"{selected_format.upper()} Files (*.{selected_format})"
        )


        if not file_path:
            return

        try:
            if selected_format == "pdf":
                if self.report_mode == "full":
                    self.report_controller.export_full_pdf(
                        file_path
                    )

                else:
                    marked_data = self.report_controller.marked_evidence

                    if not marked_data:
                        QMessageBox.warning(
                            self,
                            "No Evidence",
                            "No marked evidence selected."
                        )
                        return

                    self.report_controller.export_full_pdf(
                        file_path,
                        marked_data=marked_data
                    )

            elif selected_format == "csv":
                if self.report_mode == "full":
                    self.report_controller.export_full_csv(file_path)
                else:
                    self.report_controller.export_marked_csv(
                        file_path,
                        self.report_controller.marked_evidence
                    )

            elif selected_format == "json":
                self.report_controller.export_full_json(file_path)

            elif selected_format == "html":
                self.report_controller.export_full_html(file_path)

            QMessageBox.information(
                self,
                "Success",
                f"Report generated successfully to:\n{file_path}"
            )

        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to generate report: {e}")
            QMessageBox.critical(self,"Export Error",str(e))