from config.config import settings
from services.bedrock_embeddings import embed_query, rerank_texts
from services.qdrant import filter_by_chat_id, search

MAX_CHUNKS_RETRIEVED = settings.max_chunks_retrieved
MAX_CHUNKS_RERANKED = settings.max_chunks_reranked


def search_in_docs(query, chat_id):
    """Search for the question in the documentation."""
    query_vector = embed_query(query)[0]
    query_filter = filter_by_chat_id(chat_id)
    points = search(
        query_vector,
        query_filter,
        MAX_CHUNKS_RETRIEVED,
    )
    print(f"Found {len(points)} points")
    try:
        texts = [point.payload["text"] for point in points]
        reranked = rerank_texts(query, texts, MAX_CHUNKS_RERANKED)
        points = [points[r["index"]] for r in reranked]
        return points
    except Exception as e:
        return points
