# Architecture

The OMERTAOS Windows Agentic Bridge runs inside WSL and exposes OMERTA Gateway/Control functionality to Windows MCP clients through stdio. The bridge contains a TypeScript MCP server and a lightweight React UI for configuration and status.

## Components
- **MCP bridge server** (`bridge-server/`): registers MCP tools that call OMERTA HTTP APIs.
- **UI console** (`bridge-ui/`): surfaces connection state, tool exposure toggles, and log tail.
- **ODR manifest** (`manifests/omertaos-wsl.mcp.json`): instructs ODR to launch the bridge through `wsl.exe`.

## Data flow
```text
+---------------------------+
|  Windows Agent Host       |
|  (Copilot / custom host)  |
+-------------+-------------+
              |
              |  MCP protocol (stdio) via ODR
              v
+---------------------------+       HTTP (local)
|  ODR (odr.exe)            +--------------------+
|  MCP registry/launcher    |                    |
+-------------+-------------+                    |
              | command + args                   |
              v                                  |
      C:\\Windows\\System32\\wsl.exe                |
              |                                  |
              v                                  |
+---------------------------+   HTTP             |
|  OMERTA MCP Bridge        +--------------------+
|  (Node.js, TypeScript)    |                    |
+-------------+-------------+                    |
              |                                  |
              v                                  v
      +-------------+                    +-------------+
      | OMERTA GW   |                    | OMERTA Ctrl |
      | (API)       |                    | (API)       |
      +-------------+                    +-------------+
```

## Tool mapping
- **Platform**: `omerta.list_agents`, `omerta.get_agent`, `omerta.run_task`, `omerta.get_task_status`, `omerta.get_health`
- **Business**: `omerta.run_agent_intent`, `omerta.search_memory`, `omerta.store_memory`
- **Admin**: `omerta.restart_component`, `omerta.get_metrics`

## Security
- Admin tools should be disabled by default when exposing to untrusted clients.
- Configuration is read from environment variables; secrets are not committed to the repo.
- Input schemas (Zod) guard parameters before hitting OMERTA endpoints.
