# 🕵️ Android Digital Forensics Tool

> **A professional-grade, open-source forensic acquisition and analysis suite for Android devices.**
> *Optimized for Windows & Linux | Supports Android 5.0 - 14.0+*

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey)
![Status](https://img.shields.io/badge/Status-Active-success)

## 📖 Overview

The **Android Forensics Tool** is designed to extract, parse, and visualize digital evidence from Android smartphones. Unlike standard ADB tools, it employs a **multi-layered extraction strategy** that combines direct file access (Root), system backups (Non-Root), and minimal-privilege API queries to maximize data recovery even on secure, modern Android versions.

It features a modern **GUI Dashboard** and a built-in **Report Viewer**, eliminating the need for external spreadsheet software to analyze results.

---

## 🚀 Key Features

### 1. Multi-Vector Data Extraction
We use four distinct methods to gather evidence, ensuring success even if one method fails:

*   **Communication Artifacts**:
    *   **SMS/MMS**: Recovers full conversation history, timestamps, and sender details.
    *   **Call Logs**: Incoming, outgoing, and missed call history with duration.
    *   **Contacts**: Saved contacts, phone numbers, and last contacted timestamps.
    *   **User Dictionary**: Recovers custom words typed by the user (slang, names, potential passwords).
    *   **Calendar Events**: Schedule, appointments, and location data.

*   **Application & System Intelligence**:
    *   **App Usage Stats**: (Non-Root supported) Analyzes `usagestats` to prove *when* specific apps were used and for how long.
    *   **Installed Apps**: Lists all 3rd party applications and their installation dates.
    *   **Permissions Analysis**: Identifies apps with dangerous permissions (e.g., Camera, Location).
    *   **Chrome History**: Parses web browsing history, titles, and visit times.

*   **File System**:
    *   **Shared Storage Extraction**: Automatically retrieves photos, videos, and documents from user directories (`/sdcard/DCIM`, `/Documents`, etc.).

### 2. Built-in Report Viewer (New!)
No more CSVs! The tool includes a powerful analysis dashboard:
*   **Unified Timeline**: See SMS, Calls, and System Events in one chronological stream.
*   **Dynamic Filtering**: Filter by "SMS", "Call", "Calendar", or "App Usage" instantly.
*   **Full-Text Search**: Find keywords like "password", "meet", or specific phone numbers.
*   **Detailed Inspection**: View full message bodies, including special characters and emojis.

### 3. Smart Extraction Engine
*   **Auto-Switching**: Automatically detects if a device is Rooted or Non-Rooted and selects the best extraction strategy.
*   **Case Management**: Automatically organizes evidence into `cases/Case_Name_Date/` folders.
*   **Hash Verification**: Calculates MD5 hashes for all extracted files to ensure forensic integrity.

---

## 🛠️ Installation

### Prerequisites
1.  **Python 3.8+**: [Download Here](https://www.python.org/downloads/)
2.  **ADB (Android Debug Bridge)**: Must be installed and added to your system `PATH`.
    *   *Windows*: Install "Platform Tools" via Android Studio or stand-alone.

### Setup
```bash
# 1. Clone the repository
git clone https://github.com/Start-5/AndroidForensicsTool.git
cd AndroidForensicsTool

# 2. Install dependencies
pip install -r requirements.txt
```

---

## 📱 User Guide (GUI)

### Step 1: Prepare Your Device
1.  On the Android phone, go to **Settings > About Phone**.
2.  Tap **Build Number** 7 times to enable Developer Mode.
3.  Go to **Developer Options** and enable **USB Debugging**.
4.  Connect the phone to your PC. Accept the "Allow USB Debugging?" prompt on the screen.

### Step 2: Launch the Tool
**Windows Users**:
```bash
python gui_windows.py
```

### Step 3: Create a Case
1.  Enter a **Case Name** (e.g., "Investigation_001") in the top field.
2.  Click **"Check Device Connection"**. You should see a green checkmark if ADB is working.

### Step 4: Extract Evidence
Choose the method that matches your device:

*   **Option A: Non-Rooted (Standard)**
    *   Click **"Extract via Backup (Non-Root)"**.
    *   **Action Required**: Watch your phone screen! You will be asked to "Back up my data". Tap **"Back up my data"** (bottom right) without entering a password.
    *   *What happens?* The tool performs a full desktop backup, queries Content Providers for SMS/Calendar, and dumps system stats.

*   **Option B: Rooted (Advanced)**
    *   Click **"Extract All Data (Root)"**.
    *   *What happens?* Direct copying of SQlite databases from protected system folders.

### Step 5: Analyze Results
1.  Wait for the progress bar to reach 100%. Check the "Summary" tab for extraction status.
2.  Click **"Parse & Generate Report"**. This processes the raw raw files into a timeline.
3.  Click **"View Report"** to open the Analysis Window.
    *   Use the **Filter Dropdown** to isolate specific evidence (e.g., just "User Dictionary").
    *   Click valid rows to see details in the bottom pane.

---

## ⚠️ Troubleshooting

**"ADB Not Found"**
*   Ensure `adb` is in your Windows Environment Variables (PATH).
*   Try running `adb devices` in a separate command prompt to verify connectivity.

**"Extraction Failed / Backup Empty"**
*   Did you tap "Back up my data" on the phone? The tool waits for this confirmation.
*   Some newer phones (Android 12+) may block standard ADB backups for certain apps. The tool automatically falls back to "Content Query" (API) mode to still get SMS and Contacts.

**"Permission Denied"**
*   Common on non-rooted devices when trying to pull specific /data/ files. Use "Extract via Backup" instead.

---

## ⚖️ Legal Disclaimer

**This software is intended for educational, research, and authorized forensic use only.**
The developers assume no liability and are not responsible for any misuse or damage caused by this program. Always ensure you have proper legal authorization (e.g., ownership, warrant, or consent) before extracting data from a device.
