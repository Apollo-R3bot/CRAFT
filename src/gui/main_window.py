from PySide6.QtGui import QAction, Qt
from PySide6.QtWidgets import QMainWindow, QToolBar, QVBoxLayout, QWidget

from controllers.main_controller import MainController
from gui.acquire_dialog import EvidenceSourceAndDestination

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.control = MainController() 

        self.setWindowTitle("CRAFT - Cross Browser Artifact Forensics Tool v1.0.0")
        self.setGeometry(100, 100, 1200, 800)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        #MenuBar and Menu
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu("File")
        acquire_evidence = fileMenu.addAction("Acquire Evicence")
        acquire_evidence.triggered.connect(self.open_acquire_dialog)

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

        #Toolbar
        toolbar = QToolBar()
        self.addToolBar(Qt.LeftToolBarArea, toolbar)
        toolbar.setStyleSheet("QToolBar { padding: 5px; spacing: 10px; font-size: 30px; }")


        acquire_evidence = QAction("Home", self)
        toolbar.addAction(acquire_evidence)
        acquire_evidence.triggered.connect(self.open_acquire_dialog)
        toolbar.addSeparator()

        acquire_evidence = QAction("Acquire Evidence", self)
        toolbar.addAction(acquire_evidence)
        acquire_evidence.triggered.connect(self.open_acquire_dialog)
        toolbar.addSeparator()

        analysis = QAction("Analyzed Evidence", self)
        toolbar.addAction(analysis)
        analysis.triggered.connect(self.control.quit_app)
        toolbar.addSeparator()

        analysis = QAction("Verify Evidence", self)
        toolbar.addAction(analysis)
        analysis.triggered.connect(self.control.quit_app)
        toolbar.addSeparator()

        report = QAction("Reports", self)
        toolbar.addAction(report)
        report.triggered.connect(self.control.quit_app)
        toolbar.addSeparator()

    def open_acquire_dialog(self):
        dialog = EvidenceSourceAndDestination()
        dialog.exec()