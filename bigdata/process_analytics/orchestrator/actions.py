"""Action definitions for the self-evolving controller."""

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class OrchestrationAction:
    """Representation of a command for OMERTAOS orchestrators."""

    name: str
    parameters: Dict[str, Any]
    confidence: float = 0.0
