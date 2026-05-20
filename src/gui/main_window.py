from PySide6.QtGui import QAction, Qt
from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QMainWindow, QSplitter, QStackedWidget, QTableWidget, QTableWidgetItem, QToolBar, QVBoxLayout, QWidget

from controllers.artifacts.artifact_count_controller import get_artifact_count
from controllers.artifacts.autofill_page import AutofillController
from controllers.artifacts.bookmark_page import BookmarkController
from controllers.artifacts.cache_page import CacheController
from controllers.artifacts.cookie_page import CookieController
from controllers.artifacts.download_page import DownloadController
from controllers.artifacts.history_page import HistoryController
from controllers.artifacts.dashboard_page import DashboardController
from controllers.artifacts.logins_page import LoginsController
from controllers.artifacts.search_term_page import SearchTermController
from controllers.artifacts.session_page import SessionsController
from controllers.artifacts.top_sites_page import TopSitesController
from controllers.main_controller import MainController
from controllers.report_controller import ReportController
from gui.evidence_acquisition_dialog import EvidenceAcquisition
from gui.evidence_analysis_dialog import EvidenceAnalysis
from gui.report_generation_dialog import ReportGenerationDialog

class MainWindow(QMainWindow):
    def __init__(self, evidence_path=None, logger=None):
        super().__init__()
        self.control = MainController()
        self.evidence_path = evidence_path
        self.logger = logger

        if evidence_path:
            self.control.load_evidence(evidence_path)

        self.setWindowTitle("CRAFT - Evidence Analysis")
        self.setGeometry(100, 100, 1400, 850)

        #MenuBar and Menu
        menuBar = self.menuBar()
        menuBar.setStyleSheet("""
            QMenuBar {
                padding: 5px;
            }
            QMenuBar::item {
                padding: 8px 15px;
                margin: 3px;
            }
            QMenu {
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 25px;
                margin: 2px;
            }
            QMenu::item:selected {
                border: 1px solid #efefef;
                border-radius: 4px;
            }
        """)
        fileMenu = menuBar.addMenu("File")
        acquire_evidence = fileMenu.addAction("Acquire Evicence")
        acquire_evidence.triggered.connect(self.open_acquisition_dialog)

        analyze_evidence = fileMenu.addAction("Analyze Evicence")
        analyze_evidence.triggered.connect(self.open_analysis_dialog)

        remove_evidence = fileMenu.addAction("Remove Evicence")
        integrity_verify = fileMenu.addAction("Verify Artefact")
        
        report_menu = menuBar.addMenu("Report")
        report_action = QAction("Generate Report", self)
        report_menu.addAction(report_action)
        report = ReportController(self.evidence_path)
        report_action.triggered.connect(
            lambda: ReportGenerationDialog(report, self).exec()
        )

        quit_app = fileMenu.addAction("Quit")
        quit_app.triggered.connect(self.control.quit_app)
        
        editMenu = menuBar.addMenu("Edit")
        quit_app = editMenu.addAction("Copy")
        quit_app = editMenu.addAction("Cut")
        quit_app = editMenu.addAction("Paste")

        settingMenu = menuBar.addMenu("Setting")
        helpMenu = menuBar.addMenu("Help")

        # Main container
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Splitter for sidebar + main content
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # LEFT SIDEBAR NAVIGATION
        sidebar = QWidget()
        sidebar.setFixedWidth(280)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 10, 10, 10)
        sidebar_layout.setSpacing(10)

        title = QLabel("Evidence Artifacts")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        sidebar_layout.addWidget(title)

        self.nav_list = QListWidget()
        self.nav_list.setStyleSheet("""
            QListWidget {
                font-size: 14px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 5px;
                margin: 2px;
            }
            QListWidget::item:selected {
                border: 1px solid #4a90e2;
                border-radius: 8px;
            }
        """)

        artifacts = [
            (" Dashboard"),
            (" History"),
            (" Downloads"),
            (" Cookies"),
            (" Password"),
            (" Cache"),
            (" Search Terms"),
            (" Bookmarks"),
            (" Autofill"),
            (" Sessions"),
            (" Top Sites")
        ]

        for name in artifacts:
            item = QListWidgetItem(name)
            self.nav_list.addItem(item)

        self.nav_list.currentRowChanged.connect(self.change_page)
        sidebar_layout.addWidget(self.nav_list)

        splitter.addWidget(sidebar)

        # RIGHT MAIN CONTENT AREA
        self.pages = QStackedWidget()
        splitter.addWidget(self.pages)
        splitter.setSizes([290, 1200])

        self.page_controllers = [
            DashboardController(evidence_path),
            HistoryController(evidence_path),
            DownloadController(evidence_path),
            CookieController(evidence_path),
            LoginsController(evidence_path),
            CacheController(evidence_path),
            SearchTermController(evidence_path),
            BookmarkController(evidence_path),
            AutofillController(evidence_path),
            SessionsController(evidence_path),
            TopSitesController(evidence_path)
        ]

        for controller in self.page_controllers:
            self.pages.addWidget(controller.create_page())

        self.nav_list.setCurrentRow(0)
        

    def load_evidence(self, evidence_path):
        self.evidence_path = evidence_path
        self.current_case_path = evidence_path

        # Clear old pages
        while self.pages.count():
            widget = self.pages.widget(0)
            self.pages.removeWidget(widget)
            widget.deleteLater()

        # Reload controllers/pages
        dashboard = DashboardController(evidence_path)
        history = HistoryController(evidence_path)
        downloads = DownloadController(evidence_path)
        cookies = CookieController(evidence_path)
        logins = LoginsController(evidence_path)
        cache = CacheController(evidence_path)
        search = SearchTermController(evidence_path)
        bookmarks = BookmarkController(evidence_path)
        autofill = AutofillController(evidence_path)
        sessions = SessionsController(evidence_path)
        top_sites = TopSitesController(evidence_path)
        ReportController(self.current_case_path)

        self.pages.addWidget(dashboard.create_page())
        self.pages.addWidget(history.create_page())
        self.pages.addWidget(downloads.create_page())
        self.pages.addWidget(cookies.create_page())
        self.pages.addWidget(logins.create_page())
        self.pages.addWidget(cache.create_page())
        self.pages.addWidget(search.create_page())
        self.pages.addWidget(bookmarks.create_page())
        self.pages.addWidget(autofill.create_page())
        self.pages.addWidget(sessions.create_page())
        self.pages.addWidget(top_sites.create_page())

    def open_analysis_dialog(self):
        dialog = EvidenceAnalysis(self)
        if dialog.exec():
            selected_path = dialog.evidence_path
            if selected_path:
                self.load_evidence(selected_path)

    def open_acquisition_dialog(self):
        dialog = EvidenceAcquisition(
            logger=self.logger,
            parent=self
        )

        if dialog.exec():
            new_evidence = dialog.generated_evidence_path
            if new_evidence:
                self.load_evidence(new_evidence)

    def change_page(self, index):
        if index >= 0:
            self.pages.setCurrentIndex(index)