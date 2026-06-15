import os
import pandas as pd

from controllers.artifact_controller import ArtifactTableController


class HistoryController:
    def __init__(self, evidence_path, report_controller):
        self.table = ArtifactTableController(report_controller)
        self.title = "History"
        self.evidence_path = evidence_path

    def create_page(self):
        csv_file = os.path.join(self.evidence_path, "history.csv")

        columns = []
        data = []

        required_columns = [
            "Visit Time",
            "URL",
            "Title",
            "Visit Count",
            "Visit Type",
            "Duration"
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
                data = [[
                    f"Failed to load history file: {str(e)}"
                ]]

        else:
            columns = ["Message"]
            data = [["history data not found"]]

        total_count = len(data)
        
        return self.table.create_table_page(
            self.title,
            columns,
            data,
            total_count
        )