"""FastAPI routers for control plane services."""

from .admin_onboarding import router as admin_onboarding_router
from .ai_chat import router as ai_chat_router
from .agent import router as agent_router
from .kernel_proposals import router as kernel_router
from .memory import router as memory_router
from .models import router as models_router
from .rag import router as rag_router

__all__ = [
    "admin_onboarding_router",
    "ai_chat_router",
    "agent_router",
    "kernel_router",
    "memory_router",
    "models_router",
    "rag_router",
]
