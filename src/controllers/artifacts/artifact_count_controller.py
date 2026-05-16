import os
import pandas as pd

def get_artifact_count(evidence_path, file_name):
    if not evidence_path:
        return 0

    csv_file = os.path.join(evidence_path, file_name)

    if not os.path.exists(csv_file):
        return 0

    try:
        df = pd.read_csv(csv_file)
        return len(df.index)

    except Exception:
        return 0