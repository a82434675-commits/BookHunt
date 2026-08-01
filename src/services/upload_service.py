import os
import shutil
import json
from datetime import datetime
from fastapi import UploadFile, HTTPException

UPLOAD_FOLDER = "uploads"
METADATA_FILE = os.path.join(UPLOAD_FOLDER, "metadata.json")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def upload_pdf(uuid: str, file_name: str, file: UploadFile):

    # صرف PDF قبول کریں
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    filename = f"{uuid}.pdf"
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    # Duplicate UUID چیک کریں
    if os.path.exists(filepath):
        raise HTTPException(
            status_code=409,
            detail="UUID already exists."
        )

    # File Save کریں
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Metadata تیار کریں
    metadata = {
        "uuid": uuid,
        "filename": filename,
        "original_filename": file.filename,
        "upload_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "size_bytes": os.path.getsize(filepath)
    }

    # metadata.json بنائیں یا Update کریں
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "r") as f:
            data = json.load(f)
    else:
        data = []

    data.append(metadata)

    with open(METADATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

    return metadata