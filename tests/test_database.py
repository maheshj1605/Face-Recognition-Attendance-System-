from pathlib import Path
import tempfile
import unittest

import database


class DatabaseTestCase(unittest.TestCase):

    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()

        self.original_database_path = database.DATABASE_PATH
        database.DATABASE_PATH = (
            Path(self.temp_directory.name)
            / "test_attendance.db"
        )

        database.initialize_database()

    def tearDown(self):
        database.DATABASE_PATH = self.original_database_path
        self.temp_directory.cleanup()

    def test_database_initialization(self):
        with database.get_connection() as connection:
            tables = connection.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                """
            ).fetchall()

        table_names = {
            row["name"]
            for row in tables
        }

        self.assertIn("students", table_names)
        self.assertIn("attendance", table_names)

    def test_student_insertion(self):
        student_id = database.add_student(
            student_id="ST001",
            name="Test Student",
            department="CSE",
            year="3",
            email="test@example.com",
            phone="9876543210",
            face_encoding=None,
            created_at="2026-08-30 10:00:00"
        )

        self.assertIsNotNone(student_id)

        student = database.get_student("ST001")

        self.assertIsNotNone(student)
        self.assertEqual(student["name"], "Test Student")

    def test_duplicate_student_id(self):
        student_data = {
            "student_id": "ST001",
            "name": "Test Student",
            "department": "CSE",
            "year": "3",
            "email": "test@example.com",
            "phone": "9876543210",
            "face_encoding": None,
            "created_at": "2026-08-30 10:00:00"
        }

        database.add_student(**student_data)

        with self.assertRaises(database.DatabaseError):
            database.add_student(**student_data)


if __name__ == "__main__":
    unittest.main()
