from sentence_transformers import SentenceTransformer
import logging
import os

# Setup logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Define model path (use /tmp for Lambda environment)
MODEL_PATH = os.getenv('MODEL_PATH', '/tmp/all-MiniLM-L6-v2')

# Print out the model path to ensure it's correct
logger.info(f"Trying to load model from: {MODEL_PATH}")

# Check if model is already available in the /tmp directory
if not os.path.exists(MODEL_PATH):
    logger.info(f"Model not found at {MODEL_PATH}, downloading and saving it.")
    
    try:
        # Load the model from Hugging Face and save it to /tmp directory
        model = SentenceTransformer('all-MiniLM-L6-v2')
        model.save(MODEL_PATH)  # Save model to /tmp directory
        logger.info(f"Model downloaded and saved to {MODEL_PATH}")
    except Exception as e:
        logger.exception(f"Failed to download and save model to {MODEL_PATH}: {str(e)}")
        raise

# Now load the model from the local path
try:
    logger.info(f"Loading embedding model from: {MODEL_PATH}")
    _model = SentenceTransformer(MODEL_PATH)
    logger.info("Model loaded successfully.")
except Exception as e:
    logger.exception(f"Failed to load model from {MODEL_PATH}: {str(e)}")
    raise

def embed_text_chunks(full_text: str):
    """
    Break the text into chunks, then embed the chunks.
    This function assumes that the text is already split into chunks.
    It returns a list of embeddings corresponding to each chunk.
    """
    chunks = split_text_into_chunks(full_text)
    logger.info(f"Split text into {len(chunks)} chunks.")
    embeddings = embed_lines(chunks)
    return list(zip(chunks, embeddings))

def embed_lines(lines):
    """
    Converts a list of lines into embeddings (list of vectors).
    """
    logger.info(f"Generating embeddings for {len(lines)} lines...")
    return _model.encode(lines, show_progress_bar=True).tolist()

def split_text_into_chunks(text, chunk_size=500):
    """
    Splits the extracted full text into smaller chunks based on a defined chunk_size.
    """
    chunks = []
    current_chunk = []

    for line in text.split("\n"):
        if len(" ".join(current_chunk + [line])) <= chunk_size:
            current_chunk.append(line)
        else:
            chunks.append(" ".join(current_chunk))
            current_chunk = [line]

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks
