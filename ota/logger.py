import csv
from datetime import datetime

def log_update(file_path, device_name, version):
    with open(file_path, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().isoformat(),
            device_name,
            version
        ])


def get_last_updates(file_path, limit=5):
    try:
        with open(file_path, "r") as f:
            rows = list(csv.reader(f))
    except FileNotFoundError:
        return []

    return rows[-limit:]