"""CLI sync helpers for catalog sources (latentbox)."""
from __future__ import annotations

import json
from typing import Optional

import httpx
import typer

SYNC_APP = typer.Typer(help="Sync external catalogs (e.g., Latent Box)")


def register(app: typer.Typer) -> None:
    app.add_typer(SYNC_APP, name="sync")


@SYNC_APP.command("latentbox")
def sync_latentbox(
    control_base: str = typer.Option("http://localhost:8000", help="Control API base URL"),
    tenant_id: Optional[str] = typer.Option(None, "--tenant-id", help="Tenant header if required"),
) -> None:
    """Trigger LatentBox catalog sync via the control API."""

    headers = {"accept": "application/json", "x-aion-roles": "ROLE_ADMIN"}
    if tenant_id:
        headers["tenant-id"] = tenant_id
    url = f"{control_base.rstrip('/')}/api/v1/recommendations/tools/sync"
    response = httpx.post(url, headers=headers, timeout=20.0)
    response.raise_for_status()
    payload = response.json()
    typer.echo(json.dumps(payload, indent=2))
