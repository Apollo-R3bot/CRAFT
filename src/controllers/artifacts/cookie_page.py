import os
import pandas as pd

from controllers.artifact_controller import ArtifactTableController


class CookieController:
    def __init__(self, evidence_path=None):
        self.table = ArtifactTableController()
        self.title = "Cookies"
        self.evidence_path = evidence_path

    def create_page(self):
        csv_file = os.path.join(self.evidence_path, "cookies.csv")

        columns = []
        data = []

        required_columns = [
            "Host", 
            "Name", 
            "Value", 
            "Creation Time", 
            "Last Access Time", 
            "Expiry Time", 
            "Secure", 
            "HTTP Only"
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
                data = [[f"Failed to load cookies.csv: {str(e)}"]]

        else:
            columns = ["Message"]
            data = [["cookies.csv not found"]]

        total_count = len(data)
        return self.table.create_table_page(
            self.title,
            columns,
            data,
            total_count
        )