"""
Batch script to start GHOST server on Windows.
Double-click this file to start the backend server.
"""

@echo off
cls
echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║          GHOST Relay Server - Startup                  ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.11+
    echo    Visit: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Change to script directory
cd /d "%~dp0"

REM Check if .env file exists
if not exist "ghost_relay\.env" (
    echo ⚠️  WARNING: No .env file found!
    echo    The server needs your Gemini API key.
    echo.
    echo    1. Edit ghost_relay\.env
    echo    2. Replace 'your_api_key_here' with your actual key
    echo    3. Save and run this script again
    echo.
    pause
    exit /b 1
)

REM Check if .env has API key configured
findstr /C:"your_api_key_here" "ghost_relay\.env" >nul
if not errorlevel 1 (
    echo ❌ ERROR: API key not configured!
    echo    Edit ghost_relay\.env and add your Gemini API key
    pause
    exit /b 1
)

echo ✓ Python found
echo ✓ Configuration found
echo.
echo 🚀 Starting GHOST Relay Server...
echo    Server will be available at: http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo.

REM Change to ghost_relay directory
cd ghost_relay

REM Start the server
python main_server.py

if errorlevel 1 (
    echo.
    echo ❌ Error starting server!
    echo    Check the output above for details.
    pause
)
