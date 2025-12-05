param(
    [string]$ManifestPath = "${PWD}\manifests\omertaos-wsl.mcp.json"
)

if (-not (Get-Command odr.exe -ErrorAction SilentlyContinue)) {
    Write-Error "odr.exe not found on PATH"; exit 1
}

Write-Host "Registering MCP manifest at $ManifestPath"
& odr.exe mcp add $ManifestPath

Write-Host "Currently registered manifests:"
& odr.exe mcp list
