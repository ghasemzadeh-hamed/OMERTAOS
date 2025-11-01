"""Serve a lightweight HTML/WS interface for the terminal explorer."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from uvicorn import Config, Server


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>AION Explorer</title>
  <style>
    body { font-family: monospace; background: #101010; color: #ededed; padding: 1rem; }
    a { color: #6cf; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); gap: 1rem; }
    .card { border: 1px solid #333; padding: 0.75rem; border-radius: 0.25rem; background: #1b1b1b; }
  </style>
</head>
<body>
  <h1>AION Explorer</h1>
  <p>Connected to: <strong>{api}</strong></p>
  <p>Token: <code>{token}</code></p>
  <div class="grid">
    <div class="card"><h2>Providers</h2><p>Inspect and manage model backends.</p></div>
    <div class="card"><h2>Modules</h2><p>Attach, upgrade, and rollback AIP modules.</p></div>
    <div class="card"><h2>DataSources</h2><p>Review connectors and run health checks.</p></div>
    <div class="card"><h2>Router</h2><p>View policy and reload routes.</p></div>
    <div class="card"><h2>Chat</h2><p>Chat-based configuration assistant.</p></div>
    <div class="card"><h2>Health</h2><p>Summaries of system metrics.</p></div>
    <div class="card"><h2>Logs</h2><p>Follow worker events and audit trails.</p></div>
    <div class="card"><h2>Admin</h2><p>RBAC, auth tokens, and user management.</p></div>
  </div>
</body>
</html>
"""


@dataclass
class TuiServerService:
    port: int
    api_url: str
    token: str

    def run(self) -> None:
        app = FastAPI()

        @app.get("/")
        async def index() -> HTMLResponse:
            return HTMLResponse(HTML_TEMPLATE.format(api=self.api_url, token=self.token))

        config = Config(app=app, host="0.0.0.0", port=self.port, log_level="info")
        server = Server(config)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(server.serve())
