import os
import pandas as pd

from controllers.artifact_controller import ArtifactTableController


class DownloadController:
    def __init__(self, evidence_path=None):
        self.table = ArtifactTableController()
        self.title = "Downloads"
        self.evidence_path = evidence_path

    def create_page(self):
        csv_file = os.path.join(self.evidence_path, "downloads.csv")

        columns = []
        data = []

        if os.path.exists(csv_file):
            try:
                df = pd.read_csv(csv_file)
                columns = df.columns.tolist()
                data = df.values.tolist()

            except Exception as e:
                columns = ["Error"]
                data = [[f"Failed to load downloads.csv: {str(e)}"]]

        else:
            columns = ["Message"]
            data = [["downloads.csv not found"]]

        total_count = len(data)
        return self.table.create_table_page(
            self.title,
            columns,
            data,
            total_count
        )