# backend/app/rag/chunk.py
from typing import List, Dict

CHUNK_SIZE = 800      # characters
CHUNK_OVERLAP = 150  # characters


def chunk_text(pages: List[Dict]) -> List[Dict]:
    """
    Converts page-level text into overlapping chunks.
    """
    chunks = []

    for page in pages:
        text = page["text"]
        page_number = page["page_number"]

        start = 0
        while start < len(text):
            end = start + CHUNK_SIZE
            chunk_text = text[start:end]

            chunks.append({
                "page_number": page_number,
                "content": chunk_text.strip()
            })

            start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks
