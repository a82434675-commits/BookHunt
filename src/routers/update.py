from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import os
import shutil
from src.storage import set_file_info, get_file_info, is_valid_uuid

router = APIRouter(
    prefix="/update",
    tags=["Update PDF"]
)

UPLOAD_FOLDER = "uploads"


@router.put("/{uuid}")
async def update_file(
    uuid: str,
    filename: str = Form(...),
    file: UploadFile = File(...)
):
    if not is_valid_uuid(uuid):
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    info = get_file_info(uuid)

    if not info:
        raise HTTPException(status_code=404, detail="File not found for this UUID")

    extension = os.path.splitext(file.filename)[1].lower()

    if extension != ".pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    old_path = os.path.join(UPLOAD_FOLDER, info["stored_filename"])
    if os.path.exists(old_path):
        os.remove(old_path)

    stored_filename = f"{uuid}{extension}"
    filepath = os.path.join(UPLOAD_FOLDER, stored_filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    set_file_info(uuid, filename, stored_filename)

    return {
        "message": "File updated successfully",
        "uuid": uuid,
        "filename": filename,
        "stored_as": stored_filename
    }