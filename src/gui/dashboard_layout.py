from PySide6.QtWidgets import (
    QScrollArea,
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

    def create_dashboard_page(self, top_left, top_right, middle_left, middle_right):
        page = QWidget()
        main_layout = QVBoxLayout(page)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # Top Row
        top_row = QHBoxLayout()
        top_row.setSpacing(15)
        top_row.addWidget(top_left)
        top_row.addWidget(top_right)

        # Middle Row
        middle_row = QHBoxLayout()
        middle_row.setSpacing(15)
        middle_row.addWidget(middle_left)
        middle_row.addWidget(middle_right)

        # Bottom Full Width Row
        bottom_row = QHBoxLayout()
        # bottom_row.addWidget(bottom_full_width)

        main_layout.addLayout(top_row)
        main_layout.addLayout(middle_row)
        main_layout.addLayout(bottom_row)
        main_layout.addStretch()

        # Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(page)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)

        # Final page
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.addWidget(scroll)

        return page
