# Android Forensics Tool - Enhanced Edition

A Python-based digital forensics tool for extracting and analyzing communication artifacts and system data from Android devices. Optimized for both **Rooted** and **Non-Rooted** devices (Android 13+ support).

## key Features

### 🔍 Advanced Extraction
- **SMS/MMS Extraction**: Parses detailed message history.
- **Call Log Analysis**: Extracts incoming, outgoing, and missed calls.
- **Browser History**: Analyzes Chrome browsing activity.
- **Shared Storage**: (NEW) Extracts photos, videos, and documents from user folders.
- **System Dump**: (NEW) Collects installed app lists, permissions, and device props.
- **App Usage Stats**: (NEW) Analyzes `usagestats` to reveal recent app activity.
- **Content Query**: (NEW) Direct API access for **Calendar Events**, **User Dictionary**, and **Contacts** without root.

### 📊 Analysis & Reporting
- **Timeline Generation**: Creates a master chronological timeline of all events.
- **Hash Validation**: Verifies integrity of extracted files with MD5 hashes.
- **Case Management**: Organizes evidence into case-specific folders.
- **Built-in Report Viewer**: (NEW) view, filter, and search your evidence directly in the tool (No Excel needed!).

## Prerequisites

### Hardware
- Target: Android Phone (Developer Mode ON)
- Host: Computer (Windows/Linux/Mac)

### Software
- **Python 3.x**: Required for running the tool
- **ADB (Android Debug Bridge)**: Must be installed and in your system PATH.

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### 1. Launch the GUI
Run the Windows-optimized interface:
```bash
python gui_windows.py
```

### 2. Connect Device
- Enable **USB Debugging** on your phone.
- Click **"Check Device Connection"** in the tool.

### 3. Extract Evidence
*   **Rooted Devices**: Click "Extract All Data (Root)" for fast, direct file access.
*   **Non-Rooted Devices**: Click **"Extract via Backup (Non-Root)"**.
    *   This runs a smart multi-stage extraction:
        1.  **ADB Backup**: Tries to get databases.
        2.  **Shared Storage**: Pulls photos/docs.
        3.  **System Dump**: Grabs app lists & usage stats.
        4.  **Content Query**: Asks the OS for SMS/Calendar data directly (Great for Android 13+).

### 4. Analyze
- Click **"Parse & Generate Report"**.
- Click **"View Report"** to open the built-in viewer.
    - **Filter**: Dropdown to see only "SMS", "Calendar", etc.
    - **Search**: Type keywords to find evidence instantly.

## Project Structure

```
AndroidForensicsTool/
    ├── gui_windows.py       # Main GUI Application
    ├── core_extractor.py    # Extraction Engine (Root & Non-Root logic)
    ├── parser.py            # Data Parsers (SQL, XML, Text)
    ├── cases/               # Output Directory
    │   └── Case_Name/       # Specific Case Folder
    │       ├── evidence/    # Raw Extracted Files
    │       └── Forensic_Report.csv
    ├── requirements.txt     # Python dependencies
    └── README.md            # This file
```

## Database Locations (Reference)

| Artifact | Method | Path/Source |
|----------|--------|-------------|
| SMS/MMS | Root / Backup | `/data/data/com.android.providers.telephony/databases/mmssms.db` |
| Contacts | Root / Query | `/data/data/com.android.providers.contacts/databases/contacts2.db` |
| Calendar | Query | `content://com.android.calendar/events` |
| App Usage | System Dump | `dumpsys usagestats` |

## Legal Notice

This tool is for educational and authorized forensic purposes only. Always ensure you have proper authorization before analyzing any device.
