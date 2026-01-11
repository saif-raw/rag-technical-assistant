# backend/app/rag/ingest.py
from pathlib import Path
from fastapi import UploadFile
from app.rag.extract_text import extract_text_by_page
from app.rag.chunk import chunk_text
from app.rag.diagram import extract_and_describe_diagrams
from app.services.embeddings import embed_texts
from app.services.vector_store import FaissVectorStore, INDEX_PATH, META_PATH
from app.services.s3 import upload_file_to_s3
import os

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def save_uploaded_file(file: UploadFile) -> str:
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    return str(file_path)


def process_document(file_path: str):
    file_name = Path(file_path).name
    s3_key = f"manuals/{file_name}"

    # 1. Extract text
    pages = extract_text_by_page(file_path)

    # 2. Extract diagrams (NOW RETURNS LIST OF CHUNKS)
    diagram_chunks = extract_and_describe_diagrams(file_path)

    # 3. Chunk text pages
    text_chunks = chunk_text(pages)

    # 4. Normalize all chunks
    all_chunks = []

    for c in text_chunks:
        all_chunks.append({
            "content": c["content"],
            "file_name": file_name,
            "pdf_page": c["page_number"],
            "s3_key": s3_key,
            "source_type": "text"
        })

    for d in diagram_chunks:
        all_chunks.append({
            "content": d["content"],
            "file_name": file_name,
            "pdf_page": d["pdf_page"],
            "s3_key": s3_key,
            "source_type": "diagram"
        })

    # 5. Embed with Titan
    texts = [c["content"] for c in all_chunks]
    embeddings = embed_texts(texts)

    # 6. Store (LOAD OR CREATE)
    vector_store = FaissVectorStore(dim=embeddings.shape[1])

    # Load existing index if present
    if os.path.exists(INDEX_PATH) and os.path.exists(META_PATH):
        vector_store.load()

    vector_store.add(embeddings, all_chunks)
    vector_store.save()

    # 7. Upload artifacts
    upload_file_to_s3(file_path, s3_key)
    upload_file_to_s3(INDEX_PATH, "index/faiss.index")
    upload_file_to_s3(META_PATH, "index/metadata.pkl")

    return {
        "pages": len(pages),
        "chunks": len(all_chunks),
        "diagrams": len(diagram_chunks)
    }
