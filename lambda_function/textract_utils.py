import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

textract = boto3.client('textract')

def fetch_textract_results(job_id: str) -> str:
    """Paginate through all Textract results and return plain text as one string."""
    pages = []
    next_token = None

    try:
        while True:
            resp = textract.get_document_text_detection(JobId=job_id, NextToken=next_token) \
                   if next_token else textract.get_document_text_detection(JobId=job_id)

            for block in resp.get('Blocks', []):
                if block['BlockType'] == 'LINE':
                    pages.append(block['Text'])

            next_token = resp.get('NextToken')
            if not next_token:
                break

        full_text = "\n".join(pages)
        logger.info(f"Fetched {len(pages)} lines. Total characters={len(full_text)}")
        return full_text

    except Exception as e:
        logger.exception(f"Error fetching Textract results: {str(e)}")
        raise
