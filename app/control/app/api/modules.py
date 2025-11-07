"""Module management endpoints."""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException

from app.control.app.core.deps import get_state
from app.control.app.core.state import ControlState, Module
from app.control.app.schemas.module import ModuleManifest, ModuleOut

router = APIRouter(prefix="/api/modules", tags=["modules"])


@router.post("", response_model=ModuleOut, status_code=201)
async def add_module(
    manifest: ModuleManifest,
    state: ControlState = Depends(get_state),
) -> ModuleOut:
    module = Module(
        name=manifest.name,
        version=manifest.version,
        description=manifest.description or "",
    )
    await state.add_module(module)
    return ModuleOut(**manifest.dict(), enabled=True)


@router.post("/{name}/enable", response_model=ModuleOut)
async def enable_module(name: str, state: ControlState = Depends(get_state)) -> ModuleOut:
    if name not in state.modules:
        raise HTTPException(status_code=404, detail="module not found")
    state.modules[name].enabled = True
    module = state.modules[name]
    return ModuleOut(**module.__dict__)


@router.post("/{name}/upgrade")
async def upgrade_module(name: str, state: ControlState = Depends(get_state)) -> dict:
    if name not in state.modules:
        raise HTTPException(status_code=404, detail="module not found")
    return {"status": "ok", "message": f"module {name} upgrade simulated"}


@router.post("/{name}/rollback")
async def rollback_module(name: str, state: ControlState = Depends(get_state)) -> dict:
    if name not in state.modules:
        raise HTTPException(status_code=404, detail="module not found")
    return {"status": "ok", "message": f"module {name} rollback simulated"}


@router.get("", response_model=List[ModuleOut])
async def list_modules(state: ControlState = Depends(get_state)) -> List[ModuleOut]:
    return [ModuleOut(**module.__dict__) for module in state.modules.values()]


@router.get("/{name}/health")
async def module_health(name: str, state: ControlState = Depends(get_state)) -> dict:
    module = state.modules.get(name)
    if module is None:
        raise HTTPException(status_code=404, detail="module not found")
    return {"status": "ok" if module.enabled else "disabled"}
