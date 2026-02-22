from __future__ import annotations

import logging
import pathlib
import time
from typing import Dict

import httpx
import yaml
from config import get_config, load_scope


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

BASE_DIR = pathlib.Path(__file__).resolve().parents[1]
CONFIG_PATH = pathlib.Path(
    get_config("AION_CONFIG_FILE", BASE_DIR / "config" / "aion.yaml")
)
API_ROOT = get_config("AION_CONTROL_API", "http://control:8000")
DEFAULT_TIMEOUT = httpx.Timeout(60.0, connect=10.0)

CONFIG_SCHEMAS: Dict[str, Dict[str, object]] = {
    "wandb": {
        "type": "object",
        "properties": {
            "entity": {"type": "string"},
            "project": {"type": "string", "default": "aion"},
            "api_key": {"type": "string", "format": "password"},
        },
        "required": ["api_key"],
    },
    "mlflow": {
        "type": "object",
        "properties": {
            "tracking_uri": {
                "type": "string",
                "default": "http://mlflow:5000",
            },
            "artifact_root": {"type": "string", "default": "/mlruns"},
        },
    },
    "neptune": {
        "type": "object",
        "properties": {
            "project": {"type": "string"},
            "api_token": {"type": "string", "format": "password"},
        },
        "required": ["api_token"],
    },
    "presidio-analyzer": {
        "type": "object",
        "properties": {
            "languages": {
                "type": "array",
                "items": {"type": "string"},
                "default": ["en", "fa"],
            },
            "pii_kinds": {
                "type": "array",
                "items": {"type": "string"},
                "default": ["PHONE_NUMBER", "EMAIL_ADDRESS"],
            },
        },
    },
    "presidio-anonymizer": {
        "type": "object",
        "properties": {
            "languages": {
                "type": "array",
                "items": {"type": "string"},
                "default": ["en", "fa"],
            },
            "pii_kinds": {
                "type": "array",
                "items": {"type": "string"},
                "default": ["PHONE_NUMBER", "EMAIL_ADDRESS"],
            },
        },
    },
    "s3": {
        "type": "object",
        "properties": {
            "endpoint": {"type": "string"},
            "access_key": {"type": "string"},
            "secret_key": {"type": "string", "format": "password"},
            "bucket": {"type": "string"},
        },
        "required": ["endpoint", "access_key", "secret_key"],
    },
}


def load_config() -> Dict[str, Dict[str, str]]:
    cfg = load_scope(str(CONFIG_PATH))
    catalog_cfg = cfg.get("catalog", {})
    return catalog_cfg if isinstance(catalog_cfg, dict) else {}


def catalog_seed_path(seed_file: str | None) -> pathlib.Path:
    if not seed_file:
        seed_file = "config/catalog.seed.yaml"
    path = pathlib.Path(seed_file)
    if not path.is_absolute():
        path = (BASE_DIR / path).resolve()
    return path


def pull_pypi(client: httpx.Client, pkg: str) -> Dict[str, str]:
    name = pkg.split()[0]
    logger.debug("Fetching PyPI metadata", extra={"package": name})
    resp = client.get(f"https://pypi.org/pypi/{name}/json")
    resp.raise_for_status()
    info = resp.json().get("info", {})
    return {
        "latest_version": info.get("version", ""),
        "license": info.get("license", ""),
        "summary": info.get("summary", ""),
    }


def sync_once(seed_path: str | pathlib.Path | None = None) -> None:
    catalog_cfg = load_config()
    path = catalog_seed_path(seed_path or catalog_cfg.get("seed_file"))
    logger.info("Starting catalog sync", extra={"seed_path": str(path)})

    with path.open("r", encoding="utf-8") as fh:
        seed = yaml.safe_load(fh)["catalog"]

    with httpx.Client(timeout=DEFAULT_TIMEOUT) as client:
        for category, tools in seed.items():
            for item in tools:
                meta = pull_pypi(client, item["pypi"])
                schema = item.get("config_schema") or CONFIG_SCHEMAS.get(item["name"], {})
                payload = {
                    "category": category,
                    "tool": {
                        "name": item["name"],
                        "display_name": item["name"].replace("-", " ").title(),
                        "pypi_name": item["pypi"],
                        "repo_url": item.get("repo"),
                        "docs_url": item.get("docs"),
                        "description": meta["summary"],
                        "latest_version": meta["latest_version"],
                        "license": meta["license"],
                        "tags": item.get("tags", []),
                        "config_schema": schema,
                    },
                }
                logger.info(
                    "Upserting tool",
                    extra={"category": category, "name": item["name"]},
                )
                response = client.post(f"{API_ROOT}/catalog/upsert", json=payload)
                response.raise_for_status()


def sync_forever() -> None:
    cfg = load_config()
    days = cfg.get("catalog", {}).get("sync_every_days", 7)
    interval = max(float(days), 1.0) * 86400
    while True:
        try:
            sync_once()
        except Exception:  # pragma: no cover - defensive logging
            logger.exception("Catalog sync failed")
        time.sleep(interval)


if __name__ == "__main__":
    sync_forever()
