from fastapi import APIRouter, HTTPException, Form
from src.storage import get_file_info, load_metadata, save_metadata

router = APIRouter(
    prefix="/rename",
    tags=["Rename PDF"]
)


@router.patch("/{uuid}")
def rename_file(uuid: str, filename: str = Form(...)):
    info = get_file_info(uuid)

    if not info:
        raise HTTPException(status_code=404, detail="File not found for this UUID")

    if not filename.strip():
        raise HTTPException(status_code=400, detail="File name cannot be empty")

    data = load_metadata()
    data[uuid]["filename"] = filename
    save_metadata(data)

    return {
        "message": "File renamed successfully",
        "uuid": uuid,
        "filename": filename
    }