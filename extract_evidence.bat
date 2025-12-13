@echo off
REM Android Forensics Tool - Evidence Extraction Script (Windows)
REM This script automates the extraction of database files from an Android device

echo === Android Forensics - Evidence Extraction ===
echo.

REM Check if ADB is available
where adb >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] ADB not found. Please install Android Debug Bridge.
    echo Installation: https://developer.android.com/studio/command-line/adb
    exit /b 1
)

REM Check if device is connected
adb devices | findstr /R "device$" >nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] No Android device detected.
    echo Please:
    echo   1. Connect your Android device via USB
    echo   2. Enable USB Debugging
    echo   3. Accept the debugging prompt on your device
    exit /b 1
)

echo [INFO] Device detected
echo.

REM Create evidence directory
if not exist "evidence" mkdir evidence

REM Enable root mode
echo [INFO] Attempting to enable root mode...
adb root
timeout /t 2 /nobreak >nul

echo.
echo === Extracting Database Files ===
echo.

REM Extract SMS/MMS database
echo [1/3] Extracting SMS/MMS database...
adb pull /data/data/com.android.providers.telephony/databases/mmssms.db ./evidence/ >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   [OK] SMS database extracted successfully
) else (
    echo   [FAIL] Failed to extract SMS database (may require root or path may differ)
)

REM Extract Call Logs
echo [2/3] Extracting Call Logs...
adb pull /data/data/com.android.providers.contacts/databases/calllog.db ./evidence/ >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   [OK] Call log database extracted successfully
) else (
    echo   [FAIL] Failed to extract call log database (may require root or path may differ)
    echo   [INFO] Trying alternative location (contacts2.db)...
    adb pull /data/data/com.android.providers.contacts/databases/contacts2.db ./evidence/ >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo   [OK] Contacts database extracted (call logs may be inside)
    )
)

REM Extract Chrome History
echo [3/3] Extracting Chrome History...
adb pull /data/data/com.android.chrome/app_chrome/Default/History ./evidence/ >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   [OK] Chrome history extracted successfully
) else (
    echo   [FAIL] Failed to extract Chrome history (Chrome may not be installed or path may differ)
)

echo.
echo === Extraction Complete ===
echo.
echo Extracted files are in the 'evidence' folder.
echo You can now run: python main.py

