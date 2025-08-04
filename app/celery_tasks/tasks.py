import uuid

from services.bedrock_embeddings import embed_texts
from services.chunking import extract_content_from_url, flatten_markdown_chunks
from services.qdrant import store_points

from .worker import app


@app.task
def process_documentation_task(url: str, chat_id: str):
    """Task to process documentation."""
    sections = extract_content_from_url(url)
    chunks = flatten_markdown_chunks(sections, max_length=1024)
    texts = [chunk["content"] for chunk in chunks]
    vectors = embed_texts(texts)
    ids = [str(uuid.uuid4()) for _ in chunks]
    payloads = [
        {"text": chunk["content"], "url": url, "chat_id": chat_id} for chunk in chunks
    ]
    n_documents = store_points(ids, payloads, vectors)
    print(f"Indexed {n_documents}")
