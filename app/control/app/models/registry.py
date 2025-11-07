from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from threading import RLock
from typing import Any, Dict, Iterable, List, Optional

import os

import httpx
import yaml

from app.control.app.config import get_settings


class PrivacyLevel(str, Enum):
    LOCAL_ONLY = "local-only"
    HYBRID = "hybrid"
    ALLOW_API = "allow-api"

    @classmethod
    def from_value(cls, value: str | None) -> "PrivacyLevel":
        if not value:
            return cls.ALLOW_API
        try:
            return cls(value)
        except ValueError as exc:
            raise ValueError(f"unknown privacy level: {value}") from exc


PRIVACY_ORDER: Dict[PrivacyLevel, int] = {
    PrivacyLevel.LOCAL_ONLY: 0,
    PrivacyLevel.HYBRID: 1,
    PrivacyLevel.ALLOW_API: 2,
}


@dataclass(slots=True)
class ModelRecord:
    name: str
    provider: str
    mode: str
    engine: str
    privacy: PrivacyLevel
    intents: List[str]
    latency_budget_ms: Optional[int] = None
    display_name: Optional[str] = None
    credentials_env: Optional[str] = None
    health_endpoint: Optional[str] = None
    health_method: str = "GET"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "display_name": self.display_name or self.name,
            "provider": self.provider,
            "mode": self.mode,
            "engine": self.engine,
            "privacy": self.privacy.value,
            "intents": sorted(self.intents),
            "latency_budget_ms": self.latency_budget_ms,
            "credentials_env": self.credentials_env,
            "health": {
                "endpoint": self.health_endpoint,
                "method": self.health_method,
            },
            "metadata": self.metadata,
        }


class ModelRegistry:
    def __init__(
        self,
        policy_file: Path | str | None = None,
        *,
        health_timeout: float = 3.0,
    ) -> None:
        settings = get_settings()
        self._policy_file = (
            Path(policy_file)
            if policy_file
            else Path(settings.policies_directory).resolve() / "models.yaml"
        )
        self._lock = RLock()
        self._records: Dict[str, ModelRecord] = {}
        self._intents: Dict[str, List[ModelRecord]] = {}
        self._defaults: Dict[str, Any] = {}
        self._health_timeout = health_timeout
        self.reload()

    @property
    def defaults(self) -> Dict[str, Any]:
        return self._defaults

    def reload(self) -> None:
        with self._lock:
            if not self._policy_file.exists():
                self._records = {}
                self._intents = {}
                self._defaults = {}
                return

            data = yaml.safe_load(self._policy_file.read_text()) or {}
            self._defaults = data.get("defaults", {})

            records: Dict[str, ModelRecord] = {}
            intents_map: Dict[str, List[ModelRecord]] = {}
            for raw in data.get("models", []):
                try:
                    record = self._parse_record(raw)
                except Exception as exc:  # pragma: no cover - defensive
                    raise ValueError(
                        f"invalid model definition for {raw.get('name')}: {exc}"
                    ) from exc
                records[record.name] = record
                for intent in record.intents:
                    intents_map.setdefault(intent, []).append(record)

            for intent_records in intents_map.values():
                intent_records.sort(key=self._sort_key)

            self._records = records
            self._intents = intents_map

    def list_models(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [record.to_dict() for record in self._records.values()]

    def get(self, name: str) -> Optional[ModelRecord]:
        with self._lock:
            return self._records.get(name)

    def for_intent(self, intent: str) -> List[ModelRecord]:
        with self._lock:
            return list(self._intents.get(intent, []))

    async def select_model(
        self,
        intent: str,
        *,
        requested_privacy: PrivacyLevel | str | None = None,
        preferred: Optional[Iterable[str]] = None,
        require_healthy: bool = True,
    ) -> Optional[ModelRecord]:
        privacy = (
            requested_privacy
            if isinstance(requested_privacy, PrivacyLevel)
            else PrivacyLevel.from_value(str(requested_privacy) if requested_privacy else None)
        )

        preferred_set = {name for name in preferred or []}

        candidates = self.for_intent(intent)
        if preferred_set:
            candidates = [c for c in candidates if c.name in preferred_set]

        candidates = [
            c
            for c in candidates
            if PRIVACY_ORDER[c.privacy] <= PRIVACY_ORDER[privacy]
        ]

        if not candidates:
            return None

        if not require_healthy:
            return candidates[0]

        return await self._first_healthy(candidates)

    async def ensure_health(self, name: str) -> Dict[str, Any]:
        record = self.get(name)
        if not record:
            raise LookupError(f"model {name} not registered")
        return await self._check_health(record)

    async def _first_healthy(
        self, records: Iterable[ModelRecord]
    ) -> Optional[ModelRecord]:
        async with httpx.AsyncClient(timeout=self._health_timeout) as client:
            for record in records:
                health = await self._check_health(record, client=client)
                if health.get("status") != "unhealthy":
                    return record
        return None

    async def _check_health(
        self,
        record: ModelRecord,
        *,
        client: httpx.AsyncClient | None = None,
    ) -> Dict[str, Any]:
        if not record.health_endpoint:
            return {"status": "unknown"}

        close_client = False
        if client is None:
            client = httpx.AsyncClient(timeout=self._health_timeout)
            close_client = True

        try:
            response = await client.request(
                record.health_method,
                record.health_endpoint,
                headers=self._auth_headers(record),
            )
            response.raise_for_status()
            payload: Dict[str, Any] = {
                "status": "healthy",
                "status_code": response.status_code,
            }
            if response.headers.get("content-type", "").startswith("application/json"):
                payload["details"] = response.json()
            return payload
        except httpx.HTTPError as exc:
            return {
                "status": "unhealthy",
                "status_code": getattr(exc.response, "status_code", None),
                "error": str(exc),
            }
        finally:
            if close_client:
                await client.aclose()

    def _auth_headers(self, record: ModelRecord) -> Dict[str, str]:
        if not record.credentials_env:
            return {}
        # Support secrets sourced from the environment or mounted files.
        token = os.getenv(record.credentials_env)
        if not token:
            secret_path = Path(f".secrets/{record.credentials_env}")
            if secret_path.exists():
                token = secret_path.read_text().strip()
        if not token:
            return {}
        return {"Authorization": f"Bearer {token}"}

    def _sort_key(self, record: ModelRecord) -> tuple[int, int, str]:
        privacy_rank = PRIVACY_ORDER[record.privacy]
        latency = record.latency_budget_ms or 999_999
        return (privacy_rank, latency, record.name)

    def _parse_record(self, raw: Dict[str, Any]) -> ModelRecord:
        privacy = PrivacyLevel.from_value(raw.get("privacy"))
        health = raw.get("health", {}) or {}
        return ModelRecord(
            name=raw["name"],
            provider=raw.get("provider", "unknown"),
            mode=raw.get("mode", "api"),
            engine=raw.get("engine", "chat"),
            privacy=privacy,
            intents=list({intent for intent in raw.get("intents", [])}),
            latency_budget_ms=raw.get("latency_budget_ms"),
            display_name=raw.get("display_name"),
            credentials_env=raw.get("credentials_env"),
            health_endpoint=health.get("endpoint"),
            health_method=(health.get("method") or "GET").upper(),
            metadata=raw.get("metadata", {}),
        )


def get_model_registry() -> ModelRegistry:
    return _MODEL_REGISTRY


_MODEL_REGISTRY = ModelRegistry()
