# backend/app/services/embeddings.py
from .bedrock import get_bedrock_client
import json
import os

EMBEDDING_MODEL_ID = os.getenv("EMBEDDING_MODEL_ID")


def generate_embedding(text: str) -> list:
    """
    Generates vector embedding for a given text.
    Actual call will be added later.
    """
    if not text:
        raise ValueError("Text cannot be empty")

    # Placeholder for now
    return []
