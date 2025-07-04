from sentence_transformers import SentenceTransformer
import logging
import os

# Setup logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Update this if you use a different folder name for your model
LOCAL_MODEL_PATH = os.path.join(os.path.dirname(__file__), "all-MiniLM-L6-v2")

def initialize_model():
    """Load model from local path inside the Lambda package."""
    try:
        logger.info(f"Loading model from {LOCAL_MODEL_PATH}")
        model = SentenceTransformer(LOCAL_MODEL_PATH)
        return model
    except Exception as e:
        logger.exception(f"Model initialization failed: {str(e)}")
        raise

# Load the model only once
model = initialize_model()

def embed_text_chunks(full_text: str):
    """
    Break the text into chunks, then embed the chunks.
    Returns list of (chunk, embedding) tuples.
    """
    try:
        chunks = split_text_into_chunks(full_text)
        logger.info(f"Split text into {len(chunks)} chunks.")

        embeddings = model.encode(
            chunks,
            batch_size=4,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        return list(zip(chunks, embeddings.tolist()))

    except Exception as e:
        logger.exception(f"Embedding failed: {str(e)}")
        raise

def split_text_into_chunks(text: str, chunk_size: int = 500):
    """
    Splits text into chunks of approximately `chunk_size` characters.
    """
    chunks = []
    current_chunk = []
    current_length = 0

    for line in text.split("\n"):
        line_length = len(line)
        if current_length + line_length <= chunk_size:
            current_chunk.append(line)
            current_length += line_length
        else:
            if current_chunk:
                chunks.append(" ".join(current_chunk))
            current_chunk = [line]
            current_length = line_length

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks
