# ADB Backup Feature for Non-Rooted Devices

## Overview

The Android Forensics Tool now supports extracting data from **non-rooted Android devices** using the ADB backup method. This feature allows you to extract SMS, call logs, and browser history without requiring root access.

## How It Works

### ADB Backup Method

1. **Creates App-Specific Backups**: Uses `adb backup` to create backups of specific Android packages
2. **Parses Backup Files**: Extracts and parses the Android backup format (compressed tar archive)
3. **Extracts Databases**: Finds and extracts SQLite databases from the backup
4. **Verifies Data**: Performs the same verification as root extraction

### Supported Data Types

- ✅ **SMS/MMS**: `com.android.providers.telephony`
- ✅ **Call Logs**: `com.android.providers.contacts`
- ✅ **Chrome History**: `com.android.chrome`

## Usage

### In GUI Applications

1. **Connect your device** and click "Check Device Connection"
2. **Click "Extract via Backup (Non-Root)"** button
3. **Approve backups on your device**:
   - A backup prompt will appear on your Android device
   - Tap "Back up my data" for each app backup
   - Make sure your device screen is unlocked
4. **Wait for extraction** - progress will be shown in real-time
5. **View results** in the Summary, Errors, and Verification tabs

### Important Notes

⚠️ **User Interaction Required**: You must approve each backup on your Android device screen. The backup prompt appears automatically when the extraction starts.

⚠️ **Device Must Be Unlocked**: Keep your device screen unlocked during the backup process.

⚠️ **App Must Support Backup**: Some apps may not allow backup. If an app doesn't support backup, you'll see an error message.

## Backup File Format

Android backup files (`.ab` files) have a specific format:

```
[24 bytes] Magic string: "ANDROID BACKUP\n"
[4 bytes]  Version number (little-endian)
[4 bytes]  Compression flag (1 = deflate, 0 = none)
[rest]     Tar archive (possibly compressed with zlib)
```

The tool automatically:
1. Reads and validates the backup header
2. Decompresses if needed (zlib deflate)
3. Extracts the tar archive
4. Searches for database files
5. Copies databases to the evidence folder

## Backup Locations

Backups are stored in:
- **Backup files**: `evidence/{data_type}_backup.ab`
- **Extracted tar**: `evidence/backup_extracted/backup.tar`
- **Extracted databases**: `evidence/backup_extracted/extract_{data_type}/`
- **Final databases**: `evidence/{database_name}` (same as root extraction)

## Troubleshooting

### Backup Not Created

**Problem**: Backup file is not created or is empty

**Solutions**:
1. Make sure you approved the backup on your device
2. Keep device screen unlocked
3. Check that USB debugging is enabled
4. Try a different USB cable/port
5. Some apps don't support backup - you may need root for those

### Backup Parsing Fails

**Problem**: Error parsing backup file

**Solutions**:
1. Verify backup file exists and has content (>24 bytes)
2. Check backup file isn't corrupted
3. Try creating a new backup
4. Some Android versions use different backup formats

### Database Not Found in Backup

**Problem**: Backup created but database not found

**Solutions**:
1. The app may not include databases in backup
2. Database might be in a different location
3. Try using root extraction method if available
4. Check app backup settings on device

### Timeout Errors

**Problem**: Backup times out

**Solutions**:
1. Approve backup quickly on device (within 2 minutes)
2. Make sure device screen stays on
3. Don't disconnect USB during backup
4. Try one app at a time

## Comparison: Root vs Backup Method

| Feature | Root Method | Backup Method |
|---------|------------|---------------|
| **Requires Root** | ✅ Yes | ❌ No |
| **User Interaction** | ❌ No | ✅ Yes (approve on device) |
| **Speed** | ⚡ Fast | 🐢 Slower |
| **Completeness** | ✅ All data | ⚠️ Depends on app |
| **Reliability** | ✅ High | ⚠️ Medium |
| **Setup Complexity** | 🔴 High (root) | 🟢 Low (just USB debugging) |

## Best Practices

1. **Try Root Method First**: If your device is rooted, use root extraction (faster, more reliable)

2. **Use Backup for Non-Rooted**: Only use backup method when root is not available

3. **Keep Device Unlocked**: Always keep device screen unlocked during backup

4. **Approve Promptly**: Approve backup prompts quickly to avoid timeouts

5. **Check App Settings**: Some apps have backup settings that need to be enabled

6. **Verify Results**: Always check the Verification tab to ensure data completeness

## Technical Details

### Backup Creation Command

```bash
adb backup -f {backup_file} -noapk {package_name}
```

- `-f`: Specify output file
- `-noapk`: Skip APK files (faster, smaller)
- `package_name`: Android package to backup

### Backup Parsing Process

1. Read 24-byte magic string
2. Read 4-byte version
3. Read 4-byte compression flag
4. Read remaining data
5. Decompress if compression flag = 1
6. Extract tar archive
7. Search for database files
8. Copy to evidence directory

### Database Search Paths

The tool searches for databases in these backup paths:

- **SMS**: `apps/com.android.providers.telephony/db/mmssms.db`
- **Calls**: `apps/com.android.providers.contacts/db/calllog.db`
- **Chrome**: `apps/com.android.chrome/f/app_chrome/Default/History`

If not found in expected paths, the tool searches all `.db` files in the backup.

## Limitations

1. **App Support**: Not all apps support ADB backup
2. **User Approval**: Requires manual approval on device
3. **Speed**: Slower than root extraction
4. **Completeness**: May not include all app data
5. **Android Version**: Some older Android versions have backup limitations

## Future Enhancements

- Full device backup option
- Automatic backup approval (if possible)
- Support for more apps
- Backup encryption handling
- Incremental backup support

