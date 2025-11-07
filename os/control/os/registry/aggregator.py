"""Backend aggregator for AI registry providers and manifests."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, Tuple

import httpx
import yaml

from os.control.os.core.logger import get_logger

LOGGER = get_logger(__name__)


PROVIDER_DISPLAY_NAMES: dict[str, str] = {
    "openai": "OpenAI",
    "google": "Google Gemini",
    "google-deepmind": "Google Gemini",
    "meta": "Meta Llama",
    "alibaba": "Alibaba Qwen",
    "deepseek": "DeepSeek",
    "deepseek-ai": "DeepSeek",
    "mistral": "Mistral",
    "ollama": "Ollama",
    "custom": "Custom Models",
}

PROVIDER_ENV_VARS: dict[str, str] = {
    "openai": "OPENAI_API_KEY",
    "google": "GOOGLE_API_KEY",
    "google-deepmind": "GOOGLE_API_KEY",
    "meta": "META_API_KEY",
    "alibaba": "ALIBABA_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
    "deepseek-ai": "DEEPSEEK_API_KEY",
    "mistral": "MISTRAL_API_KEY",
}

LOCAL_PROVIDERS = {"ollama"}


def _compact(obj: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in obj.items()
        if value not in (None, "", [], {}, set())
    }


def _guess_provider_from_path(path: str) -> Optional[str]:
    parts = path.split("/")
    if len(parts) >= 2 and parts[0] == "models":
        return parts[1].lower()
    return None


def _read_yaml(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
    except FileNotFoundError:
        LOGGER.warning("Manifest not found", extra={"path": str(path)})
        return {}
    except yaml.YAMLError as exc:
        LOGGER.warning("Invalid YAML in manifest", extra={"path": str(path), "error": str(exc)})
        return {}
    return data if isinstance(data, dict) else {}


@dataclass(slots=True)
class ProviderContext:
    name: str
    requires_api_key: bool
    manifests: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def env_var(self) -> Optional[str]:
        if not self.requires_api_key:
            return None
        return PROVIDER_ENV_VARS.get(self.name, f"{self.name.upper()}_API_KEY")

    @property
    def display_name(self) -> str:
        return PROVIDER_DISPLAY_NAMES.get(self.name, self.name.replace("-", " ").title())


class RegistryAggregator:
    """Aggregate registry manifests with runtime provider checks."""

    def __init__(self, root: Path | None = None) -> None:
        base = Path(root) if root else Path(os.getenv("AION_REGISTRY_DIR", "ai_registry"))
        self._root = base.resolve()
        self._index_path = self._root / "REGISTRY.yaml"

    async def build(self) -> dict[str, Any]:
        index = self._load_index()
        providers = self._collect_providers(index)
        provider_payloads = [await self._build_provider_payload(context) for context in providers]
        provider_payloads.sort(key=lambda item: item["display_name"])
        payload = {
            "registryVersion": index.get("registry_version", "1.0"),
            "metadata": index.get("metadata", {}),
            "providers": provider_payloads,
            "customModels": self._load_custom_models(),
            "services": self._load_services(),
            "generatedAt": datetime.now(tz=timezone.utc).isoformat(timespec="seconds"),
        }
        return payload

    def _load_index(self) -> dict[str, Any]:
        if not self._index_path.exists():
            LOGGER.debug("Registry index missing", extra={"path": str(self._index_path)})
            return {}
        try:
            with self._index_path.open("r", encoding="utf-8") as handle:
                data = yaml.safe_load(handle) or {}
        except yaml.YAMLError as exc:
            LOGGER.warning("Failed to parse registry index", extra={"error": str(exc)})
            return {}
        return data if isinstance(data, dict) else {}

    def _collect_providers(self, index: dict[str, Any]) -> list[ProviderContext]:
        catalog = index.get("catalog") or {}
        model_entries = catalog.get("models") or []
        providers: dict[str, ProviderContext] = {}
        for entry in model_entries:
            normalized = self._normalize_catalog_entry(entry)
            if not normalized:
                continue
            manifest_path = self._root / normalized["path"]
            manifest = _read_yaml(manifest_path)
            provider_name = str(
                manifest.get("provider")
                or normalized.get("provider")
                or _guess_provider_from_path(normalized["path"])
                or "unknown"
            ).lower()
            record = self._manifest_to_record(manifest, normalized["path"], provider_name)
            if provider_name not in providers:
                providers[provider_name] = ProviderContext(
                    name=provider_name,
                    requires_api_key=bool(normalized.get("requiresApiKey")),
                    manifests=[record] if record else [],
                    metadata={"paths": [normalized["path"]]},
                )
            else:
                context = providers[provider_name]
                context.requires_api_key = context.requires_api_key or bool(normalized.get("requiresApiKey"))
                if record:
                    context.manifests.append(record)
                context.metadata.setdefault("paths", []).append(normalized["path"])
        return list(providers.values())

    def _normalize_catalog_entry(self, entry: Any) -> Optional[dict[str, Any]]:
        if isinstance(entry, str):
            return {"path": entry, "requiresApiKey": False}
        if isinstance(entry, dict):
            path = entry.get("path")
            if not path:
                return None
            normalized = {"path": path, "requiresApiKey": bool(entry.get("requiresApiKey"))}
            for key in ("provider", "displayName"):
                if key in entry:
                    normalized[key] = entry[key]
            return normalized
        return None

    def _manifest_to_record(self, manifest: dict[str, Any], rel_path: str, provider: str) -> dict[str, Any]:
        if not manifest:
            return {
                "name": Path(rel_path).stem,
                "provider": provider,
                "path": rel_path,
                "source": "manifest",
            }
        record = {
            "name": manifest.get("name", Path(rel_path).stem),
            "display_name": manifest.get("display_name") or manifest.get("name", Path(rel_path).stem),
            "provider": provider,
            "version": str(manifest.get("version")) if manifest.get("version") is not None else None,
            "description": manifest.get("description"),
            "modality": manifest.get("modality", []),
            "path": rel_path,
            "source": "manifest",
            "download": manifest.get("download"),
            "integrity": manifest.get("integrity"),
        }
        metadata = {
            "license": manifest.get("license"),
            "access": manifest.get("access"),
            "resources": manifest.get("resources"),
            "compat": manifest.get("compat"),
            "auto_update": manifest.get("auto_update"),
            "admin_approval_required": manifest.get("admin_approval_required"),
            "release_date": manifest.get("release_date"),
        }
        record["metadata"] = _compact(metadata)
        return _compact(record)

    async def _build_provider_payload(self, context: ProviderContext) -> dict[str, Any]:
        manifests = sorted(context.manifests, key=lambda item: item.get("name", ""))
        env_var = context.env_var
        available: list[dict[str, Any]] = []
        enabled = True
        error: Optional[str] = None

        if context.name in LOCAL_PROVIDERS:
            available, error = await self._fetch_local_provider(context.name)
            enabled = error is None
            if available:
                manifests_with_source = [dict(model, source="manifest") for model in manifests]
                available.extend(manifests_with_source)
        elif context.requires_api_key:
            api_key = os.getenv(env_var or "") if env_var else None
            if not api_key:
                enabled = False
                error = f"{env_var or context.name.upper() + '_API_KEY'} not configured"
                available = []
            else:
                available = list(manifests)
        else:
            available = list(manifests)

        payload = {
            "name": context.name,
            "display_name": context.display_name,
            "requiresApiKey": context.requires_api_key,
            "enabled": enabled,
            "env": env_var,
            "models": {
                "available": available,
                "manifests": manifests,
            },
        }
        if context.metadata:
            payload["metadata"] = context.metadata
        if error:
            payload["error"] = error
        return payload

    async def _fetch_local_provider(self, name: str) -> Tuple[list[dict[str, Any]], Optional[str]]:
        if name == "ollama":
            return await self._fetch_ollama_catalog()
        return [], None

    async def _fetch_ollama_catalog(self) -> Tuple[list[dict[str, Any]], Optional[str]]:
        base_url = (
            os.getenv("OLLAMA_API_BASE")
            or os.getenv("OLLAMA_HOST")
            or "http://127.0.0.1:11434"
        ).rstrip("/")
        endpoint = f"{base_url}/api/tags"
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(5.0, connect=2.0)) as client:
                response = await client.get(endpoint)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            LOGGER.warning("Failed to query Ollama registry", extra={"error": str(exc), "endpoint": endpoint})
            return [], f"Ollama registry request failed: {exc}".strip()
        try:
            payload = response.json()
        except ValueError as exc:
            LOGGER.warning("Invalid JSON from Ollama", extra={"error": str(exc)})
            return [], "Ollama registry returned invalid JSON"
        records = []
        for item in payload.get("models", []):
            record = _compact(
                {
                    "name": item.get("name"),
                    "modified_at": item.get("modified_at"),
                    "size": item.get("size"),
                    "digest": item.get("digest"),
                    "source": "runtime",
                }
            )
            if record:
                records.append(record)
        return records, None

    def _load_custom_models(self) -> list[dict[str, Any]]:
        custom_dir = self._root / "models" / "custom"
        if not custom_dir.exists():
            return []
        entries: list[dict[str, Any]] = []
        for path in sorted(custom_dir.rglob("*.yaml")):
            manifest = _read_yaml(path)
            provider = str(manifest.get("provider") or "custom").lower()
            entries.append(self._manifest_to_record(manifest, path.relative_to(self._root).as_posix(), provider))
        entries.sort(key=lambda item: item.get("name", ""))
        return entries

    def _load_services(self) -> list[dict[str, Any]]:
        services_dir = self._root / "services"
        if not services_dir.exists():
            return []
        entries: list[dict[str, Any]] = []
        for path in sorted(services_dir.rglob("*.yaml")):
            manifest = _read_yaml(path)
            record = _compact(
                {
                    "name": manifest.get("name", Path(path).stem),
                    "category": manifest.get("category"),
                    "version": manifest.get("version"),
                    "description": manifest.get("description"),
                    "path": path.relative_to(self._root).as_posix(),
                }
            )
            entries.append(record)
        entries.sort(key=lambda item: item.get("name", ""))
        return entries


__all__ = ["RegistryAggregator"]
