import json
import logging
from botocore.exceptions import BotoCoreError, ClientError
from lambda_function.textract_job import process_textract_job
from lambda_function.response import make_response

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        result = process_textract_job(event)
        return make_response(200, {"extracted_text": result})

    except (BotoCoreError, ClientError) as e:
        logger.exception("AWS error occurred")
        return make_response(500, f"AWS error: {e}")

    except Exception as e:
        logger.exception("Unexpected error occurred")
        return make_response(500, f"Unexpected error: {e}")
