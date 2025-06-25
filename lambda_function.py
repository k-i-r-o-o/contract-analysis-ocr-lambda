import json
import os
import time
import logging
import boto3
from botocore.exceptions import BotoCoreError, ClientError

# Configure logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Constants
POLL_INTERVAL = int(os.environ.get('POLL_INTERVAL', 5))  # adjustable via env var

# Clients
textract = boto3.client('textract')
s3 = boto3.client('s3')


def lambda_handler(event, context):
    try:
        # Get S3 bucket & object key
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

        # Poll job status
        status = "IN_PROGRESS"
        while status == "IN_PROGRESS":
            time.sleep(POLL_INTERVAL)
            result = textract.get_document_text_detection(JobId=job_id)
            status = result['JobStatus']
            logger.info(f"Job status: {status}")

        if status != "SUCCEEDED":
            logger.error(f"Textract failed with status: {status}")
            return _response(500, f"Textract failed with status: {status}")

        # Fetch all pages
        full_text = _fetch_textract_results(job_id)
        logger.info(f"Extracted text length: {len(full_text)} chars")

        return _response(200, {"extracted_text": full_text})

    except (BotoCoreError, ClientError) as e:
        logger.exception("AWS error occurred")
        return _response(500, f"AWS error: {e}")

    except Exception as e:
        logger.exception("Unexpected error occurred")
        return _response(500, f"Unexpected error: {e}")


def _fetch_textract_results(job_id):
    """Fetch all pages of the Textract job results."""
    pages = []
    next_token = None
    while True:
        result = textract.get_document_text_detection(
            JobId=job_id,
            NextToken=next_token
        ) if next_token else textract.get_document_text_detection(JobId=job_id)

        for block in result.get('Blocks', []):
            if block['BlockType'] == 'LINE':
                pages.append(block['Text'])

        next_token = result.get('NextToken')
        if not next_token:
            break

    return "\n".join(pages)


def _response(status_code, body):
    """Helper to format API Gateway-style responses."""
    return {
        "statusCode": status_code,
        "body": json.dumps(body)
    }


# Local test only
# if __name__ == "__main__":
#     with open('test_event.json') as f:
#         event = json.load(f)
#     print(lambda_handler(event, None))
