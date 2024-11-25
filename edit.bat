@echo off
setlocal

:: Set UTF-8 code page
chcp 65001 > nul

:: Get script directory
set "SCRIPT_DIR=%~dp0"

:: Display welcome message
echo =======================================
echo    Welcome to ByEdit Editor Enhancer
echo    Starting up, please wait...
echo =======================================

:: Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not detected, please install Python 3.7 or higher
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Check if parameters exist
if not "%~1"=="" (
    echo [NOTE] Currently only supports dragging files to editor window
    echo Please run the edit command directly, then drag files into the editor
    pause
    exit /b 1
)

:: Call Python script
echo [INFO] Starting editor...
python "%SCRIPT_DIR%open_editor.py"
if errorlevel 1 (
    echo [ERROR] Startup failed, please check configuration or reinstall
    echo Press any key to exit...
    pause > nul
)