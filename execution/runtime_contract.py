from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class RuntimeCommand:
    tenant_id: str
    agent_id: str
    argv: list[str]


class RuntimeExecutor(Protocol):
    async def execute(self, command: RuntimeCommand) -> dict[str, object]: ...
