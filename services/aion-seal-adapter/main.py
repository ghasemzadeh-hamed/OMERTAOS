from fastapi import FastAPI

from .trainer import run_seal_iteration

app = FastAPI(title="AION SEAL Adapter", version="1.0.0")


@app.post("/run")
def run_once() -> dict:
    return run_seal_iteration()
