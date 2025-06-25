import time
import logging
import os
import boto3
from lambda_function.textract_utils import fetch_textract_results

logger = logging.getLogger()
logger.setLevel(logging.INFO)
textract = boto3.client('textract')
POLL_INTERVAL = int(os.environ.get('POLL_INTERVAL', 5))

def process_textract_job(event):
    record = event['Records'][0]
    bucket_name = record['s3']['bucket']['name']
    object_key = record['s3']['object']['key']
    logger.info(f"Processing file: {object_key} in bucket: {bucket_name}")

    # Start Textract job
    response = textract.start_document_text_detection(
        DocumentLocation={'S3Object': {'Bucket': bucket_name, 'Name': object_key}}
    )
    job_id = response['JobId']
    logger.info(f"Started Textract Job: {job_id}")

    # Poll for completion
    status = "IN_PROGRESS"
    while status == "IN_PROGRESS":
        time.sleep(POLL_INTERVAL)
        status = textract.get_document_text_detection(JobId=job_id)['JobStatus']
        logger.info(f"Job status: {status}")

    if status != "SUCCEEDED":
        raise RuntimeError(f"Textract failed with status: {status}")

    return fetch_textract_results(job_id)
