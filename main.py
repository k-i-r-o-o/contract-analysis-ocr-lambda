# main.py
import json
import logging
import boto3
from lambda_function.handler import lambda_handler

logging.basicConfig(level=logging.INFO)

BUCKET_NAME = "contract-upload-bucket-mvp"       # Update with your bucket name
PREFIX = ""                              # Optionally set a prefix
REGION = "us-east-1"                     # Your bucket’s region

def get_latest_s3_object(bucket: str, prefix: str = "") -> dict:
    """Retrieve the key and metadata of the most recently uploaded S3 object."""
    client = boto3.client("s3", region_name=REGION)
    paginator = client.get_paginator('list_objects_v2')
    page_iter = paginator.paginate(Bucket=bucket, Prefix=prefix)

    latest = None
    for page in page_iter:
        for obj in page.get("Contents", []):
            if latest is None or obj['LastModified'] > latest['LastModified']:
                latest = obj

    if not latest:
        raise RuntimeError("No objects found in S3 bucket.")
    return latest

def build_s3_event(bucket: str, key: str) -> dict:
    """Construct a Lambda-style S3 ‘ObjectCreated’ event."""
    return {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": bucket},
                    "object": {"key": key}
                }
            }
        ]
    }

def main():
    logging.info("Fetching the latest S3 object...")
    obj = get_latest_s3_object(BUCKET_NAME, PREFIX)
    logging.info(f"Latest key: {obj['Key']} (at {obj['LastModified']})")

    event = build_s3_event(BUCKET_NAME, obj['Key'])
    response = lambda_handler(event, None)

    print("Handler response:")
    print(response)

if __name__ == "__main__":
    main()
