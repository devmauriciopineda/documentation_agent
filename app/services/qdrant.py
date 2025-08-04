from typing import Optional

from qdrant_client import QdrantClient, models

from app.config.config import settings

URL_QDRANT = settings.qdrant_url
client = QdrantClient(
    URL_QDRANT,
    port=6333,
    grpc_port=6334,
    timeout=30,
)
COLLECTION_NAME = settings.collection_name
MAX_CHUNKS_RETRIEVED = settings.max_chunks_retrieved


def store_points(ids, payloads, vectors):
    """Store points in the Qdrant collection."""
    length = len(ids)
    BATCH_SIZE = 2000
    start = 0
    while start < length:
        end = min(start + BATCH_SIZE, length)
        batch_ids = ids[start:end]
        batch_payloads = payloads[start:end]
        batch_vectors = vectors[start:end]
        store_batch_of_points(batch_ids, batch_payloads, batch_vectors)
        start += BATCH_SIZE


def store_batch_of_points(ids, payloads, vectors):
    """Store a batch of points in the Qdrant collection."""
    points = client.upsert(
        collection_name=COLLECTION_NAME,
        points=models.Batch(
            ids=ids,
            payloads=payloads,
            vectors=vectors,
        ),
    )
    return points


def search(query_vector, filter, limit: Optional[int] = MAX_CHUNKS_RETRIEVED):
    """Search for points in the Qdrant collection."""
    hits = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        query_filter=filter,
        limit=limit,
    )
    points = hits.points
    return points


def filter_by_chat_id(chat_id: str) -> models.Filter:
    """Create a filter for the specified chat."""
    return models.Filter(
        must=[
            models.FieldCondition(
                key="chat_id",
                match=models.MatchValue(
                    value=chat_id,
                ),
            )
        ]
    )
