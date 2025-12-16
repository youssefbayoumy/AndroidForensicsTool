@echo off
REM Windows Launcher for Android Forensics Tool GUI

echo Starting Android Forensics Tool (Windows)...
echo.

REM Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.x from https://www.python.org/
    pause
    exit /b 1
)

REM Run the Windows GUI
python gui_windows.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo An error occurred. Please check the error message above.
    pause
)

