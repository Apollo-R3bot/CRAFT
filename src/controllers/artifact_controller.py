import json
import os
import pandas as pd

from PySide6.QtCore import Qt, QDate, QRect, QSize
from PySide6.QtGui import QColor, QPainter, QPen, QBrush, QFont
from PySide6.QtWidgets import (
    QCheckBox, QDateEdit, QFileDialog, QHBoxLayout,
    QLineEdit, QMessageBox, QPushButton, QWidget,
    QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QStyledItemDelegate, QFrame
)


STATUS_COLORS = {
    'Active':      (QColor("#0a381d"), QColor('#4ade80')),
    'Deleted':     (QColor("#310d0d"), QColor('#f87171')),
    'Complete':    (QColor('#0a381d'), QColor('#4ade80')),
    'Cancelled':   (QColor("#511919"), QColor("#f49a9a")),
    'Interrupted': (QColor('#2d1f00'), QColor('#fbbf24')),
    'CLEARED':     (QColor('#1c1917'), QColor('#fb923c')),
}

PRIMARY_CL   = "#1e3a5f"
SECONDARY_CL = "#1A7FAE"
BG_CL        = "#1e3a5f"

# ── Clear message background, border, text color) ────────────────
CLEAR_MSG_BG = "None"
CLEAR_MSG_BORDER = "#fbbf24"
CLEAR_MSG_TEXT = "#fde68a"

def _load_clear_info(evidence_path: str) -> dict:
    result = {"clear_range": None, "last_browser_close": None, "first_visit_time": None}
    prefs_path = os.path.join(evidence_path, "preferences.json")
    if not os.path.exists(prefs_path):
        return result
    try:
        with open(prefs_path, encoding="utf-8") as f:
            prefs = json.load(f)
        browser_info = prefs.get("browser_info", {})
        clear_data   = prefs.get("clear_data", {})
        result["clear_range"] = (
            browser_info.get("last_selected_clear_data_range")
            or clear_data.get("time_period_label")
        )
        result["last_browser_close"] = browser_info.get("last_browser_close")
    except Exception:
        pass
    return result


def _build_clear_message(clear_range: str, last_close: str, data: list, columns: list):
    is_all_time = clear_range.strip().lower() == "all time"
    has_records = len(data) > 0

    first_time = ""
    if has_records and "Visit Time" in columns:
        vt_idx = columns.index("Visit Time")
        times = [
            str(row[vt_idx])
            for row in data
            if len(row) > vt_idx
            and str(row[0]) == "Active"
            and str(row[vt_idx]) not in ("", "nan", "None")
        ]

        if times:
            first_time = sorted(times)[0]

    if is_all_time and not has_records:
        return (
            "The browsing history was cleared for All Time — no records remain."
        )

    elif is_all_time and has_records:
        if first_time:
            return (
                f"Browsing history was cleared for All Time before {first_time}. "
                "Records shown were created after the clear event."
            )

        return (
            "Browsing history was cleared for All Time. "
            "Records shown survived the clear."
        )

    close_str = (
        f" Browser last closed at {last_close}."
        if last_close else ""
    )

    return (
        f"Browsing history was cleared for {clear_range}.{close_str}"
    )

def _clear_message_widget(message: str) -> QWidget:
    frame = QFrame()
    frame.setStyleSheet(f"""
        QFrame {{
            background: {CLEAR_MSG_BG};
            border: 1px solid {CLEAR_MSG_BORDER};
            border-radius: 6px;
        }}
    """)

    layout = QHBoxLayout(frame)
    layout.setContentsMargins(14, 8, 14, 8)

    icon = QLabel("⚠")
    icon.setStyleSheet(f"""
        color: {CLEAR_MSG_BORDER};
        font-size: 16px;
        border: none;
        background: transparent;
    """)

    label = QLabel(message)
    label.setWordWrap(True)
    label.setStyleSheet(f"""
        color: {CLEAR_MSG_TEXT};
        font-size: 12px;
        font-weight: 500;
        border: none;
        background: transparent;
    """)

    layout.addWidget(icon)
    layout.addWidget(label, 1)

    return frame

