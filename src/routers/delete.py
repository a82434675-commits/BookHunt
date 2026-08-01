from fastapi import APIRouter, HTTPException
import os
from src.storage import get_file_info, delete_file_info

router = APIRouter(
    prefix="/delete",
    tags=["Delete PDF"]
)

UPLOAD_FOLDER = "uploads"


@router.delete("/{uuid}")
def delete_file(uuid: str):
    info = get_file_info(uuid)

    if not info:
        raise HTTPException(status_code=404, detail="File not found for this UUID")

    filepath = os.path.join(UPLOAD_FOLDER, info["stored_filename"])

    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except PermissionError:
            raise HTTPException(
                status_code=423,
                detail="File is open elsewhere, please close it first"
            )

    delete_file_info(uuid)

    return {
        "message": "File deleted successfully",
        "uuid": uuid,
        "filename": info["filename"]
    }