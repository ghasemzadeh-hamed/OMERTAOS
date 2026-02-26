from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from control_plane.runtime_client import ExecutionContextPayload, RuntimeDaemonClient
from kernel.multitenant.execution_context import ExecutionContext


@dataclass(frozen=True)
class PluginSpec:
    name: str
    image: str
    command: list[str]
    required_capabilities: set[str]
    cpu_limit: str = "1"
    memory_limit: str = "512m"
    seccomp_profile: str = "default"
    mounts: tuple[str, ...] = tuple()
    signature: str = ""


class ContainerExecutor:
    def __init__(self, runtime_client: RuntimeDaemonClient | None = None) -> None:
        self._runtime = runtime_client or RuntimeDaemonClient()

    def validate(self, context: ExecutionContext, spec: PluginSpec, payload: dict[str, Any]) -> None:
        if not spec.required_capabilities.issubset(context.capabilities):
            missing = spec.required_capabilities - context.capabilities
            raise PermissionError(f"missing capabilities: {sorted(missing)}")
        if "grpc" not in payload:
            raise ValueError("plugin payload must use grpc envelope")
        self._verify_signature(spec, payload)

    def execute(self, context: ExecutionContext, spec: PluginSpec, grpc_payload: dict[str, Any]) -> dict[str, Any]:
        self.validate(context, spec, grpc_payload)
        payload = ExecutionContextPayload(
            agent_id=spec.name,
            tenant_id=context.tenant_id,
            cpu_cores=max(1, int(float(spec.cpu_limit))),
            memory_mb=max(64, int(spec.memory_limit.rstrip("mM")) if spec.memory_limit.lower().endswith("m") else 512),
            gpu_enabled=False,
            capabilities=sorted(context.capabilities),
        )
        response = self._runtime.start_agent(payload, image=spec.image, argv=spec.command)
        return {
            "plugin": spec.name,
            "tenant_id": context.tenant_id,
            "returncode": 0 if response.get("ok") else 1,
            "stdout": response.get("message", ""),
            "stderr": "",
            "runtime": response,
        }

    def _verify_signature(self, spec: PluginSpec, payload: dict[str, Any]) -> None:
        if not spec.signature:
            raise PermissionError("unsigned plugin")
        body = json.dumps(payload, sort_keys=True).encode("utf-8")
        digest = hashlib.sha256(body).hexdigest()
        if digest != spec.signature:
            raise PermissionError("plugin signature mismatch")


def load_plugin_spec(plugin_dir: str) -> PluginSpec:
    data = json.loads((Path(plugin_dir) / "plugin.json").read_text(encoding="utf-8"))
    mounts = tuple(data.get("mounts", []))
    return PluginSpec(
        name=data["name"],
        image=data["image"],
        command=list(data.get("command", [])),
        required_capabilities=set(data.get("required_capabilities", [])),
        cpu_limit=str(data.get("cpu_limit", "1")),
        memory_limit=str(data.get("memory_limit", "512m")),
        seccomp_profile=str(data.get("seccomp_profile", "default")),
        mounts=mounts,
        signature=str(data.get("signature", "")),
    )
