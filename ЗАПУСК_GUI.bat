@echo off
chcp 65001 >nul
echo ========================================
echo Price Monitor - Запуск GUI
echo ========================================
echo.

cd /d "%~dp0"

echo Проверка Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден!
    echo.
    echo Установите Python 3.11+ с https://www.python.org/downloads/
    echo При установке поставьте галочку "Add Python to PATH"
    pause
    exit /b 1
)

echo [OK] Python найден
echo.
echo Запуск GUI приложения...
echo.

python portable_build\gui_app.py

if errorlevel 1 (
    echo.
    echo [ОШИБКА] Ошибка запуска
    echo.
    echo Возможные причины:
    echo 1. Не установлены зависимости: pip install -r requirements.txt
    echo 2. Файл gui_app.py поврежден
    echo.
    pause
)

