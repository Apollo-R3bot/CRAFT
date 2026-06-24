import os
import pandas as pd


class TimelineController:
    def __init__(self, evidence_path):
        self.evidence_path = evidence_path

    def build_timeline(self):
        timeline = []

        files = {
            "History": "history.csv",
            "Downloads": "downloads.csv",
        }

        for artifact, file_name in files.items():
            path = os.path.join(
                self.evidence_path,
                file_name
            )

            if not os.path.exists(path):
                continue

            df = pd.read_csv(path)

            if artifact == "History":
                for _, row in df.iterrows():
                    timeline.append([
                        row["Visit Time"],
                        artifact,
                        row["URL"],
                    ])

            elif artifact == "Downloads":
                for _, row in df.iterrows():
                    timeline.append([
                        row["End Time"],
                        artifact,
                        row["Tab URL"],
                        row["File Path"],
                    ])
        return pd.DataFrame(
            timeline,
            columns=[
                "Timestamp",
                "Artifact Type",
                "Description",
                "Source"
            ]
        )