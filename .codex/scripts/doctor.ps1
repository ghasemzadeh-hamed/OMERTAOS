Write-Host "====================================="
Write-Host "OMERTAOS Doctor"
Write-Host "====================================="

$checks = @()

function Add-Check {
    param(
        [string]$Name,
        [bool]$Ok,
        [string]$Details = ""
    )

    $script:checks += [PSCustomObject]@{
        Name = $Name
        Status = if ($Ok) { "OK" } else { "MISSING" }
        Details = $Details
    }
}

Add-Check "Git" ([bool](Get-Command git -ErrorAction SilentlyContinue))
Add-Check "Python" ([bool]((Get-Command python -ErrorAction SilentlyContinue) -or (Get-Command py -ErrorAction SilentlyContinue)))
Add-Check "Node" ([bool](Get-Command node -ErrorAction SilentlyContinue))
Add-Check "npm" ([bool](Get-Command npm -ErrorAction SilentlyContinue))
Add-Check "Docker" ([bool](Get-Command docker -ErrorAction SilentlyContinue))
Add-Check "Docker Compose" ([bool](Get-Command docker -ErrorAction SilentlyContinue))
Add-Check "Rust Cargo" ([bool](Get-Command cargo -ErrorAction SilentlyContinue))
Add-Check "ripgrep rg" ([bool](Get-Command rg -ErrorAction SilentlyContinue))

$checks | Format-Table -AutoSize

Write-Host ""
Write-Host "Git branch:"
if (Get-Command git -ErrorAction SilentlyContinue) {
    git branch --show-current
}

Write-Host ""
Write-Host "Important OMERTAOS paths:"

$paths = @(
    "console",
    "gateway",
    "control",
    "runtime-daemon",
    "data",
    "registry",
    "schemas",
    "policies",
    "integrations",
    "deploy/native",
    "deploy/docker",
    "requirements.txt",
    "pyproject.toml",
    ".env.example",
    ".env.schema",
    "dev.env"
)

foreach ($path in $paths) {
    if (Test-Path $path) {
        Write-Host "OK: $path"
    } else {
        Write-Host "MISSING: $path"
    }
}

Write-Host ""
Write-Host "Docker quickstart config check:"
if ((Get-Command docker -ErrorAction SilentlyContinue) -and (Test-Path "docker-compose.quickstart.yml")) {
    docker compose -f docker-compose.quickstart.yml config | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "OK: docker-compose.quickstart.yml config"
    } else {
        Write-Host "FAILED: docker-compose.quickstart.yml config"
    }
} else {
    Write-Host "SKIPPED: Docker or docker-compose.quickstart.yml not available."
}

Write-Host ""
Write-Host "Doctor completed."
