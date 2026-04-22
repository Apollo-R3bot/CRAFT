import sys, os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('CRAFT')
    main_window = MainWindow()
    main_window.showMaximized()    

    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()