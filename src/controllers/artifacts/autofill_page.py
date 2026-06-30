import os
import pandas as pd

from controllers.artifact_controller import ArtifactTableController, _build_clear_message, _load_clear_info


class AutofillController:
    def __init__(self, evidence_path=None, report_controller=None, logger=None):
        self.table = ArtifactTableController(report_controller)
        self.title = "Autofill"
        self.evidence_path = evidence_path
        self.logger = logger

    def create_page(self):
        csv_file = os.path.join(self.evidence_path, "autofill.csv")

        columns = []
        data = []

        if os.path.exists(csv_file):
            try:
                df = pd.read_csv(csv_file)

                columns = df.columns.tolist()
                data = df.values.tolist()

            except Exception as e:
                if self.logger:
                    self.logger.error(f"Failed to load autofill: {e}")
                columns = ["Error"]
                data = [[f"Failed to load autofill file: {str(e)}"]]

        else:
            if self.logger:
                self.logger.error("autofill file not found")
            columns = ["Message"]
            data = [["autofill file not found"]]

        # ── Build bottom banner ────────────────────────────────────────
        bottom_message = ""

        info = _load_clear_info(self.evidence_path)
        clear_range = info["clear_range"]
        last_close  = info["last_browser_close"]

        if clear_range and clear_range.lower() not in ("unknown", ""):
            bottom_message = _build_clear_message(
                clear_range, last_close, data, columns
            )

        total_count = len(data)

        return self.table.create_table_page(
            self.title,
            columns,
            data,
            total_count,
            bottom_message=bottom_message,
        )