class StatusBadgeDelegate(QStyledItemDelegate):
    PADDING_H = 10
    PADDING_V = 3
    RADIUS    = 8

    def paint(self, painter: QPainter, option, index):
        from PySide6.QtWidgets import QStyle
        status = index.data(Qt.DisplayRole)

        if status not in STATUS_COLORS:
            super().paint(painter, option, index)
            return

        pill_bg, pill_fg = STATUS_COLORS[status]

        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)

        cell_bg = index.data(Qt.BackgroundRole)
        if cell_bg is not None:
            painter.fillRect(option.rect, cell_bg)
        else:
            painter.fillRect(option.rect, option.palette.base())

        if option.state & QStyle.State_Selected:
            sel_color = option.palette.highlight().color()
            sel_color.setAlpha(120)
            painter.fillRect(option.rect, sel_color)

        font = QFont(option.font)
        font.setPointSize(max(font.pointSize() - 1, 8))
        font.setBold(True)
        painter.setFont(font)

        fm       = painter.fontMetrics()
        text_w   = fm.horizontalAdvance(status)
        text_h   = fm.height()
        pill_w   = text_w + self.PADDING_H * 2
        pill_h   = text_h + self.PADDING_V * 2

        cell      = option.rect
        pill_x    = cell.x() + (cell.width()  - pill_w) // 2
        pill_y    = cell.y() + (cell.height() - pill_h) // 2
        pill_rect = QRect(pill_x, pill_y, pill_w, pill_h)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(pill_bg))
        painter.drawRoundedRect(pill_rect, self.RADIUS, self.RADIUS)

        painter.setPen(QPen(pill_fg))
        painter.drawText(pill_rect, Qt.AlignCenter, status)

        painter.restore()

    def sizeHint(self, option, index) -> QSize:
        status = index.data(Qt.DisplayRole)
        if status not in STATUS_COLORS:
            return super().sizeHint(option, index)
        fm = option.fontMetrics
        return QSize(
            fm.horizontalAdvance(status) + self.PADDING_H * 2,
            fm.height() + self.PADDING_V * 2 + 4,
        )


