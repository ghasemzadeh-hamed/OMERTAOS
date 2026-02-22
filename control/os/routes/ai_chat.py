from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from kernel.ai_router import AIRouter, RouteContext
from kernel.governance_hook import GovernanceHook
from kernel.integration_layer import ControlClient, IntegrationLayer
from kernel.policy_engine import PolicyEngine

router = APIRouter(prefix="/ai", tags=["ai"])


class Msg(BaseModel):
    role: str
    content: str


class ChatReq(BaseModel):
    task: Dict[str, Any] = {}
    messages: List[Msg]


class FastAPIControlClient(ControlClient):
    def lookup_agents(self, intent: str, tags):
        return [{"id": "router-agent", "intent": intent, "tags": tags}]

    def query_resources(self, intent: str, context: Dict[str, Any]):
        return {"intent": intent, "context": context, "resource": "control"}


def create_router_engine() -> AIRouter:
    policy_path = Path("policies/linux-personal.json")
    policy_engine = PolicyEngine(policy_path=policy_path)
    governance = GovernanceHook()
    integration = IntegrationLayer(control_client=FastAPIControlClient())
    return AIRouter(policy_engine=policy_engine, governance_hook=governance, integration_layer=integration)


@router.post("/chat")
def chat(body: ChatReq) -> Dict[str, Any]:
    try:
        router_engine = create_router_engine()
        messages = [{"role": message.role, "content": message.content} for message in body.messages]
        context = RouteContext(
            user_id="api-user",
            session_id="api-session",
            channel="http",
            metadata={"roles": ["api"], "risk_score": 0.0},
        )
        intent = str(body.task.get("intent", "chat"))
        decision = router_engine.route(intent, {"messages": messages, "task": body.task}, context)
        return asdict(decision)
    except Exception as exc:  # pragma: no cover - surface FastAPI error
        raise HTTPException(500, f"router failed: {exc}") from exc
