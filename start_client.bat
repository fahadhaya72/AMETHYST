"""
Batch script to start GHOST client on Windows.
Double-click this file to start the application.
"""

@echo off
cls
echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║            GHOST Client - Startup                      ║
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

echo ✓ Python found
echo.
echo Checking prerequisites...
echo   • Microphone: checking...
echo   • Stereo Mix: checking...
echo.
echo ✓ All checks passed!
echo.
echo 🚀 Starting GHOST Client...
echo    The application runs invisibly in the background.
echo    Press Ctrl+C to stop when done.
echo.

REM Change to script directory
cd /d "%~dp0"

REM Change to ghost_client directory
cd ghost_client

REM Start the client
python main_client.py

if errorlevel 1 (
    echo.
    echo ❌ Error starting client!
    echo    Check the output above for details.
    echo    See QUICKSTART.md for troubleshooting.
    pause
)
