import os
from typing import Any, Dict

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/agent", tags=["agent"])
AGENT_TOKEN = os.getenv("AGENT_API_TOKEN", "")


class AgentReq(BaseModel):
    goal: str
    context: Dict[str, Any] = {}


def _fake_console_api_list_tasks() -> list[Dict[str, str]]:
    """Placeholder for wiring into the real console API."""
    return [{"id": "t1", "title": "Demo Task"}, {"id": "t2", "title": "Bootstrap"}]


@router.post("/run")
def run_agent(body: AgentReq, x_agent_token: str = Header(default="")) -> Dict[str, Any]:
    if AGENT_TOKEN and x_agent_token != AGENT_TOKEN:
        raise HTTPException(403, "forbidden")
    try:
        plan = (
            "Plan: understand goal → call ConsoleAPI.list_tasks → show result "
            f"(goal={body.goal})"
        )
        result = _fake_console_api_list_tasks()
        return {"plan": plan, "result": result}
    except Exception as exc:  # pragma: no cover - surface FastAPI error
        raise HTTPException(500, f"agent failed: {exc}") from exc
