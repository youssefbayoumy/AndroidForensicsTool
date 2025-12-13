# Android Forensics Tool

A Python-based digital forensics tool for extracting and analyzing communication artifacts from Android devices.

## Features

- **SMS/MMS Extraction**: Parses SMS messages from Android devices
- **Call Log Analysis**: Extracts call history including incoming, outgoing, and missed calls
- **Browser History**: Analyzes Chrome browsing history
- **Timeline Generation**: Creates chronological reports of all extracted artifacts

## Prerequisites

### Hardware
- Target: Android Phone (reset and generate test data)
- Host: Computer (Windows/Linux/Mac)

### Software
- **Python 3.x**: Required for running the tool
- **ADB (Android Debug Bridge)**: For communicating with the Android device
- **Root Access** (Highly Recommended): Required to access `/data/data/` directories

## Setup Instructions

### Step 1: Enable USB Debugging on Android Device

1. Go to **Settings > About Phone**
2. Tap **Build Number** 7 times until it says "You are a developer"
3. Go back to **Settings > System > Developer Options**
4. Enable **USB Debugging**

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Root Access (Recommended)

Forensics tools usually require root privileges to access `/data/data/`, where user databases are stored. 

- If you cannot root the phone, you'll need to use the `adb backup` method (more complex to parse)
- This guide assumes you have root access (e.g., via Magisk or SuperSU) or can run `adb root`

### Step 4: Extract Database Files

Use ADB to pull the database files from your Android device:

```bash
# Enable root mode
adb root

# Create evidence folder (if not exists)
mkdir -p evidence

# Extract SMS/MMS database
adb pull /data/data/com.android.providers.telephony/databases/mmssms.db ./evidence/

# Extract Call Logs
adb pull /data/data/com.android.providers.contacts/databases/calllog.db ./evidence/

# Extract Chrome History
adb pull /data/data/com.android.chrome/app_chrome/Default/History ./evidence/
```

**Note**: Paths may vary slightly by Android version. If `calllog.db` doesn't exist, it might be inside `contacts2.db`.

## Usage

1. Place your extracted `.db` files in the `evidence/` folder
2. Run the main script:

```bash
python main.py
```

3. The tool will generate a `Forensic_Report.csv` file with a chronological timeline of all artifacts

## Project Structure

```
AndroidForensicsTool/
    ├── main.py              # Main orchestrator script
    ├── parser.py            # Database parsing functions
    ├── requirements.txt     # Python dependencies
    ├── README.md           # This file
    └── evidence/           # Place your .db files here
        ├── mmssms.db
        ├── calllog.db
        └── History
```

## Database Locations

| Artifact | Typical Path |
|----------|-------------|
| SMS/MMS | `/data/data/com.android.providers.telephony/databases/mmssms.db` |
| Contacts | `/data/data/com.android.providers.contacts/databases/contacts2.db` |
| Call Logs | `/data/data/com.android.providers.contacts/databases/calllog.db` |
| Chrome History | `/data/data/com.android.chrome/app_chrome/Default/History` |

## Output

The tool generates a CSV file (`Forensic_Report.csv`) containing:
- **Date/Time**: Chronologically sorted timestamps
- **Artifact Type**: SMS, Call Log, or Browser History
- **Details**: Message content, phone numbers, URLs, etc.

## Testing

1. **Populate the Phone**: 
   - Send a few texts to the phone
   - Make some calls
   - Visit some websites (e.g., search for "how to hide assets")

2. **Extract**: Use ADB to pull the `.db` files into your evidence folder

3. **Run**: Execute `python main.py`

4. **Analyze**: Open the generated CSV file to see the chronological sequence

## Future Enhancements

- **App List**: Parse `/data/system/packages.xml` to list all installed apps
- **GUI**: Use tkinter or PyQt for a graphical interface
- **Hash Validation**: Calculate MD5 hashes of `.db` files before analysis to prove they haven't been tampered with
- **Additional Artifacts**: WhatsApp, Telegram, Instagram, etc.

## Troubleshooting

- **"No evidence files found"**: Ensure database files are in the `evidence/` folder with correct names
- **Permission Denied**: Make sure you have root access and `adb root` is enabled
- **Database locked**: Close any applications that might be using the database files
- **Path not found**: Android versions may have slightly different paths - check your device's specific paths

## Legal Notice

This tool is for educational and authorized forensic purposes only. Always ensure you have proper authorization before analyzing any device.

