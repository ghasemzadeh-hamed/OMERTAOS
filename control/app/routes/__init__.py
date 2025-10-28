"""FastAPI routers for control plane services."""

from .admin_onboarding import router as admin_onboarding_router
from .kernel_proposals import router as kernel_router
from .memory import router as memory_router
from .models import router as models_router

__all__ = [
    "admin_onboarding_router",
    "kernel_router",
    "memory_router",
    "models_router",
]
