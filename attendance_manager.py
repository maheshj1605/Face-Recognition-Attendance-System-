from datetime import datetime
import database


def mark_attendance(student_id):
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    if database.attendance_exists(student_id, date):
        return False, "Attendance already marked"

    added = database.add_attendance(student_id, date, time)
    if added:
        return True, f"Attendance marked at {time}"
    return False, "Attendance could not be recorded"


def get_attendance(date=None, department=None, search_text=None):
    return database.get_attendance(date, department, search_text)
