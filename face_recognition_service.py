import pickle
import cv2
import face_recognition
import numpy as np

import database
from config import CAMERA_INDEX, FRAME_SCALE, RECOGNITION_TOLERANCE


def load_known_faces():
    known_encodings = []
    known_students = []

    for row in database.get_face_encodings():
        try:
            encoding = pickle.loads(row["face_encoding"])
            known_encodings.append(np.asarray(encoding))
            known_students.append({
                "student_id": row["student_id"],
                "name": row["name"],
            })
        except (pickle.PickleError, ValueError, TypeError):
            # Ignore one bad encoding instead of stopping all recognition.
            continue

    return known_encodings, known_students


def open_camera():
    camera = cv2.VideoCapture(CAMERA_INDEX)
    if not camera.isOpened():
        camera.release()
        raise RuntimeError(
            "Camera could not be opened. Check the camera connection and permissions."
        )
    return camera


def capture_single_face():
    """Open the camera and return one encoding after a valid single-face capture."""
    camera = open_camera()
    captured_encoding = None

    try:
        while True:
            success, frame = camera.read()
            if not success:
                raise RuntimeError("Could not read a frame from the camera.")

            small_frame = cv2.resize(frame, (0, 0), fx=FRAME_SCALE, fy=FRAME_SCALE)
            rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            locations = face_recognition.face_locations(rgb_frame, model="hog")

            display = frame.copy()
            cv2.putText(
                display,
                "Show exactly one face | Press C to capture | Q to cancel",
                (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 255, 0),
                2,
            )

            if len(locations) == 0:
                cv2.putText(
                    display, "No face detected",
                    (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2
                )
            elif len(locations) > 1:
                cv2.putText(
                    display, "Multiple faces detected",
                    (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2
                )
            else:
                cv2.putText(
                    display, "One face detected - ready",
                    (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
                )

            cv2.imshow("Capture Face", display)
            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                return None
            if key == ord("c") and len(locations) == 1:
                encodings = face_recognition.face_encodings(rgb_frame, locations)
                if encodings:
                    captured_encoding = encodings[0]
                    return captured_encoding
    finally:
        camera.release()
        cv2.destroyAllWindows()


def recognize_from_camera(on_recognized=None):
    """Run the live recognition loop until Q is pressed."""
    known_encodings, known_students = load_known_faces()
    if not known_encodings:
        raise RuntimeError("No registered face encodings are available.")

    camera = open_camera()
    frame_number = 0
    current_matches = []

    try:
        while True:
            success, frame = camera.read()
            if not success:
                raise RuntimeError("Could not read a frame from the camera.")

            frame_number += 1

            if frame_number % 3 == 0:
                small_frame = cv2.resize(
                    frame, (0, 0), fx=FRAME_SCALE, fy=FRAME_SCALE
                )
                rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                locations = face_recognition.face_locations(rgb_frame, model="hog")
                encodings = face_recognition.face_encodings(rgb_frame, locations)

                current_matches = []
                for location, encoding in zip(locations, encodings):
                    distances = face_recognition.face_distance(
                        known_encodings, encoding
                    )
                    best_index = int(np.argmin(distances))
                    distance = float(distances[best_index])

                    if distance <= RECOGNITION_TOLERANCE:
                        student = known_students[best_index]
                        current_matches.append((location, student, distance))
                        if on_recognized:
                            on_recognized(student)
                    else:
                        current_matches.append((location, None, distance))

            for location, student, distance in current_matches:
                top, right, bottom, left = [int(value / FRAME_SCALE) for value in location]
                if student:
                    label = f"{student['name']} ({student['student_id']})"
                    status = "Recognized"
                else:
                    label = "Unknown Person"
                    status = "Unknown"

                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(
                    frame, label, (left, max(25, top - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2
                )
                cv2.putText(
                    frame, status, (left, bottom + 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 2
                )

            cv2.putText(
                frame, "Press Q to stop",
                (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2
            )
            cv2.imshow("Face Recognition", frame)

            if (cv2.waitKey(1) & 0xFF) == ord("q"):
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()
