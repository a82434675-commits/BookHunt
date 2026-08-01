from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
from src.storage import get_file_info

router = APIRouter(
    prefix="/download",
    tags=["Download PDF"]
)

UPLOAD_FOLDER = "uploads"


@router.get("/{uuid}")
def download_file(uuid: str):
    info = get_file_info(uuid)

    if not info:
        raise HTTPException(status_code=404, detail="File not found for this UUID")

    filepath = os.path.join(UPLOAD_FOLDER, info["stored_filename"])

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File missing from storage")

    return FileResponse(
        path=filepath,
        media_type="application/pdf",
        filename=f"{info['filename']}.pdf"
    )