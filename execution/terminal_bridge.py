from __future__ import annotations

from dataclasses import dataclass

from control_plane.runtime_client import ExecutionContextPayload, RuntimeDaemonClient
from kernel.multitenant.execution_context import ExecutionContext


@dataclass(frozen=True)
class CommandPolicy:
    allowed_prefixes: tuple[str, ...] = ("echo", "ls", "cat", "python")

    def validate(self, command: list[str]) -> None:
        if not command:
            raise ValueError("command required")
        if command[0] not in self.allowed_prefixes:
            raise PermissionError(f"command not allowed: {command[0]}")


class TerminalBridge:
    def __init__(self, runtime_client: RuntimeDaemonClient | None = None, policy: CommandPolicy | None = None) -> None:
        self._runtime = runtime_client or RuntimeDaemonClient()
        self._policy = policy or CommandPolicy()

    def run(self, context: ExecutionContext, command: list[str]) -> dict[str, object]:
        self._policy.validate(command)
        payload = ExecutionContextPayload(
            agent_id="terminal-bridge",
            tenant_id=context.tenant_id,
            cpu_cores=1,
            memory_mb=256,
            gpu_enabled=False,
            capabilities=sorted(context.capabilities),
        )
        response = self._runtime.execute_command(payload, command)
        response["audit"] = {"tenant_id": context.tenant_id, "command": command}
        return response
