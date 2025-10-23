from functools import lru_cache
from pydantic import BaseSettings, AnyUrl


class Settings(BaseSettings):
    database_url: AnyUrl = 'postgresql+asyncpg://postgres:postgres@postgres:5432/aion'
    redis_url: str = 'redis://redis:6379/0'
    qdrant_url: str = 'http://qdrant:6333'
    minio_endpoint: str = 'minio:9000'
    minio_access_key: str = 'minioadmin'
    minio_secret_key: str = 'minioadmin'
    gateway_url: AnyUrl = 'http://gateway:8080'
    bridge_token: str = 'bridge-secret'
    openai_api_key: str | None = None
    router_model: str = 'gpt-3.5-turbo'
    grpc_endpoint: str = 'http://execution:50051'

    class Config:
        env_prefix = 'CONTROL_'
        env_file = '.env'


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
