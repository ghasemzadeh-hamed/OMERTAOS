Write-Host "====================================="
Write-Host "OMERTAOS Native Setup"
Write-Host "====================================="
# Resolve repository root even if script is executed from .codex/scripts
if ($env:CODEX_WORKTREE_PATH -and (Test-Path $env:CODEX_WORKTREE_PATH)) {
    Set-Location $env:CODEX_WORKTREE_PATH
} else {
    $repoRoot = git -C $PSScriptRoot rev-parse --show-toplevel 2>$null

    if ($repoRoot) {
        Set-Location $repoRoot
    } else {
        $fallbackRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
        Set-Location $fallbackRoot
    }
}
$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "Current location:"
Get-Location

Write-Host ""
Write-Host "Checking Git..."
if (Get-Command git -ErrorAction SilentlyContinue) {
    git --version
    Write-Host "Current branch:"
    git branch --show-current
} else {
    Write-Host "Git not found."
}

Write-Host ""
Write-Host "Checking runtimes..."

if (Get-Command python -ErrorAction SilentlyContinue) {
    python --version
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    py -3 --version
} else {
    Write-Host "Python not found."
}

if (Get-Command node -ErrorAction SilentlyContinue) {
    node --version
} else {
    Write-Host "Node not found."
}

if (Get-Command npm -ErrorAction SilentlyContinue) {
    npm --version
} else {
    Write-Host "npm not found."
}

if (Get-Command cargo -ErrorAction SilentlyContinue) {
    cargo --version
} else {
    Write-Host "Rust/Cargo not found. Runtime build may be unavailable."
}

if (Get-Command docker -ErrorAction SilentlyContinue) {
    docker --version
} else {
    Write-Host "Docker not found. Docker actions will be unavailable."
}

Write-Host ""
Write-Host "Creating local runtime folders..."

$folders = @(
    ".\logs",
    ".\tmp",
    ".\.cache",
    ".\.cache\tmp",
    ".\storage",
    ".\storage\backups",
    ".\storage\exports",
    ".\storage\imports"
)

foreach ($folder in $folders) {
    if (!(Test-Path $folder)) {
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
        Write-Host "Created: $folder"
    } else {
        Write-Host "Exists: $folder"
    }
}

Write-Host ""
Write-Host "Python dependency setup..."

if (Test-Path ".\requirements.txt") {
    if (!(Test-Path ".\.venv")) {
        if (Get-Command python -ErrorAction SilentlyContinue) {
            python -m venv .venv
        } elseif (Get-Command py -ErrorAction SilentlyContinue) {
            py -3 -m venv .venv
        }
    }

    if (Test-Path ".\.venv\Scripts\python.exe") {
        .\.venv\Scripts\python.exe -m pip install --upgrade pip
        .\.venv\Scripts\python.exe -m pip install -r requirements.txt
    } else {
        Write-Host "Virtualenv python not found. Skipping pip install."
    }
} else {
    Write-Host "requirements.txt not found. Skipping Python dependency install."
}

Write-Host ""
Write-Host "Node dependency setup..."

function Invoke-NpmInstall {
    param(
        [string]$ProjectPath
    )

    $packageJson = Join-Path $ProjectPath "package.json"

    if (!(Test-Path $packageJson)) {
        Write-Host "No package.json in $ProjectPath"
        return
    }

    Write-Host "Installing Node dependencies in $ProjectPath"

    Push-Location $ProjectPath

    try {
        $oldErrorActionPreference = $ErrorActionPreference
        $ErrorActionPreference = "Continue"

        if (Test-Path ".\package-lock.json") {
            npm ci --loglevel=error 2>&1 | ForEach-Object { Write-Host $_ }
        } else {
            npm install --loglevel=error 2>&1 | ForEach-Object { Write-Host $_ }
        }

        $npmExitCode = $LASTEXITCODE
        $ErrorActionPreference = $oldErrorActionPreference

        if ($npmExitCode -ne 0) {
            throw "npm install failed in $ProjectPath with exit code $npmExitCode"
        }
    }
    finally {
        $ErrorActionPreference = $oldErrorActionPreference
        Pop-Location
    }
}

$nodeProjects = @(
    ".\console",
    ".\gateway"
)

foreach ($project in $nodeProjects) {
    Invoke-NpmInstall -ProjectPath $project
}

Write-Host ""
Write-Host "Docker config validation, if available..."

if ((Get-Command docker -ErrorAction SilentlyContinue) -and (Test-Path ".\docker-compose.quickstart.yml")) {
    docker compose -f docker-compose.quickstart.yml config | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "OK: docker-compose.quickstart.yml config"
    } else {
        Write-Host "WARNING: docker-compose.quickstart.yml config failed."
    }
} else {
    Write-Host "Docker config validation skipped."
}

Write-Host ""
Write-Host "Native setup completed."
Write-Host "No long-running service was started."
