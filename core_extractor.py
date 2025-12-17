"""
Core extraction and verification module for Android Forensics Tool
Handles ADB communication, data extraction, and completeness verification
"""

import os
import subprocess
import sqlite3
import hashlib
import platform
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import time
import tarfile
import zlib
import shutil

class AndroidExtractor:
    """Core class for extracting and verifying Android data"""
    
    # Database paths for different Android versions
    DATABASE_PATHS = {
        'sms': [
            '/data/data/com.android.providers.telephony/databases/mmssms.db',
            '/data/data/com.android.mms/databases/mmssms.db'
        ],
        'calls': [
            '/data/data/com.android.providers.contacts/databases/calllog.db',
            '/data/data/com.android.providers.contacts/databases/contacts2.db'
        ],
        'chrome': [
            '/data/data/com.android.chrome/app_chrome/Default/History',
            '/data/data/com.chrome.browser/app_chrome/Default/History'
        ],
        'contacts': [
            '/data/data/com.android.providers.contacts/databases/contacts2.db'
        ],
        'wifi': [
            '/data/misc/wifi/WifiConfigStore.xml',
            '/data/misc/wifi/wpa_supplicant.conf'
        ],
        'packages': [
            '/data/system/packages.xml'
        ]
    }
    
    # Package names for ADB backup (non-rooted devices)
    BACKUP_PACKAGES = {
        'sms': 'com.android.providers.telephony',
        'calls': 'com.android.providers.contacts',
        'chrome': 'com.android.chrome',
        'contacts': 'com.android.providers.contacts'
    }
    
    # Backup paths within extracted backup
    BACKUP_PATHS = {
        'sms': [
            'apps/com.android.providers.telephony/db/mmssms.db',
            'apps/com.android.providers.telephony/db/mmssms.db-journal',
            'apps/com.android.mms/db/mmssms.db'
        ],
        'calls': [
            'apps/com.android.providers.contacts/db/calllog.db',
            'apps/com.android.providers.contacts/db/contacts2.db'
        ],
        'chrome': [
            'apps/com.android.chrome/f/app_chrome/Default/History',
            'apps/com.android.chrome/f/app_chrome/Default/History-journal'
        ],
        'chrome': [
            'apps/com.android.chrome/f/app_chrome/Default/History',
            'apps/com.android.chrome/f/app_chrome/Default/History-journal'
        ],
        'contacts': [
            'apps/com.android.providers.contacts/db/contacts2.db'
        ]
    }
    
    # Shared storage paths to investigate
    SHARED_PATHS = [
        '/sdcard/DCIM/',
        '/sdcard/Download/',
        '/sdcard/Documents/',
        '/sdcard/Pictures/'
    ]
    
    def __init__(self, evidence_dir: str = "evidence"):
        self.evidence_dir = Path(evidence_dir)
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir = self.evidence_dir / "backup_extracted"
        self.backup_dir.mkdir(exist_ok=True)
        self.is_windows = platform.system() == "Windows"
        self.adb_path = self._find_adb()
        
    def _find_adb(self) -> str:
        """Find ADB executable path"""
        if self.is_windows:
            # Common Windows ADB locations
            possible_paths = [
                "adb.exe",
                os.path.join(os.environ.get("LOCALAPPDATA", ""), "Android", "Sdk", "platform-tools", "adb.exe"),
                os.path.join(os.environ.get("ProgramFiles", ""), "Android", "android-sdk", "platform-tools", "adb.exe"),
            ]
        else:
            possible_paths = ["adb", "/usr/bin/adb", "/usr/local/bin/adb"]
        
        for path in possible_paths:
            try:
                result = subprocess.run([path, "version"], 
                                      capture_output=True, 
                                      timeout=5)
                if result.returncode == 0:
                    return path
            except:
                continue
        
        return "adb"  # Fallback to PATH
    
    def check_adb_available(self) -> Tuple[bool, str]:
        """Check if ADB is available and working"""
        try:
            result = subprocess.run([self.adb_path, "version"], 
                                  capture_output=True, 
                                  text=True,
                                  timeout=5)
            if result.returncode == 0:
                return True, "ADB is available"
            else:
                return False, f"ADB returned error: {result.stderr}"
        except FileNotFoundError:
            return False, "ADB not found in PATH"
        except Exception as e:
            return False, f"Error checking ADB: {str(e)}"
    
    def check_device_connected(self) -> Tuple[bool, str]:
        """Check if Android device is connected"""
        try:
            result = subprocess.run([self.adb_path, "devices"], 
                                  capture_output=True, 
                                  text=True,
                                  timeout=10)
            
            if result.returncode != 0:
                return False, "Failed to run ADB devices command"
            
            lines = result.stdout.strip().split('\n')
            devices = [line for line in lines[1:] if line.strip() and 'device' in line]
            
            if not devices:
                return False, "No Android device detected"
            
            return True, f"Device connected: {devices[0].split()[0]}"
        except Exception as e:
            return False, f"Error checking device: {str(e)}"
    
    def enable_root(self) -> Tuple[bool, str]:
        """Attempt to enable root mode"""
        try:
            result = subprocess.run([self.adb_path, "root"], 
                                  capture_output=True, 
                                  text=True,
                                  timeout=10)
            time.sleep(2)  # Wait for root to take effect
            
            # Verify root
            check_result = subprocess.run([self.adb_path, "shell", "su", "-c", "id"], 
                                        capture_output=True, 
                                        text=True,
                                        timeout=5)
            
            if "uid=0" in check_result.stdout:
                return True, "Root access enabled"
            else:
                return False, "Root access not available (some files may be inaccessible)"
        except Exception as e:
            return False, f"Error enabling root: {str(e)}"
    
    def extract_database(self, remote_path: str, local_name: str) -> Tuple[bool, str, Optional[str]]:
        """
        Extract a database file from Android device
        
        Returns:
            (success, message, local_path)
        """
        local_path = self.evidence_dir / local_name
        
        try:
            # Try to pull the file
            result = subprocess.run([self.adb_path, "pull", remote_path, str(local_path)], 
                                  capture_output=True, 
                                  text=True,
                                  timeout=30)
            
            if result.returncode == 0 and local_path.exists():
                # Verify file is not empty
                if local_path.stat().st_size > 0:
                    return True, f"Successfully extracted {local_name}", str(local_path)
                else:
                    return False, f"Extracted file is empty: {local_name}", None
            else:
                return False, f"Failed to extract {local_name}: {result.stderr}", None
        except subprocess.TimeoutExpired:
            return False, f"Timeout while extracting {local_name}", None
        except Exception as e:
            return False, f"Error extracting {local_name}: {str(e)}", None
    
    def verify_database(self, db_path: str, expected_tables: List[str]) -> Tuple[bool, Dict]:
        """
        Verify database integrity and completeness
        
        Returns:
            (is_valid, verification_details)
        """
        if not os.path.exists(db_path):
            return False, {"error": "File does not exist"}
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            verification = {
                "file_exists": True,
                "file_size": os.path.getsize(db_path),
                "tables_found": tables,
                "expected_tables": expected_tables,
                "tables_present": all(table in tables for table in expected_tables),
                "row_counts": {}
            }
            
            # Count rows in expected tables
            for table in expected_tables:
                if table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    verification["row_counts"][table] = cursor.fetchone()[0]
                else:
                    verification["row_counts"][table] = 0
            
            conn.close()
            
            is_valid = verification["file_exists"] and verification["tables_present"]
            return is_valid, verification
            
        except sqlite3.Error as e:
            return False, {"error": f"Database error: {str(e)}"}
        except Exception as e:
            return False, {"error": f"Verification error: {str(e)}"}
    
    def calculate_hash(self, file_path: str) -> str:
        """Calculate MD5 hash of a file"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            return f"Error: {str(e)}"
    
    def create_backup(self, package_name: str, backup_file: str, progress_callback=None) -> Tuple[bool, str]:
        """
        Create ADB backup for a specific package (for non-rooted devices)
        
        Args:
            package_name: Android package name (e.g., com.android.providers.telephony)
            backup_file: Path to save backup file
            progress_callback: Optional callback for progress updates
        
        Returns:
            (success, message)
        """
        try:
            backup_path = Path(backup_file)
            
            if progress_callback:
                progress_callback(0, f"Creating backup for {package_name}...", 0)
            
            # ADB backup command - user needs to approve on device
            # Using -f flag to specify output file, -noapk to skip APK files
            cmd = [self.adb_path, "backup", "-f", str(backup_path), "-noapk", package_name]
            
            if progress_callback:
                progress_callback(0, f"Please approve backup on your device...", 10)
            
            # Start the backup process
            # Note: This requires user interaction on the device
            # Use communicate with input to handle the backup prompt
            process = subprocess.Popen(cmd, 
                                      stdin=subprocess.PIPE,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE,
                                      text=True,
                                      bufsize=0)
            
            # Wait for backup to complete (with timeout)
            # User must approve on device - we just wait
            try:
                stdout, stderr = process.communicate(input="\n", timeout=120)  # 2 minute timeout
                
                # Check if backup file was created and has content
                if backup_path.exists():
                    file_size = backup_path.stat().st_size
                    if file_size > 24:  # Must be larger than just the header
                        return True, f"Backup created successfully: {file_size} bytes"
                    else:
                        return False, "Backup file is too small (user may not have approved)"
                else:
                    error_msg = stderr if stderr else "Backup file was not created"
                    return False, f"Backup failed: {error_msg}"
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
                return False, "Backup timed out (user may not have approved on device)"
                
        except Exception as e:
            return False, f"Error creating backup: {str(e)}"
    
    def parse_backup_file(self, backup_file: str) -> Tuple[bool, str, str]:
        """
        Parse Android backup file and extract tar archive
        
        Android backup format:
        - First 24 bytes: "ANDROID BACKUP" magic string
        - Next 4 bytes: version (int, little-endian)
        - Next 4 bytes: compression flag (1 = deflate, 0 = none)
        - Rest: tar archive (possibly compressed)
        
        Returns:
            (success, message, extracted_tar_path)
        """
        try:
            backup_path = Path(backup_file)
            if not backup_path.exists():
                return False, "Backup file does not exist", ""
            
            with open(backup_path, 'rb') as f:
                # Read magic string
                magic = f.read(24)
                if magic != b"ANDROID BACKUP\n":
                    return False, "Invalid backup file format (wrong magic string)", ""
                
                # Read version
                version = int.from_bytes(f.read(4), byteorder='little')
                
                # Read compression flag
                compression = int.from_bytes(f.read(4), byteorder='little')
                
                # Read the rest (tar archive)
                tar_data = f.read()
            
            # Decompress if needed
            if compression == 1:
                try:
                    tar_data = zlib.decompress(tar_data)
                except zlib.error as e:
                    return False, f"Failed to decompress backup: {str(e)}", ""
            
            # Save extracted tar
            tar_path = self.backup_dir / "backup.tar"
            with open(tar_path, 'wb') as f:
                f.write(tar_data)
            
            return True, f"Backup parsed successfully (version {version}, compression: {compression})", str(tar_path)
            
        except Exception as e:
            return False, f"Error parsing backup: {str(e)}", ""
    
    def extract_from_backup(self, tar_path: str, data_type: str, local_name: str) -> Tuple[bool, str, Optional[str]]:
        """
        Extract database from backup tar archive
        
        Returns:
            (success, message, local_path)
        """
        try:
            # Extract tar archive
            extract_dir = self.backup_dir / f"extract_{data_type}"
            extract_dir.mkdir(exist_ok=True)
            
            with tarfile.open(tar_path, 'r') as tar:
                # Look for the database in backup paths
                found = False
                for backup_path in self.BACKUP_PATHS.get(data_type, []):
                    try:
                        # Try to extract the file
                        member = tar.getmember(backup_path)
                        tar.extract(member, extract_dir)
                        found = True
                        
                        # Get the extracted file path
                        extracted_file = extract_dir / backup_path
                        if extracted_file.exists():
                            # Copy to evidence directory with proper name
                            local_path = self.evidence_dir / local_name
                            shutil.copy2(extracted_file, local_path)
                            
                            return True, f"Extracted {data_type} from backup", str(local_path)
                    except KeyError:
                        continue
                
                if not found:
                    # Try to find any database files in the backup
                    members = tar.getmembers()
                    for member in members:
                        if member.name.endswith('.db') or 'History' in member.name:
                            if data_type in member.name.lower() or any(
                                keyword in member.name.lower() 
                                for keyword in ['sms', 'mms', 'call', 'chrome', 'history']
                            ):
                                tar.extract(member, extract_dir)
                                extracted_file = extract_dir / member.name
                                if extracted_file.exists():
                                    local_path = self.evidence_dir / local_name
                                    shutil.copy2(extracted_file, local_path)
                                    return True, f"Extracted {data_type} from backup (found: {member.name})", str(local_path)
                    
                    return False, f"Database not found in backup for {data_type}", None
                    
        except Exception as e:
            return False, f"Error extracting from backup: {str(e)}", None
    
    def extract_via_backup(self, progress_callback=None) -> Dict:
        """
        Extract data using ADB backup method (for non-rooted devices)
        
        Returns:
            Dictionary with extraction results
        """
        results = {
            "success": False,
            "extracted_files": {},
            "verification_results": {},
            "errors": [],
            "warnings": [],
            "method": "backup"
        }
        
        total_steps = 15
        current_step = 0
        
        def update_progress(step, message, percentage=None):
            nonlocal current_step
            current_step = step
            if progress_callback:
                if percentage is None:
                    percentage = int((step / total_steps) * 100)
                progress_callback(step, message, percentage)
        
        # Step 1: Check ADB
        update_progress(1, "Checking ADB availability...", 5)
        adb_ok, adb_msg = self.check_adb_available()
        if not adb_ok:
            results["errors"].append({
                "step": "ADB Check",
                "message": adb_msg,
                "fix_instructions": self._get_adb_fix_instructions()
            })
            return results
        
        # Step 2: Check device
        update_progress(2, "Checking device connection...", 10)
        device_ok, device_msg = self.check_device_connected()
        if not device_ok:
            results["errors"].append({
                "step": "Device Check",
                "message": device_msg,
                "fix_instructions": self._get_device_fix_instructions()
            })
            return results
        
        # Step 3: Combined Backup
        extraction_tasks = [
            ("sms", "mmssms.db", ["sms"]),
            ("calls", "calllog.db", ["calls"]),
            ("contacts", "contacts2.db", ["contacts", "raw_contacts"]),
            ("chrome", "History", ["urls"])
        ]

        # Identify unique packages to backup
        unique_packages = set()
        for idx, (data_type, local_name, expected_tables) in enumerate(extraction_tasks):
            pkg = self.BACKUP_PACKAGES.get(data_type)
            if pkg: unique_packages.add(pkg)
            
        packages_str = " ".join(unique_packages)
        backup_file = self.evidence_dir / "combined_backup.ab"
        
        update_progress(3, f"Requesting backup for all data sources...", 30)
        
        # We use a slightly different backup method: backup all defined packages at once
        success, message = self.create_backup(packages_str, str(backup_file), progress_callback)
        
        if success:
            update_progress(4, "Parsing combined backup...", 40)
            parse_ok, parse_msg, tar_path = self.parse_backup_file(str(backup_file))
            
            if parse_ok:
                # Now extract everything from this single tarball
                for idx, (data_type, local_name, expected_tables) in enumerate(extraction_tasks, start=5):
                    update_progress(idx, f"Extracting {data_type} from backup...", 40 + (idx * 5))
                    
                    extract_ok, extract_msg, local_path = self.extract_from_backup(tar_path, data_type, local_name)
                    
                    if extract_ok:
                        results["extracted_files"][data_type] = {
                            "path": local_path,
                            "method": "backup",
                            "message": extract_msg
                        }
                        
                        # Verify
                        if local_name.endswith('.xml'):
                             is_valid, verification = True, {"file_exists": True, "type": "xml"}
                        else:
                             is_valid, verification = self.verify_database(local_path, expected_tables)
                             
                        results["verification_results"][data_type] = verification
                    else:
                        results["errors"].append({
                            "step": f"{data_type} Extraction",
                            "message": extract_msg
                        })
            else:
                 results["errors"].append({"step": "Backup Parse", "message": parse_msg})
        else:
             results["errors"].append({"step": "Combined Backup Creation", "message": message})
        
        # Calculate hashes
        update_progress(13, "Calculating file hashes...", 85)
        for data_type, file_info in results["extracted_files"].items():
            if data_type == 'shared_storage': continue # Skip hashing entire folder for now
            file_path = file_info["path"]
            file_info["hash"] = self.calculate_hash(file_path)
            
        # Step: Extract Shared Storage (Works on Android 13+)
        update_progress(14, "Extracting Shared Storage (Photos/Downloads)...", 90)
        shared_res = self.extract_shared_storage()
        if shared_res['success']:
            results['extracted_files']['shared_storage'] = shared_res
            results['warnings'].append({
                "step": "Shared Storage",
                "message": f"Extracted {shared_res['file_count']} files from shared storage"
            })
            
        # Step: System Dump (Shell Commands fallback)
        update_progress(14.5, "Running System Dump (Shell Commands)...", 95)
        sys_res = self.extract_system_dump()
        if sys_res['success']:
            results['extracted_files']['system_dump'] = sys_res

        # Step: Content Query (Direct API Access)
        update_progress(14.8, "Running Content Query (SMS/Calls/Contacts)...", 98)
        content_res = self.extract_content_query()
        if content_res['success']:
            results['extracted_files']['content_query'] = content_res
        
        # Final verification: If we got ANYTHING, we consider it a partial success
        if results["extracted_files"]:
             results["success"] = True
        
        update_progress(15, "Backup extraction complete!", 100)
        return results

    def extract_content_query(self) -> Dict:
        """
        Extract data using 'content query' shell command.
        This often works on non-rooted devices where direct DB access fails.
        """
        local_dir = self.evidence_dir / "content_query"
        local_dir.mkdir(exist_ok=True)
        
        queries = {
            "sms.txt": "content query --uri content://sms/",
            "calls.txt": "content query --uri content://call_log/calls",
            "contacts.txt": "content query --uri content://contacts/phones/ --projection display_name:number:last_time_contacted",
            "calendar.txt": "content query --uri content://com.android.calendar/events --projection title:dtstart:eventLocation",
            "dictionary.txt": "content query --uri content://user_dictionary/words --projection word:frequency"
        }
        
        extracted_count = 0
        try:
            for filename, cmd in queries.items():
                out_file = local_dir / filename
                try:
                    # Run adb shell <cmd> as a single string
                    result = subprocess.run(f'{self.adb_path} shell "{cmd}"', 
                                          shell=True,
                                          capture_output=True, 
                                          text=True, 
                                          timeout=20)
                    
                    # Even if it errors (SecurityException), we save what we got
                    with open(out_file, "w", encoding='utf-8') as f:
                        if result.returncode == 0 and result.stdout:
                            f.write(result.stdout)
                            extracted_count += 1
                        elif result.stderr:
                             f.write(f"ERROR: {result.stderr}")
                except Exception as e:
                    with open(out_file, "w") as f: f.write(str(e))
            
            return {
                "success": True,
                "path": str(local_dir),
                "message": f"attempted {len(queries)} content queries"
            }
        except Exception as e:
             return {"success": False, "error": str(e), "path": ""}

    def extract_system_dump(self) -> Dict:
        """
        Extract system info using shell commands (Workaround for failed backups)
        """
        local_dir = self.evidence_dir / "system_dump"
        local_dir.mkdir(exist_ok=True)
        
        commands = {
            "packages_list.txt": "pm list packages -f -3",
            "system_props.txt": "getprop",
            "battery_stats.txt": "dumpsys battery",
            "network_info.txt": "ip address show",
            "usagestats.txt": "dumpsys usagestats",
            "permissions.txt": "pm list permissions -g -f"
        }
        
        extracted_count = 0
        try:
            for filename, cmd in commands.items():
                out_file = local_dir / filename
                with open(out_file, "w", encoding='utf-8') as f:
                    # Run adb shell <cmd>
                    result = subprocess.run([self.adb_path, "shell", cmd], 
                                          capture_output=True, text=True, timeout=15)
                    f.write(result.stdout)
                    extracted_count += 1
            
            return {
                "success": True,
                "path": str(local_dir),
                "message": f"ran {extracted_count} shell commands"
            }
        except Exception as e:
             return {"success": False, "error": str(e), "path": ""}

    def extract_shared_storage(self, limit: int = 5) -> Dict:
        """
        Pull shared storage files using direct ADB pull.
        Limited to 5 files for testing purposes as requested.
        """
        local_dir = self.evidence_dir / "shared_storage"
        local_dir.mkdir(exist_ok=True)
        
        count = 0
        try:
            files_to_pull = []
            
            # Use 'find' on the device to get a list of files across all target paths
            # We verify the path exists first to avoid errors
            for remote_base in self.SHARED_PATHS:
                if count >= limit: break
                
                # Check if path exists
                check = subprocess.run([self.adb_path, "shell", "ls", remote_base], capture_output=True)
                if check.returncode != 0:
                    continue

                # Find files (type f) inside the directory, limiting output
                # We prioritize images/videos usually found in these folders
                cmd = [self.adb_path, "shell", f"find {remote_base} -type f | head -n {limit - count}"]
                
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                    if result.returncode == 0 and result.stdout.strip():
                        paths = result.stdout.strip().split('\n')
                        for p in paths:
                            p = p.strip()
                            if p and p not in files_to_pull:
                                files_to_pull.append(p)
                                count += 1
                except:
                    continue

            # Now pull the identified files
            for remote_file in files_to_pull:
                try:
                    # Construct local path maintaining structure relative to /sdcard/
                    # e.g. /sdcard/DCIM/Camera/IMG.jpg -> evidence/shared_storage/DCIM/Camera/IMG.jpg
                    rel_path = remote_file.replace('/sdcard/', '')
                    # Handle cases where path doesn't start with /sdcard/
                    if rel_path.startswith('/'): rel_path = rel_path[1:]
                    
                    target_file = local_dir / rel_path
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    subprocess.run([self.adb_path, "pull", remote_file, str(target_file)], 
                                 capture_output=True, timeout=30)
                except Exception as e:
                    print(f"Failed to pull {remote_file}: {e}")
                    
            return {
                "success": True, 
                "path": str(local_dir), 
                "file_count": count,
                "message": f"Extracted {count} files (Test Mode)"
            }
        except Exception as e:
            return {"success": False, "error": str(e), "file_count": 0}
    
    def extract_all_data(self, progress_callback=None) -> Dict:
        """
        Extract all possible data from Android device
        
        Args:
            progress_callback: Function to call with (step, message, percentage)
        
        Returns:
            Dictionary with extraction results
        """
        results = {
            "success": False,
            "extracted_files": {},
            "verification_results": {},
            "errors": [],
            "warnings": []
        }
        
        total_steps = 10
        current_step = 0
        
        def update_progress(step, message, percentage=None):
            nonlocal current_step
            current_step = step
            if progress_callback:
                if percentage is None:
                    percentage = int((step / total_steps) * 100)
                progress_callback(step, message, percentage)
        
        # Step 1: Check ADB
        update_progress(1, "Checking ADB availability...", 10)
        adb_ok, adb_msg = self.check_adb_available()
        if not adb_ok:
            results["errors"].append({
                "step": "ADB Check",
                "message": adb_msg,
                "fix_instructions": self._get_adb_fix_instructions()
            })
            return results
        
        # Step 2: Check device
        update_progress(2, "Checking device connection...", 20)
        device_ok, device_msg = self.check_device_connected()
        if not device_ok:
            results["errors"].append({
                "step": "Device Check",
                "message": device_msg,
                "fix_instructions": self._get_device_fix_instructions()
            })
            return results
        
        # Step 3: Enable root
        update_progress(3, "Attempting to enable root access...", 30)
        root_ok, root_msg = self.enable_root()
        if not root_ok:
            results["warnings"].append({
                "step": "Root Access",
                "message": root_msg
            })
            results["root_available"] = False
        else:
            results["root_available"] = True
        
        # Step 4-6: Extract databases (try root method first)
        extraction_tasks = [
            ("sms", "mmssms.db", ["sms"]),
            ("calls", "calllog.db", ["calls"]),
            ("contacts", "contacts2.db", ["contacts"]),
            ("chrome", "History", ["urls"]),
            ("wifi", "WifiConfigStore.xml", []), # XML files don't have tables
            ("packages", "packages.xml", [])     # XML files don't have tables
        ]
        
        for idx, (data_type, local_name, expected_tables) in enumerate(extraction_tasks, start=4):
            update_progress(idx, f"Extracting {data_type}...", 30 + (idx * 10))
            
            # Try all possible paths for this data type
            extracted = False
            for remote_path in self.DATABASE_PATHS[data_type]:
                success, message, local_path = self.extract_database(remote_path, local_name)
                if success:
                    results["extracted_files"][data_type] = {
                        "path": local_path,
                        "remote_path": remote_path,
                        "message": message
                    }
                    extracted = True
                    
                    # Verify the database (skip for XML files)
                    update_progress(idx + 0.5, f"Verifying {data_type} data...", 30 + (idx * 10) + 5)
                    
                    if local_name.endswith('.xml'):
                        # Simple existence check for XML
                        is_valid = True
                        verification = {"file_exists": True, "type": "xml"}
                    else:
                        is_valid, verification = self.verify_database(local_path, expected_tables)
                    
                    results["verification_results"][data_type] = verification
                    
                    if not is_valid:
                        results["warnings"].append({
                            "step": f"{data_type.upper()} Verification",
                            "message": f"Database verification issues: {verification.get('error', 'Unknown')}"
                        })
                    break
            
            if not extracted and not root_ok:
                # If root failed and extraction failed, suggest backup method
                results["warnings"].append({
                    "step": f"{data_type.upper()} Extraction",
                    "message": f"Root extraction failed. Try using 'Extract via Backup' method for non-rooted devices."
                })
            elif not extracted:
                results["errors"].append({
                    "step": f"{data_type.upper()} Extraction",
                    "message": f"Failed to extract {data_type} from all known locations",
                    "fix_instructions": self._get_extraction_fix_instructions(data_type)
                })
        
        # Step 7: Calculate hashes
        update_progress(8, "Calculating file hashes...", 80)
        for data_type, file_info in results["extracted_files"].items():
            file_path = file_info["path"]
            file_info["hash"] = self.calculate_hash(file_path)
        
        # Step 8: Final verification
        update_progress(9, "Performing final verification...", 90)
        if results["extracted_files"]:
            results["success"] = True
        
        update_progress(10, "Extraction complete!", 100)
        return results
    
    def _get_adb_fix_instructions(self) -> List[str]:
        """Get instructions for fixing ADB issues"""
        if self.is_windows:
            return [
                "1. Download Android Platform Tools from: https://developer.android.com/studio/releases/platform-tools",
                "2. Extract the zip file",
                "3. Add the platform-tools folder to your system PATH",
                "4. Or place adb.exe in the same folder as this application",
                "5. Restart this application"
            ]
        else:
            return [
                "1. Install ADB using your package manager:",
                "   - Ubuntu/Debian: sudo apt-get install android-tools-adb",
                "   - Fedora: sudo dnf install android-tools",
                "   - Arch: sudo pacman -S android-tools",
                "2. Or download from: https://developer.android.com/studio/releases/platform-tools",
                "3. Make sure ADB is in your PATH",
                "4. Restart this application"
            ]
    
    def _get_device_fix_instructions(self) -> List[str]:
        """Get instructions for fixing device connection issues"""
        return [
            "1. Connect your Android device to your computer via USB",
            "2. On your Android device:",
            "   - Go to Settings > About Phone",
            "   - Tap 'Build Number' 7 times to enable Developer Options",
            "   - Go to Settings > System > Developer Options",
            "   - Enable 'USB Debugging'",
            "3. When prompted on your device, allow USB debugging",
            "4. Make sure you're using a data cable (not just charging)",
            "5. Try a different USB port or cable if issues persist",
            "6. On some devices, you may need to select 'File Transfer' mode"
        ]
    
    def _get_extraction_fix_instructions(self, data_type: str) -> List[str]:
        """Get instructions for fixing extraction issues"""
        return [
            f"1. The {data_type} database may not exist on this device",
            "2. Make sure the device is rooted (required for accessing /data/data/)",
            "3. Try running: adb root (in a terminal)",
            "4. Verify the app is installed (e.g., Chrome for browser history)",
            "5. Some devices may have different database paths",
            "6. Check if the data exists using: adb shell ls /data/data/",
            "7. For non-rooted devices, use the 'Extract via Backup' option"
        ]
    
    def _get_backup_fix_instructions(self, data_type: str) -> List[str]:
        """Get instructions for fixing backup extraction issues"""
        return [
            f"1. Make sure you approved the backup on your Android device",
            "2. The backup prompt appears on your device screen - tap 'Back up my data'",
            "3. If no prompt appeared, the app may not support backup",
            f"4. Verify the app is installed: adb shell pm list packages | grep {self.BACKUP_PACKAGES.get(data_type, '')}",
            "5. Some apps may not allow backup (check app settings)",
            "6. Try unlocking your device screen during backup",
            "7. Make sure USB debugging is enabled and authorized",
            "8. If backup fails, you may need to root the device for direct extraction"
        ]

