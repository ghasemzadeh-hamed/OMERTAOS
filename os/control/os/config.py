import os
from functools import lru_cache
from typing import Any, Dict, List

from pydantic import Field, PrivateAttr
from pydantic_settings import BaseSettings

from os.secrets import SecretProvider, SecretProviderError, get_secret_provider


def _normalize_boolean(value: str | None) -> bool:
    if value is None:
        return False
    normalised = value.strip().lower()
    return normalised in {"1", "true", "yes", "on"}


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
    grpc_tls_secret_path: str | None = "secret/aionos/dev/control-tls"
    grpc_tls_client_ca_secret_path: str | None = None
    grpc_require_client_cert: bool = True

    postgres_secret_path: str = "kv/data/aionos/db-main"
    minio_secret_path: str = "kv/data/aionos/minio"

    _postgres_dsn: str | None = PrivateAttr(default=None)
    _minio_config: Dict[str, Any] | None = PrivateAttr(default=None)
    _secret_provider: SecretProvider | None = PrivateAttr(default=None)
    _grpc_tls_certificate: bytes | None = PrivateAttr(default=None)
    _grpc_tls_private_key: bytes | None = PrivateAttr(default=None)
    _grpc_tls_client_ca: bytes | None = PrivateAttr(default=None)

    class Config:
        env_prefix = "AION_CONTROL_"
        env_file = ".env"
        fields = {"environment": {"env": "AION_ENV"}}

    environment: str = "dev"

    def initialise_secrets(self, provider: SecretProvider | None = None) -> None:
        disable_env = os.getenv("AION_CONTROL_DISABLE_SECRETS")
        if disable_env is not None:
            disable_secrets = disable_env == "1"
        else:
            vault_enabled_raw = os.getenv("AION_VAULT_ENABLED") or os.getenv("VAULT_ENABLED")
            if vault_enabled_raw is not None:
                disable_secrets = not _normalize_boolean(vault_enabled_raw)
            else:
                disable_secrets = not os.getenv("AION_VAULT_ADDR")

        if disable_secrets:
            self._postgres_dsn = os.getenv(
                "AION_CONTROL_POSTGRES_DSN",
                "postgresql://aion:aion@postgres:5432/aion",
            )
            self._minio_config = {
                "endpoint": os.getenv("AION_CONTROL_MINIO_ENDPOINT", "minio:9000"),
                "access_key": os.getenv("AION_CONTROL_MINIO_ACCESS_KEY", "minio"),
                "secret_key": os.getenv("AION_CONTROL_MINIO_SECRET_KEY", "miniosecret"),
                "secure": bool(int(os.getenv("AION_CONTROL_MINIO_SECURE", "0"))),
                "bucket": os.getenv("AION_CONTROL_MINIO_BUCKET", "aion-raw"),
            }
            return
        self._secret_provider = provider or get_secret_provider()
        try:
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

            self._load_tls_materials()
        except SecretProviderError:
            # Fall back to environment configuration when Vault integration is unavailable.
            self._postgres_dsn = os.getenv(
                "AION_CONTROL_POSTGRES_DSN",
                "postgresql://aion:aion@postgres:5432/aion",
            )
            self._minio_config = {
                "endpoint": os.getenv("AION_CONTROL_MINIO_ENDPOINT", "minio:9000"),
                "access_key": os.getenv("AION_CONTROL_MINIO_ACCESS_KEY", "minio"),
                "secret_key": os.getenv("AION_CONTROL_MINIO_SECRET_KEY", "miniosecret"),
                "secure": bool(int(os.getenv("AION_CONTROL_MINIO_SECURE", "0"))),
                "bucket": os.getenv("AION_CONTROL_MINIO_BUCKET", "aion-raw"),
            }

            cert_env = os.getenv("AION_CONTROL_TLS_CERT")
            key_env = os.getenv("AION_CONTROL_TLS_KEY")
            ca_env = os.getenv("AION_CONTROL_TLS_CA")
            if cert_env and key_env:
                self._grpc_tls_certificate = cert_env.encode()
                self._grpc_tls_private_key = key_env.encode()
            if ca_env:
                self._grpc_tls_client_ca = ca_env.encode()

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

    @property
    def grpc_tls_certificate(self) -> bytes | None:
        return self._grpc_tls_certificate

    @property
    def grpc_tls_private_key(self) -> bytes | None:
        return self._grpc_tls_private_key

    @property
    def grpc_tls_client_ca(self) -> bytes | None:
        return self._grpc_tls_client_ca

    def _load_tls_materials(self) -> None:
        secret_path = os.getenv(
            "AION_CONTROL_TLS_SECRET_PATH",
            self.grpc_tls_secret_path or "",
        ).strip()
        client_ca_path = os.getenv(
            "AION_CONTROL_TLS_CLIENT_CA_SECRET_PATH",
            self.grpc_tls_client_ca_secret_path or "",
        ).strip()

        if secret_path:
            payload = self._secret_provider.get_secret(secret_path)
            if isinstance(payload, str):
                raise SecretProviderError(
                    "Control TLS secret must be an object containing certificate and private_key"
                )
            certificate = _first_string(payload, ["certificate", "cert", "public_cert"])
            private_key = _first_string(payload, ["private_key", "key"])
            ca_chain = _normalise_chain(payload.get("ca_chain") or payload.get("ca") or payload.get("certificate_authority"))
            if not certificate or not private_key:
                raise SecretProviderError(
                    "Control TLS secret must include 'certificate' and 'private_key' fields"
                )
            self._grpc_tls_certificate = certificate.encode()
            self._grpc_tls_private_key = private_key.encode()
            if ca_chain:
                self._grpc_tls_client_ca = b"\n".join([entry.encode() for entry in ca_chain])

        if client_ca_path:
            payload = self._secret_provider.get_secret(client_ca_path)
            if isinstance(payload, str):
                self._grpc_tls_client_ca = payload.encode()
            else:
                ca_chain = _normalise_chain(
                    payload.get("ca_chain") or payload.get("ca") or payload.get("certificate")
                )
                if ca_chain:
                    self._grpc_tls_client_ca = b"\n".join([entry.encode() for entry in ca_chain])


def _first_string(payload: Dict[str, Any], keys: List[str]) -> str | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _normalise_chain(value: Any) -> list[str] | None:
    if not value:
        return None
    if isinstance(value, str):
        return [value.strip()]
    if isinstance(value, list):
        result: list[str] = []
        for item in value:
            if isinstance(item, str) and item.strip():
                result.append(item.strip())
        return result or None
    return None


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    settings.postgres_secret_path = os.getenv("AION_DB_SECRET_PATH", settings.postgres_secret_path)
    settings.minio_secret_path = os.getenv("AION_MINIO_SECRET_PATH", settings.minio_secret_path)
    settings.initialise_secrets()
    return settings
