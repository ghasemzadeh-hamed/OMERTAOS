from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .db import init_db
from .routers import tasks

settings = get_settings()

app = FastAPI(title='AION Control Plane')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(tasks.router)


@app.on_event('startup')
async def startup_event():
    await init_db()


@app.get('/health')
async def health() -> dict[str, str]:
    return {'status': 'ok'}
