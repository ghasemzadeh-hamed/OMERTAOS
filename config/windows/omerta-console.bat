@echo off
setlocal enabledelayedexpansion
set SCRIPT_DIR=%~dp0
set APP_DIR=%SCRIPT_DIR%..\..
for %%I in ("%APP_DIR%") do set APP_DIR=%%~fI
set ENV_FILE=%APP_DIR%\.env
cd /d "%APP_DIR%\console"
set NODE_ENV=production
if "%CONSOLE_PORT%"=="" set CONSOLE_PORT=3001
node "%APP_DIR%\console\node_modules\next\dist\bin\next" start --hostname 0.0.0.0 --port %CONSOLE_PORT%
