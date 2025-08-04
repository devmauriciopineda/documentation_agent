from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="app/.env")

    # aws
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str
    aws_embeddings_model: str
    aws_rerank_model: str
    aws_rerank_region: str

    # Google
    google_api_key: str

    # Inference config
    llm_name: str
    temperature: float
    tokens: int

    # Qdrant
    collection_name: str
    qdrant_url: str

    # Rag config
    max_chunks_retrieved: int
    max_chunks_reranked: int
    default_chunk_size: int
    default_chunk_overlap: int

    # Rabbit
    rabbitmq_default_user: str
    rabbitmq_default_pass: str

    # Postgres
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: str


settings = Settings()
