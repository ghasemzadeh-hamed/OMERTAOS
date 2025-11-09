"""Provisioning control-plane endpoints for on-demand capabilities."""
from __future__ import annotations

import json
import logging
import os
import socket
import subprocess
import time
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, List, Mapping

import yaml
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from urllib.request import urlopen
from urllib.error import URLError
from jinja2 import Template


router = APIRouter(prefix="/provision", tags=["provision"])


REPO_ROOT = Path(__file__).resolve().parents[4]
REGISTRY_PATH = REPO_ROOT / "registry" / "capabilities.yaml"
POLICY_PATH = REPO_ROOT / "policies" / "consent.yaml"
PROVISION_ROOT = REPO_ROOT / ".provision"
LOCK_PATH = PROVISION_ROOT / "lock.json"
LOG_PATH = REPO_ROOT / "logs" / "provisioner.log"


logger = logging.getLogger("aionos.provisioner")
if not logger.handlers:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(LOG_PATH)
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class EnsureRequest(BaseModel):
    """Request payload for the ensure endpoint."""

    capability_id: str
    tenant: str | None = None
    params: dict[str, Any] | None = None


@dataclass
class Capability:
    """Represents a capability entry pulled from the registry."""

    capability_id: str
    payload: Mapping[str, Any]

    @property
    def provider(self) -> str:
        return str(self.payload.get("provider", "")).strip()

    @property
    def template(self) -> str | None:
        template = self.payload.get("template")
        return str(template) if template is not None else None

    @property
    def env(self) -> Dict[str, Any]:
        return dict(self.payload.get("env", {}) or {})

    @property
    def vault_env(self) -> Dict[str, str]:
        return dict(self.payload.get("vault_env", {}) or {})

    @property
    def health(self) -> Dict[str, Any]:
        return dict(self.payload.get("health", {}) or {})

    @property
    def depends_on(self) -> List[str]:
        raw = self.payload.get("depends_on", [])
        if raw is None:
            return []
        if isinstance(raw, (list, tuple)):
            return [str(item) for item in raw]
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="depends_on must be a list")


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"configuration not found: {path}")
    try:
        data = yaml.safe_load(path.read_text()) or {}
    except yaml.YAMLError as exc:  # pragma: no cover - validation
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"failed to parse {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"invalid structure in {path}")
    return data


def _load_policy() -> dict[str, Any]:
    return _load_yaml(POLICY_PATH)


def _load_registry() -> dict[str, Capability]:
    data = _load_yaml(REGISTRY_PATH)
    capabilities: dict[str, Capability] = {}
    for key, payload in (data.get("capabilities") or {}).items():
        capabilities[key] = Capability(capability_id=key, payload=payload or {})
    return capabilities


def _consent_mode(policy: Mapping[str, Any], capability_id: str) -> str:
    caps = policy.get("capabilities") or {}
    cap_entry = caps.get(capability_id) or {}
    if isinstance(cap_entry, Mapping):
        mode = cap_entry.get("mode")
        if isinstance(mode, str):
            return mode.upper()
    global_mode = (policy.get("global") or {}).get("default_mode", "AUTO")
    return str(global_mode).upper()


def _auto_on_no_messaging(policy: Mapping[str, Any]) -> bool:
    global_section = policy.get("global") or {}
    value = global_section.get("auto_on_no_messaging", True)
    return bool(value)


def _load_from_vault(ref: str) -> str:
    path, field = ref.split("#", 1)
    env_key = field.upper()
    value = os.environ.get(env_key)
    if value:
        return value
    logger.warning("Vault lookup for %s unresolved; returning placeholder", ref)
    return "CHANGEME"


def _render_template(template_path: Path, env: Mapping[str, Any], vault_env: Mapping[str, str]) -> str:
    try:
        template = Template(template_path.read_text())
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"template missing: {template_path}") from exc

    render_env: dict[str, Any] = dict(env)
    for key, ref in vault_env.items():
        render_env[key] = _load_from_vault(ref)
    return template.render(**render_env)


