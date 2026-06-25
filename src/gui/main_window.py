import json
import os

from PySide6.QtGui import QAction, Qt
from PySide6.QtWidgets import (
    QFileDialog, QFrame, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QMainWindow, QSplitter, QStackedWidget, QTableWidget, QTableWidgetItem,
    QToolBar, QVBoxLayout, QWidget
)

from controllers.artifacts.artifact_count_controller import get_artifact_count
from controllers.artifacts.autofill_page import AutofillController
from controllers.artifacts.bookmark_page import BookmarkController
from controllers.artifacts.cookie_page import CookieController
from controllers.artifacts.download_page import DownloadController
from controllers.artifacts.history_page import HistoryController
from controllers.artifacts.dashboard_page import DashboardController
from controllers.artifacts.logins_page import LoginsController
from controllers.artifacts.search_term_page import SearchTermController
from controllers.artifacts.top_sites_page import TopSitesController
from controllers.main_controller import MainController
from controllers.report_controller import ReportController
from gui.evidence_acquisition_dialog import EvidenceAcquisition
from gui.evidence_analysis_dialog import EvidenceAnalysis
from gui.report_generation_dialog import ReportGenerationDialog


SIDEBAR_BG    = "#06080f"
CONTENT_BG    = "#06080f"
MENUBAR_BG    = "#06080f"
SEPARATOR_CLR = "#1e3a5f"
TEXT_PRIMARY  = "#e2e8f0"
TEXT_MUTED    = "#94a3b8"
TEXT_DIM      = "#475569"
ACCENT        = "#38bdf8"
NAV_HOVER     = "#0f141f"
NAV_SELECTED     = "#0f141f"
# NAV_SELECTED  = "#0f2460"

