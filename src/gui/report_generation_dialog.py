
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

class ReportGenerationDialog(QDialog):
    def __init__(self, report_controller, parent=None):
        super().__init__(parent)
        self.report_controller = report_controller

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
        self.html_radio = QRadioButton("HTML")

        # Default selected
        self.pdf_radio.setChecked(True)

        # Group buttons
        self.format_group = QButtonGroup(self)
        self.format_group.addButton(self.pdf_radio)
        self.format_group.addButton(self.csv_radio)
        self.format_group.addButton(self.json_radio)
        self.format_group.addButton(self.html_radio)

        format_layout.addWidget(self.pdf_radio)
        format_layout.addWidget(self.csv_radio)
        format_layout.addWidget(self.json_radio)
        format_layout.addWidget(self.html_radio)

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
        elif self.html_radio.isChecked():
            selected_format = "html"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Report",
            f"forensic_report.{selected_format}",
            f"{selected_format.upper()} Files (*.{selected_format})"
        )

        if not file_path:
            return

        try:
            if selected_format == "pdf":
                self.report_controller.export_full_pdf(file_path)

            elif selected_format == "csv":
                self.report_controller.export_full_csv(file_path)

            elif selected_format == "json":
                self.report_controller.export_full_json(file_path)

            elif selected_format == "html":
                self.report_controller.export_full_html(file_path)

            QMessageBox.information(
                self,
                "Success",
                f"Report generated successfully:\n{file_path}"
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Error",
                str(e)
            )