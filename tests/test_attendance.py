from pathlib import Path
import tempfile
import unittest

import attendance_manager
import database


class AttendanceTestCase(unittest.TestCase):

    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()

        self.original_database_path = database.DATABASE_PATH
        database.DATABASE_PATH = (
            Path(self.temp_directory.name)
            / "test_attendance.db"
        )

        database.initialize_database()

        database.add_student(
            student_id="ST001",
            name="Test Student",
            department="CSE",
            year="3",
            email="test@example.com",
            phone="9876543210",
            face_encoding=None,
            created_at="2026-08-30 10:00:00"
        )

    def tearDown(self):
        database.DATABASE_PATH = self.original_database_path
        self.temp_directory.cleanup()

    def test_attendance_insertion(self):
        added = database.add_attendance(
            student_id="ST001",
            date="2026-08-30",
            time="09:30:00",
            status="Present"
        )

        self.assertTrue(added)

        records = database.get_attendance(
            date="2026-08-30"
        )

        self.assertEqual(len(records), 1)
        self.assertEqual(
            records[0]["student_id"],
            "ST001"
        )
        self.assertEqual(
            records[0]["status"],
            "Present"
        )

    def test_duplicate_attendance_prevention(self):
        first_record = database.add_attendance(
            student_id="ST001",
            date="2026-08-30",
            time="09:30:00",
            status="Present"
        )

        second_record = database.add_attendance(
            student_id="ST001",
            date="2026-08-30",
            time="10:15:00",
            status="Present"
        )

        self.assertTrue(first_record)
        self.assertFalse(second_record)

        records = database.get_attendance(
            date="2026-08-30"
        )

        self.assertEqual(len(records), 1)

    def test_attendance_exists(self):
        date = "2026-08-30"

        self.assertFalse(
            database.attendance_exists(
                "ST001",
                date
            )
        )

        database.add_attendance(
            student_id="ST001",
            date=date,
            time="09:30:00",
            status="Present"
        )

        self.assertTrue(
            database.attendance_exists(
                "ST001",
                date
            )
        )

    def test_mark_attendance(self):
        success, message = (
            attendance_manager.mark_attendance("ST001")
        )

        self.assertTrue(success)
        self.assertIn(
            "Attendance marked",
            message
        )

        success, message = (
            attendance_manager.mark_attendance("ST001")
        )

        self.assertFalse(success)
        self.assertEqual(
            message,
            "Attendance already marked"
        )


if __name__ == "__main__":
    unittest.main()