class MainWindow(QMainWindow):
    def load_machine_info(self):
        if not self.evidence_path:
            return {}
        prefs_file = os.path.join(self.evidence_path, "preferences.json")
        if not os.path.exists(prefs_file):
            return {}
        try:
            with open(prefs_file, "r", encoding="utf-8") as f:
                prefs = json.load(f)
            return prefs.get("machine_info", {})
        except Exception:
            return {}

    def load_browser_info(self):
        if not self.evidence_path:
            return {}
        prefs_file = os.path.join(self.evidence_path, "preferences.json")
        if not os.path.exists(prefs_file):
            return {}
        try:
            with open(prefs_file, "r", encoding="utf-8") as f:
                prefs = json.load(f)
            return prefs.get("browser_info", {})
        except Exception:
            return {}

    def __init__(self, evidence_path=None, logger=None):
        super().__init__()
        self.control           = MainController()
        self.evidence_path     = evidence_path
        self.report_controller = ReportController(self.evidence_path)
        self.logger            = logger

        if evidence_path:
            self.control.load_evidence(evidence_path)

        self.setWindowTitle("CRAFT - Evidence Analysis")
        self.setGeometry(100, 100, 1400, 850)

        # ── Menu bar ───────────────────────────────────────────────────
        menuBar = self.menuBar()
        menuBar.setStyleSheet(f"""
            QMenuBar {{
                background: {MENUBAR_BG};
                color: {TEXT_PRIMARY};
                padding: 5px;
                border-bottom: 1px solid {SEPARATOR_CLR};
            }}
            QMenuBar::item {{
                padding: 8px 15px;
                margin: 3px;
                color: {TEXT_MUTED};
                border-radius: 6px;
            }}
            QMenuBar::item:selected {{
                background: {NAV_HOVER};
                color: {TEXT_PRIMARY};
            }}
            QMenu {{
                background: {NAV_SELECTED};
                color: {TEXT_PRIMARY};
                border: 1px solid {SEPARATOR_CLR};
                border-radius: 8px;
                padding: 5px;
            }}
            QMenu::item {{
                padding: 8px 25px;
                margin: 2px;
                color: {TEXT_MUTED};
            }}
            QMenu::item:selected {{
                background: {SEPARATOR_CLR};
                color: {TEXT_PRIMARY};
                border-radius: 4px;
            }}
        """)

        fileMenu = menuBar.addMenu("File")

        acquire_evidence = fileMenu.addAction("Acquire Evidence")
        acquire_evidence.triggered.connect(self.open_acquisition_dialog)

        analyze_evidence = fileMenu.addAction("Analyze Evidence")
        analyze_evidence.triggered.connect(self.open_analysis_dialog)

        report_menu   = menuBar.addMenu("Report")
        report_action = QAction("Generate Report", self)
        report_menu.addAction(report_action)
        report_action.triggered.connect(
            lambda: ReportGenerationDialog(
                self.report_controller, report_mode="full", parent=self
            ).exec()
        )

        export_marked_btn = QAction("Export Evidence", self)
        report_menu.addAction(export_marked_btn)
        export_marked_btn.triggered.connect(
            lambda: ReportGenerationDialog(
                self.report_controller, report_mode="marked", parent=self
            ).exec()
        )

        quit_app = fileMenu.addAction("Quit")
        quit_app.triggered.connect(self.control.quit_app)
        helpMenu = menuBar.addMenu("Help")

        # ── Central widget ─────────────────────────────────────────────
        central_widget = QWidget()
        central_widget.setStyleSheet(f"background: {CONTENT_BG};")
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Splitter ───────────────────────────────────────────────────
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(1)
        splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background: {SEPARATOR_CLR};
            }}
        """)
        main_layout.addWidget(splitter)

        # ── LEFT SIDEBAR ───────────────────────────────────────────────
        sidebar = QWidget()
        sidebar.setFixedWidth(270)
        sidebar.setStyleSheet(f"background: {SIDEBAR_BG};")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 8, 0, 8)
        sidebar_layout.setSpacing(0)

        # Machine info panel
        machine_info = self.load_machine_info()

        info_widget = QWidget()
        info_widget.setStyleSheet("background: transparent;")
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(12, 8, 12, 8)
        info_layout.setSpacing(3)

        def field_row(label, value):
            row    = QWidget()
            row.setStyleSheet("background: transparent;")
            hbox   = QHBoxLayout(row)
            hbox.setContentsMargins(0, 0, 0, 0)
            hbox.setSpacing(6)

            lbl = QLabel(f"{label}:")
            lbl.setFixedWidth(64)
            lbl.setStyleSheet(f"font-size: 13px; color: {TEXT_DIM};")

            val = QLabel(str(value) if value else "—")
            val.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {TEXT_MUTED};")
            val.setWordWrap(True)

            hbox.addWidget(lbl)
            hbox.addWidget(val, 1)
            info_layout.addWidget(row)

        field_row("HOST", machine_info.get("hostname"))
        field_row("USER", machine_info.get("username"))
        field_row("OS", machine_info.get("os_version"))

        sidebar_layout.addWidget(info_widget)

        # Separator between info panel and nav list
        sep_h = QFrame()
        sep_h.setFrameShape(QFrame.Shape.HLine)
        sep_h.setStyleSheet(f"color: {SEPARATOR_CLR}; margin: 4px 12px;")
        sidebar_layout.addWidget(sep_h)

        # Navigation list
        self.nav_list = QListWidget()
        self.nav_list.setStyleSheet(f"""
            QListWidget {{
                font-size: 14px;
                padding: 5px;
                border: none;
                background: transparent;
                color: {TEXT_PRIMARY};
            }}
            QListWidget::item {{
                padding: 8px 10px;
                margin: 2px 4px;
                border-radius: 8px;
                color: {TEXT_MUTED};
            }}
            QListWidget::item:hover {{
                background: {NAV_HOVER};
                color: {TEXT_PRIMARY};
            }}
            QListWidget::item:selected {{
                background: {NAV_SELECTED};
                border-radius: 8px;
                color: {TEXT_PRIMARY};
            }}
        """)

        for name in [
            " Dashboard",
            " History",
            " Downloads",
            " Cookies",
            " Password",
            " Search Terms",
            " Bookmarks",
            " Form Data",
            " Frequently Websites",
        ]:
            self.nav_list.addItem(QListWidgetItem(name))

        self.nav_list.currentRowChanged.connect(self.change_page)
        sidebar_layout.addWidget(self.nav_list)

        splitter.addWidget(sidebar)

        # ── RIGHT CONTENT AREA ─────────────────────────────────────────
        self.pages = QStackedWidget()
        self.pages.setStyleSheet(f"QStackedWidget {{ background: {CONTENT_BG}; }}")
        splitter.addWidget(self.pages)
        splitter.setSizes([270, 1400])

        self.page_controllers = [
            DashboardController(self.evidence_path, self.report_controller),
            HistoryController(self.evidence_path, self.report_controller),
            DownloadController(self.evidence_path, self.report_controller),
            CookieController(self.evidence_path, self.report_controller),
            LoginsController(self.evidence_path, self.report_controller),
            SearchTermController(self.evidence_path, self.report_controller),
            BookmarkController(self.evidence_path, self.report_controller),
            AutofillController(self.evidence_path, self.report_controller),
            TopSitesController(self.evidence_path, self.report_controller),
        ]

        for controller in self.page_controllers:
            self.pages.addWidget(controller.create_page())

        self.nav_list.setCurrentRow(0)

    # ── Evidence loading ────────────────────────────────────────────────

    def load_evidence(self, evidence_path):
        self.evidence_path     = evidence_path
        self.current_case_path = evidence_path

        while self.pages.count():
            widget = self.pages.widget(0)
            self.pages.removeWidget(widget)
            widget.deleteLater()

        for ctrl in [
            DashboardController(self.evidence_path, self.report_controller),
            HistoryController(self.evidence_path, self.report_controller),
            DownloadController(self.evidence_path, self.report_controller),
            CookieController(self.evidence_path, self.report_controller),
            LoginsController(self.evidence_path, self.report_controller),
            SearchTermController(self.evidence_path, self.report_controller),
            BookmarkController(self.evidence_path, self.report_controller),
            AutofillController(self.evidence_path, self.report_controller),
            TopSitesController(self.evidence_path, self.report_controller),
        ]:
            self.pages.addWidget(ctrl.create_page())

        ReportController(self.current_case_path)

    def open_analysis_dialog(self):
        dialog = EvidenceAnalysis(self)
        if dialog.exec():
            selected_path = dialog.evidence_path
            if selected_path:
                self.load_evidence(selected_path)

    def open_acquisition_dialog(self):
        dialog = EvidenceAcquisition(logger=self.logger, parent=self)
        if dialog.exec():
            new_evidence = dialog.generated_evidence_path
            if new_evidence:
                self.load_evidence(new_evidence)

    def change_page(self, index):
        if index >= 0:
            self.pages.setCurrentIndex(index)