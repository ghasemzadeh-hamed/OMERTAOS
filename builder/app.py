"""Adapter builder service for external modules."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .adapter_generator.generator import AdapterGenerator


class VendorSpec(BaseModel):
    name: str
    version: str = Field(pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$")
    protocol: str = Field(pattern=r"^(rest|grpc)$")
    endpoint: str
    schema: Dict[str, object]
    target_intent: str


app = FastAPI(title="aionOS Adapter Builder", version="1.0.0")

generator = AdapterGenerator(output_dir=Path("artifacts"))


@app.post("/v1/builder/adapter")
def build_adapter(spec: VendorSpec):
    try:
        artifact = generator.generate(spec.dict())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return artifact
