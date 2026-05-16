from PySide6.QtGui import QAction, Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QMainWindow, QSplitter, QStackedWidget, QTableWidget, QTableWidgetItem, QToolBar, QVBoxLayout, QWidget

from controllers.artifacts.artifact_count_controller import get_artifact_count
from controllers.artifacts.autofill_page import AutofillController
from controllers.artifacts.bookmark_page import BookmarkController
from controllers.artifacts.cache_page import CacheController
from controllers.artifacts.cookie_page import CookieController
from controllers.artifacts.download_page import DownloadController
from controllers.artifacts.history_page import HistoryController
from controllers.artifacts.dashboard_controller import DashboardController
from controllers.artifacts.logins_page import LoginsController
from controllers.artifacts.search_term_page import SearchTermController
from controllers.artifacts.session_page import SessionsController
from controllers.main_controller import MainController

class MainWindow(QMainWindow):
    def __init__(self, evidence_path=None):
        super().__init__()
        self.control = MainController()

        if evidence_path:
            self.control.load_evidence(evidence_path)

        self.setWindowTitle("CRAFT - Evidence Analysis")
        self.setGeometry(100, 100, 1400, 850)

        #MenuBar and Menu
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu("File")
        acquire_evidence = fileMenu.addAction("Acquire Evicence")

        analyze_evidence = fileMenu.addAction("Analyze Evicence")
        remove_evidence = fileMenu.addAction("Remove Evicence")
        integrity_verify = fileMenu.addAction("Verify Artefact")
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
            (" Dashboard", 1),
            (" History", get_artifact_count(evidence_path, "history.csv")),
            (" Downloads", get_artifact_count(evidence_path, "downloads.csv")),
            (" Cookies", get_artifact_count(evidence_path, "cookies.csv")),
            (" Password", get_artifact_count(evidence_path, "logins.csv")),
            (" Cache", get_artifact_count(evidence_path, "caches.csv")),
            (" Search Terms", get_artifact_count(evidence_path, "search_terms.csv")),
            (" Bookmarks", get_artifact_count(evidence_path, "bookmarks.csv")),
            (" Autofill", get_artifact_count(evidence_path, "autofill.csv")),
            (" Sessions", get_artifact_count(evidence_path, "sessions.csv")),
            (" Top Sites", 5),
        ]

        for name, count in artifacts:
            # item = QListWidgetItem(f"{name} ({count})")
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
            SessionsController(evidence_path)
        ]

        for controller in self.page_controllers:
            self.pages.addWidget(controller.create_page())

        self.nav_list.setCurrentRow(0)



    def change_page(self, index):
        if index >= 0:
            self.pages.setCurrentIndex(index)