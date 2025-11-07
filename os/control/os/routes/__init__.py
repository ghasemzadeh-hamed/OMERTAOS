"""FastAPI routers for control plane services."""

from os.control.os.routes.admin_onboarding import router as admin_onboarding_router
from os.control.os.routes.ai_chat import router as ai_chat_router
from os.control.os.routes.agent import router as agent_router
from os.control.os.routes.config import router as config_router
from os.control.os.routes.profile import router as profile_router
from os.control.os.routes.kernel_proposals import router as kernel_router
from os.control.os.routes.memory import router as memory_router
from os.control.os.routes.models import router as models_router
from os.control.os.routes.rag import router as rag_router

try:  # pragma: no cover - optional SEAL router
    from os.control.os.routes.seal import router as seal_router
except Exception:  # pragma: no cover
    from fastapi import APIRouter

    seal_router = APIRouter()

__all__ = [
    "admin_onboarding_router",
    "ai_chat_router",
    "agent_router",
    "config_router",
    "profile_router",
    "kernel_router",
    "memory_router",
    "models_router",
    "rag_router",
    "seal_router",
]
