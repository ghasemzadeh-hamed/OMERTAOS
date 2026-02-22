"""Implementation helpers for ``aion doctor``."""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Tuple

DEFAULT_API = "http://127.0.0.1:8001"


@dataclass
class DoctorService:
    verbose: bool = False
    api_base: str = DEFAULT_API

    def run(self) -> Tuple[bool, str]:
        try:
            request = urllib.request.Request(f"{self.api_base}/api/health")
            with urllib.request.urlopen(request, timeout=5) as response:  # nosec B310
                payload = response.read().decode("utf-8")
        except urllib.error.URLError as exc:  # pragma: no cover - network failure
            return False, f"Failed to contact control plane: {exc}"

        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            return False, "Health endpoint returned invalid JSON"

        healthy = data.get("status") == "ok"
        lines = ["Control plane health"]
        for component, status in sorted(data.get("details", {}).items()):
            if isinstance(status, dict):
                display = status.get("status", status)
            else:
                display = status
            lines.append(f"- {component}: {display}")
        if self.verbose and "latencies" in data:
            lines.append("Latency metrics:")
            for key, value in data["latencies"].items():
                lines.append(f"  * {key}: {value} ms")
        return healthy, "\n".join(lines)
