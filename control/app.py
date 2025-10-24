from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

REGISTRY_PATH = Path("bigdata/models/registry.yaml")
POLICY_PATH = Path("bigdata/models/policy.sample.json")
ACTIVITY_LOG = Path("logs/activity.log")

app = FastAPI(title="AION Control Plane")


class PolicyReloadRequest(BaseModel):
    version: Optional[str] = None


class PolicyState(BaseModel):
    version: str
    artifact: Path


state: Optional[PolicyState] = None
previous_state: Optional[PolicyState] = None


@app.on_event("startup")
async def bootstrap() -> None:
    ACTIVITY_LOG.parent.mkdir(parents=True, exist_ok=True)
    await reload_policy(PolicyReloadRequest())


@app.post("/router/policy/reload")
async def reload_policy(request: PolicyReloadRequest) -> dict:
    global state, previous_state

    registry_entries = _load_registry()
    target = None
    if request.version:
        target = next((entry for entry in registry_entries if entry["version"] == request.version), None)
    if target is None and registry_entries:
        target = registry_entries[-1]

    artifact_path = Path(POLICY_PATH if target is None else target["artifact"])
    if not artifact_path.exists():
        artifact_path = POLICY_PATH

    try:
        content = json.loads(artifact_path.read_text())
    except json.JSONDecodeError as exc:
        if previous_state:
            state, previous_state = previous_state, state
        raise HTTPException(status_code=400, detail=f"Invalid policy: {exc}") from exc

    previous_state = state
    state = PolicyState(version=content.get("version", "unknown"), artifact=artifact_path)
    _record_activity(actor_id="system", action="router_policy_reload", meta={"version": state.version})
    return {"status": "ok", "version": state.version}


@app.post("/router/policy/rollback")
async def rollback_policy() -> dict:
    global state, previous_state
    if previous_state is None:
        raise HTTPException(status_code=400, detail="No previous policy to rollback to")
    state, previous_state = previous_state, state
    _record_activity(actor_id="system", action="router_policy_rollback", meta={"version": state.version})
    return {"status": "ok", "version": state.version}


def _load_registry() -> list:
    if not REGISTRY_PATH.exists():
        return []
    entries: list = []
    version: Optional[str] = None
    artifact: Optional[str] = None
    for line in REGISTRY_PATH.read_text().splitlines():
        line = line.strip()
        if line.startswith("- version"):
            if version and artifact:
                entries.append({"version": version, "artifact": artifact})
            version = line.split(":", 1)[1].strip()
            artifact = None
        elif line.startswith("artifact"):
            artifact = line.split(":", 1)[1].strip()
    if version and artifact:
        entries.append({"version": version, "artifact": artifact})
    return entries


def _record_activity(actor_id: str, action: str, meta: dict) -> None:
    ACTIVITY_LOG.parent.mkdir(parents=True, exist_ok=True)
    with ACTIVITY_LOG.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({
            "actor_id": actor_id,
            "entity_type": "router_policy",
            "entity_id": action,
            "action": action,
            "meta": meta,
        }) + "\n")
