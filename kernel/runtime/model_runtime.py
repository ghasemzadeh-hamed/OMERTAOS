from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ModelRuntime:
    model_id: str
    provider: str

    def infer(self, prompt: str, **kwargs: Any) -> dict[str, Any]:
        return {"model_id": self.model_id, "provider": self.provider, "output": prompt, "meta": kwargs}
