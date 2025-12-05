# OMERTAOS Windows Agentic Bridge

This subsystem packages a WSL-hosted MCP server that proxies OMERTAOS capabilities to Windows Agentic and other MCP-aware hosts via ODR.

## Contents
- [`bridge-server/`](./bridge-server/): TypeScript MCP server running inside WSL and exposing MCP tools over stdio
- [`bridge-ui/`](./bridge-ui/): Vite/React UI for configuration, tool exposure, and health/status
- [`manifests/`](./manifests/omertaos-wsl.mcp.json): ODR manifest for launching the bridge via `wsl.exe`
- [`scripts/`](./scripts/): Helper scripts for registration and health checks
- [`docs/`](./docs/README.md): Detailed architecture, setup, and security guides

## Quick start (WSL)
1. Install Node.js 20+ and pnpm/npm.
2. Copy `.env.example` to `.env` inside `bridge-server/` and update OMERTA endpoints.
3. Build the bridge server: `cd bridge-server && npm install && npm run build`.
4. Launch the bridge: `node dist/index.js`.
5. Start the UI: `cd bridge-ui && npm install && npm run dev -- --host`.

## Register with ODR (Windows)
Use `scripts/register-odr.ps1` from PowerShell:
```powershell
cd integrations/windows-agentic-bridge
./scripts/register-odr.ps1 -ManifestPath "C:\path\to\omertaos-wsl.mcp.json"
```

For detailed instructions see `docs/SETUP_WINDOWS_AGENTIC.md` and `docs/SETUP_WSL.md`.

## خلاصه پلان اجرایی (FA)
1) **OMERTA روی WSL**: Docker Desktop + WSL2، کلون `OMERTAOS` و اجرای `./install.sh --profile user` یا compose dev.
2) **سلامت اولیه**: `curl http://localhost:3000/healthz` و `curl http://localhost:8000/healthz`.
3) **ساخت پل MCP در WSL**: تعریف حداقل ابزارها (`run_task`، `list_agents`، `get_health`) با `OMERTA_GATEWAY_URL` و توکن dev.
4) **Manifest و ODR روی ویندوز**: تنظیم JSON با `wsl.exe`، اجرای `odr.exe mcp add ...` و بررسی `odr.exe mcp list`.
5) **Agent Host نمونه (اختیاری)**: یک Agent ساده با Microsoft Agent Framework که `omerta_run_task` و `omerta_list_agents` را مصرف می‌کند.
