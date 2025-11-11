"""FastAPI server exposing process analytics capabilities."""

from fastapi import FastAPI

from .routers import analytics, decisions, events

app = FastAPI(title="OMERTAOS Process Analytics API")

app.include_router(events.router, prefix="/events", tags=["events"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
app.include_router(decisions.router, prefix="/decisions", tags=["decisions"])
