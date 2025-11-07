import time
from typing import Dict, List, Any

import yaml

from app.control.app.config_paths import resolve_config_path
from app.control.app.llm_local import LocalLLM


class AIRouter:
    def __init__(self) -> None:
        self.config_path = resolve_config_path()
        try:
            with open(self.config_path, "r", encoding="utf-8") as stream:
                self.cfg = yaml.safe_load(stream) or {}
        except FileNotFoundError as exc:  # pragma: no cover - defensive guard
            raise FileNotFoundError(
                "AION-OS config file not found. Set AIONOS_CONFIG_PATH or add"
                f" config/aionos.config.yaml (looked at {self.config_path})."
            ) from exc
        models_cfg = self.cfg.get("models", {})
        local_cfg = models_cfg.get("local") or {}
        routing_cfg = models_cfg.get("routing") or {}
        self.mode = routing_cfg.get("mode", "local-first")
        self.allow_remote = bool(routing_cfg.get("allow_remote", False))
        self.local = LocalLLM(
            model=local_cfg.get("model", "llama3.2:3b"),
            engine=local_cfg.get("engine", "ollama"),
            ctx=int(local_cfg.get("ctx", 4096)),
            temperature=float(local_cfg.get("temperature", 0.2)),
        )

    def route(self, task: Dict[str, Any], messages: List[Dict[str, str]]) -> Dict[str, Any]:
        started = time.time()
        # Route locally for now; remote routing can be enabled via config
        output = self.local.chat(messages, stream=False)
        latency_ms = int((time.time() - started) * 1000)
        return {
            "provider": "local",
            "engine": self.local.engine,
            "model": self.local.model,
            "latency_ms": latency_ms,
            "output": output,
        }
