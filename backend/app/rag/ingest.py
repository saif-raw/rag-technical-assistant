# backend/app/rag/ingest.py
import os
from app.rag.extract_text import extract_text_by_page
from app.rag.chunk import chunk_text
from fastapi import UploadFile
from pathlib import Path

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def save_uploaded_file(file: UploadFile) -> str:
    """
    Saves uploaded file to local disk.
    Returns file path.
    """
    file_path = UPLOAD_DIR / file.filename

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    return str(file_path)

def process_document(file_path: str):
    """
    Full preprocessing pipeline:
    PDF → text → chunks
    """
    pages = extract_text_by_page(file_path)
    chunks = chunk_text(pages)

    return {
        "pages": len(pages),
        "chunks": len(chunks),
        "data": chunks
    }

