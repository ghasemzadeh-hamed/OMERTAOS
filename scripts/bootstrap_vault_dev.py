#!/usr/bin/env python3
"""Bootstrap a local HashiCorp Vault for AION-OS development."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict

import hvac
import requests
try:
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID
except ImportError as exc:  # pragma: no cover - dependency hint
    raise SystemExit(
        "cryptography is required. Install dependencies with 'pip install hvac cryptography requests'."
    ) from exc

REPO_ROOT = Path(__file__).resolve().parents[1]
DOT_VAULT = REPO_ROOT / ".vault"
UNSEAL_FILE = DOT_VAULT / "dev-unseal.json"
ENV_FILE = REPO_ROOT / ".env.vault.dev"
HOST_VAULT_ADDR = (
    os.environ.get("AION_VAULT_ADDR_HOST")
    or os.environ.get("AION_VAULT_ADDR")
    or "http://127.0.0.1:8200"
)
ENV_VAULT_ADDR = os.environ.get("AION_VAULT_ADDR_CONTAINER", "http://vault:8200")
VAULT_KV_MOUNT = os.environ.get("AION_VAULT_KV_MOUNT", "secret")
AION_ENV = os.environ.get("AION_ENV", "dev")
BOOTSTRAP_TIMEOUT = float(os.environ.get("AION_VAULT_BOOTSTRAP_TIMEOUT", "180"))

DEV_POLICY_NAME = "aionos-dev"
BASE_DEV_SECRETS: Dict[str, Dict[str, Any]] = {
    "secret/data/aionos/dev/db-main": {
        "data": {
            "username": "aion",
            "password": "aion",
            "host": "postgres",
            "port": 5432,
            "database": "aion",
        }
    },
    "secret/data/aionos/dev/minio": {
        "data": {
            "endpoint": "http://minio:9000",
            "access_key": "minio",
            "secret_key": "miniosecret",
            "secure": False,
            "bucket": "aion-raw",
        }
    },
    "secret/data/aionos/dev/admin-token": {
        "data": {"token": "dev-admin-token"}
    },
    "secret/data/aionos/dev/gateway-api-keys": {
        "data": {"dev-key": "admin"},
    },
}


def run_compose() -> None:
    """Ensure the Vault container is running via docker compose."""

    cmd = ["docker", "compose", "up", "-d", "vault"]
    try:
        subprocess.run(cmd, cwd=REPO_ROOT, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError as exc:  # pragma: no cover - developer environment requirement
        raise SystemExit("docker compose is required to bootstrap Vault") from exc
    except subprocess.CalledProcessError as exc:
        sys.stderr.write(exc.stderr.decode() if isinstance(exc.stderr, (bytes, bytearray)) else str(exc))
        raise SystemExit("Failed to start Vault service via docker compose") from exc


def wait_for_vault(url: str, timeout: float = 60.0) -> None:
    """Poll the Vault health endpoint until it responds."""

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            response = requests.get(f"{url}/v1/sys/health", timeout=2, verify=False)
        except requests.RequestException:
            time.sleep(1)
            continue
        if response.status_code in {200, 429, 472, 473, 501, 503}:
            return
        time.sleep(1)
    raise TimeoutError(f"Vault at {url} did not become reachable within {timeout} seconds")


def initialise_and_unseal(client: hvac.Client) -> Dict[str, str]:
    """Initialise Vault if required and return credentials."""

    creds: Dict[str, str] = {}
    if not client.sys.is_initialized():
        init_result = client.sys.initialize(secret_shares=1, secret_threshold=1)
        creds["root_token"] = init_result["root_token"]
        creds["unseal_key"] = init_result["keys_base64"][0]
    if client.sys.is_sealed():
        if not creds.get("unseal_key") and UNSEAL_FILE.exists():
            stored = json.loads(UNSEAL_FILE.read_text())
            creds.setdefault("unseal_key", stored.get("unseal_key", ""))
            creds.setdefault("root_token", stored.get("root_token", ""))
        key = creds.get("unseal_key")
        if not key:
            raise SystemExit("Vault is sealed and no unseal key is available. Check .vault/dev-unseal.json")
        client.sys.submit_unseal_key(key)
    return creds


def persist_dev_material(creds: Dict[str, str]) -> None:
    """Store root token and unseal key locally for development."""

    DOT_VAULT.mkdir(exist_ok=True)
    data = {"unseal_key": creds.get("unseal_key"), "root_token": creds.get("root_token")}
    UNSEAL_FILE.write_text(json.dumps(data, indent=2))
    os.chmod(UNSEAL_FILE, 0o600)


def ensure_kv_mount(client: hvac.Client) -> None:
    mounts = client.sys.list_mounted_secrets_engines().get("data", {})
    if f"{VAULT_KV_MOUNT}/" not in mounts:
        client.sys.enable_secrets_engine("kv", path=VAULT_KV_MOUNT, options={"version": 2})


def ensure_policy(client: hvac.Client) -> None:
    policy_hcl = f"""
    path "{VAULT_KV_MOUNT}/data/aionos/dev/*" {{
      capabilities = ["create", "read", "update", "delete", "list"]
    }}
    path "{VAULT_KV_MOUNT}/metadata/aionos/dev/*" {{
      capabilities = ["list", "delete"]
    }}
    """
    client.sys.create_or_update_policy(name=DEV_POLICY_NAME, policy=policy_hcl)


def ensure_dev_token(client: hvac.Client) -> str:
    token_response = client.auth.token.create(
        policies=[DEV_POLICY_NAME],
        period="24h",
        renewable=True,
        explicit_max_ttl="0",
        display_name="aionos-dev-token",
    )
    return token_response["auth"]["client_token"]


def seed_dev_secrets(client: hvac.Client, secrets: Dict[str, Dict[str, Any]]) -> None:
    for path, payload in secrets.items():
        client.adapter.request("POST", path, json=payload)


def generate_tls_materials() -> Dict[str, Dict[str, Any]]:
    print("[vault-bootstrap] Generating development TLS materials")
    ca_key = rsa.generate_private_key(public_exponent=65537, key_size=4096)
    ca_subject = x509.Name(
        [
            x509.NameAttribute(NameOID.COMMON_NAME, "AIONOS Dev CA"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "AION-OS"),
        ]
    )
    ca_cert = (
        x509.CertificateBuilder()
        .subject_name(ca_subject)
        .issuer_name(ca_subject)
        .public_key(ca_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow() - timedelta(minutes=5))
        .not_valid_after(datetime.utcnow() + timedelta(days=365))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .add_extension(x509.KeyUsage(
            digital_signature=True,
            key_encipherment=True,
            key_cert_sign=True,
            crl_sign=True,
            content_commitment=False,
            data_encipherment=False,
            key_agreement=False,
            encipher_only=False,
            decipher_only=False,
        ), critical=True)
        .sign(ca_key, hashes.SHA256())
    )

    def _issue_cert(common_name: str, *, client_auth: bool) -> tuple[str, str]:
        key = rsa.generate_private_key(public_exponent=65537, key_size=4096)
        subject = x509.Name(
            [
                x509.NameAttribute(NameOID.COMMON_NAME, common_name),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "AION-OS"),
            ]
        )
        builder = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(ca_cert.subject)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.utcnow() - timedelta(minutes=5))
            .not_valid_after(datetime.utcnow() + timedelta(days=180))
            .add_extension(
                x509.ExtendedKeyUsage(
                    [
                        ExtendedKeyUsageOID.CLIENT_AUTH
                        if client_auth
                        else ExtendedKeyUsageOID.SERVER_AUTH
                    ]
                ),
                critical=False,
            )
        )
        if not client_auth:
            builder = builder.add_extension(
                x509.SubjectAlternativeName([x509.DNSName(common_name)]),
                critical=False,
            )
        cert = builder.sign(private_key=ca_key, algorithm=hashes.SHA256())
        key_pem = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode()
        cert_pem = cert.public_bytes(serialization.Encoding.PEM).decode()
        return key_pem, cert_pem

    control_key, control_cert = _issue_cert("control.internal", client_auth=False)
    gateway_key, gateway_cert = _issue_cert("gateway.internal", client_auth=True)

    ca_cert_pem = ca_cert.public_bytes(serialization.Encoding.PEM).decode()
    ca_key_pem = ca_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()

    return {
        "secret/data/aionos/dev/control-tls": {
            "data": {
                "certificate": control_cert,
                "private_key": control_key,
                "ca_chain": [ca_cert_pem],
            }
        },
        "secret/data/aionos/dev/gateway-tls": {
            "data": {
                "certificate": gateway_cert,
                "private_key": gateway_key,
                "ca_chain": [ca_cert_pem],
            }
        },
        "secret/data/aionos/dev/mtls-ca": {
            "data": {
                "certificate": ca_cert_pem,
            }
        },
        "secret/data/aionos/dev/dev-ca": {
            "data": {
                "certificate": ca_cert_pem,
                "private_key": ca_key_pem,
            }
        },
    }


def write_env_file(token: str) -> None:
    lines = [
        f"AION_VAULT_ADDR={ENV_VAULT_ADDR}",
        f"AION_VAULT_KV_MOUNT={VAULT_KV_MOUNT}",
        f"AION_VAULT_TOKEN={token}",
        f"AION_ENV={AION_ENV}",
    ]
    ENV_FILE.write_text("\n".join(lines) + "\n")
    os.chmod(ENV_FILE, 0o600)


def main() -> None:
    print("[vault-bootstrap] Starting Vault dev bootstrap")
    run_compose()
    try:
        wait_for_vault(HOST_VAULT_ADDR, timeout=BOOTSTRAP_TIMEOUT)
    except TimeoutError:
        try:
            subprocess.run(
                ["docker", "compose", "logs", "--no-color", "vault"],
                cwd=REPO_ROOT,
                check=False,
            )
        except Exception:  # pragma: no cover - best effort diagnostics
            pass
        raise

    client = hvac.Client(url=HOST_VAULT_ADDR)
    creds = initialise_and_unseal(client)
    if creds.get("root_token"):
        client.token = creds["root_token"]
        persist_dev_material(creds)
    elif client.token is None:
        if UNSEAL_FILE.exists():
            stored = json.loads(UNSEAL_FILE.read_text())
            token = stored.get("root_token")
            if token:
                client.token = token
    if not client.is_authenticated():
        raise SystemExit("Vault bootstrap requires a root token; check .vault/dev-unseal.json")

    ensure_kv_mount(client)
    ensure_policy(client)
    dev_secrets = dict(BASE_DEV_SECRETS)
    dev_secrets.update(generate_tls_materials())
    seed_dev_secrets(client, dev_secrets)
    dev_token = ensure_dev_token(client)
    write_env_file(dev_token)

    print(f"[vault-bootstrap] Wrote development token to {ENV_FILE.relative_to(REPO_ROOT)}")
    print("[vault-bootstrap] Store generated TLS material securely and replace placeholders in Vault.")

if __name__ == "__main__":
    try:
        main()
    except Exception as error:  # pragma: no cover - developer feedback
        sys.stderr.write(f"[vault-bootstrap] Error: {error}\n")
        sys.exit(1)
