import sqlite3
from pathlib import Path
from config import DATABASE_PATH


class DatabaseError(Exception):
    """Raised when a database operation cannot be completed."""


def get_connection():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    try:
        with get_connection() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    department TEXT NOT NULL,
                    year TEXT NOT NULL,
                    email TEXT,
                    phone TEXT,
                    face_encoding BLOB,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT NOT NULL,
                    date TEXT NOT NULL,
                    time TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'Present',
                    FOREIGN KEY (student_id) REFERENCES students(student_id)
                        ON DELETE RESTRICT,
                    UNIQUE(student_id, date)
                );
                """
            )
    except sqlite3.Error as exc:
        raise DatabaseError(f"Could not initialize database: {exc}") from exc


def add_student(student_id, name, department, year, email, phone, face_encoding, created_at):
    try:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO students
                (student_id, name, department, year, email, phone, face_encoding, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    student_id, name, department, year, email, phone,
                    face_encoding, created_at
                ),
            )
            return cursor.lastrowid
    except sqlite3.IntegrityError as exc:
        if "students.student_id" in str(exc):
            raise DatabaseError("Student ID already exists.") from exc
        raise DatabaseError(f"Could not add student: {exc}") from exc
    except sqlite3.Error as exc:
        raise DatabaseError(f"Could not add student: {exc}") from exc


def update_student(student_id, name, department, year, email, phone):
    try:
        with get_connection() as connection:
            connection.execute(
                """
                UPDATE students
                SET name=?, department=?, year=?, email=?, phone=?
                WHERE student_id=?
                """,
                (name, department, year, email, phone, student_id),
            )
    except sqlite3.Error as exc:
        raise DatabaseError(f"Could not update student: {exc}") from exc


def update_face_encoding(student_id, face_encoding):
    try:
        with get_connection() as connection:
            connection.execute(
                "UPDATE students SET face_encoding=? WHERE student_id=?",
                (face_encoding, student_id),
            )
    except sqlite3.Error as exc:
        raise DatabaseError(f"Could not update face encoding: {exc}") from exc


def clear_face_encoding(student_id):
    update_face_encoding(student_id, None)


def delete_student(student_id):
    try:
        with get_connection() as connection:
            connection.execute(
                "DELETE FROM students WHERE student_id=?", (student_id,)
            )
    except sqlite3.IntegrityError as exc:
        raise DatabaseError(
            "This student has attendance records. Remove those records first "
            "if deletion is really required."
        ) from exc
    except sqlite3.Error as exc:
        raise DatabaseError(f"Could not delete student: {exc}") from exc


def get_student(student_id):
    with get_connection() as connection:
        return connection.execute(
            "SELECT * FROM students WHERE student_id=?", (student_id,)
        ).fetchone()


def get_all_students(search_text=""):
    with get_connection() as connection:
        if search_text.strip():
            term = f"%{search_text.strip()}%"
            return connection.execute(
                """
                SELECT * FROM students
                WHERE student_id LIKE ? OR name LIKE ?
                ORDER BY name
                """,
                (term, term),
            ).fetchall()
        return connection.execute(
            "SELECT * FROM students ORDER BY name"
        ).fetchall()


def get_face_encodings():
    with get_connection() as connection:
        return connection.execute(
            """
            SELECT student_id, name, face_encoding
            FROM students
            WHERE face_encoding IS NOT NULL
            ORDER BY name
            """
        ).fetchall()


def attendance_exists(student_id, date):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT 1 FROM attendance WHERE student_id=? AND date=?",
            (student_id, date),
        ).fetchone()
        return row is not None


def add_attendance(student_id, date, time, status="Present"):
    try:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO attendance(student_id, date, time, status)
                VALUES (?, ?, ?, ?)
                """,
                (student_id, date, time, status),
            )
            return True
    except sqlite3.IntegrityError:
        return False
    except sqlite3.Error as exc:
        raise DatabaseError(f"Could not record attendance: {exc}") from exc


def get_attendance(date=None, department=None, search_text=None):
    query = """
        SELECT a.student_id, s.name, s.department, a.date, a.time, a.status
        FROM attendance a
        JOIN students s ON s.student_id = a.student_id
        WHERE 1=1
    """
    parameters = []

    if date:
        query += " AND a.date=?"
        parameters.append(date)
    if department and department != "All":
        query += " AND s.department=?"
        parameters.append(department)
    if search_text:
        query += " AND (a.student_id LIKE ? OR s.name LIKE ?)"
        term = f"%{search_text.strip()}%"
        parameters.extend([term, term])

    query += " ORDER BY a.date DESC, a.time DESC"

    with get_connection() as connection:
        return connection.execute(query, parameters).fetchall()


def get_departments():
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT DISTINCT department FROM students ORDER BY department"
        ).fetchall()
        return [row["department"] for row in rows]


def count_students():
    with get_connection() as connection:
        return connection.execute("SELECT COUNT(*) FROM students").fetchone()[0]


def count_present(date):
    with get_connection() as connection:
        return connection.execute(
            "SELECT COUNT(*) FROM attendance WHERE date=? AND status='Present'",
            (date,),
        ).fetchone()[0]


def count_absent(date):
    total = count_students()
    return max(total - count_present(date), 0)
