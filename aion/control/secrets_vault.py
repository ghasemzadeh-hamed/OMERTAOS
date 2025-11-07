from __future__ import annotations

import json
import os
import pathlib
import hashlib
from typing import Any, Dict


class Vault:
    """Simple abstraction over file-based or HashiCorp Vault secrets storage."""

    def __init__(self, cfg: Dict[str, Any]):
        self.cfg = cfg
        self.provider = cfg.get("provider", "file")

    # Public API -----------------------------------------------------------------
    def get(self, path: str) -> Dict[str, Any]:
        if self.provider == "file":
            return self._file_get(path)
        return self._hv_get(path)

    def put(self, path: str, data: Dict[str, Any]) -> None:
        if self.provider == "file":
            self._file_put(path, data)
        else:
            self._hv_put(path, data)

    # File provider ---------------------------------------------------------------
    def _key(self) -> bytes:
        raw_key = os.environ.get("AION_VAULT_KEY")
        if not raw_key:
            raise RuntimeError("AION_VAULT_KEY missing")
        return hashlib.sha256(raw_key.encode()).digest()[:32]

    def _file_path(self) -> pathlib.Path:
        return pathlib.Path(self.cfg["file"]["path"]).expanduser()

    def _file_load(self) -> Dict[str, Any]:
        path = self._file_path()
        if not path.exists():
            return {}
        blob = path.read_bytes()
        if not blob:
            return {}
        if len(blob) < 28:
            raise RuntimeError("Vault file corrupted: nonce/tag missing")
        from Crypto.Cipher import AES

        nonce, tag, ct = blob[:12], blob[12:28], blob[28:]
        cipher = AES.new(self._key(), AES.MODE_GCM, nonce=nonce)
        data = cipher.decrypt_and_verify(ct, tag)
        return json.loads(data.decode())

    def _file_dump(self, payload: Dict[str, Any]) -> None:
        from Crypto.Cipher import AES

        cipher = AES.new(self._key(), AES.MODE_GCM)
        data = json.dumps(payload).encode()
        ciphertext, tag = cipher.encrypt_and_digest(data)
        payload_bytes = cipher.nonce + tag + ciphertext
        path = self._file_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload_bytes)

    def _file_get(self, path: str) -> Dict[str, Any]:
        data = self._file_load()
        return data.get(path, {})

    def _file_put(self, path: str, payload: Dict[str, Any]) -> None:
        data = self._file_load()
        data[path] = payload
        self._file_dump(data)

    # HashiCorp provider ----------------------------------------------------------
    def _hv_client(self):  # pragma: no cover - optional dependency
        import hvac

        addr = self.cfg["hashicorp"]["addr"]
        token = self.cfg["hashicorp"].get("token")
        return hvac.Client(url=addr, token=token)

    def _hv_get(self, path: str) -> Dict[str, Any]:  # pragma: no cover - optional
        mount = self.cfg["hashicorp"]["mount"]
        response = self._hv_client().secrets.kv.v2.read_secret_version(
            mount_point=mount, path=path
        )
        return response["data"]["data"]

    def _hv_put(self, path: str, payload: Dict[str, Any]) -> None:  # pragma: no cover
        mount = self.cfg["hashicorp"]["mount"]
        self._hv_client().secrets.kv.v2.create_or_update_secret(
            mount_point=mount, path=path, secret=payload
        )
