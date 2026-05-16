from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
)


class DashboardLayout:
    def create_card(self, title_text, content_widget=None):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                border: 1px solid #dcdcdc;
                border-radius: 6px;
                padding: 5px;
                background: none;
            }
        """)

        layout = QVBoxLayout(card)

        title = QLabel(title_text)
        title.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title)

        if content_widget:
            layout.addWidget(content_widget)

        return card

    def create_dashboard_page(self, top_left, top_right, bottom_left, bottom_right):
        page = QWidget()
        main_layout = QVBoxLayout(page)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        heading = QLabel("Evidence Summary")
        heading.setStyleSheet("font-size: 24px; font-weight: bold;")
        main_layout.addWidget(heading)

        # Top Row
        top_row = QHBoxLayout()
        top_row.setSpacing(15)
        top_row.addWidget(top_left)
        top_row.addWidget(top_right)

        # Bottom Row
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(15)
        bottom_row.addWidget(bottom_left)
        bottom_row.addWidget(bottom_right)

        main_layout.addLayout(top_row)
        main_layout.addLayout(bottom_row)

        return page
