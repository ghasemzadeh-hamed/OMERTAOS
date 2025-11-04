import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse

from .profiles import load_profile
from .router import decide

load_dotenv()

ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")
CONFIGS_DIR = Path(os.getenv("CONFIGS_DIR", "./configs")).resolve()
PROFILE_NAME = os.getenv("PROFILE", "user")
BASE_DIR = Path(__file__).resolve().parents[3]
STATE: Dict[str, Any] = {"pending": None, "active": None, "history": []}


def check_auth(header: Optional[str]) -> bool:
    if not ADMIN_TOKEN:
        return True
    if not header or not header.startswith("Bearer "):
        return False
    return header[7:] == ADMIN_TOKEN


def write_pending(item: Dict[str, Any]) -> None:
    CONFIGS_DIR.mkdir(parents=True, exist_ok=True)
    target = CONFIGS_DIR / "pending.json"
    target.write_text(json.dumps(item, indent=2))


def propose_patch(patch: Dict[str, Any], ttl_sec: int = 900) -> Dict[str, Any]:
    now = time.time()
    pending = {
        "ts": now,
        "patch": patch,
        "ttl": now + ttl_sec,
        "state": "proposed"
    }
    STATE["pending"] = pending
    return {"ok": True, "pending": pending}


def apply_pending() -> Dict[str, Any]:
    pending = STATE.get("pending")
    if not pending:
        return {"ok": False, "error": "no pending"}
    pending["state"] = "applied"
    write_pending(pending)
    STATE["active"] = pending
    history = STATE.setdefault("history", [])
    history.append(pending)
    STATE["pending"] = None
    return {"ok": True, "active": pending}


def revert_active() -> Dict[str, Any]:
    if not STATE.get("active"):
        return {"ok": False, "error": "no active"}
    STATE["active"] = None
    target = CONFIGS_DIR / "pending.json"
    if target.exists():
        target.unlink()
    return {"ok": True}


def build_app() -> FastAPI:
    app = FastAPI(title="OMERTAOS Control", version="0.2.0")

    @app.get("/healthz")
    async def healthz():
        profile = load_profile(PROFILE_NAME, str(BASE_DIR))
        mode = profile.get("features", {}).get("router", {}).get("default_mode", "auto")
        selected = decide(mode, {"local_ok": True, "api_ok": True})
        return {"ok": True, "profile": PROFILE_NAME, "router_mode": selected}

    @app.post("/v1/config/propose")
    async def propose(body: Dict[str, Any], authorization: Optional[str] = Header(default=None)):
        if not check_auth(authorization):
            raise HTTPException(status_code=403, detail="forbidden")
        ttl = int(body.pop("ttl_sec", 900))
        return JSONResponse(propose_patch(body, ttl))

    @app.post("/v1/config/apply")
    async def apply(authorization: Optional[str] = Header(default=None)):
        if not check_auth(authorization):
            raise HTTPException(status_code=403, detail="forbidden")
        return JSONResponse(apply_pending())

    @app.post("/v1/config/revert")
    async def revert(authorization: Optional[str] = Header(default=None)):
        if not check_auth(authorization):
            raise HTTPException(status_code=403, detail="forbidden")
        return JSONResponse(revert_active())

    @app.post("/v1/router/policy/reload")
    async def policy_reload(authorization: Optional[str] = Header(default=None)):
        if not check_auth(authorization):
            raise HTTPException(status_code=403, detail="forbidden")
        profile = load_profile(PROFILE_NAME, str(BASE_DIR))
        return {"ok": True, "profile": profile.get("name", PROFILE_NAME)}


    if PROFILE_NAME.lower() in ("ent", "enterprise", "enterprise-vip"):
        from ..seal.main import router as seal_router  # type: ignore
        app.include_router(seal_router)
    return app


def app() -> FastAPI:
    return build_app()
