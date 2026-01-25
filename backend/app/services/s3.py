from botocore.config import Config
import boto3
import os
from botocore.exceptions import ClientError

def get_s3_client():
    """
    Standardized S3 client for consistent signatures.
    """
    region = os.getenv("AWS_REGION", "us-east-1")
    return boto3.client(
        "s3",
        region_name=region,
        config=Config(
            signature_version="s3v4",
            s3={"addressing_style": "virtual"}
        )
    )

def get_bucket_name():
    bucket = os.getenv("S3_BUCKET_NAME")
    if not bucket:
        raise RuntimeError("S3_BUCKET_NAME is not set in environment.")
    return bucket

def generate_presigned_pdf_url(file_name: str, page: int, expires_in: int = 3600):
    try:
        s3_client = boto3.client("s3", region_name="us-east-1")
        key = f"manuals/{file_name}" 
        url = s3_client.generate_presigned_url(
            ClientMethod="get_object",
            Params={
                "Bucket": "rag-technical-assistant-manuals",
                "Key": key,
                "ResponseContentType": "application/pdf",
                "ResponseContentDisposition": "inline",
            },
            ExpiresIn=expires_in,
        )

        return f"{url}#page={int(page)}"

    except Exception as e:
        print(f"CRITICAL S3 ERROR: {e}")
        return "#"

def upload_file_to_s3(local_path: str, s3_key: str):
    if not os.path.exists(local_path):
        raise FileNotFoundError(f"{local_path} does not exist")

    s3 = get_s3_client()
    bucket = get_bucket_name()
    s3.upload_file(local_path, bucket, s3_key)
    return f"s3://{bucket}/{s3_key}"

def download_file(s3_key: str, local_path: str):
    s3 = get_s3_client()
    bucket = get_bucket_name()
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    s3.download_file(bucket, s3_key, local_path)
    return local_path

def file_exists(s3_key: str) -> bool:
    s3 = get_s3_client()
    bucket = get_bucket_name()
    try:
        s3.head_object(Bucket=bucket, Key=s3_key)
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        raise