from PySide6.QtWidgets import QHeaderView, QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem


class ArtifactTableController:
    def __init__(self):
        pass

    def create_table_page(self, title, columns=None, data=None, total_count=0):
        page = QWidget()
        layout = QVBoxLayout(page)

        heading = QLabel(f"{title} ({total_count})")
        heading.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(heading)

        table = QTableWidget()
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)
        table.setRowCount(len(data))

        for row_index, row_data in enumerate(data):
            for col_index, value in enumerate(row_data):
                table.setItem(
                    row_index,
                    col_index,
                    QTableWidgetItem(str(value))
                )

        header = table.horizontalHeader()
        header.setStretchLastSection(True)
        # header.setSectionResizeMode(QHeaderView.ResizeToContents)
        layout.addWidget(table)

        return page
