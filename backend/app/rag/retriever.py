# backend/app/rag/retriever.py

from app.services.embeddings import embed_texts
from app.services.vector_store import FaissVectorStore, INDEX_PATH, META_PATH
from app.services.s3 import download_file, file_exists
import os

_VECTOR_STORE = None


# backend/app/rag/retriever.py - Update _load_vector_store

def _load_vector_store():
    global _VECTOR_STORE
    if _VECTOR_STORE is not None:
        return _VECTOR_STORE

    # Check local disk first - only download if missing
    if not os.path.exists(INDEX_PATH) or not os.path.exists(META_PATH):
        print("Index not found locally. Syncing from S3...")
        if not file_exists("index/faiss.index"):
            return None
        download_file("index/faiss.index", INDEX_PATH)
        download_file("index/metadata.pkl", META_PATH)

    store = FaissVectorStore(dim=768)
    store.load()
    _VECTOR_STORE = store
    return store


def retrieve_context(query: str, top_k: int = 12):
    vector_store = _load_vector_store()
    if not vector_store:
        return []

    query_embedding = embed_texts([query])
    raw_results = vector_store.search(query_embedding, top_k=top_k)

    query_lower = query.lower()
    wants_diagram = any(k in query_lower for k in [
        "diagram", "figure", "schematic", "layout", "drawing", "curve"
    ])

    text_chunks = [r for r in raw_results if r["source_type"] == "text"]
    diagram_chunks = [r for r in raw_results if r["source_type"] == "diagram"]

    selected = []

    # Always include diagrams if requested
    if wants_diagram and diagram_chunks:
        selected.extend(diagram_chunks[:2])

    # Then include best text chunks
    for r in text_chunks:
        if len(selected) >= 4:
            break
        selected.append(r)

    return selected