from fastapi import APIRouter, HTTPException
import os
from src.storage import load_metadata, get_file_info

router = APIRouter(
    prefix="/files",
    tags=["Files"]
)

UPLOAD_FOLDER = "uploads"


@router.get("/")
def list_files():
    data = load_metadata()

    files = []
    for uuid, info in data.items():
        filepath = os.path.join(UPLOAD_FOLDER, info["stored_filename"])
        file_size = os.path.getsize(filepath) if os.path.exists(filepath) else None

        files.append({
            "uuid": uuid,
            "filename": info["filename"],
            "uploaded_at": info.get("uploaded_at"),
            "file_size_bytes": file_size
        })

    # سب سے نئی File سب سے اوپر
    files.sort(key=lambda f: f["uploaded_at"] or "", reverse=True)

    return {
        "total_files": len(files),
        "files": files
    }


@router.get("/{uuid}")
def get_file_details(uuid: str):
    info = get_file_info(uuid)

    if not info:
        raise HTTPException(status_code=404, detail="File not found for this UUID")

    filepath = os.path.join(UPLOAD_FOLDER, info["stored_filename"])

    file_size = None
    if os.path.exists(filepath):
        file_size = os.path.getsize(filepath)

    return {
        "uuid": uuid,
        "filename": info["filename"],
        "uploaded_at": info.get("uploaded_at"),
        "file_size_bytes": file_size,
        "exists_on_disk": os.path.exists(filepath)
    }