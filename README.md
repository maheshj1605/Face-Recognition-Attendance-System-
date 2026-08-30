# Face Recognition Attendance System

A local desktop attendance management system built with Python. The application uses a webcam to recognize registered students and automatically records their attendance.

The system is designed for offline use after installation and keeps face encodings and attendance data on the local computer.

---

## Features

- Student registration
- Student ID validation
- Duplicate Student ID protection
- Webcam face capture
- Single-face validation during registration
- Face encoding storage
- Live face recognition
- Unknown-person detection
- Automatic attendance marking
- One attendance record per student per day
- SQLite database
- Student management
- Search students
- Update student information
- Delete student
- Re-capture face
- Delete stored face encoding
- Attendance search
- Attendance date filtering
- Department filtering
- Today's attendance
- Complete attendance history
- CSV export
- Tkinter desktop GUI
- Unit tests
- GitHub Actions
- Windows `.exe` generation using PyInstaller

---

## Technologies

- Python 3
- Tkinter
- OpenCV
- face_recognition
- NumPy
- SQLite3
- Python csv module
- PyInstaller
- Git
- GitHub Actions

No web framework or cloud biometric API is required.

---

# Project Structure

```text
face-recognition-attendance/
│
├── main.py
├── config.py
├── database.py
├── face_recognition_service.py
├── attendance_manager.py
├── student_manager.py
├── export_manager.py
├── utils.py
│
├── data/
│   └── .gitkeep
│
├── faces/
│   └── .gitkeep
│
├── assets/
│   └── README.md
│
├── tests/
│   ├── test_database.py
│   └── test_attendance.py
│
├── .github/
│   └── workflows/
│       └── build-windows.yml
│
├── requirements.txt
├── .gitignore
├── README.md
└── LICENSE
