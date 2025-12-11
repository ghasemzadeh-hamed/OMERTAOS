# OMERTAOS Windows Agentic Bridge Docs

This folder collects the onboarding and design documents for the OMERTA MCP bridge that exposes WSL-hosted OMERTAOS tooling to Windows Agentic clients via ODR.

## Documents
- [`ARCHITECTURE.md`](./ARCHITECTURE.md): detailed component view and tool mapping
- [`SETUP_WSL.md`](./SETUP_WSL.md): WSL-side installation and configuration
- [`SETUP_WINDOWS_AGENTIC.md`](./SETUP_WINDOWS_AGENTIC.md): Windows-side registration with ODR
- [`SECURITY.md`](./SECURITY.md): threat model and mitigations
- Top-level index: [`../README.md`](../README.md)

## Execution plan (FA)
1) نصب Docker Desktop + WSL2، کلون `OMERTAOS` و اجرای `./install.sh --profile user` یا compose dev.
2) صحت سلامت Gateway/Control با `curl` روی پورت‌های 3000 و 8000.
3) ساخت پل MCP در WSL با حداقل ابزارها (`run_task`، `list_agents`، `get_health`) و تنظیم `OMERTA_GATEWAY_URL` + توکن.
4) ثبت manifest با `wsl.exe` و `odr.exe mcp add ...` و بررسی با `odr.exe mcp list`.
5) (اختیاری) Agent Host نمونه با Microsoft Agent Framework که ابزارهای OMERTA را مصرف کند.

## High-level diagram
```text
+-----------------------------+
|  Windows Agent (Copilot)    |
+--------------+--------------+
               |
               |  MCP over stdio
               v
+-----------------------------+
|  ODR (MCP registry/launcher)|
+--------------+--------------+
               |
               |  wsl.exe launches bridge
               v
+-----------------------------+
|  WSL2                       |
|  OMERTA MCP Bridge (Node)   |
+--------------+--------------+
               |
               |  HTTP (local)
               v
+------------------+   +------------------+
| OMERTA Gateway   |   | OMERTA Control   |
+------------------+   +------------------+
```
