from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="app/.env")

    # aws_access_key_id: str
    # aws_secret_access_key: str
    # aws_region: str = "us-east-1"
    rabbitmq_default_user: str
    rabbitmq_default_pass: str
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: str


settings = Settings()
