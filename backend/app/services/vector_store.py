# backend/app/services/vector_store.py
import faiss
import pickle
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

os.makedirs(DATA_DIR, exist_ok=True)

INDEX_PATH = os.path.join(DATA_DIR, "faiss.index")
META_PATH = os.path.join(DATA_DIR, "metadata.pkl")

class FaissVectorStore:
    def __init__(self, dim: int):
        self.dim = dim
        self.index = faiss.IndexFlatL2(dim)
        self.metadata = []

    def add(self, vectors: np.ndarray, metadatas: list):
        self.index.add(vectors)
        self.metadata.extend(metadatas)

    def save(self):
        faiss.write_index(self.index, INDEX_PATH)
        with open(META_PATH, "wb") as f:
            pickle.dump(self.metadata, f)

    def load(self):
        if os.path.exists(INDEX_PATH):
            self.index = faiss.read_index(INDEX_PATH)
        if os.path.exists(META_PATH):
            with open(META_PATH, "rb") as f:
                self.metadata = pickle.load(f)

    def search(self, query_vector, top_k=5):
        if self.index.ntotal == 0:
            return []

        _, indices = self.index.search(query_vector, top_k)
        results = []

        for idx in indices[0]:
            if idx < len(self.metadata):
                results.append(self.metadata[idx])

        unique = {}
        for r in results:
            key = (r["file_name"], r["pdf_page"], r["source_type"])
            if key not in unique:
                unique[key] = r

        return list(unique.values())

