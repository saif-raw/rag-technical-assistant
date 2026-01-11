# backend/app/services/embeddings.py
import boto3
import json
import numpy as np

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

EMBEDDING_MODEL_ID = "amazon.titan-embed-text-v1"


def embed_texts(texts):
    """
    Generate embeddings for a list of texts using Titan.
    """
    embeddings = []

    for text in texts:
        body = json.dumps({
            "inputText": text
        })

        response = bedrock.invoke_model(
            modelId=EMBEDDING_MODEL_ID,
            body=body
        )

        result = json.loads(response["body"].read())
        embeddings.append(result["embedding"])

    return np.array(embeddings).astype("float32")
