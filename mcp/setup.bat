@echo off
REM ClashGuard MCP — One-Click Setup for Windows
REM This script sets up the complete Python environment and dependencies

setlocal enabledelayedexpansion

echo.
echo ========================================
echo ClashGuard MCP — Setup Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.11+ from https://www.python.org
    pause
    exit /b 1
)

echo [OK] Python detected
python --version

REM Get project root
cd /d "%~dp0"
set PROJECT_ROOT=%cd%

echo [OK] Project root: %PROJECT_ROOT%
echo.

REM Step 1: Create virtual environment
echo [STEP 1/5] Creating Python virtual environment...
if exist venv (
    echo [SKIP] venv already exists
) else (
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
)

REM Step 2: Activate virtual environment
echo [STEP 2/5] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment activated

REM Step 3: Upgrade pip
echo [STEP 3/5] Upgrading pip...
python -m pip install --upgrade pip --quiet
echo [OK] pip upgraded

REM Step 4: Install dependencies
echo [STEP 4/5] Installing dependencies...
echo This may take 2-3 minutes...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    echo Try running: pip install -r requirements.txt
    pause
    exit /b 1
)
echo [OK] All dependencies installed

REM Step 5: Run verification
echo [STEP 5/5] Verifying installation...
python test_setup.py
if errorlevel 1 (
    echo [ERROR] Verification failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo [SUCCESS] Setup completed!
echo ========================================
echo.
echo Next steps:
echo 1. Set up Claude Desktop config (see SETUP_GUIDE.md)
echo 2. To start the MCP server: python server.py
echo 3. To run tests: pytest tests/ -v
echo 4. To see demo: python -c "from test_setup import *"
echo.
echo For detailed instructions, see: SETUP_GUIDE.md
echo.
pause
