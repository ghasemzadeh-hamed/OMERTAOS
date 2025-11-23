Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# DEPRECATED: use scripts/quicksetup.ps1 for container-based bootstrap. This native installer will
# be removed in a future release once replacements are available.

function Assert-Command {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [string]$VersionCommand,
        [string]$MinimumVersion
    )

    $command = Get-Command $Name -ErrorAction SilentlyContinue
    if (-not $command) {
        throw "Required command '$Name' not found in PATH."
    }

    if ($VersionCommand -and $MinimumVersion) {
        $versionOutput = & $Name $VersionCommand
        if ($versionOutput -match '([0-9]+)\.([0-9]+)\.([0-9]+)') {
            $major = [int]$matches[1]
            if ($major -lt [int]($MinimumVersion.Split('.')[0])) {
                throw "'$Name' version $versionOutput does not meet requirement $MinimumVersion or higher."
            }
        }
    }
}

$scriptDir = Split-Path -Parent $PSCommandPath
$repoFromScript = Resolve-Path (Join-Path $scriptDir '..') -ErrorAction SilentlyContinue
$usingLocalRepo = $false
if ($repoFromScript -and (Test-Path (Join-Path $repoFromScript '.git'))) {
    $AppDir = $repoFromScript
    $AppRoot = Split-Path -Parent $AppDir
    $usingLocalRepo = $true
} else {
    $AppRoot = if ($env:APP_ROOT) { $env:APP_ROOT } else { 'C:\\Omerta' }
    $Repo = if ($env:REPO) { $env:REPO } else { 'https://github.com/Hamedghz/OMERTAOS.git' }
    if (Test-Path (Join-Path $AppRoot '.git')) {
        $AppDir = $AppRoot
    } else {
        $AppDir = Join-Path $AppRoot 'OMERTAOS'
    }
}
$EnvFile = Join-Path $AppDir '.env'
$NssmPath = if ($env:NSSM_PATH) { $env:NSSM_PATH } else { 'C:\\nssm\\nssm.exe' }

Assert-Command -Name git -VersionCommand '--version' -MinimumVersion '2.0.0'
Assert-Command -Name python -VersionCommand '--version' -MinimumVersion '3.11.0'
Assert-Command -Name node -VersionCommand '--version' -MinimumVersion '18.0.0'

if (-not (Test-Path $NssmPath)) {
    throw "NSSM executable not found at '$NssmPath'. Set NSSM_PATH to override."
}

if (-not $usingLocalRepo) {
    if (-not (Test-Path $AppRoot)) {
        New-Item -ItemType Directory -Force -Path $AppRoot | Out-Null
    }

    if (-not (Test-Path (Join-Path $AppDir '.git'))) {
        Write-Host "Cloning repository into $AppDir"
        git clone $Repo $AppDir | Out-Null
    } else {
        Write-Host "Updating existing repository in $AppDir"
        Push-Location $AppDir
        git pull --ff-only
        Pop-Location
    }
} else {
    Write-Host "Using repository at $AppDir detected next to script. Skipping clone/update."
}

if (-not (Test-Path $EnvFile)) {
    Copy-Item (Join-Path $AppDir 'config/templates/.env.example') $EnvFile
}

foreach ($project in @('console', 'gateway')) {
    $projectEnv = Join-Path (Join-Path $AppDir $project) '.env'
    Copy-Item $EnvFile $projectEnv -Force
}

$venvPath = Join-Path $AppDir '.venv'
$venvPython = Join-Path $venvPath 'Scripts\\python.exe'
if (-not (Test-Path $venvPath)) {
    Write-Host 'Creating Python virtual environment'
    python -m venv $venvPath
}

Write-Host 'Installing Python dependencies'
Push-Location $AppDir
& $venvPython -m pip install --upgrade pip setuptools wheel | Out-Null
& $venvPython -m pip install .
Pop-Location

if (-not (Get-Command pnpm -ErrorAction SilentlyContinue)) {
    Write-Host 'Installing pnpm globally'
    npm install -g pnpm@9 | Out-Null
}

foreach ($project in @('console', 'gateway')) {
    Write-Host "Installing Node dependencies for $project"
    Push-Location (Join-Path $AppDir $project)
    if (Test-Path "pnpm-lock.yaml") {
        pnpm install --frozen-lockfile | Out-Null
    }
    else {
        pnpm install --no-frozen-lockfile | Out-Null
    }
    Pop-Location
}

Write-Host 'Building console'
Push-Location (Join-Path $AppDir 'console')
pnpm build | Out-Null
Pop-Location

Write-Host 'Building gateway'
Push-Location (Join-Path $AppDir 'gateway')
pnpm build | Out-Null
Pop-Location

if (-not (Test-Path $EnvFile)) {
    Copy-Item (Join-Path $AppDir 'config/templates/.env.example') $EnvFile
}

function Get-EnvValue {
    param(
        [string]$FilePath,
        [string]$Key
    )
    if (-not (Test-Path $FilePath)) { return $null }
    foreach ($line in Get-Content -Path $FilePath) {
        if ($line -match '^\s*#') { continue }
        if ($line -match "^$Key=(.*)") {
            return $matches[1]
        }
    }
    return $null
}

$existingUrl = Get-EnvValue -FilePath $EnvFile -Key 'DATABASE_URL'
$existingUser = ''
$existingPass = ''
$existingName = ''
if ($existingUrl -and $existingUrl -match '^postgresql://([^:]+):([^@]+)@[^/]+/(.+)$') {
    $existingUser = $matches[1]
    $existingPass = $matches[2]
    $existingName = $matches[3]
}

