import boto3
textract = boto3.client('textract')

def fetch_textract_results(job_id):
    pages = []
    next_token = None
    while True:
        result = textract.get_document_text_detection(
            JobId=job_id, NextToken=next_token
        ) if next_token else textract.get_document_text_detection(JobId=job_id)

        for block in result.get('Blocks', []):
            if block['BlockType'] == 'LINE':
                pages.append(block['Text'])

        next_token = result.get('NextToken')
        if not next_token:
            break
    return "\n".join(pages)
