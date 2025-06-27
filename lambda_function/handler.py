import json
import logging
from botocore.exceptions import BotoCoreError, ClientError

# Import the pipeline steps
from lambda_function.textract_job import process_textract_job
from lambda_function.embedding_utils import embed_text_chunks
from lambda_function.vector_store import store_embeddings
from lambda_function.response import make_response

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        # 1. Extract plain text from S3 via Textract
        full_text = process_textract_job(event)

  # In lambda_handler
        vectors_and_chunks = embed_text_chunks(full_text)
        logger.info(f"Generated {len(vectors_and_chunks)} embeddings")

# Unpack vectors_and_chunks into chunks and embeddings
        chunks, embeddings = zip(*vectors_and_chunks)  # This separates the chunks and embeddings

# Store them in the vector DB
        store_embeddings(list(chunks), list(embeddings))  # Convert to list because zip returns tuples


        # Return success response
        return make_response(
            200, {"message": "File processed successfully and vectors stored!"}
        )

    except (BotoCoreError, ClientError) as e:
        # Handle AWS service errors more specifically
        logger.exception("AWS error occurred: %s", e)
        return make_response(500, {"error": f"AWS error: {str(e)}"})

    except Exception as e:
        # Catch any other unexpected errors
        logger.exception("Unexpected error occurred: %s", e)
        return make_response(500, {"error": f"Unexpected error: {str(e)}"})
