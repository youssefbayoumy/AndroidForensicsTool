# Android Forensics Tool - GUI Applications

## Overview

This project includes two fully functional GUI applications for extracting and analyzing Android device data:

- **Windows Application** (`gui_windows.py`) - Optimized for Windows 7/8/10/11
- **Linux Application** (`gui_linux.py`) - Optimized for Linux distributions

Both applications provide the same comprehensive functionality with platform-specific optimizations.

## Features

### ✅ Complete Feature Set

- **Automatic Data Extraction**: Extracts all supported data types without user intervention
- **Data Completeness Verification**: Verifies data integrity before and after extraction
- **Comprehensive Error Handling**: User-friendly error messages with step-by-step fix instructions
- **Real-time Progress Indicators**: Visual progress bars and status messages
- **Non-Technical User Friendly**: Intuitive interface designed for users without technical background

### 📊 Supported Data Types

1. **SMS/MMS Messages** - All text messages (incoming and outgoing)
2. **Call Logs** - All call records (incoming, outgoing, missed)
3. **Chrome Browser History** - Complete browsing history

### 🔍 Data Verification

- File existence verification
- Database integrity checks
- Table presence validation
- Row count verification
- MD5 hash calculation for forensic integrity

## Installation

### Prerequisites

1. **Python 3.7 or higher**
   - Windows: Download from [python.org](https://www.python.org/downloads/)
   - Linux: Usually pre-installed, or install via package manager

2. **ADB (Android Debug Bridge)**
   - Windows: Download from [Android Developer](https://developer.android.com/studio/releases/platform-tools)
   - Linux: Install via package manager (see below)

3. **Required Python Packages**
   ```bash
   pip install -r requirements.txt
   ```

### Linux ADB Installation

```bash
# Ubuntu/Debian
sudo apt-get install android-tools-adb

# Fedora
sudo dnf install android-tools

# Arch Linux
sudo pacman -S android-tools
```

## Usage

### Windows

1. **Double-click** `run_windows.bat`
   - OR run from command prompt: `python gui_windows.py`

2. **Connect your Android device** via USB

3. **Enable USB Debugging** on your device:
   - Settings > About Phone > Tap "Build Number" 7 times
   - Settings > Developer Options > Enable "USB Debugging"

4. **Click "Check Device Connection"** in the GUI

5. **Click "Extract All Data"** to start automatic extraction

6. **Click "Parse & Generate Report"** to create the forensic timeline

7. **Click "View Report"** to open the generated CSV file

### Linux

1. **Run the launcher script**:
   ```bash
   ./run_linux.sh
   ```
   - OR run directly: `python3 gui_linux.py`

2. Follow the same steps as Windows (steps 2-7 above)

## Application Workflow

### Step 1: Device Connection Check
- Verifies ADB is installed and working
- Checks if Android device is connected
- Provides fix instructions if issues are detected

### Step 2: Automatic Data Extraction
The application automatically:
1. Enables root access (if available)
2. Extracts SMS database from all known locations
3. Extracts call logs from all known locations
4. Extracts Chrome history from all known locations
5. Verifies each extracted file
6. Calculates MD5 hashes for forensic integrity

### Step 3: Data Verification
- Checks file existence and size
- Validates database structure
- Verifies required tables are present
- Counts rows in each table
- Displays verification results in dedicated tab

### Step 4: Error Handling
If errors occur:
- Clear error messages explain what went wrong
- Step-by-step fix instructions are provided
- Errors are categorized by type
- Warnings are shown for non-critical issues

### Step 5: Report Generation
- Parses all extracted databases
- Creates chronological timeline
- Exports to CSV format
- Displays record counts

## User Interface

### Main Window Components

1. **Device Status Section**
   - Shows current device connection status
   - "Check Device Connection" button

2. **Progress Section**
   - Real-time progress bar (0-100%)
   - Step-by-step status messages

3. **Action Buttons**
   - 🔍 Extract All Data
   - 📊 Parse & Generate Report
   - 📄 View Report

4. **Results Tabs**
   - **Summary**: Overview of extracted files and status
   - **Errors & Fixes**: Detailed error messages with fix instructions
   - **Verification**: Data integrity verification results

5. **Status Bar**
   - Current operation status
   - Color-coded messages (green=success, red=error, blue=in progress)

## Error Handling

### Common Errors and Fixes

#### ADB Not Found
**Error**: "ADB not found in PATH"

**Fix Instructions**:
- Windows: Download Android Platform Tools and add to PATH
- Linux: Install via package manager (see Installation section)

#### Device Not Connected
**Error**: "No Android device detected"

**Fix Instructions**:
1. Connect device via USB
2. Enable USB Debugging in Developer Options
3. Allow USB debugging when prompted on device
4. Use a data cable (not just charging)
5. Try different USB port

#### Root Access Required
**Warning**: "Root access not available"

**Fix Instructions**:
1. Root your device (using Magisk, SuperSU, etc.)
2. Run `adb root` in terminal
3. Some data may be inaccessible without root

#### Database Extraction Failed
**Error**: "Failed to extract [data type]"

**Fix Instructions**:
1. Verify device is rooted
2. Check if the app is installed (e.g., Chrome for browser history)
3. Try running `adb root` manually
4. Some devices have different database paths

## Data Verification

The application performs comprehensive verification:

### Before Extraction
- Checks ADB availability
- Verifies device connection
- Attempts root access

### During Extraction
- Verifies file was successfully pulled
- Checks file is not empty
- Validates file size

### After Extraction
- Database integrity checks
- Table presence verification
- Row count validation
- MD5 hash calculation

All verification results are displayed in the "Verification" tab.

## Output Files

### Extracted Databases
- Location: `evidence/` folder
- Files:
  - `mmssms.db` - SMS/MMS messages
  - `calllog.db` - Call logs
  - `History` - Chrome browser history

### Forensic Report
- File: `Forensic_Report.csv`
- Format: Chronological timeline of all artifacts
- Columns: Date, Artifact Type, Details (varies by type)

## Technical Details

### Architecture
- **Core Module** (`core_extractor.py`): Handles all ADB communication and extraction
- **Parser Module** (`parser.py`): Parses SQLite databases
- **GUI Modules**: Platform-specific user interfaces

### Threading
- All extraction operations run in background threads
- UI remains responsive during extraction
- Progress updates in real-time

### Platform Optimizations

**Windows**:
- Uses Windows Vista/7/8/10 theme
- Segoe UI fonts
- Windows-specific file opening

**Linux**:
- Uses Clam theme (GTK-like)
- DejaVu Sans fonts
- xdg-open for file opening

## Troubleshooting

### Application Won't Start
- Check Python is installed: `python --version` or `python3 --version`
- Install dependencies: `pip install -r requirements.txt`
- Check for error messages in terminal

### Extraction Fails
- Verify device is connected: `adb devices`
- Check USB debugging is enabled
- Ensure device is rooted (for /data/data/ access)
- Check the "Errors & Fixes" tab for specific instructions

### No Data Extracted
- Some devices may have different database paths
- Verify the apps are installed (SMS app, Chrome, etc.)
- Check if device is rooted
- Review verification tab for details

### Report Generation Fails
- Ensure extraction completed successfully
- Check that database files exist in `evidence/` folder
- Verify database files are not corrupted
- Check error messages in the application

## Support

For issues or questions:
1. Check the "Errors & Fixes" tab in the application
2. Review this documentation
3. Check that all prerequisites are installed
4. Verify device connection and root access

## Legal Notice

This tool is for educational and authorized forensic purposes only. Always ensure you have proper authorization before analyzing any device.

