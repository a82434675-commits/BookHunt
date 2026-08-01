from fastapi import APIRouter, HTTPException, Form
import os
from pypdf import PdfReader
from src.storage import get_file_info, load_metadata

router = APIRouter(
    prefix="/query",
    tags=["Query PDF"]
)

UPLOAD_FOLDER = "uploads"


def extract_pdf_text(filepath: str) -> str:
    reader = PdfReader(filepath)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


def search_in_text(full_text: str, question: str, context_chars: int = 200):
    keywords = [word.strip(".,?!") for word in question.split() if len(word) > 2]

    results = []
    lower_text = full_text.lower()

    for keyword in keywords:
        keyword_lower = keyword.lower()
        start_index = 0

        while True:
            index = lower_text.find(keyword_lower, start_index)
            if index == -1:
                break

            snippet_start = max(0, index - context_chars)
            snippet_end = min(len(full_text), index + len(keyword) + context_chars)
            snippet = full_text[snippet_start:snippet_end].strip()

            results.append({
                "matched_keyword": keyword,
                "snippet": snippet
            })

            start_index = index + len(keyword)

    return results


@router.post("/{uuid}")
async def query_pdf(uuid: str, question: str = Form(...)):

    info = get_file_info(uuid)

    if not info:
        raise HTTPException(status_code=404, detail="File not found for this UUID")

    filepath = os.path.join(UPLOAD_FOLDER, info["stored_filename"])

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File missing from storage")

    pdf_text = extract_pdf_text(filepath)

    if not pdf_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from this PDF")

    matches = search_in_text(pdf_text, question)

    if not matches:
        return {
            "uuid": uuid,
            "filename": info["filename"],
            "question": question,
            "answer": "No relevant content found.",
            "matches": []
        }

    top_matches = matches[:5]

    return {
        "uuid": uuid,
        "filename": info["filename"],
        "question": question,
        "total_matches": len(matches),
        "matches": top_matches
    }


@router.post("/")
async def query_all_files(question: str = Form(...)):
    data = load_metadata()

    if not data:
        return {
            "question": question,
            "total_files_searched": 0,
            "results": []
        }

    all_results = []

    for uuid, info in data.items():
        filepath = os.path.join(UPLOAD_FOLDER, info["stored_filename"])

        if not os.path.exists(filepath):
            continue

        try:
            pdf_text = extract_pdf_text(filepath)
        except Exception:
            continue

        if not pdf_text.strip():
            continue

        matches = search_in_text(pdf_text, question)

        if matches:
            all_results.append({
                "uuid": uuid,
                "filename": info["filename"],
                "total_matches": len(matches),
                "top_matches": matches[:3]
            })

    return {
        "question": question,
        "total_files_searched": len(data),
        "files_with_matches": len(all_results),
        "results": all_results
    }