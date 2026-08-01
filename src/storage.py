import json
import os
import uuid as uuid_lib
import hashlib
from datetime import datetime

UPLOAD_FOLDER = "uploads"
METADATA_FILE = "metadata.json"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def is_valid_uuid(value: str) -> bool:
    try:
        uuid_lib.UUID(value)
        return True
    except (ValueError, AttributeError, TypeError):
        return False


def load_metadata():
    if not os.path.exists(METADATA_FILE):
        return {}
    with open(METADATA_FILE, "r") as f:
        return json.load(f)


def save_metadata(data):
    with open(METADATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


def set_file_info(uuid: str, filename: str, stored_filename: str, file_hash: str):
    data = load_metadata()
    data[uuid] = {
        "filename": filename,
        "stored_filename": stored_filename,
        "uploaded_at": datetime.now().isoformat(),
        "file_hash": file_hash
    }
    save_metadata(data)


def get_file_info(uuid: str):
    data = load_metadata()
    return data.get(uuid)


def delete_file_info(uuid: str):
    data = load_metadata()
    if uuid in data:
        del data[uuid]
        save_metadata(data)


def filename_exists(filename: str) -> bool:
    data = load_metadata()
    filename_clean = filename.strip().lower()

    for info in data.values():
        if info["filename"].strip().lower() == filename_clean:
            return True

    return False


def calculate_file_hash(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()


def file_hash_exists(file_hash: str):
    """
    اگر یہی File پہلے سے موجود ہو تو اس کی معلومات واپس دیتا ہے، ورنہ None۔
    """
    data = load_metadata()

    for uuid, info in data.items():
        if info.get("file_hash") == file_hash:
            return {"uuid": uuid, "filename": info["filename"]}

    return None