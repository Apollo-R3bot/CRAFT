import json
from matplotlib import colors
import pandas as pd

from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import QComboBox, QDateEdit, QFileDialog, QHBoxLayout, QHeaderView, QLineEdit, QMessageBox, QPushButton, QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

class ArtifactTableController:
    def __init__(self):
        self.table = None
        self.file_type_dropdown = None

    def create_table_page(self, title, columns=None, data=None, total_count=0, time_column=0):
        page = QWidget()
        layout = QVBoxLayout(page)

        heading = QLabel(f"{title} ({total_count})")
        heading.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(heading)

        # Filter Section
        controls_layout = QHBoxLayout()

        # Search input (auto search)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search...")
        controls_layout.addWidget(self.search_input)

        # Start date
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat("yyyy-MM-dd")
        self.start_date.setDate(QDate.currentDate())
        controls_layout.addWidget(self.start_date)

        # End date
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat("yyyy-MM-dd")
        self.end_date.setDate(QDate.currentDate())
        controls_layout.addWidget(self.end_date)

        # Filter button
        self.filter_btn = QPushButton("Apply Filter")
        controls_layout.addWidget(self.filter_btn)
        layout.addLayout(controls_layout)

        export_button = QPushButton("Save Table as CSV")
        export_button.clicked.connect(self.export_results_to_csv)
        controls_layout.addWidget(export_button)

        self.table = QTableWidget()
        table = self.table
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)
        table.setSortingEnabled(True)

        header = table.horizontalHeader()
        header.setStretchLastSection(True)
        layout.addWidget(table)

        # Load Table Function
        def load_table(filtered_data):
            table.setRowCount(len(filtered_data))

            for row_index, row_data in enumerate(filtered_data):
                for col_index, value in enumerate(row_data):
                    table.setItem(
                        row_index,
                        col_index,
                        QTableWidgetItem(str(value))
                    )
        load_table(data)

        # Auto Search Function
        def auto_search():
            keyword = self.search_input.text().lower().strip()
            filtered = []

            for row in data:
                row_text = " ".join(
                    [str(cell).lower() for cell in row]
                )

                if keyword in row_text:
                    filtered.append(row)

            load_table(filtered)
        self.search_input.textChanged.connect(auto_search)

        # Date Filter Function
        possible_time_columns = [
            "Visit Time",
            "Start Time",
            "End Time",
            "Creation Time",
            "Created Time",
            "Created Date",
            "Last Access Time",
            "Expiry Time",
            "First Used",
            "Last Used",
            "Timestamp",
            "Time",
            "Date"
        ]

        detected_time_column = None
        for col in possible_time_columns:
            if col in columns:
                detected_time_column = col
                break

        def apply_date_filter():
            if not detected_time_column:
                load_table(data)
                return

            filtered = []
            time_index = columns.index(detected_time_column)

            start = self.start_date.date().toPython()
            end = self.end_date.date().toPython()
            for row in data:
                try:
                    row_date = str(row[time_index]).split(" ")[0]
                    parsed_date = QDate.fromString(
                        row_date,
                        "yyyy-MM-dd"
                    ).toPython()

                    if start <= parsed_date <= end:
                        filtered.append(row)

                except Exception:
                    continue

            load_table(filtered)
        self.filter_btn.clicked.connect(apply_date_filter)

        return page

    def export_results_to_csv(self):
        if not self.table:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            None,
            "Save CSV",
            "",
            "CSV Files (*.csv)"
        )

        if not file_path:
            return

        headers = []

        for col in range(self.table.columnCount()):
            header_item = self.table.horizontalHeaderItem(col)
            if header_item:
                headers.append(header_item.text())
            else:
                headers.append(f"Column {col}")
        rows = []

        for row in range(self.table.rowCount()):
            if self.table.isRowHidden(row):
                continue

            row_data = []

            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item:
                    row_data.append(item.text())
                else:
                    row_data.append("")

            rows.append(row_data)

        df = pd.DataFrame(rows, columns=headers)
        df.to_csv(file_path,index=False,encoding="utf-8-sig")

        QMessageBox.information(
            None,
            "Success",
            f"CSV exported successfully:\n{file_path}"
        )