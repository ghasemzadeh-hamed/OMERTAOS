"""FastAPI router modules for the headless control plane."""
from control.os.api.providers import router as providers_router
from control.os.api.router import router as router_policy_router
from control.os.api.datasources import router as datasources_router
from control.os.api.modules import router as modules_router
from control.os.api.health import router as health_router
from control.os.api.webhooks import router as webhook_router
from control.os.api.registry import router as registry_router
from control.os.api.agent_catalog import catalog_router, agents_router
from control.os.api.recommendations import recommendations_router
from control.os.api.feature_catalog import router as feature_catalog_router

__all__ = [
    "providers_router",
    "router_policy_router",
    "datasources_router",
    "modules_router",
    "health_router",
    "webhook_router",
    "registry_router",
    "recommendations_router",
    "catalog_router",
    "agents_router",
    "feature_catalog_router",
]
