# backend/app/services/bedrock.py
import os
import boto3

AWS_REGION = os.getenv("AWS_REGION")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID")
EMBEDDING_MODEL_ID = os.getenv("EMBEDDING_MODEL_ID")


def get_bedrock_client():
    """
    Centralized Bedrock client.
    IAM auth only. No hardcoded credentials.
    """
    return boto3.client(
        service_name="bedrock-runtime",
        region_name=AWS_REGION
    )
