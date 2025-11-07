"""FastAPI router modules for the headless control plane."""
from os.control.os.api.providers import router as providers_router
from os.control.os.api.router import router as router_policy_router
from os.control.os.api.datasources import router as datasources_router
from os.control.os.api.modules import router as modules_router
from os.control.os.api.health import router as health_router
from os.control.os.api.webhooks import router as webhook_router

__all__ = [
    "providers_router",
    "router_policy_router",
    "datasources_router",
    "modules_router",
    "health_router",
    "webhook_router",
]
