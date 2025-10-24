"""NETD dynamic network overlay manager."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(slots=True)
class WireGuardPeer:
    public_key: str
    endpoint: str
    allowed_ips: List[str]


class NetworkOverlayManager:
    """Tracks overlay peers and generated routing plans."""

    def __init__(self) -> None:
        self._peers: Dict[str, WireGuardPeer] = {}

    def upsert_peer(self, peer: WireGuardPeer) -> None:
        self._peers[peer.public_key] = peer

    def remove_peer(self, public_key: str) -> None:
        self._peers.pop(public_key, None)

    def plan(self) -> Dict[str, object]:
        return {
            "peers": [
                {
                    "public_key": peer.public_key,
                    "endpoint": peer.endpoint,
                    "allowed_ips": peer.allowed_ips,
                }
                for peer in self._peers.values()
            ]
        }
