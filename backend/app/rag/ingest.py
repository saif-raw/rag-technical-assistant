# backend/app/rag/ingest.py
import os
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
