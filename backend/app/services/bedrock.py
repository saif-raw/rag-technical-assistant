# backend/app/services/bedrock.py

import boto3
import os
from dotenv import load_dotenv

load_dotenv()

bedrock = boto3.client(
    "bedrock-runtime",
    region_name=os.getenv("AWS_REGION", "us-east-1")
)

MODEL_ID = os.getenv("BEDROCK_MODEL_ID")
#print(">>> BEDROCK_MODEL_ID =", MODEL_ID)


def invoke_llm(prompt: str) -> str:
    """
    Non-streaming invocation (used by /ask).
    """
    if not MODEL_ID:
        raise RuntimeError("BEDROCK_MODEL_ID is not set")

    response = bedrock.converse(
        modelId=MODEL_ID,
        messages=[
            {
                "role": "user",
                "content": [{"text": prompt}],
            }
        ],
        inferenceConfig={
            "temperature": 0.2,
            "maxTokens": 512,
            "topP": 0.9,
        },
    )

    return response["output"]["message"]["content"][0]["text"]


def stream_llm(prompt: str):
    """
    Streaming invocation (used by /ask/stream).
    """
    if not MODEL_ID:
        raise RuntimeError("BEDROCK_MODEL_ID is not set")

    response = bedrock.converse_stream(
        modelId=MODEL_ID,
        messages=[
            {
                "role": "user",
                "content": [{"text": prompt}],
            }
        ],
        inferenceConfig={
            "temperature": 0.2,
            "maxTokens": 512,
            "topP": 0.9,
        },
    )

    for event in response["stream"]:
        if "contentBlockDelta" in event:
            delta = event["contentBlockDelta"]["delta"]
            if "text" in delta:
                yield delta["text"]
