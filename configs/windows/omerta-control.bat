@echo off
setlocal enabledelayedexpansion
set SCRIPT_DIR=%~dp0
set APP_DIR=%SCRIPT_DIR%..\..
for %%I in ("%APP_DIR%") do set APP_DIR=%%~fI
set ENV_FILE=%APP_DIR%\.env
if exist "%ENV_FILE%" (
  set "ENV_FILE=%ENV_FILE%"
)
cd /d "%APP_DIR%\control"
"%APP_DIR%\.venv\Scripts\python.exe" "%APP_DIR%\control\run_uvicorn.py"
