import pandas as pd
import parser  # Import the file we created above
import os
import sys

# Define paths to your evidence
print("--- Starting Forensic Analysis ---")

case_name = input("Enter Case Name (default: 'Default_Case'): ").strip()
if not case_name:
    case_name = 'Default_Case'

case_dir = os.path.join("cases", case_name)
evidence_dir = os.path.join(case_dir, "evidence")
os.makedirs(evidence_dir, exist_ok=True)

# Define paths to your evidence
sms_db = os.path.join(evidence_dir, 'mmssms.db')
call_db = os.path.join(evidence_dir, 'calllog.db')
chrome_db = os.path.join(evidence_dir, 'History')
contacts_db = os.path.join(evidence_dir, 'contacts2.db')
wifi_xml = os.path.join(evidence_dir, 'WifiConfigStore.xml')
packages_xml = os.path.join(evidence_dir, 'packages.xml')
shared_storage_dir = os.path.join(evidence_dir, 'shared_storage')
content_query_dir = os.path.join(evidence_dir, 'content_query')

# Check if evidence files exist
evidence_files = {
    'SMS': sms_db,
    'Call Logs': call_db,
    'Chrome History': chrome_db,
    'Contacts': contacts_db,
    'WiFi': wifi_xml,
    'Apps': packages_xml
}

missing_files = []
for artifact_type, file_path in evidence_files.items():
    if not os.path.exists(file_path):
        missing_files.append(f"{artifact_type}: {file_path}")
        print(f"[WARNING] {artifact_type} database not found at {file_path}")

if missing_files and len(missing_files) == len(evidence_files):
    print(f"\n[ERROR] No evidence files found in {evidence_dir}.")
    print("Please extract data first or place database files in the folder.")
    print("Expected files:")
    for artifact_type, file_path in evidence_files.items():
        print(f"  - {file_path}")
    sys.exit(1)

# 1. Parse Artifacts
print("\nParsing artifacts...")
sms_data = pd.DataFrame()
call_data = pd.DataFrame()
browser_data = pd.DataFrame()
contact_data = pd.DataFrame()
wifi_data = pd.DataFrame()
pkg_data = pd.DataFrame()
storage_data = pd.DataFrame()
query_data = pd.DataFrame()

if os.path.exists(sms_db):
    print("Parsing SMS...")
    sms_data = parser.parse_sms(sms_db)
    print(f"  Found {len(sms_data)} SMS messages")
else:
    print("[SKIP] SMS database not found")

if os.path.exists(call_db):
    print("Parsing Calls...")
    call_data = parser.parse_call_logs(call_db)
    print(f"  Found {len(call_data)} call records")
else:
    print("[SKIP] Call log database not found")

if os.path.exists(chrome_db):
    print("Parsing Browser History...")
    browser_data = parser.parse_chrome_history(chrome_db)
    print(f"  Found {len(browser_data)} browser history entries")
else:
    print("[SKIP] Chrome history database not found")

if os.path.exists(contacts_db):
    print("Parsing Contacts...")
    contact_data = parser.parse_contacts(contacts_db)
    print(f"  Found {len(contact_data)} contacts")
else:
    print("[SKIP] Contacts database not found")

if os.path.exists(wifi_xml):
    print("Parsing WiFi...")
    wifi_data = parser.parse_wifi(wifi_xml)
    print(f"  Found {len(wifi_data)} wifi networks")

if os.path.exists(packages_xml):
    print("Parsing Installed Apps...")
    pkg_data = parser.parse_packages(packages_xml)
    print(f"  Found {len(pkg_data)} installed apps")

if os.path.exists(shared_storage_dir):
    print("Parsing Shared Storage...")
    storage_data = parser.parse_shared_storage(shared_storage_dir)
    print(f"  Found {len(storage_data)} files in shared storage")

if os.path.exists(content_query_dir):
    print("Parsing Content Query Data...")
    query_data = parser.parse_content_query(content_query_dir)
    print(f"  Found {len(query_data)} content query records")

# 2. Merge Data for Timeline Analysis
print("\nGenerating Timeline...")
all_dataframes = [df for df in [sms_data, call_data, browser_data, contact_data, wifi_data, pkg_data, storage_data, query_data] if not df.empty]

if not all_dataframes:
    print("[ERROR] No data found to analyze. Please check your evidence files.")
    sys.exit(1)

all_evidence = pd.concat(all_dataframes, ignore_index=True)

# 3. Sort by Date to reconstruct the story
timeline = all_evidence.sort_values(by='date')

# 4. Export Report
output_file = os.path.join(case_dir, 'Forensic_Report.csv')
timeline.to_csv(output_file, index=False)
print(f"\nAnalysis Complete. Report saved to {output_file}")
print(f"Total artifacts analyzed: {len(timeline)}")

# Preview timeline
print("\n--- Timeline Preview (First 10 entries) ---")
print(timeline.head(10).to_string())

# Preview suspicious activity (Example: Filter for a specific number)
# Uncomment and modify the target_number to search for specific activity
# target_number = "123456789"  # Replace with a number you created on the test phone
# suspicious = timeline[timeline.astype(str).apply(lambda x: x.str.contains(target_number, na=False)).any(axis=1)]
# 
# if not suspicious.empty:
#     print("\n[!] Suspicious Activity Found:")
#     print(suspicious[['date', 'artifact_type', 'type', 'body', 'url']])

