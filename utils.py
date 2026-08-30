import re
from datetime import datetime


def validate_student_form(student):
    required = ("student_id", "name", "department", "year")
    if any(not student.get(field, "").strip() for field in required):
        return False, "Student ID, name, department and year are required."

    if student.get("email") and not re.fullmatch(
        r"[^@\s]+@[^@\s]+\.[^@\s]+", student["email"].strip()
    ):
        return False, "Please enter a valid email address."

    if student.get("phone") and not re.fullmatch(r"[0-9+\-\s()]{7,20}", student["phone"].strip()):
        return False, "Please enter a valid phone number."

    return True, ""


def today():
    return datetime.now().strftime("%Y-%m-%d")


def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
