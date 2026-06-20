from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from observability.audit import emit_audit
from shared.secret_store.provider import SecretProviderError, get_secret_provider

from .healthcheck import test_profile
from .models import ProxyProfile
from .schemas import ProxyProfileCreate, ProxyProfileOut, ProxyProfileUpdate, ProxySecrets

SENSITIVE_FIELDS = ("uuid", "password", "private_key", "public_key", "short_id")


class LocalSecretProvider:
    def __init__(self) -> None:
        root = Path(os.getenv("AION_CONTROL_SECRET_DIR", ".aion/secrets"))
        root.mkdir(parents=True, exist_ok=True)
        self.root = root

    def _file(self, path: str) -> Path:
        safe = path.strip("/").replace("/", "__")
        return self.root / f"{safe}.json"

    def get_secret(self, path: str) -> dict[str, str]:
        secret_file = self._file(path)
        if not secret_file.exists():
            raise SecretProviderError(f"Secret not found at '{path}'")
        return json.loads(secret_file.read_text(encoding="utf-8"))

    def set_secret(self, path: str, payload: dict[str, str]) -> None:
        secret_file = self._file(path)
        secret_file.write_text(json.dumps(payload), encoding="utf-8")
        try:
            secret_file.chmod(0o600)
        except OSError:
            pass

    def delete_secret(self, path: str) -> None:
        self._file(path).unlink(missing_ok=True)


def _secret_provider():
    if os.getenv("AION_CONTROL_DISABLE_SECRETS", "1") == "1":
        return LocalSecretProvider()
    provider = get_secret_provider()
    if not hasattr(provider, "set_secret"):
        raise SecretProviderError("Configured secret provider cannot write proxy secrets")
    return provider


def _secret_path(profile_id: int) -> str:
    prefix = os.getenv("AION_PROXY_SECRET_PREFIX", "aion/network/proxy-profiles")
    return f"{prefix.strip('/')}/{profile_id}"


def _materialise_secrets(secrets: ProxySecrets | None) -> dict[str, str]:
    if not secrets:
        return {}
    payload = secrets.model_dump(exclude_none=True)
    return {key: value for key, value in payload.items() if key in SENSITIVE_FIELDS and value}


def _store_secrets(profile: ProxyProfile, secrets: ProxySecrets | None) -> None:
    payload = _materialise_secrets(secrets)
    if not payload:
        return
    path = profile.secret_ref or _secret_path(profile.id)
    _secret_provider().set_secret(path, payload)
    profile.secret_ref = path


def _delete_secrets(profile: ProxyProfile) -> None:
    if profile.secret_ref:
        try:
            _secret_provider().delete_secret(profile.secret_ref)
        except Exception:
            pass


def _to_out(profile: ProxyProfile) -> ProxyProfileOut:
    return ProxyProfileOut(
        id=profile.id,
        name=profile.name,
        type=profile.type,
        enabled=profile.enabled,
        scope=profile.scope,
        host=profile.host,
        port=profile.port,
        transport=profile.transport,
        security=profile.security,
        sni=profile.sni,
        flow=profile.flow,
        path=profile.path,
        fallback_direct=profile.fallback_direct,
        health_check_url=profile.health_check_url,
        is_default=profile.is_default,
        has_secrets=bool(profile.secret_ref),
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


def list_profiles(db: Session, active_only: bool = False) -> list[ProxyProfileOut]:
    query = select(ProxyProfile).order_by(ProxyProfile.scope, ProxyProfile.name)
    if active_only:
        query = query.where(ProxyProfile.enabled.is_(True))
    return [_to_out(row) for row in db.scalars(query).all()]


def resolve_proxy_environment(db: Session, scope: str = "global") -> dict[str, str]:
    profile = db.scalars(
        select(ProxyProfile)
        .where(ProxyProfile.scope.in_([scope, "global"]))
        .where(ProxyProfile.enabled.is_(True))
        .where(ProxyProfile.is_default.is_(True))
        .order_by(desc(ProxyProfile.scope == scope))
    ).first()
    if not profile or profile.type == "direct":
        return {}
    if profile.type == "http":
        proxy = f"http://{profile.host}:{profile.port}"
        return {"HTTP_PROXY": proxy, "HTTPS_PROXY": proxy}
    if profile.type == "socks5":
        return {"ALL_PROXY": f"socks5://{profile.host}:{profile.port}"}
    if profile.type == "vless":
        return {
            "HTTP_PROXY": "http://proxy-router:10809",
            "HTTPS_PROXY": "http://proxy-router:10809",
            "ALL_PROXY": "socks5://proxy-router:10808",
        }
    return {}


def get_profile(db: Session, profile_id: int) -> ProxyProfile | None:
    return db.get(ProxyProfile, profile_id)


def get_profile_out(profile: ProxyProfile) -> ProxyProfileOut:
    return _to_out(profile)


def create_profile(db: Session, payload: ProxyProfileCreate, actor: str, tenant_id: str) -> ProxyProfileOut:
    profile = ProxyProfile(**payload.model_dump(exclude={"secrets"}))
    db.add(profile)
    db.flush()
    _store_secrets(profile, payload.secrets)
    db.commit()
    db.refresh(profile)
    emit_audit("network.proxy_profile.create", actor, tenant_id)
    return _to_out(profile)


def update_profile(
    db: Session,
    profile: ProxyProfile,
    payload: ProxyProfileUpdate,
    actor: str,
    tenant_id: str,
) -> ProxyProfileOut:
    updates = payload.model_dump(exclude_unset=True, exclude={"secrets"})
    for key, value in updates.items():
        setattr(profile, key, value.value if hasattr(value, "value") else value)
    _store_secrets(profile, payload.secrets)
    profile.updated_at = datetime.now(UTC)
    db.commit()
    db.refresh(profile)
    emit_audit("network.proxy_profile.update", actor, tenant_id)
    return _to_out(profile)


def delete_profile(db: Session, profile: ProxyProfile, actor: str, tenant_id: str) -> None:
    _delete_secrets(profile)
    db.delete(profile)
    db.commit()
    emit_audit("network.proxy_profile.delete", actor, tenant_id)


def set_enabled(db: Session, profile: ProxyProfile, enabled: bool, actor: str, tenant_id: str) -> ProxyProfileOut:
    profile.enabled = enabled
    profile.updated_at = datetime.now(UTC)
    db.commit()
    db.refresh(profile)
    emit_audit(f"network.proxy_profile.{'enable' if enabled else 'disable'}", actor, tenant_id)
    return _to_out(profile)


def set_default(db: Session, profile: ProxyProfile, actor: str, tenant_id: str) -> ProxyProfileOut:
    for current in db.scalars(select(ProxyProfile).where(ProxyProfile.scope == profile.scope)).all():
        current.is_default = current.id == profile.id
    profile.enabled = True
    db.commit()
    db.refresh(profile)
    emit_audit("network.proxy_profile.set_default", actor, tenant_id)
    return _to_out(profile)


async def run_test(profile: ProxyProfile, actor: str, tenant_id: str, target_url: str | None = None) -> dict[str, object]:
    result = await test_profile(profile, target_url)
    emit_audit("network.proxy_profile.test", actor, tenant_id)
    return result
