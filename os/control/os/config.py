import os
from functools import lru_cache
from typing import Any, Dict, List

from pydantic import Field, PrivateAttr
from pydantic_settings import BaseSettings

from os.secrets import SecretProvider, SecretProviderError, get_secret_provider


def _build_postgres_dsn(payload: Dict[str, Any]) -> str:
    username = payload.get("username") or payload.get("user")
    password = payload.get("password")
    host = payload.get("host", "localhost")
    port = payload.get("port", 5432)
    database = payload.get("database") or payload.get("dbname")
    params = payload.get("options")

    if not username or not password or not database:
        raise SecretProviderError(
            "Database secret must include 'username', 'password', and 'database' fields"
        )

    from urllib.parse import quote_plus

    safe_user = quote_plus(str(username))
    safe_pass = quote_plus(str(password))
    host_part = f"{host}:{port}" if port else str(host)
    dsn = f"postgresql://{safe_user}:{safe_pass}@{host_part}/{database}"
    if params:
        dsn = f"{dsn}?{params}"
    return dsn


class Settings(BaseSettings):
    api_prefix: str = "/v1"
    cors_origins: List[str] = Field(default_factory=lambda: ["*"])
    redis_url: str = "redis://redis:6379/0"
    mongo_dsn: str = "mongodb://mongo:27017"
    kafka_bootstrap: str = "kafka:9092"
    qdrant_url: str = "http://qdrant:6333"
    tracing_endpoint: str = "http://otel-collector:4318/v1/traces"
    models_directory: str = "/data/models"
    policies_directory: str = "../policies"
    memory_storage_path: str = "./.memory"
    memory_default_retention_days: int = 90
    default_budget: float = 0.02
    hard_budget_cap: float = 0.2
    local_latency_p95: int = 600
    api_latency_p95: int = 2000
    hybrid_latency_p95: int = 2300
    grpc_host: str = "0.0.0.0"
    grpc_port: int = 50051
    grpc_tls_cert: str = "config/certs/control-server.pem"
    grpc_tls_key: str = "config/certs/control-server-key.pem"
    grpc_tls_client_ca: str | None = "config/certs/dev-ca.pem"
    grpc_require_client_cert: bool = True

    postgres_secret_path: str = "kv/data/aionos/db-main"
    minio_secret_path: str = "kv/data/aionos/minio"

    _postgres_dsn: str | None = PrivateAttr(default=None)
    _minio_config: Dict[str, Any] | None = PrivateAttr(default=None)
    _secret_provider: SecretProvider | None = PrivateAttr(default=None)

    class Config:
        env_prefix = "AION_CONTROL_"
        env_file = ".env"

    def initialise_secrets(self, provider: SecretProvider | None = None) -> None:
        self._secret_provider = provider or get_secret_provider()
        db_secret = self._secret_provider.get_secret(self.postgres_secret_path)
        if isinstance(db_secret, str):
            raise SecretProviderError(
                "Database secret must be an object containing connection parameters"
            )
        self._postgres_dsn = _build_postgres_dsn(db_secret)

        minio_secret = self._secret_provider.get_secret(self.minio_secret_path)
        if isinstance(minio_secret, str):
            raise SecretProviderError(
                "MinIO secret must be an object containing endpoint and credentials"
            )
        self._minio_config = {
            "endpoint": minio_secret.get("endpoint", "minio:9000"),
            "access_key": minio_secret.get("access_key"),
            "secret_key": minio_secret.get("secret_key"),
            "secure": bool(minio_secret.get("secure", False)),
            "bucket": minio_secret.get("bucket", "aion-raw"),
        }

    @property
    def postgres_dsn(self) -> str:
        if not self._postgres_dsn:
            raise SecretProviderError("Postgres DSN requested before secrets were initialised")
        return self._postgres_dsn

    @property
    def minio_config(self) -> Dict[str, Any]:
        if not self._minio_config:
            raise SecretProviderError("MinIO configuration requested before secrets were initialised")
        return self._minio_config


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    settings.postgres_secret_path = os.getenv("AION_DB_SECRET_PATH", settings.postgres_secret_path)
    settings.minio_secret_path = os.getenv("AION_MINIO_SECRET_PATH", settings.minio_secret_path)
    settings.initialise_secrets()
    return settings
