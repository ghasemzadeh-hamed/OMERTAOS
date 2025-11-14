#!/usr/bin/env python3
"""Generate short-lived development certificates when Vault is disabled."""
from __future__ import annotations

import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CERT_ROOT = ROOT / "config" / "certs"
DEV_DIR = CERT_ROOT / "dev"
MARKER = DEV_DIR / ".generated"
CA_KEY = DEV_DIR / "dev-ca.key"
CA_CERT = DEV_DIR / "dev-ca.pem"
CONTROL_KEY = DEV_DIR / "control-server-key.pem"
CONTROL_CERT = DEV_DIR / "control-server-cert.pem"
GATEWAY_KEY = DEV_DIR / "gateway-client-key.pem"
GATEWAY_CERT = DEV_DIR / "gateway-client-cert.pem"
SERIAL = DEV_DIR / "dev-ca.srl"
VALID_DAYS = 14


def _run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def ensure_dev_directory() -> None:
    DEV_DIR.mkdir(parents=True, exist_ok=True)


def generate_ca() -> None:
    if CA_KEY.exists() and CA_CERT.exists():
        return
    _run(
        [
            "openssl",
            "req",
            "-x509",
            "-newkey",
            "rsa:4096",
            "-nodes",
            "-sha256",
            "-keyout",
            str(CA_KEY),
            "-out",
            str(CA_CERT),
            "-days",
            str(VALID_DAYS),
            "-subj",
            "/CN=AIONOS Dev CA",
        ]
    )


def _write_ext_file(*lines: str) -> str:
    config = tempfile.NamedTemporaryFile("w", delete=False)
    try:
        for line in lines:
            config.write(line + "\n")
        return config.name
    finally:
        config.close()


def issue_server_certificate() -> None:
    if CONTROL_KEY.exists() and CONTROL_CERT.exists():
        return
    csr = DEV_DIR / "control-server.csr"
    _run(
        [
            "openssl",
            "req",
            "-new",
            "-newkey",
            "rsa:4096",
            "-nodes",
            "-sha256",
            "-keyout",
            str(CONTROL_KEY),
            "-out",
            str(csr),
            "-subj",
            "/CN=control.dev.aionos",
        ]
    )
    ext_file = _write_ext_file(
        "subjectAltName=DNS:control.dev.aionos,IP:127.0.0.1",
        "extendedKeyUsage=serverAuth",
        "keyUsage=digitalSignature,keyEncipherment",
        "basicConstraints=CA:false",
    )
    try:
        _run(
            [
                "openssl",
                "x509",
                "-req",
                "-sha256",
                "-in",
                str(csr),
                "-CA",
                str(CA_CERT),
                "-CAkey",
                str(CA_KEY),
                "-CAcreateserial",
                "-CAserial",
                str(SERIAL),
                "-out",
                str(CONTROL_CERT),
                "-days",
                str(VALID_DAYS),
                "-extfile",
                ext_file,
            ]
        )
    finally:
        Path(ext_file).unlink(missing_ok=True)
        csr.unlink(missing_ok=True)


def issue_client_certificate() -> None:
    if GATEWAY_KEY.exists() and GATEWAY_CERT.exists():
        return
    csr = DEV_DIR / "gateway-client.csr"
    _run(
        [
            "openssl",
            "req",
            "-new",
            "-newkey",
            "rsa:4096",
            "-nodes",
            "-sha256",
            "-keyout",
            str(GATEWAY_KEY),
            "-out",
            str(csr),
            "-subj",
            "/CN=gateway.dev.aionos",
        ]
    )
    ext_file = _write_ext_file(
        "extendedKeyUsage=clientAuth",
        "keyUsage=digitalSignature",
        "basicConstraints=CA:false",
    )
    try:
        _run(
            [
                "openssl",
                "x509",
                "-req",
                "-sha256",
                "-in",
                str(csr),
                "-CA",
                str(CA_CERT),
                "-CAkey",
                str(CA_KEY),
                "-CAserial",
                str(SERIAL),
                "-out",
                str(GATEWAY_CERT),
                "-days",
                str(VALID_DAYS),
                "-extfile",
                ext_file,
            ]
        )
    finally:
        Path(ext_file).unlink(missing_ok=True)
        csr.unlink(missing_ok=True)


def write_marker() -> None:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    MARKER.write_text(f"generated_at={timestamp}\nvalid_days={VALID_DAYS}\n", encoding="ascii")


def main() -> int:
    ensure_dev_directory()
    generate_ca()
    issue_server_certificate()
    issue_client_certificate()
    write_marker()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except subprocess.CalledProcessError as exc:
        print(f"Failed to generate development certificates: {exc}", file=sys.stderr)
        sys.exit(exc.returncode)
