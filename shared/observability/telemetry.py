from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TraceContext:
    trace_id: str
    span_id: str


def health(component: str) -> dict[str, str]:
    return {"status": "ok", "component": component}


def metric(name: str, value: float, **labels: str) -> dict[str, Any]:
    return {"name": name, "value": value, "labels": labels, "ts": time.time()}


def log(component: str, level: str, message: str, **fields: Any) -> str:
    payload = {"component": component, "level": level, "message": message, **fields, "ts": time.time()}
    return json.dumps(payload, sort_keys=True)
