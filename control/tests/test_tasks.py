import os
import pytest
from httpx import ASGITransport, AsyncClient

os.environ['POSTGRES_URL'] = 'sqlite+aiosqlite:///./test_control.db'
os.environ['REDIS_URL'] = 'redis://localhost:6379/0'

from control.app.main import app  # noqa: E402
from control.app.database import async_session_factory, engine  # noqa: E402
from control.app.models import SQLModel, User  # noqa: E402
from control.app.security import hash_password  # noqa: E402


@pytest.mark.asyncio
async def test_health():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as client:
        response = await client.get('/health')
        assert response.status_code == 200
        assert response.json() == {'status': 'ok'}


@pytest.mark.asyncio
async def test_user_and_task_flow():
    # Monkeypatch router to bypass redis and external calls
    from control.app.ai_router import AIRouter

    class DummyRouter(AIRouter):
        async def decide(self, task):  # type: ignore
            from control.app.schemas import RouterDecision
            return RouterDecision(decision='api', reason='test')

        async def execute(self, task, payload):  # type: ignore
            from control.app.schemas import RouterDecision, RouterResponse
            return RouterResponse(decision=RouterDecision(decision='api', reason='test'), output={'result': 'ok'})

        async def record_activity(self, session, task, action, payload):  # type: ignore
            return None

    app.dependency_overrides = {}
    app.state.router = DummyRouter(redis=None)  # type: ignore

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)

    async with async_session_factory() as session:
        user = User(email='admin@test', hashed_password=hash_password('secret'), role='admin')
        session.add(user)
        await session.commit()
        await session.refresh(user)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as client:
        login = await client.post('/auth/login', json={'email': 'admin@test', 'password': 'secret', 'role': 'admin'})
        assert login.status_code == 200, login.text
        token = login.json()['token']
        create = await client.post(
            '/tasks',
            headers={'Authorization': f'Bearer {token}'},
            json={'intent': 'test', 'params': {'x': 1}, 'priority': 1},
        )
        assert create.status_code == 202, create.text
        body = create.json()
        assert body['intent'] == 'test'

