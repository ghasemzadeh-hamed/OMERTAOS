"""FastAPI routes for interacting with the plugin registry."""
from fastapi import APIRouter, HTTPException

from ..plugins.registry import REGISTRY
from .schemas import PluginCallRequest

router = APIRouter(prefix="/plugins", tags=["plugins"])
_DEFAULT_HINT = "see pyproject optional-dependencies"


@router.get("/")
def list_plugins() -> dict[str, list[str]]:
    """Return a sorted list of available plugin keys."""
    return {"available": sorted(REGISTRY.keys())}


@router.post("/call")
def call_plugin(request: PluginCallRequest):
    """Invoke a plugin entry point if it exists."""
    name = request.name.lower().strip()
    if not name:
        raise HTTPException(status_code=400, detail="Plugin name is required")
    if name not in REGISTRY:
        raise HTTPException(status_code=404, detail=f"Plugin '{name}' not registered")

    entry = REGISTRY[name]
    try:
        module = entry.module
    except RuntimeError as exc:
        raise HTTPException(status_code=424, detail=str(exc)) from exc

    if not hasattr(module, "aion_entry"):
        return {"status": "loaded", "note": "module loaded; no 'aion_entry' exported"}

    params = request.params or {}
    try:
        return module.aion_entry(**params)
    except ModuleNotFoundError as exc:  # pragma: no cover - relies on optional deps
        hint = entry.extra_hint or _DEFAULT_HINT
        raise HTTPException(
            status_code=424,
            detail=f"Missing dependency for plugin '{name}'. Install extras: {hint}",
        ) from exc
    except TypeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
