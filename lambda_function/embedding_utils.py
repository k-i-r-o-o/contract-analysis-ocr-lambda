from sentence_transformers import SentenceTransformer
import logging
import os
from pathlib import Path

# Setup logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Lambda-specific configuration
MODEL_NAME = 'all-MiniLM-L6-v2'
MODEL_CACHE_DIR = '/tmp/sentence_transformers'

def initialize_model():
    """Initialize model with Lambda-optimized caching"""
    try:
        # Configure cache directory
        os.makedirs(MODEL_CACHE_DIR, exist_ok=True)
        os.environ['SENTENCE_TRANSFORMERS_HOME'] = MODEL_CACHE_DIR
        
        logger.info(f"Loading model {MODEL_NAME}...")
        return SentenceTransformer(MODEL_NAME)
    except Exception as e:
        logger.exception(f"Model initialization failed: {str(e)}")
        raise

# Global model instance (persists across warm starts)
model = initialize_model()

def embed_text_chunks(full_text: str):
    """
    Break the text into chunks, then embed the chunks.
    Returns list of (chunk, embedding) tuples.
    """
    try:
        chunks = split_text_into_chunks(full_text)
        logger.info(f"Split text into {len(chunks)} chunks.")
        
        # Generate embeddings with Lambda-optimized settings
        embeddings = model.encode(
            chunks,
            batch_size=4,  # Conservative for Lambda memory
            show_progress_bar=False,  # Disabled for Lambda
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        
        return list(zip(chunks, embeddings.tolist()))  # Convert to list for JSON serialization
        
    except Exception as e:
        logger.exception(f"Embedding failed: {str(e)}")
        raise

def split_text_into_chunks(text: str, chunk_size: int = 500):
    """
    Splits text into chunks of approximately chunk_size characters.
    More memory-efficient implementation.
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