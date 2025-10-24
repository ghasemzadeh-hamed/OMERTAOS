from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='allow')

    postgres_url: str = 'postgresql+asyncpg://aion:aion@localhost:5432/aion'
    redis_url: str = 'redis://localhost:6379/0'
    jwt_secret: str = 'changeme'
    execution_endpoint: str = 'http://localhost:50051'
    openai_api_key: str | None = None
    ollama_url: str | None = 'http://localhost:11434'


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
