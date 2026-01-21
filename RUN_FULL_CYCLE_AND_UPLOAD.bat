@echo off
setlocal enableextensions enabledelayedexpansion

REM Determine project root (directory of this BAT)
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM Prepare logs
if not exist "logs" mkdir "logs" >nul 2>&1
for /f "tokens=1-4 delims=/. " %%a in ("%date%") do set D=%%d-%%b-%%c
for /f "tokens=1-3 delims=:.," %%h in ("%time%") do set T=%%h-%%i-%%j
set "TS=%D%_%T%"
set "TS=%TS: =0%"
set "LOG_FILE=%SCRIPT_DIR%logs\run_%TS%.log"

echo =============================================== > "%LOG_FILE%"
echo Coffee Price Monitor - Full Cycle Run           >> "%LOG_FILE%"
echo Started: %date% %time%                          >> "%LOG_FILE%"
echo Project: %SCRIPT_DIR%                           >> "%LOG_FILE%"
echo =============================================== >> "%LOG_FILE%"

REM Prefer venv Python if exists
set "PY_BIN=python"
if exist "%SCRIPT_DIR%venv\Scripts\python.exe" set "PY_BIN=%SCRIPT_DIR%venv\Scripts\python.exe"

REM Ensure .env exists (for upload_data.py)
if not exist ".env" (
  echo [WARN] .env not found in project root. Upload may fail without API_KEY/API_UPLOAD_URL >> "%LOG_FILE%"
)

echo [STEP 1] Running full cycle... >> "%LOG_FILE%"
"%PY_BIN%" run_full_cycle.py >> "%LOG_FILE%" 2>&1
set "RC=%ERRORLEVEL%"
echo [INFO] run_full_cycle.py exit code: %RC% >> "%LOG_FILE%"

echo.>>"%LOG_FILE%"
echo [STEP 2] Uploading last result to web... >> "%LOG_FILE%"
"%PY_BIN%" upload_data.py >> "%LOG_FILE%" 2>&1
set "RC2=%ERRORLEVEL%"
echo [INFO] upload_data.py exit code: %RC2% >> "%LOG_FILE%"

echo.>>"%LOG_FILE%"
echo Finished: %date% %time% >> "%LOG_FILE%"
echo Log saved to: "%LOG_FILE%"

echo.
echo ===============================================
echo Done. Log: "%LOG_FILE%"
echo Close this window or press any key to open log.
pause >nul
start "Log" notepad.exe "%LOG_FILE%"

exit /b %RC2%
