"""FastAPI application for the optional plugin control surface."""

from __future__ import annotations

from fastapi import FastAPI

from .routes.plugins import router as plugins_router

app = FastAPI(title="AION Control Plugins", version="1.0.0")
app.include_router(plugins_router)

__all__ = ["app"]