class ArtifactTableController:
    def __init__(self, report_controller=None):
        self.table              = None
        self.file_type_dropdown = None
        self.report_controller  = report_controller
        self.title              = ""
        self._badge_delegate    = StatusBadgeDelegate()

    def create_table_page(self,title,columns=None,data=None,total_count=0,time_column=0,bottom_message: str = ""):
        self.title = title

        page   = QWidget()
        layout = QVBoxLayout(page)

        heading = QLabel(f"{title} ({total_count})")
        heading.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(heading)

        # ── Controls ──────────────────────────────────────────────────────
        controls_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                color: #e2e8f0;
                border: 1px solid {PRIMARY_CL};
                border-radius: 6px;
                padding: 6px;
            }}
        """)
        self.search_input.setPlaceholderText("Search URL, title, domain, keywords...")
        controls_layout.addWidget(self.search_input)

        self.start_date = QDateEdit()
        self.start_date.setStyleSheet(f"QDateEdit {{border: 1px solid {PRIMARY_CL};border-radius: 6px;padding: 4px;}}")
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat("yyyy-MM-dd")
        self.start_date.setDate(QDate.currentDate())
        controls_layout.addWidget(self.start_date)

        self.end_date = QDateEdit()
        self.end_date.setStyleSheet(f"QDateEdit {{border: 1px solid {PRIMARY_CL};border-radius: 6px;padding: 4px;}}")
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat("yyyy-MM-dd")
        self.end_date.setDate(QDate.currentDate())
        controls_layout.addWidget(self.end_date)

        self.filter_btn = QPushButton("Apply Filter")
        self.filter_btn.setStyleSheet(f"""
            QPushButton {{border: 1px solid {PRIMARY_CL};border-radius: 6px;padding: 6px;}}
            QPushButton:hover {{background: {SECONDARY_CL};border-color: {SECONDARY_CL};}}
        """)
        controls_layout.addWidget(self.filter_btn)
        layout.addLayout(controls_layout)

        export_button = QPushButton("Save Table as CSV")
        export_button.setStyleSheet(f"""
            QPushButton {{border: 1px solid {PRIMARY_CL};border-radius: 6px;padding: 6px;}}
            QPushButton:hover {{background: {SECONDARY_CL};border-color: {SECONDARY_CL};}}
        """)
        export_button.clicked.connect(self.export_results_to_csv)
        controls_layout.addWidget(export_button)

        # ── Table ─────────────────────────────────────────────────────────
        self.table = QTableWidget()
        table      = self.table
        table.setSortingEnabled(True)
        table.verticalHeader().setVisible(False)
        table.setColumnCount(len(columns) + 1)
        table.setHorizontalHeaderLabels(["Mark"] + columns)
        table.setStyleSheet(f"""
            QTableWidget {{
                color: #e2e8f0;
                gridline-color: #1e3a5f;
                border-bottom: 1px solid #1e3a5f;
                border-radius: 6px;
            }}
            QTableWidget::item {{
                padding: 6px 8px;
                border: none;
                color: #e2e8f0;
            }}
            QHeaderView::section {{
                background: {PRIMARY_CL};
                color: #38bdf8;
                border: none;
                border-bottom: 1px solid {PRIMARY_CL};
                font-size: 13px;
            }}
            QCheckBox {{margin: 6px; color: #e2e8f0;}}
            QCheckBox::indicator {{
                width: 15px; height: 15px;
                border: 1px solid {PRIMARY_CL}; border-radius: 4px;
            }}
            QCheckBox::indicator:checked {{
                background: {SECONDARY_CL}; border: 1px solid {SECONDARY_CL};
            }}
            QCheckBox::indicator:hover {{border-color: {SECONDARY_CL};}}
        """)

        STATUS_COL = (columns.index("Status") + 1) if "Status" in columns else 1
        table.setItemDelegateForColumn(STATUS_COL, self._badge_delegate)
        self._status_col = STATUS_COL

        header = table.horizontalHeader()
        header.setStretchLastSection(True)
        layout.addWidget(table)

        # ── Bottom message banner ──────────────────────────────────────────
        # Rendered below the table when bottom_message is provided.
        # Shown/hidden based on whether filtered data is empty or not.
        self._bottom_banner = None
        if bottom_message:
            self._bottom_banner = _clear_message_widget(
                bottom_message
            )
            layout.addWidget(self._bottom_banner)

        # ── load_table ────────────────────────────────────────────────────
        def load_table(filtered_data):
            table.setRowCount(len(filtered_data))

            for row_index, row_data in enumerate(filtered_data):
                checkbox = QCheckBox()
                existing = self.report_controller.marked_evidence.get(
                    self.title, pd.DataFrame()
                )
                if not existing.empty:
                    row_dict = {columns[i]: str(row_data[i]) for i in range(len(columns))}
                    if row_dict in existing.astype(str).to_dict("records"):
                        checkbox.setChecked(True)

                checkbox.stateChanged.connect(
                    lambda _, r=row_index: self.save_marked_evidence()
                )
                cb_widget = QWidget()
                cb_widget.setStyleSheet("background: transparent;")
                cb_layout = QHBoxLayout(cb_widget)
                cb_layout.addWidget(checkbox)
                cb_layout.setAlignment(Qt.AlignCenter)
                cb_layout.setContentsMargins(0, 0, 0, 0)
                table.setCellWidget(row_index, 0, cb_widget)

                for col_index, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    if (col_index + 1) == self._status_col and str(value) in STATUS_COLORS:
                        _, fg = STATUS_COLORS[str(value)]
                        item.setForeground(QBrush(fg))
                    table.setItem(row_index, col_index + 1, item)

            # Keep banner visible regardless of filter state
            if self._bottom_banner:
                self._bottom_banner.setVisible(True)

        load_table(data)

        # ── Auto search ───────────────────────────────────────────────────
        def auto_search():
            keyword  = self.search_input.text().lower().strip()
            filtered = [
                row for row in data
                if keyword in " ".join(str(c).lower() for c in row)
            ]
            load_table(filtered)

        self.search_input.textChanged.connect(auto_search)

        # ── Date filter ───────────────────────────────────────────────────
        possible_time_columns = [
            "Visit Time", "Start Time", "End Time", "Creation Time",
            "Created Time", "Created Date", "Last Access Time",
            "Expiry Time", "First Used", "Last Used", "Timestamp", "Time", "Date",
        ]
        detected_time_column = next(
            (col for col in possible_time_columns if col in columns), None
        )

        def apply_date_filter():
            if not detected_time_column:
                load_table(data)
                return
            time_index = columns.index(detected_time_column)
            start      = self.start_date.date().toPython()
            end        = self.end_date.date().toPython()
            filtered   = []
            for row in data:
                try:
                    row_date    = str(row[time_index]).split(" ")[0]
                    parsed_date = QDate.fromString(row_date, "yyyy-MM-dd").toPython()
                    if start <= parsed_date <= end:
                        filtered.append(row)
                except Exception:
                    continue
            load_table(filtered)

        self.filter_btn.clicked.connect(apply_date_filter)

        return page

    # ── Helpers ────────────────────────────────────────────────────────────
    def save_marked_evidence(self):
        if not self.table or not self.report_controller:
            return
        marked_rows = self.get_marked_rows()
        if not marked_rows:
            self.report_controller.marked_evidence.pop(self.title, None)
            return
        self.report_controller.marked_evidence[self.title] = pd.DataFrame(marked_rows)

    def export_results_to_csv(self, logger=None):
        if not self.table:
            return
        file_path, _ = QFileDialog.getSaveFileName(
            None, "Save CSV", "", "CSV Files (*.csv)"
        )
        if not file_path:
            return
        headers = [
            self.table.horizontalHeaderItem(col).text()
            if self.table.horizontalHeaderItem(col) else f"Column {col}"
            for col in range(self.table.columnCount())
        ]
        rows = []
        for row in range(self.table.rowCount()):
            if self.table.isRowHidden(row):
                continue
            rows.append([
                self.table.item(row, col).text()
                if self.table.item(row, col) else ""
                for col in range(self.table.columnCount())
            ])
        pd.DataFrame(rows, columns=headers).to_csv(
            file_path, index=False, encoding="utf-8-sig"
        )
        
        if logger:
            logger.error(f"CSV exported successfully to: {file_path}")
        QMessageBox.information(None, "Success", f"CSV exported successfully to:\n{file_path}")

    def get_marked_rows(self):
        headers = [
            self.table.horizontalHeaderItem(col).text()
            for col in range(1, self.table.columnCount())
        ]
        marked_rows = []
        for row in range(self.table.rowCount()):
            widget = self.table.cellWidget(row, 0)
            if not widget:
                continue
            checkbox = widget.findChild(QCheckBox)
            if checkbox and checkbox.isChecked():
                marked_rows.append({
                    headers[col - 1]: (
                        self.table.item(row, col).text()
                        if self.table.item(row, col) else ""
                    )
                    for col in range(1, self.table.columnCount())
                })
        return marked_rows