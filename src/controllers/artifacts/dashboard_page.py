import json
import os
import pandas as pd
from urllib.parse import urlparse
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget, QVBoxLayout
from PySide6.QtGui import QPixmap, Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from datetime import datetime

from controllers.artifact_controller import ArtifactTableController
from controllers.main_controller import MainController
from gui.dashboard_layout import DashboardLayout
from services.utils.utils import format_size


class DashboardController:
    def __init__(self, evidence_path=None, report_controller=None, logger=None):
        self.table = ArtifactTableController(report_controller)
        
        self.evidence_path = evidence_path
        self.layout_builder = DashboardLayout()
        self.control = MainController()
        self.logger = logger

        if evidence_path:
            self.control.load_evidence(evidence_path)

    def get_created_date(self, folder_path):
        if not folder_path or not os.path.exists(folder_path):
            return "Unknown"

        try:
            created_time = os.path.getctime(folder_path)
            return datetime.fromtimestamp(created_time).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return "Unknown"

    def get_folder_size(self, folder_path):
        total_size = 0
        if not folder_path or not os.path.exists(folder_path):
            return "0 B"

        for dirpath, dirnames, filenames in os.walk(folder_path):
            for file in filenames:
                file_path = os.path.join(dirpath, file)
                if os.path.exists(file_path):
                    total_size += os.path.getsize(file_path)
                    
        return format_size(total_size)

    def create_browser_info_widget(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        json_file = os.path.join(
            self.evidence_path,
            "preferences.json"
        )

        if not os.path.exists(json_file):
            layout.addWidget(QLabel("No browser information found"))

            return self.layout_builder.create_card(
                "Browser Information",
                widget
            )

        try:
            with open(json_file,"r",encoding="utf-8") as f:
                browser_info = json.load(f)
                item = browser_info.get("browser_info",{})
                row = QWidget()
                row_layout = QHBoxLayout(row)

                browser_type = item.get("browser_type","Unknown")
                browser_version = item.get("browser_version","Unknown")
                installed_date = item.get("installed_date","Unknown")
                profile_user = item.get("profile_user","Unknown")

                # Browser Logo
                logo_label = QLabel()
                browser_lower = browser_type.lower()
                icon_map = {
                    "chrome": "chrome.png",
                    "edge": "edge.png",
                    "firefox": "firefox.png",
                    "opera": "opera.png"
                }

                icon_file = icon_map.get(browser_lower,"default.png")
                base_dir = os.path.abspath(
                    os.path.join(
                        os.path.dirname(__file__),
                        "..",
                        ".."
                    )
                )

                icon_path = os.path.join(base_dir,"resources","icons",icon_file)

                if os.path.exists(icon_path):
                    pixmap = QPixmap(icon_path)
                    pixmap = pixmap.scaled(
                        64,
                        64,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )

                    logo_label.setPixmap(pixmap)
                else:
                    logo_label.setText("No Logo")

                logo_label.setStyleSheet("""
                    QLabel {
                        border: none;
                        background: transparent;
                        padding: 0px;
                    }
                """)
                logo_label.setFixedSize(90, 90)
                row_layout.addWidget(logo_label)

                # Browser Info Text
                info_layout = QVBoxLayout()
                info_layout.addWidget(QLabel(f"Browser: {browser_type}"))
                info_layout.addWidget(QLabel(f"Version: {browser_version}"))
                info_layout.addWidget(QLabel(f"Installed Date: {installed_date}"))
                info_layout.addWidget(QLabel(f"User Profile: {profile_user}"))

                row_layout.addLayout(info_layout)
                layout.addWidget(row)

        except Exception as e:
            layout.addWidget(
                QLabel(
                    f"Failed to load browser info: {str(e)}"
                )
            )

        return self.layout_builder.create_card(
            "Browser Information",
            widget
        )

    def create_info_widget(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        size = self.get_folder_size(self.evidence_path)
        created_date = self.get_created_date(self.evidence_path)

        info = [
            f"Created Date: {created_date}",
            f"Size: {size}",
            f"Path: {self.evidence_path or 'Not Selected'}",
        ]
        for item in info:
            layout.addWidget(QLabel(item))
        return self.layout_builder.create_card("Evidence Information", widget)
    
    def create_top_sites_chart(self):
        figure = Figure(figsize=(5, 4))
        canvas = FigureCanvas(figure)
        ax = figure.add_subplot(111)
        history_file = os.path.join(self.evidence_path, "top_sites.csv")

        sites = []
        visits = []

        if os.path.exists(history_file):
            try:
                df = pd.read_csv(history_file)
                if "Domain" in df.columns and "Visit Count" in df.columns:
                    df = df.sort_values(
                        "Visit Count",
                        ascending=False
                    ).head(5)

                    sites = df["Domain"].tolist()
                    visits = df["Visit Count"].tolist()

            except Exception as e:
                if self.logger:
                    self.logger.error(f"Top sites chart error: {e}")

        # Fallback if no data
        if df.empty:
            ax.text(0.5,0.5,"No Data",ha="center",va="center")
            ax.axis("off")

        # PIE CHART
        ax.pie(
            visits,
            labels=sites,
            autopct="%1.1f%%",
            startangle=90
        )
        ax.axis("equal")

        return self.layout_builder.create_card(
            "Top 5 Visited Sites",
            canvas
        )

    def create_browser_account_info_widget(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        json_file = os.path.join(
            self.evidence_path,
            "preferences.json"
        )

        if not os.path.exists(json_file):
            layout.addWidget(
                QLabel("No account information found")
            )

            return self.layout_builder.create_card(
                "Account Summary",
                widget
            )

        try:
            with open(json_file,"r",encoding="utf-8") as f:
                data = json.load(f)
                accounts = data.get(
                    "signed_in_accounts",
                    []
                )

            if not accounts:
                layout.addWidget(
                    QLabel("No signed-in accounts found")
                )

                return self.layout_builder.create_card(
                    "Account Summary",
                    widget
                )

            for account in accounts:
                row = QWidget()
                row_layout = QHBoxLayout(row)

                # Profile Picture
                image_label = QLabel()
                picture_path = account.get("local_picture_path","")

                if picture_path and os.path.exists(picture_path):
                    pixmap = QPixmap(picture_path)
                    pixmap = pixmap.scaled(
                        64,
                        64,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )

                    image_label.setPixmap(pixmap)
                else:
                    image_label.setText("No Image")

                image_label.setStyleSheet("""
                    QLabel {
                        border-radius: 32;
                        border: 2px solid #cccccc;
                        background: white;
                    }
                """)
                row_layout.addWidget(image_label)

                # Account Info
                info_layout = QVBoxLayout()

                name = account.get("full_name","Unknown")
                email = account.get("email","No Email")
                account_id = account.get("account_id","N/A")

                info_layout.addWidget(QLabel(f"Name: {name}"))
                info_layout.addWidget(QLabel(f"Email: {email}"))
                info_layout.addWidget(QLabel(f"Account ID: {account_id}"))

                row_layout.addLayout(info_layout)
                layout.addWidget(row)

        except Exception as e:
            layout.addWidget(
                QLabel(
                    f"Failed to load account info: {str(e)}"
                )
            )

        return self.layout_builder.create_card(
            "Account Summary",
            widget
        )

    def create_all_activity_widget(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("All Activities Timeline")
        title.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
        """)

        layout.addWidget(title)

        sample_data = [
            "Visited google.com",
            "Downloaded report.pdf",
            "Logged into gmail.com",
            "Visited github.com"
        ]

        for item in sample_data:
            layout.addWidget(QLabel(item))

        return self.layout_builder.create_card(
            "Activity Timeline",
            widget
        )

    def create_page(self):
        top_left = self.create_browser_info_widget()
        top_right = self.create_info_widget()
        bottom_left = self.create_top_sites_chart()
        bottom_right = self.create_browser_account_info_widget()
        # bottom = self.create_all_activity_widget()

        return self.layout_builder.create_dashboard_page(
            top_left,
            top_right,
            bottom_left,
            bottom_right,
            # bottom
        )
