@echo off
REM Map Poster Generator - Automated Setup Script for Windows
REM This script sets up the entire environment for first-time users

echo ==========================================
echo Map Poster Generator - Setup
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo [OK] Python found
python --version

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo Please install Node.js 16+ from https://nodejs.org
    pause
    exit /b 1
)

echo [OK] Node.js found
node --version

echo.
echo ------------------------------------------
echo Setting up Python virtual environment...
echo ------------------------------------------

if exist ".venv" (
    echo [INFO] Virtual environment already exists
) else (
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
)

echo.
echo ------------------------------------------
echo Installing Python dependencies...
echo ------------------------------------------

.venv\Scripts\pip install --upgrade pip
if errorlevel 1 (
    echo [WARNING] Failed to upgrade pip, continuing...
)

.venv\Scripts\pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install Python dependencies
    pause
    exit /b 1
)

echo [OK] Python dependencies installed

echo.
echo ------------------------------------------
echo Installing Node.js dependencies...
echo ------------------------------------------

call npm install
if errorlevel 1 (
    echo [ERROR] Failed to install Node.js dependencies
    pause
    exit /b 1
)

echo [OK] Node.js dependencies installed

echo.
echo ------------------------------------------
echo Creating required directories...
echo ------------------------------------------

if not exist "outputs" mkdir outputs
if not exist "logs" mkdir logs
if not exist "cache" mkdir cache
if not exist ".cache" mkdir .cache

echo [OK] Directories created

echo.
echo ------------------------------------------
echo Verifying installation...
echo ------------------------------------------

.venv\Scripts\python -c "import osmnx; import matplotlib; import PIL; print('[OK] Core Python packages verified')"
if errorlevel 1 (
    echo [WARNING] Some Python packages may not be properly installed
)

echo.
echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo To run the application:
echo   1. Double-click: launch_app.bat
echo   2. Or run: npm start
echo.
echo For command-line usage:
echo   .venv\Scripts\python create_map_poster.py --city "Paris" --country "France"
echo.
pause
