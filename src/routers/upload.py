from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import os
import shutil
from src.storage import (
    set_file_info,
    is_valid_uuid,
    filename_exists,
    calculate_file_hash,
    file_hash_exists
)

router = APIRouter(
    prefix="/upload",
    tags=["Upload PDF"]
)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@router.post("/{uuid}")
async def upload_pdf(
    uuid: str,
    filename: str = Form(...),
    file: UploadFile = File(...)
):
    if not is_valid_uuid(uuid):
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    if not filename.strip():
        raise HTTPException(status_code=400, detail="File name cannot be empty")

    if filename_exists(filename):
        raise HTTPException(status_code=409, detail="A file with this name already exists")

    extension = os.path.splitext(file.filename)[1].lower()

    if extension != ".pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    # File کا Content پڑھ کر Hash نکالیں
    file_bytes = await file.read()
    file_hash = calculate_file_hash(file_bytes)

    existing = file_hash_exists(file_hash)
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"This file already exists (uploaded as \"{existing['filename']}\")"
        )

    stored_filename = f"{uuid}{extension}"
    filepath = os.path.join(UPLOAD_FOLDER, stored_filename)

    with open(filepath, "wb") as buffer:
        buffer.write(file_bytes)

    set_file_info(uuid, filename, stored_filename, file_hash)

    return {
        "message": "PDF uploaded successfully",
        "uuid": uuid,
        "filename": filename,
        "stored_as": stored_filename
    }