def _run_command(cmd: list[str]) -> None:
    try:
        subprocess.check_call(cmd)
    except FileNotFoundError as exc:  # pragma: no cover - runtime environment
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"command not found: {cmd[0]}") from exc
    except subprocess.CalledProcessError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"command failed: {' '.join(cmd)}") from exc


def _health_ok(health: Mapping[str, Any], env: Mapping[str, Any]) -> bool:
    if not health:
        return False

    if "url" in health:
        target = Template(str(health["url"])).render(**env)
        try:
            with urlopen(target, timeout=3) as response:  # nosec B310 - controlled URL
                payload = response.read()
        except URLError:
            return False
        expect = health.get("expect_json")
        if not expect:
            return True
        try:
            data = json.loads(payload.decode("utf-8"))
        except Exception:
            return False
        return all(data.get(key) == value for key, value in expect.items())

    if "tcp" in health:
        endpoints = health["tcp"]
        if not isinstance(endpoints, (list, tuple, set)):
            return False
        for entry in endpoints:
            rendered = Template(str(entry)).render(**env)
            host, _, port = rendered.partition(":")
            try:
                with socket.create_connection((host, int(port)), timeout=2):
                    pass
            except Exception:
                return False
        return True

    return False


def _update_lock(capability_id: str, template_digest: str) -> None:
    PROVISION_ROOT.mkdir(parents=True, exist_ok=True)
    lock_data: dict[str, Any] = {}
    if LOCK_PATH.exists():
        try:
            lock_data = json.loads(LOCK_PATH.read_text())
        except Exception:  # pragma: no cover - corrupted lock file
            lock_data = {}
    lock_data[capability_id] = {
        "template_digest": template_digest,
        "timestamp": time.time(),
    }
    LOCK_PATH.write_text(json.dumps(lock_data, indent=2, sort_keys=True))


def _compose_up(capability: Capability, env: Mapping[str, Any]) -> None:
    template_rel = capability.template
    if not template_rel:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="docker compose template not defined")
    template_path = (REPO_ROOT / template_rel).resolve()
    rendered = _render_template(template_path, env, capability.vault_env)
    output_path = PROVISION_ROOT / f"{capability.capability_id}.compose.yml"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered)

    template_digest = sha256(rendered.encode("utf-8")).hexdigest()
    _update_lock(capability.capability_id, template_digest)

    health_defined = bool(capability.health)
    if health_defined and _health_ok(capability.health, env):
        return

    _run_command(["docker", "compose", "-f", str(output_path), "up", "-d"])

    if not health_defined:
        return

    for _ in range(60):
        if _health_ok(capability.health, env):
            return
        time.sleep(2)

    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"capability {capability.capability_id} failed to become healthy")


def _ensure_capability(capabilities: Mapping[str, Capability], capability_id: str, params: Mapping[str, Any] | None, seen: set[str]) -> dict[str, Any]:
    if capability_id in seen:
        return {"status": "ok", "already_running": True}
    seen.add(capability_id)

    capability = capabilities.get(capability_id)
    if capability is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"capability not found: {capability_id}")

    env = capability.env.copy()
    if params:
        env.update(params)

    for dependency in capability.depends_on:
        _ensure_capability(capabilities, dependency, params, seen)

    if capability.provider == "docker_compose":
        already_running = _health_ok(capability.health, env)
        _compose_up(capability, env)
        return {"status": "ok", "already_running": already_running}

    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=f"unsupported provider: {capability.provider}")


@router.post("/ensure")
def ensure_endpoint(request: EnsureRequest) -> dict[str, Any]:
    policy = _load_policy()
    capabilities = _load_registry()

    mode = _consent_mode(policy, request.capability_id)
    if mode == "DENY":
        logger.info("Consent denied for capability %s", request.capability_id)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Denied by policy")
    if mode == "ASK":
        logger.info("Consent ASK for capability %s (auto=%s)", request.capability_id, _auto_on_no_messaging(policy))
        if not _auto_on_no_messaging(policy):
            raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED, detail="Consent required")

    result = _ensure_capability(capabilities, request.capability_id, request.params, seen=set())
    result["capability"] = request.capability_id
    logger.info(
        "Provisioned capability %s (already_running=%s)",
        request.capability_id,
        result.get("already_running"),
    )
    return result
