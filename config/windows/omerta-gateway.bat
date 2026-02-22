@echo off
setlocal enabledelayedexpansion
set SCRIPT_DIR=%~dp0
set APP_DIR=%SCRIPT_DIR%..\..
for %%I in ("%APP_DIR%") do set APP_DIR=%%~fI
set ENV_FILE=%APP_DIR%\.env
cd /d "%APP_DIR%\gateway"
set NODE_ENV=production
node "%APP_DIR%\gateway\dist\index.js"
