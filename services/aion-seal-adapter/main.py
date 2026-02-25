import logging

from fastapi import FastAPI

from .schemas import HealthResponse, SealRunResponse
from .trainer import run_seal_iteration

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

app = FastAPI(title="AION SEAL Adapter", version="1.0.0")


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", service="aion-seal-adapter")


@app.post("/run", response_model=SealRunResponse)
async def run_once() -> SealRunResponse:
    return SealRunResponse(**run_seal_iteration())
