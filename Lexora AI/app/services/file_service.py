import os
import uuid

from flask import current_app
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def save_uploaded_file(file):

    if file.filename == "":
        raise ValueError("No file selected")

    if not allowed_file(file.filename):
        raise ValueError("Unsupported file type")

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)

    extension = file.filename.rsplit(".", 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{extension}"
    save_path = os.path.join(upload_folder, unique_filename)

    file.save(save_path)

    return {
        "original_name": secure_filename(file.filename),
        "stored_name": unique_filename,
        "file_type": extension,
        "file_size": os.path.getsize(save_path),
    }


def delete_physical_file(stored_filename):
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    file_path = os.path.join(upload_folder, stored_filename)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")