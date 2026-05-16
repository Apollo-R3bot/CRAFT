import os
from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from controllers.main_controller import MainController
from gui.dashboard_layout import DashboardLayout
from services.utils.utils import format_size


class DashboardController:
    def __init__(self, evidence_path=None):
        self.evidence_path = evidence_path
        self.layout_builder = DashboardLayout()
        self.control = MainController()

        if evidence_path:
            self.control.load_evidence(evidence_path)

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

    def create_info_widget(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        size = self.get_folder_size(self.evidence_path)

        info = [
            "Browser: Chrome",
            "Created Date: 2026-05-05",
            f"Size: {size}",
            # "Evidence Name: Case_001",
            f"Path: {self.evidence_path or 'Not Selected'}",
        ]

        for item in info:
            layout.addWidget(QLabel(item))

        return self.layout_builder.create_card("Evidence Information", widget)

    def create_hash_widget(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        hashes = [
            "MD5: a1b2c3d4...",
            "SHA1: e5f6g7h8...",
            "SHA256: z9y8x7w6...",
        ]

        for item in hashes:
            layout.addWidget(QLabel(item))

        return self.layout_builder.create_card("Evidence Hash", widget)

    def create_top_sites_chart(self):
        figure = Figure(figsize=(5, 4))
        canvas = FigureCanvas(figure)

        ax = figure.add_subplot(111)

        sites = ["google.com", "youtube.com", "github.com", "bing.com", "gmail.com"]
        visits = [120, 95, 80, 60, 45]

        ax.bar(sites, visits)
        ax.set_title("Top 5 Visited Sites")
        ax.set_ylabel("Visits")
        ax.tick_params(axis='x', rotation=20)

        return self.layout_builder.create_card("Top Sites", canvas)

    def create_summary_widget(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        summary = [
            "Total Artifacts: 1,245",
            "Downloads: 152",
            "Cookies: 890",
            "Bookmarks: 212",
        ]

        for item in summary:
            layout.addWidget(QLabel(item))

        return self.layout_builder.create_card("Artifact Summary", widget)

    def create_page(self):
        top_left = self.create_info_widget()
        top_right = self.create_hash_widget()
        bottom_left = self.create_top_sites_chart()
        bottom_right = self.create_summary_widget()

        return self.layout_builder.create_dashboard_page(
            top_left,
            top_right,
            bottom_left,
            bottom_right,
        )
