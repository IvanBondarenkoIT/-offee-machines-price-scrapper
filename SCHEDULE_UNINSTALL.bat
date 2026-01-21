@echo off
setlocal enableextensions

set "TASK_NAME=CoffeePriceMonitor_Daily"
schtasks /Delete /TN "%TASK_NAME%" /F
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" (
  echo [ERROR] Failed to delete task. Exit code: %RC%
  exit /b %RC%
)
schtasks /Query /TN "%TASK_NAME%" 2>nul
if "%ERRORLEVEL%"=="0" (
  echo [WARN] Task still present.
) else (
  echo [OK] Task deleted: %TASK_NAME%
)
exit /b 0
