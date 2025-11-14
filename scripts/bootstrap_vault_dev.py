#!/usr/bin/env python3
"""Bootstrap a Vault dev server for CI and local development.

This script assumes a Vault instance is running in ``-dev`` mode and listens on
``VAULT_ADDR`` (default ``http://127.0.0.1:8200``). It waits for Vault to become
healthy, enables the KV v2 engine on ``secret/`` if necessary, and seeds a small
set of deterministic secrets required by the AION-OS services during smoke
tests. All operations are idempotent so the script can be run multiple times
without failing.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict

VAULT_ADDR = os.environ.get("VAULT_ADDR", "http://127.0.0.1:8200").rstrip("/")
ROOT_TOKEN = os.environ.get("VAULT_TOKEN") or os.environ.get("VAULT_DEV_ROOT_TOKEN_ID", "aionos-dev-root")
KV_MOUNT = os.environ.get("VAULT_KV_MOUNT", "secret").strip("/")
WAIT_SECONDS = float(os.environ.get("VAULT_WAIT_SECONDS", "120"))
DEV_CERT_DIR = Path(os.environ.get("AION_DEV_CERT_DIR", "config/certs/dev"))

BASE_SECRETS: Dict[str, Dict[str, Dict[str, str]]] = {
    f"v1/{KV_MOUNT}/data/aionos/dev/database": {
        "data": {
            "username": "aion",
            "password": "aion",
            "host": "postgres",
            "port": "5432",
            "database": "aion",
        }
    },
    f"v1/{KV_MOUNT}/data/aionos/dev/minio": {
        "data": {
            "endpoint": "http://minio:9000",
            "access_key": "minio",
            "secret_key": "miniosecret",
            "secure": "false",
            "bucket": "aion-raw",
        }
    },
    f"v1/{KV_MOUNT}/data/aionos/dev/admin-token": {
        "data": {"token": "dev-admin-token"}
    },
    f"v1/{KV_MOUNT}/data/aionos/dev/gateway-api-keys": {
        "data": {"dev-key": "admin"}
    },
}


class VaultError(RuntimeError):
    """Raised when a Vault API operation fails."""


def _log(message: str) -> None:
    print(f"[vault-bootstrap] {message}")


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None


def build_dev_secrets() -> Dict[str, Dict[str, Dict[str, str]]]:
    secrets = dict(BASE_SECRETS)

    ca_cert = _read_text(DEV_CERT_DIR / "dev-ca.pem")
    control_cert = _read_text(DEV_CERT_DIR / "control-server-cert.pem")
    control_key = _read_text(DEV_CERT_DIR / "control-server-key.pem")
    gateway_cert = _read_text(DEV_CERT_DIR / "gateway-client-cert.pem")
    gateway_key = _read_text(DEV_CERT_DIR / "gateway-client-key.pem")

    if control_cert and control_key:
        payload = {
            "certificate": control_cert.strip(),
            "private_key": control_key.strip(),
        }
        if ca_cert:
            payload["ca_chain"] = [ca_cert.strip()]
        secrets[f"v1/{KV_MOUNT}/data/aionos/dev/control-tls"] = {"data": payload}
    else:
        _log("Skipping control TLS secret generation; development certificate missing")

    if gateway_cert and gateway_key:
        payload = {
            "certificate": gateway_cert.strip(),
            "private_key": gateway_key.strip(),
        }
        if ca_cert:
            payload["ca_chain"] = [ca_cert.strip()]
        secrets[f"v1/{KV_MOUNT}/data/aionos/dev/gateway-tls"] = {"data": payload}
    else:
        _log("Skipping gateway TLS secret generation; development certificate missing")

    if ca_cert:
        secrets[f"v1/{KV_MOUNT}/data/aionos/dev/mtls-ca"] = {
            "data": {"certificate": ca_cert.strip()}
        }
    else:
        _log("Skipping mTLS CA secret generation; development CA missing")

    return secrets


def wait_for_vault() -> None:
    """Poll the health endpoint until Vault responds with a ready status."""

    deadline = time.monotonic() + WAIT_SECONDS
    health_url = f"{VAULT_ADDR}/v1/sys/health"
    allowed = {200, 204, 429, 472, 473, 501}
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(health_url, timeout=2) as response:
                if response.status in allowed:
                    _log("Vault reported healthy status")
                    return
        except urllib.error.HTTPError as exc:
            if exc.code in allowed:
                _log("Vault reported transitional health status; continuing")
                return
        except urllib.error.URLError:
            pass
        time.sleep(2)
    raise VaultError(f"Vault at {VAULT_ADDR} did not become healthy within {WAIT_SECONDS} seconds")


def _vault_request(method: str, path: str, payload: Dict[str, object] | None = None, *,
                   allowed_status: set[int] | None = None) -> tuple[int, bytes]:
    url = f"{VAULT_ADDR}/{path.lstrip('/')}"
    headers = {"X-Vault-Token": ROOT_TOKEN}
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as exc:
        if allowed_status and exc.code in allowed_status:
            return exc.code, exc.read()
        body = exc.read().decode("utf-8", "ignore")
        raise VaultError(f"Vault request {method} {path} failed ({exc.code}): {body}") from exc
    except urllib.error.URLError as exc:  # pragma: no cover - network failure info
        raise VaultError(f"Vault request {method} {path} failed: {exc}") from exc


def enable_kv_engine() -> None:
    """Ensure the KV v2 engine is mounted at the configured path."""

    path = f"v1/sys/mounts/{KV_MOUNT}"
    payload = {"type": "kv", "options": {"version": "2"}}
    status, _ = _vault_request("POST", path, payload, allowed_status={204, 400})
    if status == 204:
        _log(f"Enabled KV v2 engine at {KV_MOUNT}/")
    elif status == 400:
        _log(f"KV engine {KV_MOUNT}/ already present")


def seed_dev_secrets() -> None:
    secrets = build_dev_secrets()
    for path, payload in secrets.items():
        _vault_request("POST", path, payload)
        _log(f"Wrote secret {path}")


def main() -> int:
    _log("Waiting for Vault dev server ...")
    wait_for_vault()
    _vault_request("POST", "v1/auth/token/lookup-self", allowed_status={200})
    _log("Authenticated using dev root token")
    enable_kv_engine()
    seed_dev_secrets()
    _log("Vault dev bootstrap complete")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except VaultError as exc:
        print(f"[vault-bootstrap] Error: {exc}", file=sys.stderr)
        sys.exit(1)
