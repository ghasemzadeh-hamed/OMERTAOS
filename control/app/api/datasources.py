"""Datasource management endpoints."""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException

from ..core.deps import get_state
from ..core.state import ControlState, DataSource
from ..schemas.datasource import DataSourceCreate, DataSourceOut

router = APIRouter(prefix="/api/datasources", tags=["datasources"])


@router.post("", response_model=DataSourceOut, status_code=201)
async def add_datasource(
    payload: DataSourceCreate,
    state: ControlState = Depends(get_state),
) -> DataSourceOut:
    datasource = DataSource(
        name=payload.name,
        kind=payload.kind,
        dsn=payload.dsn,
    )
    await state.add_datasource(datasource)
    return DataSourceOut(**payload.dict(), enabled=True)


@router.get("", response_model=List[DataSourceOut])
async def list_datasources(state: ControlState = Depends(get_state)) -> List[DataSourceOut]:
    return [DataSourceOut(**datasource.__dict__) for datasource in state.datasources.values()]


@router.get("/{name}/health")
async def datasource_health(name: str, state: ControlState = Depends(get_state)) -> dict:
    datasource = state.datasources.get(name)
    if datasource is None:
        raise HTTPException(status_code=404, detail="datasource not found")
    return {"status": "ok" if datasource.enabled else "disabled"}
