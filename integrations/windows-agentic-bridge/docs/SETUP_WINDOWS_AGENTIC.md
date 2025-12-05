# Setup: Windows Agentic / ODR

1. Install ODR CLI (`odr.exe`) and ensure it is on `PATH`.
2. Ensure `wsl.exe` is available and your distro name matches the manifest (default `Ubuntu`).
3. Copy or adjust the manifest:
   ```powershell
   cd integrations/windows-agentic-bridge
   # Edit manifests/omertaos-wsl.mcp.json if custom paths are needed
   ```
4. Register the MCP server with ODR:
   ```powershell
   ./scripts/register-odr.ps1 -ManifestPath "C:\\path\\to\\omertaos-wsl.mcp.json"
   ```
5. Validate the bridge can be launched:
   ```powershell
   ./scripts/check-bridge.ps1
   ```
6. From your MCP-capable agent host, request the `omertaos-wsl` server; ODR will spawn `wsl.exe` which runs the compiled `dist/index.js` entrypoint inside WSL.
