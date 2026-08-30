import pickle
import database


def encoding_to_blob(encoding):
    return pickle.dumps(encoding, protocol=pickle.HIGHEST_PROTOCOL)


def blob_to_encoding(blob):
    if not blob:
        return None
    return pickle.loads(blob)


def add_student(student, encoding, created_at):
    return database.add_student(
        student["student_id"],
        student["name"],
        student["department"],
        student["year"],
        student["email"],
        student["phone"],
        encoding_to_blob(encoding),
        created_at,
    )


def update_student(student):
    database.update_student(
        student["student_id"],
        student["name"],
        student["department"],
        student["year"],
        student["email"],
        student["phone"],
    )


def save_face_encoding(student_id, encoding):
    database.update_face_encoding(student_id, encoding_to_blob(encoding))


def remove_face_encoding(student_id):
    database.clear_face_encoding(student_id)


def get_students(search_text=""):
    return database.get_all_students(search_text)
