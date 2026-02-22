"""Utility for validating and refreshing the Agent-OS AI Registry catalog."""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List

import yaml

REGISTRY_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_INDEX = REGISTRY_ROOT / "REGISTRY.yaml"
LOCK_FILE = REGISTRY_ROOT / "registry.lock.json"

MANIFEST_DIRS = {
    "models": REGISTRY_ROOT / "models",
    "algorithms": REGISTRY_ROOT / "algorithms",
    "services": REGISTRY_ROOT / "services",
}

# Providers that require API keys before their manifests can be used.
API_KEY_REQUIRED_PROVIDERS: set[str] = {
    "openai",
    "google",
    "alibaba",
    "deepseek",
    "mistral",
}

REQUIRED_FIELDS = {
    "models": ["kind", "name", "provider", "version", "download"],
    "algorithms": ["kind", "name", "type", "entrypoint"],
    "services": ["kind", "name", "category", "version"],
}


def _requires_api_key(kind: str, path: Path) -> bool:
    if kind != "models":
        return False
    try:
        relative = path.relative_to(REGISTRY_ROOT)
    except ValueError:
        return False
    parts = relative.parts
    if len(parts) < 2:
        return False
    provider = parts[1].lower()
    return provider in API_KEY_REQUIRED_PROVIDERS


def _manifest_relative_paths(kind: str) -> List[Dict[str, Any]]:
    base = MANIFEST_DIRS[kind]
    manifests: List[Dict[str, Any]] = []
    for path in sorted(base.rglob("*.yaml")):
        manifests.append(
            {
                "path": path.relative_to(REGISTRY_ROOT).as_posix(),
                "requiresApiKey": _requires_api_key(kind, path),
            }
        )
    return manifests


def _load_yaml(path: Path) -> Dict:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _validate_manifest(kind: str, path: Path) -> List[str]:
    errors: List[str] = []
    data = _load_yaml(path)
    required = REQUIRED_FIELDS[kind]
    missing = [field for field in required if field not in data]
    if missing:
        errors.append(
            f"{path.relative_to(REGISTRY_ROOT)} is missing required fields: {', '.join(missing)}"
        )
    if data.get("kind") != kind[:-1]:
        errors.append(
            f"{path.relative_to(REGISTRY_ROOT)} has unexpected kind '{data.get('kind')}'"
        )
    return errors


def _validate_all() -> List[str]:
    issues: List[str] = []
    for kind, directory in MANIFEST_DIRS.items():
        if not directory.exists():
            issues.append(f"Missing manifest directory: {directory}")
            continue
        for path in directory.rglob("*.yaml"):
            issues.extend(_validate_manifest(kind, path))
    return issues


def _write_registry_index() -> None:
    catalog = {
        "models": _manifest_relative_paths("models"),
        "algorithms": _manifest_relative_paths("algorithms"),
        "services": _manifest_relative_paths("services"),
    }

    if REGISTRY_INDEX.exists():
        with REGISTRY_INDEX.open("r", encoding="utf-8") as fh:
            index_data = yaml.safe_load(fh) or {}
    else:
        index_data = {}

    index_data.setdefault("registry_version", "1.0")
    index_data["catalog"] = catalog
    index_data.setdefault("installed", {"models": {}, "algorithms": {}, "services": {}})
    index_data.setdefault(
        "signing",
        {"method": "minisign", "public_key": "security/publickey.txt"},
    )
    timestamp = _dt.datetime.now(tz=_dt.timezone.utc).isoformat(timespec="seconds")
    index_data["metadata"] = {
        "generated_at": timestamp,
        "generated_by": "update_catalog.py",
    }

    with REGISTRY_INDEX.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(index_data, fh, sort_keys=False)



def _build_lockfile() -> None:
    entries: List[Dict[str, str]] = []
    for kind, directory in MANIFEST_DIRS.items():
        for path in directory.rglob("*.yaml"):
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            entries.append(
                {
                    "kind": kind[:-1],
                    "name": _load_yaml(path).get("name", path.stem),
                    "path": path.relative_to(REGISTRY_ROOT).as_posix(),
                    "sha256": digest,
                }
            )

    payload = {
        "generated_at": _dt.datetime.now(tz=_dt.timezone.utc).isoformat(timespec="seconds"),
        "entries": sorted(entries, key=lambda item: item["path"]),
    }

    with LOCK_FILE.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)



def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate", action="store_true", help="Validate manifests")
    parser.add_argument(
        "--sync-index",
        action="store_true",
        help="Rebuild REGISTRY.yaml catalog entries",
    )
    parser.add_argument(
        "--write-lock",
        action="store_true",
        help="Generate registry.lock.json with manifest hashes",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    exit_code = 0

    if args.validate:
        issues = _validate_all()
        if issues:
            exit_code = 1
            for line in issues:
                print(f"ERROR: {line}")
        else:
            print("All manifests passed validation.")

    if args.sync_index:
        _write_registry_index()
        print(f"Updated {REGISTRY_INDEX.relative_to(REGISTRY_ROOT)}")

    if args.write_lock:
        _build_lockfile()
        print(f"Wrote {LOCK_FILE.relative_to(REGISTRY_ROOT)}")

    if not any([args.validate, args.sync_index, args.write_lock]):
        # Default behavior mirrors the most common workflow: validate + sync + lock
        issues = _validate_all()
        if issues:
            for line in issues:
                print(f"ERROR: {line}")
            return 1
        _write_registry_index()
        _build_lockfile()
        print("Validation passed. Registry index and lockfile updated.")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
