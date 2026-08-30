import csv
from pathlib import Path
import database


def export_attendance(file_path, date=None):
    rows = database.get_attendance(date=date)

    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["Student ID", "Name", "Department", "Date", "Time", "Status"])
            for row in rows:
                writer.writerow([
                    row["student_id"], row["name"], row["department"],
                    row["date"], row["time"], row["status"]
                ])
    except OSError as exc:
        raise RuntimeError(f"CSV export failed: {exc}") from exc

    return len(rows)
