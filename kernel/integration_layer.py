"""Integration bridge between kernel routing and control plane orchestration."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Protocol


class Connector(Protocol):
    """Protocol representing a secure data connector."""

    name: str

    def fetch(self, intent: str, payload: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:  # pragma: no cover - interface
        ...


@dataclass
class CRMConnector:
    """Fetches account metadata from an external CRM service."""

    name: str = "crm"

    def fetch(self, intent: str, payload: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        token = os.environ.get("AION_CRM_TOKEN", "masked")
        account_id = context.get("account_id") or payload.get("account_id")
        return {
            "source": self.name,
            "account_id": account_id,
            "token_present": bool(token != "masked"),
        }


@dataclass
class DataLakeConnector:
    """Retrieves feature flags or configuration from secure storage."""

    name: str = "data_lake"

    def fetch(self, intent: str, payload: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        region = context.get("region", "global")
        return {"source": self.name, "region": region, "intent": intent}


class IntegrationLayer:
    """Maps intents into execution plans using control plane metadata."""

    def __init__(self, control_client: "ControlClient", connectors: Iterable[Connector] | None = None) -> None:
        self._control_client = control_client
        self._connectors = list(connectors or [CRMConnector(), DataLakeConnector()])

    def resolve_execution_plan(
        self,
        intent: str,
        payload: Dict[str, Any],
        context: Dict[str, Any],
        policy_tags: List[str],
    ) -> Dict[str, Any]:
        """Produce a structured execution plan for the execution plane."""
        agents = self._control_client.lookup_agents(intent=intent, tags=policy_tags)
        resources = self._control_client.query_resources(intent=intent, context=context)
        integrations: List[Dict[str, Any]] = []
        for connector in self._connectors:
            result = connector.fetch(intent=intent, payload=payload, context=context)
            integrations.append(result)
        return {
            "intent": intent,
            "agents": agents,
            "resources": resources,
            "payload": payload,
            "policy_tags": policy_tags,
            "integrations": integrations,
        }


class ControlClient:
    """Abstract client that the kernel uses to interact with the control plane."""

    def lookup_agents(self, intent: str, tags: List[str]) -> List[Dict[str, Any]]:  # pragma: no cover - interface
        raise NotImplementedError

    def query_resources(self, intent: str, context: Dict[str, Any]) -> Dict[str, Any]:  # pragma: no cover - interface
        raise NotImplementedError


__all__ = ["IntegrationLayer", "ControlClient", "CRMConnector", "DataLakeConnector"]
