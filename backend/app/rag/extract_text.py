# backend/app/rag/extract_text.py
import pdfplumber
from typing import List, Dict


def extract_text_by_page(pdf_path: str) -> List[Dict]:
    """
    Extracts text from each page of a PDF.
    Returns structured page-level content.
    """
    pages = []

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            pages.append({
                "page_number": i + 1,
                "text": text.strip()
            })

    return pages
