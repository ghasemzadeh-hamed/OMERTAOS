if (-not (Get-Command wsl.exe -ErrorAction SilentlyContinue)) {
    Write-Error "wsl.exe not available"; exit 1
}

Write-Host "WSL available. Checking bridge entrypoint..."
wsl.exe -- bash -lc "cd integrations/windows-agentic-bridge/bridge-server && node -e 'console.log(\"bridge ok\")'"
