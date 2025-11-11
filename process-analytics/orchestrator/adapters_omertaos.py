"""Adapters for applying actions within OMERTAOS."""

from typing import Any, Dict


class OMERTAOSAdapter:
    """Translate high-level actions into OMERTAOS orchestration commands."""

    def __init__(self, dispatcher):
        self.dispatcher = dispatcher

    def apply(self, action: Dict[str, Any]) -> None:
        """Send the action to the underlying dispatcher."""
        self.dispatcher.dispatch(action)
