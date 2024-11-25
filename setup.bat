@echo off
setlocal EnableDelayedExpansion

:: Get full path of script directory
set "INSTALL_DIR=%~dp0"
set "INSTALL_DIR=%INSTALL_DIR:~0,-1%"

:menu
cls
echo ============================
echo    Editor Installation
echo ============================
echo 1. Install
echo 2. Uninstall 
echo 3. Check Environment
echo 4. Exit
echo ----------------------------
set /p choice=Please select (1-4): 

if "%choice%"=="1" goto check_env
if "%choice%"=="2" goto uninstall
if "%choice%"=="3" goto check_env_only
if "%choice%"=="4" exit /b
goto menu

:check_env_only
call :check_env
pause
goto menu

:check_env
:: Check Python installation and version
echo Checking Python environment...
echo ----------------------------

:: Check Python installation and location
for /f "delims=" %%i in ('where python 2^>^&1') do (
    echo Python location: %%i
)

:: Check Python installation
python --version >nul 2>&1
if !errorlevel! neq 0 (
    echo [ERROR] Python not found
    echo Please install Python 3.7+ from: https://www.python.org/downloads/
    if "%~1"=="" pause & exit /b 1
    exit /b 1
)

:: Get and check Python version
for /f "tokens=2 delims= " %%i in ('python --version 2^>^&1') do set pyver=%%i
for /f "tokens=1,2,3 delims=." %%a in ("!pyver!") do (
    set major=%%a
    set minor=%%b
    set patch=%%c
)

echo Found Python version: !pyver!
if !major! lss 3 (
    echo [ERROR] Python version too old
    echo Required: Python 3.7 or higher
    echo Current: Python !pyver!
    if "%~1"=="" pause & exit /b 1
    exit /b 1
)
if !major!==3 if !minor! lss 7 (
    echo [ERROR] Python version too old
    echo Required: Python 3.7 or higher
    echo Current: Python !pyver!
    if "%~1"=="" pause & exit /b 1
    exit /b 1
)

:: Check pip installation
echo Checking pip installation...
python -m pip --version >nul 2>&1
if !errorlevel! neq 0 (
    echo [ERROR] pip not installed
    echo Installing pip...
    python -m ensurepip --default-pip
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to install pip
        if "%~1"=="" pause & exit /b 1
        exit /b 1
    )
)

:: Check and install required packages
echo Checking required packages...
echo ----------------------------

:: Define required packages
set "packages=fastapi uvicorn[standard] websockets python-multipart"

:: Update pip
echo Updating pip...
python -m pip install --upgrade pip

:: Install/upgrade required packages
for %%p in (%packages%) do (
    echo Checking %%p...
    python -m pip install --upgrade %%p
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to install %%p
        if "%~1"=="" pause & exit /b 1
        exit /b 1
    )
)

echo.
echo [SUCCESS] Environment check completed
echo Python version: !pyver!
echo Required packages installed
echo ----------------------------
echo.

if "%~1"=="" (
    if "%choice%"=="1" goto install
    pause
    exit /b 0
)
exit /b 0

:install
:: Run uninstall first for clean installation
set "choice=1"
goto uninstall

:do_install
:: Read current PATH from user environment
for /f "tokens=2*" %%a in ('reg query "HKCU\Environment" /v PATH') do set "USER_PATH=%%b"

:: Add to PATH
setx PATH "%USER_PATH%;%INSTALL_DIR%"

echo.
echo ============================
echo    Installation Complete
echo ============================
echo.
echo [Environment]
echo Python Version: !pyver!
echo Python Location: !INSTALL_DIR!
echo.
echo [Application]
echo 1. Editor is ready to use
echo 2. Start the editor:
echo    - In CMD: edit <文件路径>
echo    - In PowerShell: .\edit <文件路径>
echo 3. Default port: 8000
echo 4. Access via: http://localhost:8000
echo.
echo [Note]
echo - Please reopen command prompt to use the editor
echo - Use Ctrl+C to stop the editor
echo - If using PowerShell, remember to use .\edit
echo ============================
echo.
pause
goto menu

:uninstall
:: Read current PATH from user environment
for /f "tokens=2*" %%a in ('reg query "HKCU\Environment" /v PATH') do set "USER_PATH=%%b"

:: Check if already installed
echo !USER_PATH! | findstr /C:"%INSTALL_DIR%" >nul
if !errorlevel! neq 0 (
    echo.
    echo Editor not installed!
    timeout /t 2 >nul
    goto menu
)

:: Remove install directory from PATH
set "NEW_PATH=!USER_PATH:%INSTALL_DIR%;=!"
set "NEW_PATH=!NEW_PATH:;%INSTALL_DIR%=!"
set "NEW_PATH=!NEW_PATH:%INSTALL_DIR%=!"

:: Update PATH
setx PATH "!NEW_PATH!"
echo.
echo Uninstallation complete!
if "%choice%"=="1" goto do_install
timeout /t 2 >nul
goto menu