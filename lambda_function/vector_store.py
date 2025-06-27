from pinecone import Pinecone, ServerlessSpec, CloudProvider, AwsRegion
import uuid, logging
from typing import List
import numpy as np

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize Pinecone client
pc = Pinecone(api_key="pcsk_7Qjc5T_RLANSDE11Y4G9bs3jhRpR1CQwwz2x8yQcCfZ8vBcXiV24oCbTYBeFm42Zq2Xck6")


index_name = "contract-analysis"
dimension = 384  # for all-MiniLM-L6-v2

# Create index if missing
if not pc.has_index(name=index_name):
    pc.create_index(
        name=index_name,
        dimension=dimension,
        spec=ServerlessSpec(cloud=CloudProvider.AWS, region=AwsRegion.US_EAST_1)
    )

# Get host via describe_index and instantiate Index
idx_desc = pc.describe_index(name=index_name)
index = pc.Index(host=idx_desc.host)

def store_embeddings(chunks: List[str], embeddings: List[List[float]]):
    if len(chunks) != len(embeddings):
        raise ValueError("Mismatched chunks and embeddings length")

    ids = [str(uuid.uuid4()) for _ in chunks]
    embs = np.array(embeddings, dtype="float32")
    vectors = [(ids[i], embs[i].tolist(), {"text": chunks[i]}) for i in range(len(ids))]
    index.upsert(vectors=vectors)
    logger.info(f"Stored {len(chunks)} embeddings")

def search_embeddings(query_embedding: List[float], top_k: int = 5):
    q = np.array(query_embedding, dtype="float32").tolist()
    resp = index.query(vector=q, top_k=top_k, include_metadata=True)
    return resp["matches"]
