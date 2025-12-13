#!/bin/bash

# Android Forensics Tool - Evidence Extraction Script
# This script automates the extraction of database files from an Android device

echo "=== Android Forensics - Evidence Extraction ==="
echo ""

# Check if ADB is available
if ! command -v adb &> /dev/null; then
    echo "[ERROR] ADB not found. Please install Android Debug Bridge."
    echo "Installation: https://developer.android.com/studio/command-line/adb"
    exit 1
fi

# Check if device is connected
if ! adb devices | grep -q "device$"; then
    echo "[ERROR] No Android device detected."
    echo "Please:"
    echo "  1. Connect your Android device via USB"
    echo "  2. Enable USB Debugging"
    echo "  3. Accept the debugging prompt on your device"
    exit 1
fi

echo "[INFO] Device detected"
echo ""

# Create evidence directory
mkdir -p evidence

# Enable root mode
echo "[INFO] Attempting to enable root mode..."
adb root
sleep 2

# Check if root was successful
if adb shell "su -c 'id'" | grep -q "uid=0"; then
    echo "[SUCCESS] Root access granted"
else
    echo "[WARNING] Root access may not be available. Some files may not be accessible."
fi

echo ""
echo "=== Extracting Database Files ==="
echo ""

# Extract SMS/MMS database
echo "[1/3] Extracting SMS/MMS database..."
if adb pull /data/data/com.android.providers.telephony/databases/mmssms.db ./evidence/ 2>/dev/null; then
    echo "  ✓ SMS database extracted successfully"
else
    echo "  ✗ Failed to extract SMS database (may require root or path may differ)"
fi

# Extract Call Logs
echo "[2/3] Extracting Call Logs..."
if adb pull /data/data/com.android.providers.contacts/databases/calllog.db ./evidence/ 2>/dev/null; then
    echo "  ✓ Call log database extracted successfully"
else
    echo "  ✗ Failed to extract call log database (may require root or path may differ)"
    echo "  [INFO] Trying alternative location (contacts2.db)..."
    if adb pull /data/data/com.android.providers.contacts/databases/contacts2.db ./evidence/ 2>/dev/null; then
        echo "  ✓ Contacts database extracted (call logs may be inside)"
    fi
fi

# Extract Chrome History
echo "[3/3] Extracting Chrome History..."
if adb pull /data/data/com.android.chrome/app_chrome/Default/History ./evidence/ 2>/dev/null; then
    echo "  ✓ Chrome history extracted successfully"
else
    echo "  ✗ Failed to extract Chrome history (Chrome may not be installed or path may differ)"
fi

echo ""
echo "=== Extraction Complete ==="
echo ""
echo "Extracted files are in the 'evidence' folder."
echo "You can now run: python main.py"

