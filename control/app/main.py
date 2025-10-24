import asyncio
import json
import time
from uuid import uuid4

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from redis.asyncio import Redis
from sqlmodel import select

from .ai_router import AIRouter
from .database import lifespan
from .deps import get_current_user, get_db, require_role
from .models import AgentManifest, Task, User
from .schemas import TaskCreate, TaskRead, UserCreate, UserRead
from .security import create_access_token, hash_password, verify_password
from .settings import settings

REQUEST_COUNTER = Counter('control_requests_total', 'Total control plane requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('control_request_latency_seconds', 'Control plane request latency')

app = FastAPI(title='AION Control Plane', version='1.0.0', lifespan=lifespan, default_response_class=ORJSONResponse)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.on_event('startup')
async def startup_event():
    app.state.redis = Redis.from_url(settings.redis_url, decode_responses=True)
    app.state.router = AIRouter(app.state.redis)


@app.on_event('shutdown')
async def shutdown_event():
    await app.state.redis.close()


async def get_router() -> AIRouter:
    return app.state.router


@app.get('/health')
async def health():
    return {'status': 'ok'}


@app.middleware('http')
async def metrics_middleware(request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    REQUEST_COUNTER.labels(request.method, request.url.path).inc()
    REQUEST_LATENCY.observe(time.perf_counter() - start)
    return response


@app.get('/metrics')
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post('/auth/login')
async def login(body: UserCreate, session=Depends(get_db)):
    result = await session.exec(select(User).where(User.email == body.email))
    user = result.first()
    if user is None or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail='Invalid credentials')
    token = create_access_token(user.email, user.role)
    return {'token': token}


@app.post('/users', response_model=UserRead)
async def create_user(user: UserCreate, session=Depends(get_db), _: User = Depends(require_role('admin'))):
    hashed = hash_password(user.password)
    db_user = User(email=user.email, hashed_password=hashed, role=user.role)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


@app.get('/tasks', response_model=list[TaskRead])
async def list_tasks(_: User = Depends(get_current_user), session=Depends(get_db)):
    result = await session.exec(select(Task))
    return result.all()


@app.get('/tasks/{task_id}', response_model=TaskRead)
async def get_task(task_id: int, _: User = Depends(get_current_user), session=Depends(get_db)):
    result = await session.exec(select(Task).where(Task.id == task_id))
    task = result.first()
    if task is None:
        raise HTTPException(status_code=404, detail='Task not found')
    return task


@app.post('/tasks', response_model=TaskRead, status_code=202)
async def create_task(
    payload: TaskCreate,
    background: BackgroundTasks,
    user: User = Depends(get_current_user),
    session=Depends(get_db),
    router: AIRouter = Depends(get_router),
):
    task = Task(
        external_id=str(uuid4()),
        intent=payload.intent,
        params=payload.params,
        preferred_engine=payload.preferred_engine,
        priority=payload.priority,
        owner_id=user.id,
        status='queued',
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)

    background.add_task(schedule_task, task.id, payload.model_dump(), router)
    await router.record_activity(session, task, 'created', payload.model_dump())
    return task


@app.post('/tasks/{task_id}/cancel', response_model=TaskRead)
async def cancel_task(task_id: int, user: User = Depends(get_current_user), session=Depends(get_db), router: AIRouter = Depends(get_router)):
    result = await session.exec(select(Task).where(Task.id == task_id))
    task = result.first()
    if task is None:
        raise HTTPException(status_code=404, detail='Task not found')
    task.status = 'cancelled'
    await session.commit()
    await session.refresh(task)
    await router.record_activity(session, task, 'cancelled', {'actor': user.email})
    return task


@app.post('/agents/manifest', response_model=dict)
async def register_manifest(body: dict, _: User = Depends(require_role('manager')), session=Depends(get_db)):
    manifest = AgentManifest(name=body['name'], version=body.get('version', '1.0.0'), manifest=body)
    session.add(manifest)
    await session.commit()
    await session.refresh(manifest)
    return manifest.manifest


async def process_task(task_id: int, payload: dict, router: AIRouter):
    from .database import async_session_factory

    async with async_session_factory() as session:
        task_result = await session.exec(select(Task).where(Task.id == task_id))
        task = task_result.first()
        if task is None:
            return
        router_payload = TaskCreate(**payload)
        task.status = 'running'
        await session.commit()
        await session.refresh(task)
        await router.record_activity(session, task, 'started', payload)
        try:
            response = await router.execute(task, router_payload)
            task.status = 'completed'
            task.result = response.output
            await session.commit()
            await session.refresh(task)
            await router.record_activity(session, task, 'completed', response.output)
        except Exception as exc:  # pragma: no cover - runtime error handling
            task.status = 'failed'
            task.result = {'error': str(exc)}
            await session.commit()
            await session.refresh(task)
            await router.record_activity(session, task, 'failed', {'error': str(exc)})


def schedule_task(task_id: int, payload: dict, router: AIRouter):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        asyncio.run(process_task(task_id, payload, router))
    else:
        loop.create_task(process_task(task_id, payload, router))
