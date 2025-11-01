"""Generic webhook intake endpoint."""
from __future__ import annotations

import base64
import hashlib
import hmac
import ipaddress
import json
import os
import time
from datetime import datetime
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, Request

from ..core.deps import get_state
from ..core.state import ControlState, generate_event_id
from ..schemas.webhook import WebhookEnvelope

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])

MAX_BODY_BYTES = int(os.getenv("AION_WEBHOOK_MAX_BYTES", "1048576"))
TIMESTAMP_SKEW = int(os.getenv("AION_WEBHOOK_MAX_SKEW", "300"))


@router.post("/{source}")
async def intake_webhook(
    source: str,
    request: Request,
    state: ControlState = Depends(get_state),
) -> dict:
    raw_body = await request.body()
    if len(raw_body) > MAX_BODY_BYTES:
        raise HTTPException(status_code=413, detail="payload too large")

    client_host = request.client.host if request.client else None
    _validate_ip(client_host)
    _validate_signature(request.headers, raw_body)
    payload_dict, event_type, event_id = _normalize_payload(raw_body, request.headers)
    if not event_id:
        event_id = generate_event_id(raw_body)
    if not state.check_idempotency(event_id):
        raise HTTPException(status_code=409, detail="duplicate event")

    envelope = WebhookEnvelope(
        source=source,
        event_type=event_type,
        event_id=event_id,
        occurred_at=datetime.utcnow(),
        headers=dict(request.headers),
        payload=payload_dict,
    )
    await state.enqueue_event(envelope.dict())
    return {"status": "queued", "event_id": event_id}


def _validate_ip(client_ip: str | None) -> None:
    allowlist = os.getenv("AION_WEBHOOK_ALLOWLIST")
    if not allowlist or client_ip is None:
        return
    client = ipaddress.ip_address(client_ip)
    for cidr in allowlist.split(","):
        cidr = cidr.strip()
        if not cidr:
            continue
        network = ipaddress.ip_network(cidr, strict=False)
        if client in network:
            return
    raise HTTPException(status_code=403, detail="ip not allowed")


def _validate_signature(headers: Dict[str, str], body: bytes) -> None:
    secret = os.getenv("AION_WEBHOOK_SECRET")
    signature = headers.get("x-signature") or headers.get("X-Signature")
    timestamp = headers.get("x-timestamp") or headers.get("X-Timestamp")
    if secret is None or signature is None or timestamp is None:
        return
    try:
        ts = int(timestamp)
    except ValueError as exc:  # pragma: no cover - invalid header
        raise HTTPException(status_code=400, detail="invalid timestamp") from exc
    if abs(time.time() - ts) > TIMESTAMP_SKEW:
        raise HTTPException(status_code=400, detail="timestamp skew too large")
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(digest, signature):
        raise HTTPException(status_code=401, detail="invalid signature")


def _normalize_payload(body: bytes, headers: Dict[str, str]) -> tuple[object, str, str]:
    content_type = headers.get("content-type", "application/json").split(";")[0]
    if content_type in {"application/json", "text/json"}:
        try:
            data = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            data = {"raw": body.decode("utf-8", errors="ignore")}
    elif content_type in {"application/x-www-form-urlencoded"}:
        from urllib.parse import parse_qs

        data = {k: v[0] if len(v) == 1 else v for k, v in parse_qs(body.decode("utf-8")).items()}
    else:
        data = base64.b64encode(body).decode("ascii")

    event_type = "unknown"
    event_id = ""
    if isinstance(data, dict):
        event_type = str(data.get("event")) if data.get("event") else data.get("event_type", "unknown")
        event_id = str(data.get("event_id") or data.get("id") or "")
    return data, event_type or "unknown", event_id
