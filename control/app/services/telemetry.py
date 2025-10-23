from datetime import datetime
import httpx

from ..config import get_settings

settings = get_settings()


async def push_event(task_id: str, status: str, message: str | None = None) -> None:
    payload = {
        'taskId': task_id,
        'status': status,
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'message': message,
    }
    async with httpx.AsyncClient(timeout=5) as client:
        await client.post(
            f"{settings.gateway_url}/internal/telemetry",
            headers={'x-internal-token': settings.bridge_token},
            json=payload,
        )
