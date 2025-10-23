from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlmodel.ext.asyncio.session import AsyncSession

from ..config import get_settings
from ..db import get_session
from ..models import ActivityLog
from ..schemas import TaskCreate, TaskDispatchResponse
from ..services.grpc_client import execute_local_module
from ..services.router import decide_route
from ..services.telemetry import push_event

router = APIRouter(prefix='/api/tasks', tags=['tasks'])
settings = get_settings()


async def require_internal_token(x_internal_token: str = Header(...)) -> None:
    if x_internal_token != settings.bridge_token:
        raise HTTPException(status_code=401, detail='Invalid bridge token')


@router.post('', response_model=TaskDispatchResponse, dependencies=[Depends(require_internal_token)])
async def create_task(
    payload: TaskCreate,
    session: AsyncSession = Depends(get_session),
) -> TaskDispatchResponse:
    decision = await decide_route(payload)
    await push_event(payload.task_id, 'queued', decision.reason)

    status = 'queued'

    if decision.decision == 'local':
        await push_event(payload.task_id, 'running', 'Dispatching to local module')
        execution = await execute_local_module(payload.task_id, payload.intent, payload.params)
        status = execution['status']
    else:
        await push_event(payload.task_id, 'running', 'Forwarded to external service')
        status = 'completed'

    await push_event(payload.task_id, status, 'Task finished')

    log = ActivityLog(
        actor_id=1,
        entity_type='task',
        entity_id=0,
        action='dispatch',
        meta={
            'decision': decision.decision,
            'intent': payload.intent,
            'status': status
        }
    )
    session.add(log)
    await session.commit()

    return TaskDispatchResponse(
        task_id=payload.task_id,
        decision=decision.decision,
        status=status,
        reason=decision.reason,
    )
