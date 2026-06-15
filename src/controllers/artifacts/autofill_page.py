import os
import pandas as pd

from controllers.artifact_controller import ArtifactTableController


class AutofillController:
    def __init__(self, evidence_path=None, report_controller=None):
        self.table = ArtifactTableController(report_controller)
        self.title = "Autofill"
        self.evidence_path = evidence_path

    def create_page(self):
        csv_file = os.path.join(self.evidence_path, "autofill.csv")

        columns = []
        data = []

        required_columns = [
            "Field Name", 
            "Value", 
            "First Used", 
            "Last Used", 
            "Count"
        ]

        if os.path.exists(csv_file):
            try:
                df = pd.read_csv(csv_file)
                existing_columns = [
                    col for col in required_columns
                    if col in df.columns
                ]
                df = df[existing_columns]
                columns = df.columns.tolist()
                data = df.values.tolist()

            except Exception as e:
                columns = ["Error"]
                data = [[f"Failed to load autofill.csv: {str(e)}"]]

        else:
            columns = ["Message"]
            data = [["autofill.csv not found"]]

        total_count = len(data)

        return self.table.create_table_page(
            self.title,
            columns,
            data,
            total_count
        )