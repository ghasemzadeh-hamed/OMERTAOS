"""FastAPI router modules for the headless control plane."""
from .providers import router as providers_router
from .router import router as router_policy_router
from .datasources import router as datasources_router
from .modules import router as modules_router
from .health import router as health_router
from .webhooks import router as webhook_router

__all__ = [
    "providers_router",
    "router_policy_router",
    "datasources_router",
    "modules_router",
    "health_router",
    "webhook_router",
]
