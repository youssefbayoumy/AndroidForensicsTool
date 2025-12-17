import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import os
import time
import re

def parse_sms(db_path):
    """
    Parse SMS/MMS database and extract messages.
    """
    try:
        conn = sqlite3.connect(db_path)
        query = "SELECT address, date, body, type FROM sms"
        df = pd.read_sql_query(query, conn)
        conn.close()

        df['date'] = pd.to_datetime(df['date'], unit='ms')
        df['type'] = df['type'].map({1: 'Incoming', 2: 'Outgoing'})
        df['artifact_type'] = 'SMS'
        return df
    except Exception as e:
        print(f"Error parsing SMS: {e}")
        return pd.DataFrame()

def parse_call_logs(db_path):
    """
    Parse call log database and extract call records.
    """
    try:
        conn = sqlite3.connect(db_path)
        query = "SELECT number, date, duration, type FROM calls"
        df = pd.read_sql_query(query, conn)
        conn.close()

        df['date'] = pd.to_datetime(df['date'], unit='ms')
        df['type'] = df['type'].map({1: 'Incoming', 2: 'Outgoing', 3: 'Missed'})
        df['artifact_type'] = 'Call Log'
        return df
    except Exception as e:
        print(f"Error parsing Call Logs: {e}")
        return pd.DataFrame()

def parse_chrome_history(db_path):
    """
    Parse Chrome browser history database.
    """
    try:
        conn = sqlite3.connect(db_path)
        query = "SELECT url, title, last_visit_time FROM urls"
        df = pd.read_sql_query(query, conn)
        conn.close()

        df['date'] = pd.to_datetime((df['last_visit_time']/1000000)-11644473600, unit='s', errors='coerce')
        df['artifact_type'] = 'Browser History'
        return df[['date', 'url', 'title', 'artifact_type']]
    except Exception as e:
        print(f"Error parsing Chrome: {e}")
        return pd.DataFrame()

def parse_contacts(db_path):
    """
    Parse Contacts database (contacts2.db)
    """
    try:
        conn = sqlite3.connect(db_path)
        # Simplified query to get display name and data1 (phone number)
        # Note: Schema can vary, using a safe join view usually helps, but we'll try raw tables
        query = """
        SELECT 
            raw_contacts.display_name, 
            data.data1 as phone_number,
            raw_contacts.last_time_contacted
        FROM raw_contacts 
        JOIN data ON raw_contacts._id = data.raw_contact_id
        WHERE data.mimetype_id = 5 OR data.mimetype = 'vnd.android.cursor.item/phone_v2'
        """
        
        try:
            df = pd.read_sql_query(query, conn)
        except:
            # Fallback simple query
            query = "SELECT display_name FROM raw_contacts"
            df = pd.read_sql_query(query, conn)
            df['phone_number'] = 'Unknown'
            df['last_time_contacted'] = 0

        conn.close()
        
        # Convert timestamp if available
        if 'last_time_contacted' in df.columns:
             df['date'] = pd.to_datetime(df['last_time_contacted'], unit='ms')
        else:
             df['date'] = pd.NaT
             
        df['artifact_type'] = 'Contact'
        df['type'] = 'Saved Contact'
        
        # Rename columns to match main report schema roughly
        df = df.rename(columns={'display_name': 'title', 'phone_number': 'body'})
        
        return df[['date', 'title', 'body', 'artifact_type', 'type']]
        
    except Exception as e:
        print(f"Error parsing Contacts: {e}")
        return pd.DataFrame()

