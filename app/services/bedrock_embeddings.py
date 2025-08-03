from typing import List, Optional

import boto3
import cohere_aws

from config.config import settings

REGION_NAME = settings.aws_region
EMBEDDINGS_MODEL = settings.aws_embeddings_model
BATCH_SIZE = 96
RERANK_MODEL = settings.aws_rerank_model
RERANK_REGION_NAME = settings.aws_rerank_region
MAX_CHUNKS_RERANKED = settings.max_chunks_reranked


RERANK_MODEL_ARN = (
    f"arn:aws:bedrock:{RERANK_REGION_NAME}::foundation-model/{RERANK_MODEL}"
)

client = cohere_aws.Client(mode=cohere_aws.Mode.BEDROCK, region_name=REGION_NAME)
rerank_client = boto3.client('bedrock-agent-runtime', region_name=RERANK_REGION_NAME)


def embed_texts(texts: List[str], batch_size: Optional[int] = BATCH_SIZE):
    """Embed a list of texts."""
    # Max length allowed by embeddings model
    MAX_LENGTH = 2048
    texts = [t[:MAX_LENGTH] for t in texts]
    n = max(1, batch_size)
    batches = [texts[i : i + n] for i in range(0, len(texts), n)]
    embeddings = []
    for batch in batches:
        batch_embeddings = embed_batch(batch)
        embeddings.extend(batch_embeddings)
    return embeddings


def embed_batch(batch: List[str]):
    """Embed a batch of texts."""
    doc_embs = client.embed(
        texts=batch, model_id=EMBEDDINGS_MODEL, input_type='search_document'
    ).embeddings
    return doc_embs


def embed_query(text: str):
    """Embed a query."""
    texts = [text[:2048]]
    query_embs = client.embed(
        texts=texts, model_id=EMBEDDINGS_MODEL, input_type='search_query'
    ).embeddings
    return query_embs


def rerank_texts(query, texts, limit: Optional[int] = MAX_CHUNKS_RERANKED):
    """Rerank a list of texts."""
    print(f"Reranking {len(texts)} texts with limit {limit}")
    if len(texts) < limit:
        limit = len(texts)
    text_sources = []
    for text in texts:
        text_sources.append(
            {
                'type': 'INLINE',
                'inlineDocumentSource': {
                    'type': 'TEXT',
                    'textDocument': {
                        'text': text,
                    },
                },
            }
        )
    response = rerank(query, text_sources, limit)
    results = [{"index": r["index"], "score": r["relevanceScore"]} for r in response]
    return results


def rerank(text_query, text_sources, num_results):
    """Rerank a list of texts."""
    response = rerank_client.rerank(
        queries=[{'type': 'TEXT', 'textQuery': {'text': text_query}}],
        sources=text_sources,
        rerankingConfiguration={
            'type': 'BEDROCK_RERANKING_MODEL',
            'bedrockRerankingConfiguration': {
                'numberOfResults': num_results,
                'modelConfiguration': {
                    'modelArn': RERANK_MODEL_ARN,
                },
            },
        },
    )
    return response['results']
