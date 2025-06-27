import time
import logging
import os
import boto3
from lambda_function.textract_utils import fetch_textract_results

logger = logging.getLogger()
logger.setLevel(logging.INFO)

textract = boto3.client('textract')
POLL_INTERVAL = int(os.environ.get('POLL_INTERVAL', 5))  # configurable via env

def process_textract_job(event):
    try:
        # Get S3 file info
        record = event['Records'][0]
        bucket_name = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']
        logger.info(f"Processing file: {object_key} in bucket: {bucket_name}")

        # Start async Textract OCR job
        response = textract.start_document_text_detection(
            DocumentLocation={'S3Object': {'Bucket': bucket_name, 'Name': object_key}}
        )
        job_id = response['JobId']
        logger.info(f"Started Textract job with ID: {job_id}")

        # Poll Textract until completed
        status = "IN_PROGRESS"
        while status == "IN_PROGRESS":
            logger.info(f"Waiting {POLL_INTERVAL}s for job {job_id}...")
            time.sleep(POLL_INTERVAL)
            status = textract.get_document_text_detection(JobId=job_id)['JobStatus']
            logger.info(f"Textract job status: {status}")

        if status != "SUCCEEDED":
            logger.error(f"Textract job {job_id} failed with status: {status}")
            raise RuntimeError(f"Textract failed with status: {status}")

        # Fetch all results
        full_text = fetch_textract_results(job_id)
        logger.info(f"Extracted text length: {len(full_text)} characters")
        return full_text

    except Exception as e:
        logger.exception(f"Error during Textract job processing: {str(e)}")
        raise
