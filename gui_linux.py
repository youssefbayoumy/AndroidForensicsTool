"""
Linux GUI Application for Android Forensics Tool
Optimized for Linux with GTK-like styling
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import os
import sys
from pathlib import Path
import pandas as pd
import parser
from core_extractor import AndroidExtractor
from datetime import datetime

class AndroidForensicsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Android Forensics Tool - Linux")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Linux-specific styling
        self.style = ttk.Style()
        try:
            self.style.theme_use('clam')  # Linux-friendly theme
        except:
            pass
        
        # Configure colors for Linux
        self.root.configure(bg='#f5f5f5')
        
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
                              font=("DejaVu Sans", 18, "bold"),
                              bg='#f5f5f5',
                              fg='#2c3e50')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Device Status Frame
        status_frame = ttk.LabelFrame(main_frame, text="Device Status", padding="10")
        status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.status_label = tk.Label(status_frame, 
                                     text="Ready to connect device",
                                     font=("DejaVu Sans", 10),
                                     bg='#f5f5f5',
                                     fg='#34495e')
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        self.check_device_btn = ttk.Button(status_frame, 
                                           text="Check Device Connection",
                                           command=self.check_device)
        self.check_device_btn.grid(row=0, column=1, padx=10)
        
        # Progress Frame
        progress_frame = ttk.LabelFrame(main_frame, text="Extraction Progress", padding="10")
        progress_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.progress_label = tk.Label(progress_frame,
                                       text="No extraction in progress",
                                       font=("DejaVu Sans", 9),
                                       bg='#f5f5f5',
                                       fg='#7f8c8d')
        self.progress_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.progress_bar = ttk.Progressbar(progress_frame, 
                                            mode='determinate',
                                            length=400)
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        progress_frame.columnconfigure(0, weight=1)
        
        # Action Buttons Frame
        action_frame = ttk.Frame(main_frame, padding="10")
        action_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
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
        results_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        main_frame.rowconfigure(4, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(results_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Summary Tab
        self.summary_text = scrolledtext.ScrolledText(self.notebook, 
                                                      wrap=tk.WORD,
                                                      font=("DejaVu Sans Mono", 9),
                                                      bg='white',
                                                      fg='#2c3e50')
        self.notebook.add(self.summary_text, text="Summary")
        
        # Errors Tab
        self.errors_text = scrolledtext.ScrolledText(self.notebook,
                                                     wrap=tk.WORD,
                                                     font=("DejaVu Sans Mono", 9),
                                                     bg='#fff5f5',
                                                     fg='#c53030')
        self.notebook.add(self.errors_text, text="Errors & Fixes")
        
        # Verification Tab
        self.verification_text = scrolledtext.ScrolledText(self.notebook,
                                                          wrap=tk.WORD,
                                                          font=("DejaVu Sans Mono", 9),
                                                          bg='#f0fff4',
                                                          fg='#22543d')
        self.notebook.add(self.verification_text, text="Verification")
        
        # Status Bar
        status_bar = ttk.Frame(main_frame)
        status_bar.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.status_bar_label = tk.Label(status_bar,
                                        text="Ready",
                                        font=("DejaVu Sans", 8),
                                        bg='#f5f5f5',
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
        
        def extract():
            self.root.after(0, lambda: self.update_status("Starting extraction (root method)...", '#3498db'))
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
        
        def extract():
            self.root.after(0, lambda: self.update_status("Starting backup extraction...", '#3498db'))
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
        if not self.extraction_results or not self.extraction_results['extracted_files']:
            messagebox.showwarning("No Data", "Please extract data first.")
            return
        
        self.parse_btn.config(state='disabled')
        self.update_status("Parsing data and generating report...", '#3498db')
        
        def parse():
            try:
                all_data = []
                
                # Parse SMS
                if 'sms' in self.extraction_results['extracted_files']:
                    sms_path = self.extraction_results['extracted_files']['sms']['path']
                    if os.path.exists(sms_path):
                        sms_data = parser.parse_sms(sms_path)
                        if not sms_data.empty:
                            all_data.append(sms_data)
                
                # Parse Calls
                if 'calls' in self.extraction_results['extracted_files']:
                    calls_path = self.extraction_results['extracted_files']['calls']['path']
                    if os.path.exists(calls_path):
                        call_data = parser.parse_call_logs(calls_path)
                        if not call_data.empty:
                            all_data.append(call_data)
                
                # Parse Chrome
                if 'chrome' in self.extraction_results['extracted_files']:
                    chrome_path = self.extraction_results['extracted_files']['chrome']['path']
                    if os.path.exists(chrome_path):
                        browser_data = parser.parse_chrome_history(chrome_path)
                        if not browser_data.empty:
                            all_data.append(browser_data)
                
                if not all_data:
                    self.root.after(0, lambda: messagebox.showwarning(
                        "No Data", "No data could be parsed from extracted files."))
                    self.root.after(0, lambda: self.parse_btn.config(state='normal'))
                    return
                
                # Merge and sort
                timeline = pd.concat(all_data, ignore_index=True)
                timeline = timeline.sort_values(by='date')
                
                # Save report
                output_file = 'Forensic_Report.csv'
                timeline.to_csv(output_file, index=False)
                
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
        """Open the generated report"""
        report_file = 'Forensic_Report.csv'
        if not os.path.exists(report_file):
            messagebox.showwarning("Report Not Found", "Please generate a report first.")
            return
        
        # Open with default application (Linux)
        os.system(f'xdg-open "{report_file}" 2>/dev/null &')
    
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

