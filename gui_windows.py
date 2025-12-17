"""
Windows GUI Application for Android Forensics Tool
Optimized for Windows with native look and feel
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import os
import sys
from pathlib import Path
import pandas as pd
import webbrowser
import platform
import csv
import io
import parser
from core_extractor import AndroidExtractor
from datetime import datetime

class ReportViewer:
    def __init__(self, parent, dataframe):
        self.window = tk.Toplevel(parent)
        self.window.title("Forensic Report Viewer")
        self.window.geometry("1000x700")
        self.df = dataframe.fillna('') # Handle NaNs
        
        # Ensure date sorting
        if 'date' in self.df.columns:
            try:
                self.df['date'] = pd.to_datetime(self.df['date'])
                self.df = self.df.sort_values(by='date', ascending=False)
            except:
                pass

        self.setup_ui()
        self.apply_filters() # Initial population

    def setup_ui(self):
        # 1. Control Panel (Top)
        control_frame = ttk.Frame(self.window, padding="5")
        control_frame.pack(fill=tk.X)

        # Filter by Type
        ttk.Label(control_frame, text="Filter by Type:").pack(side=tk.LEFT, padx=5)
        
        # Get unique types dynamically
        unique_types = sorted(list(self.df['artifact_type'].astype(str).unique()))
        self.type_var = tk.StringVar(value="All")
        self.type_combo = ttk.Combobox(control_frame, textvariable=self.type_var, values=["All"] + unique_types, state="readonly")
        self.type_combo.pack(side=tk.LEFT, padx=5)
        self.type_combo.bind("<<ComboboxSelected>>", self.apply_filters)

        # Search
        ttk.Label(control_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda name, index, mode: self.apply_filters())
        self.search_entry = ttk.Entry(control_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        
        # Export Button (Placeholder for now)
        # ttk.Button(control_frame, text="Export CSV", command=self.export_csv).pack(side=tk.RIGHT, padx=5)

        # 2. Main Split View (Tree + Details)
        paned = ttk.PanedWindow(self.window, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Treeview Frame
        tree_frame = ttk.Frame(paned)
        paned.add(tree_frame, weight=2)

        columns = ("date", "artifact_type", "title", "body")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")
        
        # Headers
        self.tree.heading("date", text="Timestamp")
        self.tree.heading("artifact_type", text="Type")
        self.tree.heading("title", text="Source / Title")
        self.tree.heading("body", text="Content Preview")
        
        # Column sizing
        self.tree.column("date", width=150, stretch=False)
        self.tree.column("artifact_type", width=120, stretch=False)
        self.tree.column("title", width=200, stretch=False)
        self.tree.column("body", width=500, stretch=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # Detail View Frame
        detail_frame = ttk.LabelFrame(paned, text="Details", padding="5")
        paned.add(detail_frame, weight=1)
        
        # Text widget for viewing full content with special chars
        self.detail_text = tk.Text(detail_frame, wrap=tk.WORD, height=10, font=("Consolas", 10))
        self.detail_text.pack(fill=tk.BOTH, expand=True)

    def apply_filters(self, event=None):
        # Clear current items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        search_term = self.search_var.get().lower()
        selected_type = self.type_var.get()
        
        # Filter Logic
        for index, row in self.df.iterrows():
            # 1. Type Filter
            if selected_type != "All" and str(row['artifact_type']) != selected_type:
                continue
                
            # 2. Search Filter (checks all visible fields)
            row_str = f"{row['date']} {row['artifact_type']} {row['title']} {row['body']}".lower()
            if search_term and search_term not in row_str:
                continue
                
            # Truncate body for preview
            body_preview = str(row['body'])[:100].replace('\n', ' ')
            if len(str(row['body'])) > 100:
                body_preview += "..."
                
            # Insert
            # We store the FULL body in the item identifier or a separate tag if needed
            # easiest is to use the dataframe index (which we preserved)
            self.tree.insert("", tk.END, iid=index, values=(
                row['date'],
                row['artifact_type'],
                row['title'],
                body_preview
            ))

    def on_select(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return
            
        # Get dataframe index from treeview IID
        idx = int(selected_item[0])
        row = self.df.loc[idx]
        
        # Display full details
        full_text = f"Type: {row['artifact_type']}\n"
        full_text += f"Date: {row['date']}\n"
        full_text += f"Source: {row['title']}\n"
        full_text += "-"*50 + "\n"
        full_text += f"{row['body']}\n"
        
        self.detail_text.delete(1.0, tk.END)
        self.detail_text.insert(1.0, full_text)


class AndroidForensicsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Android Forensics Tool - Windows")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Windows-specific styling
        self.style = ttk.Style()
        self.style.theme_use('vista')  # Windows Vista/7/8/10 theme
        
        # Configure colors
        self.root.configure(bg='#f0f0f0')
        
        self.extractor = AndroidExtractor()
        self.extraction_results = None
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Title
        title_label = tk.Label(main_frame, 
                              text="Android Digital Forensics Tool",
                              font=("Segoe UI", 18, "bold"),
                              bg='#f0f0f0',
                              fg='#2c3e50')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Case Management Frame
        case_frame = ttk.LabelFrame(main_frame, text="Case Details", padding="10")
        case_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        tk.Label(case_frame, text="Case Name:").grid(row=0, column=0, padx=5)
        
        self.case_name_var = tk.StringVar(value=f"Case_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        self.case_entry = ttk.Entry(case_frame, textvariable=self.case_name_var, width=40)
        self.case_entry.grid(row=0, column=1, padx=5)
        
        # Device Status Frame
        status_frame = ttk.LabelFrame(main_frame, text="Device Status", padding="10")
        status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.status_label = tk.Label(status_frame, 
                                     text="Ready to connect device",
                                     font=("Segoe UI", 10),
                                     bg='#f0f0f0',
                                     fg='#34495e')
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        self.check_device_btn = ttk.Button(status_frame, 
                                           text="Check Device Connection",
                                           command=self.check_device)
        self.check_device_btn.grid(row=0, column=1, padx=10)
        
        # Progress Frame
        progress_frame = ttk.LabelFrame(main_frame, text="Extraction Progress", padding="10")
        progress_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.progress_label = tk.Label(progress_frame,
                                       text="No extraction in progress",
                                       font=("Segoe UI", 9),
                                       bg='#f0f0f0',
                                       fg='#7f8c8d')
        self.progress_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.progress_bar = ttk.Progressbar(progress_frame, 
                                            mode='determinate',
                                            length=400)
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        progress_frame.columnconfigure(0, weight=1)
        
        # Action Buttons Frame
        action_frame = ttk.Frame(main_frame, padding="10")
        action_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        self.extract_btn = ttk.Button(action_frame,
                                      text="🔍 Extract All Data (Root)",
                                      command=self.start_extraction,
                                      state='disabled')
        self.extract_btn.grid(row=0, column=0, padx=5)
        
        self.extract_backup_btn = ttk.Button(action_frame,
                                             text="💾 Extract via Backup (Non-Root)",
                                             command=self.start_backup_extraction,
                                             state='disabled')
        self.extract_backup_btn.grid(row=0, column=1, padx=5)
        
        self.parse_btn = ttk.Button(action_frame,
                                    text="📊 Parse & Generate Report",
                                    command=self.parse_and_report,
                                    state='disabled')
        self.parse_btn.grid(row=1, column=0, padx=5, pady=5)
        
        self.view_report_btn = ttk.Button(action_frame,
                                          text="📄 View Report",
                                          command=self.view_report,
                                          state='disabled')
        self.view_report_btn.grid(row=1, column=1, padx=5, pady=5)
        
        # Results Frame
        results_frame = ttk.LabelFrame(main_frame, text="Extraction Results", padding="10")
        results_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        main_frame.rowconfigure(5, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(results_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Summary Tab
        self.summary_text = scrolledtext.ScrolledText(self.notebook, 
                                                      wrap=tk.WORD,
                                                      font=("Consolas", 9),
                                                      bg='white',
                                                      fg='#2c3e50')
        self.notebook.add(self.summary_text, text="Summary")
        
        # Errors Tab
        self.errors_text = scrolledtext.ScrolledText(self.notebook,
                                                     wrap=tk.WORD,
                                                     font=("Consolas", 9),
                                                     bg='#fff5f5',
                                                     fg='#c53030')
        self.notebook.add(self.errors_text, text="Errors & Fixes")
        
        # Verification Tab
        self.verification_text = scrolledtext.ScrolledText(self.notebook,
                                                          wrap=tk.WORD,
                                                          font=("Consolas", 9),
                                                          bg='#f0fff4',
                                                          fg='#22543d')
        self.notebook.add(self.verification_text, text="Verification")
        
        # Status Bar
        status_bar = ttk.Frame(main_frame)
        status_bar.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.status_bar_label = tk.Label(status_bar,
                                        text="Ready",
                                        font=("Segoe UI", 8),
                                        bg='#f0f0f0',
                                        fg='#7f8c8d',
                                        anchor=tk.W)
        self.status_bar_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        status_bar.columnconfigure(0, weight=1)
        
    def update_status(self, message, color='#34495e'):
        """Update status bar"""
        self.status_bar_label.config(text=message, fg=color)
        self.root.update_idletasks()
    
    def update_progress(self, step, message, percentage):
        """Update progress bar and label"""
        step_str = f"Step {int(step)}" if isinstance(step, (int, float)) else f"Step {step}"
        self.progress_label.config(text=f"{step_str}: {message}")
        self.progress_bar['value'] = percentage
        self.update_status(f"Progress: {percentage}% - {message}")
        self.root.update_idletasks()
    
    def check_device(self):
        """Check if device is connected"""
        self.check_device_btn.config(state='disabled')
        self.update_status("Checking device connection...", '#3498db')
        
        def check():
            adb_ok, adb_msg = self.extractor.check_adb_available()
            if not adb_ok:
                self.root.after(0, lambda: self.show_error(
                    "ADB Not Available",
                    adb_msg,
                    self.extractor._get_adb_fix_instructions()
                ))
                self.root.after(0, lambda: self.check_device_btn.config(state='normal'))
                return
            
            device_ok, device_msg = self.extractor.check_device_connected()
            self.root.after(0, lambda: self.on_device_check_complete(device_ok, device_msg))
        
        threading.Thread(target=check, daemon=True).start()
    
    def on_device_check_complete(self, success, message):
        """Handle device check completion"""
        self.check_device_btn.config(state='normal')
        if success:
            self.status_label.config(text=f"✓ {message}", fg='#27ae60')
            self.extract_btn.config(state='normal')
            self.extract_backup_btn.config(state='normal')
            self.update_status("Device connected and ready", '#27ae60')
        else:
            self.status_label.config(text=f"✗ {message}", fg='#e74c3c')
            self.show_error("Device Not Connected", message, 
                          self.extractor._get_device_fix_instructions())
            self.update_status("Device not connected", '#e74c3c')
    
    def start_extraction(self):
        """Start the extraction process (root method)"""
        self.extract_btn.config(state='disabled')
        self.extract_backup_btn.config(state='disabled')
        self.progress_bar['value'] = 0
        self.clear_results()
        
        
        case_name = self.case_name_var.get().strip()
        if not case_name:
            messagebox.showwarning("Invalid Case Name", "Please enter a valid case name.")
            self.extract_btn.config(state='normal')
            self.extract_backup_btn.config(state='normal')
            return

        case_dir = os.path.join("cases", case_name)
        evidence_dir = os.path.join(case_dir, "evidence")
        
        # Update extractor with new path
        self.extractor = AndroidExtractor(evidence_dir=evidence_dir)
        
        def extract():
            self.root.after(0, lambda: self.update_status(f"Starting extraction for case: {case_name}...", '#3498db'))
            results = self.extractor.extract_all_data(progress_callback=self.update_progress)
            self.root.after(0, lambda: self.on_extraction_complete(results))
        
        threading.Thread(target=extract, daemon=True).start()
    
    def start_backup_extraction(self):
        """Start the backup extraction process (non-root method)"""
        self.extract_btn.config(state='disabled')
        self.extract_backup_btn.config(state='disabled')
        self.progress_bar['value'] = 0
        self.clear_results()
        
        # Show info about backup method
        messagebox.showinfo("Backup Extraction", 
                          "This method works for non-rooted devices.\n\n"
                          "You will need to approve backups on your device screen.\n"
                          "Make sure your device is unlocked and ready.")
        
        case_name = self.case_name_var.get().strip()
        if not case_name:
            messagebox.showwarning("Invalid Case Name", "Please enter a valid case name.")
            self.extract_btn.config(state='normal')
            self.extract_backup_btn.config(state='normal')
            return

        case_dir = os.path.join("cases", case_name)
        evidence_dir = os.path.join(case_dir, "evidence")
        
        # Update extractor with new path
        self.extractor = AndroidExtractor(evidence_dir=evidence_dir)

        def extract():
            self.root.after(0, lambda: self.update_status(f"Starting backup extraction for case: {case_name}...", '#3498db'))
            results = self.extractor.extract_via_backup(progress_callback=self.update_progress)
            self.root.after(0, lambda: self.on_extraction_complete(results))
        
        threading.Thread(target=extract, daemon=True).start()
    
    def on_extraction_complete(self, results):
        """Handle extraction completion"""
        self.extraction_results = results
        self.extract_btn.config(state='normal')
        self.extract_backup_btn.config(state='normal')
        
        method = results.get('method', 'root')
        method_text = "Backup extraction" if method == 'backup' else "Root extraction"
        
        if results['success']:
            self.update_status(f"{method_text} completed successfully!", '#27ae60')
            self.parse_btn.config(state='normal')
            self.display_results(results)
        else:
            self.update_status(f"{method_text} completed with errors", '#e74c3c')
            self.display_results(results)
            messagebox.showwarning("Extraction Issues", 
                                 "Some data could not be extracted. Check the Errors tab for details.")
    
    def display_results(self, results):
        """Display extraction results in tabs"""
        # Summary Tab
        summary = "=== EXTRACTION SUMMARY ===\n\n"
        summary += f"Status: {'✓ SUCCESS' if results['success'] else '✗ FAILED'}\n\n"
        
        if results['extracted_files']:
            summary += "Extracted Files:\n"
            for data_type, file_info in results['extracted_files'].items():
                summary += f"\n{data_type.upper()}:\n"
                summary += f"  File: {file_info['path']}\n"
                summary += f"  Status: {file_info['message']}\n"
                if 'hash' in file_info:
                    summary += f"  MD5 Hash: {file_info['hash']}\n"
        
        if results['warnings']:
            summary += f"\n\nWarnings: {len(results['warnings'])}\n"
        
        if results['errors']:
            summary += f"Errors: {len(results['errors'])}\n"
        
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(1.0, summary)
        
        # Errors Tab
        errors_text = "=== ERRORS AND FIXES ===\n\n"
        if results['errors']:
            for i, error in enumerate(results['errors'], 1):
                errors_text += f"ERROR {i}: {error['step']}\n"
                errors_text += f"Message: {error['message']}\n\n"
                errors_text += "How to Fix:\n"
                for instruction in error.get('fix_instructions', []):
                    errors_text += f"  {instruction}\n"
                errors_text += "\n" + "-"*50 + "\n\n"
        else:
            errors_text += "No errors encountered! ✓\n"
        
        self.errors_text.delete(1.0, tk.END)
        self.errors_text.insert(1.0, errors_text)
        
        # Verification Tab
        verification_text = "=== DATA VERIFICATION ===\n\n"
        if results['verification_results']:
            for data_type, verification in results['verification_results'].items():
                verification_text += f"{data_type.upper()}:\n"
                verification_text += f"  File Size: {verification.get('file_size', 0)} bytes\n"
                verification_text += f"  Tables Found: {', '.join(verification.get('tables_found', []))}\n"
                if verification.get('row_counts'):
                    verification_text += "  Row Counts:\n"
                    for table, count in verification['row_counts'].items():
                        verification_text += f"    {table}: {count} rows\n"
                verification_text += "\n"
        else:
            verification_text += "No verification data available\n"
        
        self.verification_text.delete(1.0, tk.END)
        self.verification_text.insert(1.0, verification_text)
    
    def parse_and_report(self):
        """Parse extracted data and generate report"""
        if not self.case_name_var.get().strip():
            messagebox.showwarning("No Case", "Please select a case first.")
            return
        
        self.parse_btn.config(state='disabled')
        self.update_status("Parsing data and generating report...", '#3498db')
        
        def parse():
            try:
                all_data = []
                
                # Define all potential evidence paths relative to the current case
                case_name = self.case_name_var.get().strip()
                case_dir = os.path.join("cases", case_name)
                evidence_dir = os.path.join(case_dir, "evidence")
                
                # Helper to check extraction results OR disk
                def get_path(key, rel_path):
                    # Priority 1: In-memory results
                    if self.extraction_results and 'extracted_files' in self.extraction_results:
                        if key in self.extraction_results['extracted_files']:
                            return self.extraction_results['extracted_files'][key]['path']
                    # Priority 2: Disk check
                    disk_path = os.path.join(evidence_dir, rel_path)
                    if os.path.exists(disk_path):
                        return disk_path
                    return None

                # 1. SMS
                path = get_path('sms', 'mmssms.db')
                if path:
                    df = parser.parse_sms(path)
                    if not df.empty: all_data.append(df)

                # 2. Calls
                path = get_path('calls', 'calllog.db')
                if path:
                    df = parser.parse_call_logs(path)
                    if not df.empty: all_data.append(df)
                    
                # 3. Chrome
                path = get_path('chrome', 'History')
                if path:
                    df = parser.parse_chrome_history(path)
                    if not df.empty: all_data.append(df)
                    
                # 4. Contacts
                path = get_path('contacts', 'contacts2.db')
                if path:
                    df = parser.parse_contacts(path)
                    if not df.empty: all_data.append(df)
                    
                # 5. WiFi
                path = get_path('wifi', 'WifiConfigStore.xml')
                if path:
                    df = parser.parse_wifi(path)
                    if not df.empty: all_data.append(df)
                    
                # 6. Packages
                path = get_path('packages', 'packages.xml')
                if path:
                    df = parser.parse_packages(path)
                    if not df.empty: all_data.append(df)
                    
                # 7. Shared Storage
                path = get_path('shared_storage', 'shared_storage')
                if path:
                    df = parser.parse_shared_storage(path)
                    if not df.empty: all_data.append(df)
                    
                # 8. System Dump
                path = get_path('system_dump', 'system_dump')
                if path:
                    df = parser.parse_system_dump(path)
                    if not df.empty: all_data.append(df)
                    
                # 9. Content Query (The requested feature)
                path = get_path('content_query', 'content_query')
                if path:
                    df = parser.parse_content_query(path)
                    if not df.empty: all_data.append(df)

                if not all_data:
                    self.root.after(0, lambda: messagebox.showwarning(
                        "No Data", "No data could be parsed. Check 'cases' folder."))
                    self.root.after(0, lambda: self.parse_btn.config(state='normal'))
                    return
                
                # Merge and sort
                timeline = pd.concat(all_data, ignore_index=True)
                timeline = timeline.sort_values(by='date')
                
                # Save report
                case_name = self.case_name_var.get().strip()
                case_dir = os.path.join("cases", case_name)
                output_file = os.path.join(case_dir, 'Forensic_Report.csv')
                
                # Ensure directory exists (in case user just typed a name without extracting)
                os.makedirs(case_dir, exist_ok=True)
                
                timeline.to_csv(output_file, index=False, escapechar='\\')
                
                self.root.after(0, lambda: self.on_report_generated(output_file, len(timeline)))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(
                    "Parse Error", f"Error parsing data: {str(e)}"))
                self.root.after(0, lambda: self.parse_btn.config(state='normal'))
        
        threading.Thread(target=parse, daemon=True).start()
    
    def on_report_generated(self, output_file, record_count):
        """Handle report generation completion"""
        self.parse_btn.config(state='normal')
        self.view_report_btn.config(state='normal')
        self.update_status(f"Report generated: {record_count} records", '#27ae60')
        messagebox.showinfo("Report Generated", 
                          f"Forensic report saved to:\n{os.path.abspath(output_file)}\n\n"
                          f"Total records: {record_count}")
    
    def view_report(self):
        """View extracted report using built-in viewer or open file"""
        case_name = self.case_name_var.get().strip()
        case_dir = os.path.join("cases", case_name)
        report_file = os.path.join(case_dir, 'Forensic_Report.csv')
        
        if not os.path.exists(report_file):
            messagebox.showwarning("Report Not Found", "Please generate a report first.")
            return

        try:
             # Load data for viewer
             df = pd.read_csv(report_file)
             ReportViewer(self.root, df)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open report viewer: {e}\nOpening file directly...")
            os.startfile(report_file)
    
    def show_error(self, title, message, fix_instructions):
        """Show error dialog with fix instructions"""
        error_msg = f"{message}\n\n"
        error_msg += "How to Fix:\n"
        for instruction in fix_instructions:
            error_msg += f"  {instruction}\n"
        
        messagebox.showerror(title, error_msg)
    
    def clear_results(self):
        """Clear all result displays"""
        self.summary_text.delete(1.0, tk.END)
        self.errors_text.delete(1.0, tk.END)
        self.verification_text.delete(1.0, tk.END)

def main():
    root = tk.Tk()
    app = AndroidForensicsGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

