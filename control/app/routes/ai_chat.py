from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..ai_router import AIRouter

router = APIRouter(prefix="/ai", tags=["ai"])


class Msg(BaseModel):
    role: str
    content: str


class ChatReq(BaseModel):
    task: Dict[str, Any] = {}
    messages: List[Msg]


@router.post("/chat")
def chat(body: ChatReq) -> Dict[str, Any]:
    try:
        router_engine = AIRouter()
        messages = [{"role": message.role, "content": message.content} for message in body.messages]
        return router_engine.route(body.task, messages)
    except Exception as exc:  # pragma: no cover - surface FastAPI error
        raise HTTPException(500, f"router failed: {exc}") from exc