$dbUser = if ($env:DB_USER) { $env:DB_USER } elseif ($existingUser) { $existingUser } else { 'omerta' }
$dbPass = if ($env:DB_PASS) { $env:DB_PASS } elseif ($existingPass) { $existingPass } else { ([guid]::NewGuid().ToString('N').Substring(0, 24)) }
$dbName = if ($env:DB_NAME) { $env:DB_NAME } elseif ($existingName) { $existingName } else { 'omerta_db' }

$databaseUrl = "postgresql://${dbUser}:${dbPass}@127.0.0.1:5432/$dbName"

if (Get-Command psql -ErrorAction SilentlyContinue) {
    Write-Host "Ensuring PostgreSQL role $dbUser"
    $roleCheck = & psql -U postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='$dbUser'" 2>$null
    if (-not $roleCheck -or -not $roleCheck.Trim()) {
        & psql -U postgres -c "CREATE USER $dbUser WITH PASSWORD '$dbPass';" | Out-Null
    }

    Write-Host "Ensuring database $dbName"
    $dbCheck = & psql -U postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$dbName'" 2>$null
    if (-not $dbCheck -or -not $dbCheck.Trim()) {
        & psql -U postgres -c "CREATE DATABASE $dbName OWNER $dbUser;" | Out-Null
    }
} else {
    Write-Warning 'psql command not found. Skipping database creation. Ensure the database exists before starting services.'
}

$envLines = Get-Content -Path $EnvFile
$updateMap = @{
    'DATABASE_URL' = $databaseUrl
    'AION_CONTROL_POSTGRES_DSN' = $databaseUrl
    'AION_DB_USER' = $dbUser
    'AION_DB_PASSWORD' = $dbPass
    'AION_DB_NAME' = $dbName
}
$seen = @{}
for ($i = 0; $i -lt $envLines.Count; $i++) {
    if ($envLines[$i] -match '^\s*([^#=]+)\s*=(.*)$') {
        $key = $matches[1]
        if ($updateMap.ContainsKey($key)) {
            $envLines[$i] = "$key=$($updateMap[$key])"
            $seen[$key] = $true
        }
    }
}
foreach ($key in $updateMap.Keys) {
    if (-not $seen.ContainsKey($key)) {
        $envLines += "$key=$($updateMap[$key])"
    }
}
Set-Content -Path $EnvFile -Value $envLines -Encoding UTF8

foreach ($project in @('console', 'gateway')) {
    Copy-Item $EnvFile (Join-Path (Join-Path $AppDir $project) '.env') -Force
}

function Install-Or-UpdateService {
    param(
        [string]$Name,
        [string]$Executable,
        [string]$Arguments,
        [string]$WorkingDirectory,
        [hashtable]$Environment
    )

    $null = & $NssmPath status $Name 2>$null
    $exists = $LASTEXITCODE -eq 0
    if ($exists) {
        & $NssmPath stop $Name | Out-Null
        & $NssmPath set $Name Application $Executable | Out-Null
        & $NssmPath set $Name AppParameters $Arguments | Out-Null
        & $NssmPath set $Name AppDirectory $WorkingDirectory | Out-Null
    } else {
        & $NssmPath install $Name $Executable $Arguments | Out-Null
        & $NssmPath set $Name AppDirectory $WorkingDirectory | Out-Null
    }

    & $NssmPath set $Name Start SERVICE_AUTO_START | Out-Null
    & $NssmPath set $Name AppExit Default Restart | Out-Null

    if ($Environment) {
        $separator = [char]0
        $envString = ($Environment.GetEnumerator() | ForEach-Object { "{0}={1}" -f $_.Key, $_.Value }) -join $separator
        & $NssmPath set $Name AppEnvironmentExtra $envString | Out-Null
    }

    & $NssmPath start $Name | Out-Null
}

$controlBat = Join-Path $AppDir 'configs\\windows\\omerta-control.bat'
$gatewayBat = Join-Path $AppDir 'configs\\windows\\omerta-gateway.bat'
$consoleBat = Join-Path $AppDir 'configs\\windows\\omerta-console.bat'

$controlEnv = @{ ENV_FILE = $EnvFile }
$gatewayEnv = @{ ENV_FILE = $EnvFile; NODE_ENV = 'production' }
$consolePort = Get-EnvValue -FilePath $EnvFile -Key 'CONSOLE_PORT'
if (-not $consolePort) { $consolePort = '3001' }
$consoleEnv = @{ ENV_FILE = $EnvFile; NODE_ENV = 'production'; CONSOLE_PORT = $consolePort }

Install-Or-UpdateService -Name 'OmertaControl' -Executable $controlBat -Arguments '' -WorkingDirectory (Join-Path $AppDir 'control') -Environment $controlEnv
Install-Or-UpdateService -Name 'OmertaGateway' -Executable $gatewayBat -Arguments '' -WorkingDirectory (Join-Path $AppDir 'gateway') -Environment $gatewayEnv
Install-Or-UpdateService -Name 'OmertaConsole' -Executable $consoleBat -Arguments '' -WorkingDirectory (Join-Path $AppDir 'console') -Environment $consoleEnv

$controlPort = Get-EnvValue -FilePath $EnvFile -Key 'CONTROL_PORT'
if (-not $controlPort) { $controlPort = '8000' }
$gatewayPort = Get-EnvValue -FilePath $EnvFile -Key 'GATEWAY_PORT'
if (-not $gatewayPort) { $gatewayPort = '3000' }

Write-Host "Installation complete."
Write-Host "  Control : http://localhost:$controlPort"
Write-Host "  Gateway : http://localhost:$gatewayPort"
Write-Host "  Console : http://localhost:$consolePort"
Write-Host "Use scripts\\smoke.ps1 to verify the installation."
