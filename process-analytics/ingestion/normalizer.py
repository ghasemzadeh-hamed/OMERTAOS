"""Additional normalization helpers for event ingestion."""

from typing import Any, Dict


def flatten_attributes(event: Dict[str, Any]) -> Dict[str, Any]:
    """Flatten nested attribute dictionaries using dotted keys."""
    attributes = event.get("attributes", {})
    flat: Dict[str, Any] = {}

    def _flatten(prefix: str, value: Any) -> None:
        if isinstance(value, dict):
            for key, val in value.items():
                _flatten(f"{prefix}.{key}" if prefix else key, val)
        else:
            flat[prefix] = value

    _flatten("", attributes)
    return {**event, "attributes": flat or attributes}
