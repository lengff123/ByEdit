@echo off
setlocal

:: Get script directory
set "SCRIPT_DIR=%~dp0"

:: Check if parameters exist
if not "%~1"=="" (
    echo Only drag-and-drop file opening is supported now, command line parameters are no longer supported
    echo Please run the edit command directly, then drag files into the editor window
    pause
    exit /b 1
)

:: Call Python script
python "%SCRIPT_DIR%open_editor.py"
if errorlevel 1 (
    echo Startup failed, press any key to exit...
    pause > nul
)