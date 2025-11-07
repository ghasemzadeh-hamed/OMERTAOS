"""FastAPI router modules for the headless control plane."""
from app.control.app.api.providers import router as providers_router
from app.control.app.api.router import router as router_policy_router
from app.control.app.api.datasources import router as datasources_router
from app.control.app.api.modules import router as modules_router
from app.control.app.api.health import router as health_router
from app.control.app.api.webhooks import router as webhook_router

__all__ = [
    "providers_router",
    "router_policy_router",
    "datasources_router",
    "modules_router",
    "health_router",
    "webhook_router",
]
