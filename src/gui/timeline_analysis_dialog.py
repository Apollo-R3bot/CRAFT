from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QDateEdit,
    QTableWidget,
    QTableWidgetItem,
    QFileDialog
)
from PySide6.QtCore import QDate
import pandas as pd

class TimelineAnalysisDialog(QDialog):

    def __init__(self, controller, parent=None):
        super().__init__(parent)

        self.controller = controller

        self.setWindowTitle("Timeline Analysis")
        self.resize(1000, 550)

        layout = QVBoxLayout(self)

        filter_layout = QHBoxLayout()

        filter_layout.addWidget(QLabel("From"))

        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(
            QDate.currentDate().addMonths(-1)
        )

        filter_layout.addWidget(self.start_date)

        filter_layout.addWidget(QLabel("To"))

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())

        filter_layout.addWidget(self.end_date)

        self.generate_btn = QPushButton(
            "Generate Timeline"
        )

        self.generate_btn.clicked.connect(
            self.load_timeline
        )

        filter_layout.addWidget(self.generate_btn)

        layout.addLayout(filter_layout)

        self.table = QTableWidget()

        self.table.setColumnCount(4)

        self.table.setHorizontalHeaderLabels([
            "Timestamp",
            "Artifact Type",
            "Description",
            "Downloaded File"
        ])

        self.table.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(self.table)

    def load_timeline(self):
        start = self.start_date.date().toPython()
        end = self.end_date.date().toPython()

        df = self.controller.build_timeline()

        if df.empty:
            return

        df["Timestamp"] = pd.to_datetime(
            df["Timestamp"],
            errors="coerce"
        )

        df = df[
            (df["Timestamp"].dt.date >= start) &
            (df["Timestamp"].dt.date <= end)
        ]

        df = df.sort_values(
            "Timestamp",
            ascending=False
        )

        self.table.setRowCount(len(df))

        for row_idx, row in enumerate(df.values.tolist()):

            for col_idx, value in enumerate(row):

                self.table.setItem(
                    row_idx,
                    col_idx,
                    QTableWidgetItem(str(value))
                )