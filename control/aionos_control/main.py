"""FastAPI application exposing plugin registry endpoints."""
from fastapi import FastAPI

from .routes import plugins

app = FastAPI(title="AION-OS Control")
app.include_router(plugins.router)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    """Health probe endpoint for readiness checks."""
    return {"status": "ok"}
