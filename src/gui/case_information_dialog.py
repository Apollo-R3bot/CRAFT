from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QHBoxLayout
)


class CaseInformationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Evidence Item Information")
        self.resize(450, 300)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Case Number"))
        self.case_number = QLineEdit()
        layout.addWidget(self.case_number)

        layout.addWidget(QLabel("Evidence Number"))
        self.evidence_number = QLineEdit()
        layout.addWidget(self.evidence_number)

        layout.addWidget(QLabel("Examiner Name"))
        self.examiner_name = QLineEdit()
        layout.addWidget(self.examiner_name)

        layout.addWidget(QLabel("Notes"))
        self.notes = QTextEdit()
        layout.addWidget(self.notes)

        buttons = QHBoxLayout()

        cancel_btn = QPushButton("Cancel")
        start_btn = QPushButton("Start Acquisition")

        cancel_btn.clicked.connect(self.reject)
        start_btn.clicked.connect(self.accept)

        buttons.addWidget(cancel_btn)
        buttons.addWidget(start_btn)

        layout.addLayout(buttons)

    def get_case_data(self):
        return {
            "case_number": self.case_number.text().strip(),
            "evidence_number": self.evidence_number.text().strip(),
            "examiner_name": self.examiner_name.text().strip(),
            "notes": self.notes.toPlainText().strip()
        }