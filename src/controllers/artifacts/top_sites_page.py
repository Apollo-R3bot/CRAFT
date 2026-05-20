import os
import pandas as pd

from controllers.artifact_controller import ArtifactTableController


class TopSitesController:
    def __init__(self, evidence_path=None):
        self.table = ArtifactTableController()
        self.title = "Top Sites"
        self.evidence_path = evidence_path

    def create_page(self):
        csv_file = os.path.join(self.evidence_path, "top_sites.csv")

        columns = []
        data = []

        if os.path.exists(csv_file):
            try:
                df = pd.read_csv(csv_file)
                columns = df.columns.tolist()
                data = df.values.tolist()

            except Exception as e:
                columns = ["Error"]
                data = [[
                    f"Failed to load top sites file: {str(e)}"
                ]]

        else:
            columns = ["Message"]
            data = [["top sites data not found"]]

        total_count = len(data)
        
        return self.table.create_table_page(
            self.title,
            columns,
            data,
            total_count
        )