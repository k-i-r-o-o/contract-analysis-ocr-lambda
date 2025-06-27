from sentence_transformers import SentenceTransformer
import logging

# Load the embedding model once per container lifetime
_model = SentenceTransformer('all-MiniLM-L6-v2')  # A lightweight embedding model

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def embed_text_chunks(full_text: str):
    """
    Break the text into chunks, then embed the chunks.
    This function assumes that the text is already split into chunks.
    It returns a list of embeddings corresponding to each chunk.
    """
    # Split the full text into chunks (here assuming we break by paragraphs or sentences)
    # You can adjust chunking based on the text length, for instance, breaking into chunks of max length
    chunks = split_text_into_chunks(full_text)
    logger.info(f"Split text into {len(chunks)} chunks.")

    # Get embeddings for the chunks
    embeddings = embed_lines(chunks)

    return list(zip(chunks, embeddings))  # Return chunks with corresponding embeddings

def embed_lines(lines):
    """
    Converts a list of lines into embeddings (list of vectors).
    """
    logger.info(f"Generating embeddings for {len(lines)} lines...")
    return _model.encode(lines, show_progress_bar=True).tolist()

def split_text_into_chunks(text, chunk_size=500):
    """
    Splits the extracted full text into smaller chunks based on a defined chunk_size.
    This function can be adjusted based on the use case (e.g., sentence-based, word-based, etc.)
    """
    chunks = []
    current_chunk = []

    for line in text.split("\n"):  # Split by newline to treat each line as a chunk
        if len(" ".join(current_chunk + [line])) <= chunk_size:
            current_chunk.append(line)
        else:
            chunks.append(" ".join(current_chunk))
            current_chunk = [line]  # Start a new chunk

    if current_chunk:
        chunks.append(" ".join(current_chunk))  # Add the last chunk

    return chunks