def parse_wifi(xml_path):
    """
    Parse WiFi Config XML
    """
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        networks = []
        # Structure varies by Android version, looking for generic SSID tags
        
        with open(xml_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            import re
            # look for SSIDs in quotes
            ssids = re.findall(r'&quot;(.*?)&quot;', content)
            
            for ssid in set(ssids):
                networks.append({
                    'date': pd.NaT, # No timestamp usually
                    'title': f"WiFi Network: {ssid}",
                    'body': 'Saved Network',
                    'artifact_type': 'WiFiConfig',
                    'type': 'System Artifact'
                })
                
        return pd.DataFrame(networks)
        
    except Exception as e:
        print(f"Error parsing WiFi: {e}")
        return pd.DataFrame()

def parse_packages(xml_path):
    """
    Parse packages.xml for installed apps
    """
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        apps = []
        for package in root.findall('package'):
            name = package.get('name')
            it = package.get('it') 
            
            if name and it:
                try:
                    if it.startswith('0x'):
                        timestamp = int(it, 16)
                    else:
                        timestamp = int(it)
                    
                    date = pd.to_datetime(timestamp, unit='ms')
                    
                    apps.append({
                        'date': date,
                        'title': f"App Installed: {name}",
                        'body': f"Package: {name}",
                        'artifact_type': 'Installed App',
                        'type': 'System Artifact'
                    })
                except:
                    continue
                    
        return pd.DataFrame(apps)
        
    except Exception as e:
        print(f"Error parsing Packages: {e}")
        return pd.DataFrame()

def parse_shared_storage(storage_path):
    """
    Scan shared storage for images and documents to add to timeline
    """
    files_list = []
    
    for root, dirs, files in os.walk(storage_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                # Get file metadata
                stats = os.stat(file_path)
                mtime = datetime.fromtimestamp(stats.st_mtime)
                
                # Determine type
                ext = file.split('.')[-1].lower()
                if ext in ['jpg', 'jpeg', 'png', 'heic']:
                    artifact_type = "Image"
                elif ext in ['mp4', 'mov']:
                    artifact_type = "Video"
                elif ext in ['pdf', 'doc', 'docx', 'txt']:
                    artifact_type = "Document"
                else:
                    continue # Skip other files to avoid noise
                    
                files_list.append({
                    'date': mtime,
                    'title': f"File: {file}",
                    'body': f"Path: {file_path}",
                    'artifact_type': artifact_type,
                    'type': 'File System'
                })
            except Exception as e:
                continue
                
    return pd.DataFrame(files_list)

def parse_system_dump(dump_path):
    """
    Parse text files from system dump (fallback method)
    """
    data_list = []
    
    # 1. Parse installed packages list
    pkg_file = os.path.join(dump_path, "packages_list.txt")
    if os.path.exists(pkg_file):
        try:
            with open(pkg_file, 'r', encoding='utf-8') as f:
                for line in f:
                    # format: package:/data/app/~~.../com.example.app-....apk=com.example.app
                    if '=' in line:
                        parts = line.strip().split('=')
                        pkg_name = parts[-1]
                        data_list.append({
                            'date': pd.NaT,
                            'title': f"Installed App: {pkg_name}",
                            'body': "Retrieved via Shell",
                            'artifact_type': 'Installed App (Shell)',
                            'type': 'System Artifact'
                        })
        except:
            pass
            
    # 2. Parsing Usage Stats (dumpsys usagestats)
    usage_file = os.path.join(dump_path, "usagestats.txt")
    if os.path.exists(usage_file):
        try:
            with open(usage_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Look for "package=com.foo.bar" alongside timestamps
                # This is a very basic parser for a complex format
                # We look for "package=" entries in the file
                import re
                matches = re.findall(r'package=([a-zA-Z0-9.]+)', content)
                for pkg in set(matches): # De-duplicate
                    data_list.append({
                        'date': pd.NaT, # Timestamp parsing from usagestats is extremely complex without root
                        'title': f"App Activity: {pkg}",
                        'body': "App appeared in Usage Stats dump",
                        'artifact_type': 'App Usage',
                        'type': 'Activity'
                    })
        except:
            pass

    # 3. Parse System Props (Model/Version)
    prop_file = os.path.join(dump_path, "system_props.txt")
    if os.path.exists(prop_file):
        try:
            props = {}
            with open(prop_file, 'r', encoding='utf-8') as f:
                for line in f:
                    # [ro.product.model]: [Pixel 6]
                    match = re.search(r'\[(.*?)\].*?\[(.*?)\]', line)
                    if match:
                        key = match.group(1)
                        val = match.group(2)
                        props[key] = val
            
            # Add interesting props
            model = props.get('ro.product.model', 'Unknown Device')
            android = props.get('ro.build.version.release', 'Unknown OS')
            
            data_list.append({
                'date': pd.NaT,
                'title': f"Device Info: {model}",
                'body': f"Android Version: {android}",
                'artifact_type': 'System Info',
                'type': 'Configuration'
            })
        except:
             pass

    return pd.DataFrame(data_list)

def parse_content_query(query_path):
    """
    Parse output from 'content query' shell commands.
    Output format: Row: 0 _id=1, person=..., body=...
    """
    data_list = []
    
    # 1. Parse SMS Query
    sms_file = os.path.join(query_path, "sms.txt")
    if os.path.exists(sms_file):
        try:
            with open(sms_file, 'r', encoding='utf-8') as f:
                content = f.read()
                rows = re.findall(r'Row: \d+ (.*?)(?=Row: \d+|$)', content, re.DOTALL)
                
                for row in rows:
                    try:
                        details = {}
                        parts = row.split(', ')
                        for part in parts:
                            if '=' in part:
                                k, v = part.split('=', 1)
                                details[k.strip()] = v.strip()
                        
                        date = pd.NaT
                        if 'date' in details:
                            date = pd.to_datetime(int(details['date']), unit='ms', errors='coerce')
                            
                        data_list.append({
                            'date': date,
                            'title': f"SMS from {details.get('address', 'Unknown')}",
                            'body': details.get('body', ''),
                            'artifact_type': 'SMS (Query)',
                            'type': 'Incoming' if 'type=1' in row else 'Outgoing'
                        })
                    except:
                        continue
        except Exception as e:
            pass

    # 2. Parse Calls Query
    call_file = os.path.join(query_path, "calls.txt")
    if os.path.exists(call_file):
        try:
             with open(call_file, 'r', encoding='utf-8') as f:
                content = f.read()
                rows = re.findall(r'Row: \d+ (.*?)(?=Row: \d+|$)', content, re.DOTALL)
                
                for row in rows:
                    try:
                        details = {}
                        parts = row.split(', ')
                        for part in parts:
                            if '=' in part:
                                k, v = part.split('=', 1)
                                details[k.strip()] = v.strip()
                        
                        date = pd.NaT
                        if 'date' in details:
                            date = pd.to_datetime(int(details['date']), unit='ms', errors='coerce')
                            
                        data_list.append({
                            'date': date,
                            'title': f"Call: {details.get('number', 'Unknown')}",
                            'body': f"Duration: {details.get('duration', '0')}s",
                            'artifact_type': 'Call Log (Query)',
                            'type': 'Call Record'
                        })
                    except:
                        continue
        except:
             pass

    # 3. Parse Contacts Query
    contact_file = os.path.join(query_path, "contacts.txt")
    if os.path.exists(contact_file):
        try:
             with open(contact_file, 'r', encoding='utf-8') as f:
                content = f.read()
                rows = re.findall(r'Row: \d+ (.*?)(?=Row: \d+|$)', content, re.DOTALL)
                
                for row in rows:
                    try:
                        details = {}
                        parts = row.split(', ')
                        for part in parts:
                            if '=' in part:
                                k, v = part.split('=', 1)
                                details[k.strip()] = v.strip()
                        
                        data_list.append({
                            'date': pd.NaT,
                            'title': f"Contact: {details.get('display_name', 'Unknown')}",
                            'body': f"Number: {details.get('number', '')}",
                            'artifact_type': 'Contact (Query)',
                            'type': 'Saved Contact'
                        })
                    except:
                        continue
        except:
             pass
             
    # 4. Parse Calendar Query
    cal_file = os.path.join(query_path, "calendar.txt")
    if os.path.exists(cal_file):
        try:
             with open(cal_file, 'r', encoding='utf-8') as f:
                content = f.read()
                rows = re.findall(r'Row: \d+ (.*?)(?=Row: \d+|$)', content, re.DOTALL)
                
                for row in rows:
                    try:
                        details = {}
                        parts = row.split(', ')
                        for part in parts:
                            if '=' in part:
                                k, v = part.split('=', 1)
                                details[k.strip()] = v.strip()
                                
                        date = pd.NaT
                        if 'dtstart' in details:
                            date = pd.to_datetime(int(details['dtstart']), unit='ms', errors='coerce')

                        data_list.append({
                            'date': date,
                            'title': f"Calendar Event: {details.get('title', 'Unknown')}",
                            'body': f"Location: {details.get('eventLocation', 'N/A')}",
                            'artifact_type': 'Calendar',
                            'type': 'Appointment'
                        })
                    except:
                        continue
        except:
             pass
             
    # 5. Parse User Dictionary
    dict_file = os.path.join(query_path, "dictionary.txt")
    if os.path.exists(dict_file):
        try:
             with open(dict_file, 'r', encoding='utf-8') as f:
                content = f.read()
                rows = re.findall(r'Row: \d+ (.*?)(?=Row: \d+|$)', content, re.DOTALL)
                
                for row in rows:
                    try:
                        details = {}
                        parts = row.split(', ')
                        for part in parts:
                            if '=' in part:
                                k, v = part.split('=', 1)
                                details[k.strip()] = v.strip()

                        data_list.append({
                            'date': pd.NaT,
                            'title': f"Dictionary Word: {details.get('word', 'Unknown')}",
                            'body': f"Frequency: {details.get('frequency', '0')}",
                            'artifact_type': 'User Dictionary',
                            'type': 'Input'
                        })
                    except:
                        continue
        except:
             pass
    
    return pd.DataFrame(data_list)
