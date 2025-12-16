# Quick Start Guide - GUI Applications

## Windows Users

1. **Install Python** (if not already installed)
   - Download from: https://www.python.org/downloads/
   - Make sure to check "Add Python to PATH" during installation

2. **Install ADB**
   - Download: https://developer.android.com/studio/releases/platform-tools
   - Extract and add to system PATH

3. **Install Dependencies**
   ```cmd
   pip install pandas
   ```

4. **Run the Application**
   - Double-click `run_windows.bat`
   - OR open Command Prompt and run: `python gui_windows.py`

## Linux Users

1. **Install Python** (usually pre-installed)
   ```bash
   # Ubuntu/Debian
   sudo apt-get install python3 python3-pip
   
   # Fedora
   sudo dnf install python3 python3-pip
   ```

2. **Install ADB**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install android-tools-adb
   
   # Fedora
   sudo dnf install android-tools
   ```

3. **Install Dependencies**
   ```bash
   pip3 install pandas
   ```

4. **Run the Application**
   ```bash
   ./run_linux.sh
   # OR
   python3 gui_linux.py
   ```

## First Time Setup

1. **Connect Android Device**
   - Use USB cable
   - Enable USB Debugging:
     - Settings > About Phone > Tap "Build Number" 7 times
     - Settings > Developer Options > Enable "USB Debugging"

2. **Open the Application**

3. **Click "Check Device Connection"**
   - Wait for confirmation

4. **Click "Extract All Data"**
   - Wait for extraction to complete (progress bar will show status)

5. **Click "Parse & Generate Report"**
   - Creates the forensic timeline

6. **Click "View Report"**
   - Opens the CSV file with all extracted data

## That's It!

The application handles everything automatically:
- ✅ Extracts all supported data types
- ✅ Verifies data completeness
- ✅ Shows errors with fix instructions
- ✅ Displays progress in real-time
- ✅ Generates comprehensive reports

For detailed information, see `GUI_README.md`

