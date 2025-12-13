import pandas as pd
import parser  # Import the file we created above
import os
import sys

# Define paths to your evidence
sms_db = 'evidence/mmssms.db'
call_db = 'evidence/calllog.db'
chrome_db = 'evidence/History'

print("--- Starting Forensic Analysis ---")

# Check if evidence files exist
evidence_files = {
    'SMS': sms_db,
    'Call Logs': call_db,
    'Chrome History': chrome_db
}

missing_files = []
for artifact_type, file_path in evidence_files.items():
    if not os.path.exists(file_path):
        missing_files.append(f"{artifact_type}: {file_path}")
        print(f"[WARNING] {artifact_type} database not found at {file_path}")

if missing_files and len(missing_files) == len(evidence_files):
    print("\n[ERROR] No evidence files found. Please ensure database files are in the 'evidence' folder.")
    print("Expected files:")
    for artifact_type, file_path in evidence_files.items():
        print(f"  - {file_path}")
    sys.exit(1)

# 1. Parse Artifacts
print("\nParsing artifacts...")
sms_data = pd.DataFrame()
call_data = pd.DataFrame()
browser_data = pd.DataFrame()

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

# 2. Merge Data for Timeline Analysis
print("\nGenerating Timeline...")
all_dataframes = [df for df in [sms_data, call_data, browser_data] if not df.empty]

if not all_dataframes:
    print("[ERROR] No data found to analyze. Please check your evidence files.")
    sys.exit(1)

all_evidence = pd.concat(all_dataframes, ignore_index=True)

# 3. Sort by Date to reconstruct the story
timeline = all_evidence.sort_values(by='date')

# 4. Export Report
output_file = 'Forensic_Report.csv'
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

