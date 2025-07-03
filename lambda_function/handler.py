import os
import tempfile
import boto3
import logging
from lambda_function.pdf_text_extractor import extract_text_from_pdf
from lambda_function.embedding_utils import embed_text_chunks
from lambda_function.vector_store import store_embeddings
from lambda_function.response import make_response

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client("s3")

def lambda_handler(event, context=None):
    try:
        # Extract bucket and key from S3 event
        record = event["Records"][0]
        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]

        logger.info(f"Received S3 event for bucket: {bucket}, key: {key}")

        # Download the file to a temp location
        with tempfile.TemporaryDirectory() as tmpdirname:
            local_path = os.path.join(tmpdirname, os.path.basename(key))
            s3_client.download_file(bucket, key, local_path)
            logger.info(f"Downloaded file to {local_path}")

            # Extract text from PDF
            full_text = extract_text_from_pdf(local_path)
            logger.info(f"Extracted {len(full_text)} characters from PDF")

            # Embed and store
            vectors_and_chunks = embed_text_chunks(full_text)
            logger.info(f"Generated {len(vectors_and_chunks)} embeddings")

            chunks, embeddings = zip(*vectors_and_chunks)
            store_embeddings(list(chunks), list(embeddings))

        return make_response(
            200, {"message": f"Processed {key} successfully and stored vectors!"}
        )

    except Exception as e:
        logger.exception("Error processing file:")
        return make_response(500, {"error": str(e)})
