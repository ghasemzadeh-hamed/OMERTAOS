from functools import lru_cache
from pydantic import BaseSettings, Field
from typing import List


class Settings(BaseSettings):
    api_prefix: str = "/v1"
    cors_origins: List[str] = Field(default_factory=lambda: ["*"])
    redis_url: str = "redis://redis:6379/0"
    postgres_dsn: str = "postgresql://aionos:aionos@postgres:5432/aionos"
    mongo_dsn: str = "mongodb://mongo:27017"
    kafka_bootstrap: str = "kafka:9092"
    qdrant_url: str = "http://qdrant:6333"
    tracing_endpoint: str = "http://otel-collector:4318/v1/traces"
    models_directory: str = "/data/models"
    policies_directory: str = "../policies"
    kernel_policy_file: str = "../policies/kernel/ai-kernel-policy.yaml"
    webhooks_policy_file: str = "../policies/webhooks.yaml"
    default_budget: float = 0.02
    hard_budget_cap: float = 0.2
    local_latency_p95: int = 600
    api_latency_p95: int = 2000
    hybrid_latency_p95: int = 2300
    tenancy_mode: str = "single"

    class Config:
        env_prefix = "AION_CONTROL_"
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
