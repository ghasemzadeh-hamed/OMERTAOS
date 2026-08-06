Write-Host "Running OMERTAOS lint checks..."

$failures = New-Object System.Collections.Generic.List[string]

function Invoke-Check {
    param(
        [string]$Name,
        [scriptblock]$Action
    )

    Write-Host ""
    Write-Host "==> $Name"
    $global:LASTEXITCODE = 0
    try {
        & $Action
        $exitCode = $LASTEXITCODE
    } catch {
        Write-Host "FAILED: $Name - $($_.Exception.Message)" -ForegroundColor Red
        $failures.Add($Name)
        return
    }

    if ($exitCode -ne 0) {
        Write-Host "FAILED: $Name (exit $exitCode)" -ForegroundColor Red
        $failures.Add($Name)
    } else {
        Write-Host "PASSED: $Name" -ForegroundColor Green
    }
}

$python = $null
if (Test-Path ".\.venv\Scripts\python.exe") {
    $python = ".\.venv\Scripts\python.exe"
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $python = "python"
}

if (Get-Command ruff -ErrorAction SilentlyContinue) {
    Invoke-Check "Python Ruff" { ruff check . }
} elseif ($python) {
    Invoke-Check "Python compile" {
        & $python -m compileall -q control data policies eventbus observability orchestration
    }
}

if (Get-Command npm -ErrorAction SilentlyContinue) {
    if (Test-Path ".\gateway\package.json") {
        Invoke-Check "Gateway ESLint" { npm run lint --prefix gateway --if-present }
    }

    if (Test-Path ".\console\package.json") {
        Invoke-Check "Console lint" { npm run lint --prefix console --if-present }
    }
}

if ((Get-Command cargo -ErrorAction SilentlyContinue) -and (Test-Path ".\runtime-daemon\Cargo.toml")) {
    Invoke-Check "Runtime rustfmt" {
        cargo fmt --manifest-path runtime-daemon/Cargo.toml -- --check
    }
}

if ($failures.Count -gt 0) {
    Write-Host ""
    Write-Host "Lint failures: $($failures -join ', ')" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "All available OMERTAOS lint checks passed." -ForegroundColor Green
