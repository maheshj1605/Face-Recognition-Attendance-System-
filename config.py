from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
FACES_DIR = BASE_DIR / "faces"
ASSETS_DIR = BASE_DIR / "assets"
DATABASE_PATH = DATA_DIR / "attendance.db"

CAMERA_INDEX = 0
FRAME_SCALE = 0.25
RECOGNITION_TOLERANCE = 0.50
PROCESS_EVERY_N_FRAMES = 3

APP_TITLE = "Face Recognition Attendance System"
WINDOW_SIZE = "1180x720"

for directory in (DATA_DIR, FACES_DIR, ASSETS_DIR):
    directory.mkdir(parents=True, exist_ok=True)
