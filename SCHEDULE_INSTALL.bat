@echo off
setlocal enableextensions

REM Usage: SCHEDULE_INSTALL.bat HH:MM
REM Example: SCHEDULE_INSTALL.bat 08:30

if "%~1"=="" (
  echo Usage: %~nx0 HH:MM
  echo Example: %~nx0 08:30
  exit /b 1
)

set "RUN_TIME=%~1"
set "SCRIPT_DIR=%~dp0"
set "TASK_NAME=CoffeePriceMonitor_Daily"
set "RUN_BAT=%SCRIPT_DIR%RUN_FULL_CYCLE_AND_UPLOAD.bat"

if not exist "%RUN_BAT%" (
  echo [ERROR] %RUN_BAT% not found
  exit /b 2
)

REM Create the task to run daily at specified time under the current user context.
REM If you need it to run when no user is logged in, uncomment /RU and /RP and set credentials.

schtasks /Create ^
  /SC DAILY ^
  /TN "%TASK_NAME%" ^
  /TR "\"%RUN_BAT%\"" ^
  /ST "%RUN_TIME%" ^
  /RL HIGHEST ^
  /F

set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" (
  echo [ERROR] Failed to create task. Exit code: %RC%
  exit /b %RC%
)

schtasks /Query /TN "%TASK_NAME%"
exit /b 0
