#!/usr/bin/env python3
"""
Unified Gmail AI GUI
Consolidates all GUI functionality into a single, maintainable interface
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "utilities"))
sys.path.insert(0, str(project_root / "core"))

try:
    from utilities.secure_loader import get_gmail_credentials
    from utilities.logger import get_logger, log_email_processing
    from utilities.config_manager import get_config
    from core.email_classifier import classify_email, ClassificationResult
    utilities_available = True
except ImportError as e:
    print(f"⚠️ Some utilities not available: {e}")
    utilities_available = False

class UnifiedGmailGUI:
    """Unified Gmail AI Manager GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 Gmail AI Manager - Unified Edition")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Initialize components
        self.logger = get_logger("gui") if utilities_available else None
        self.config = get_config() if utilities_available else None
        
        # Variables
        self.gmail_email = tk.StringVar()
        self.gmail_password = tk.StringVar()
        self.email_count = tk.StringVar(value="10")
        self.dry_run = tk.BooleanVar(value=True)
        self.classification_mode = tk.StringVar(value="Hybrid")
        
        # Processing state
        self.processing = False
        self.processed_count = 0
        
        # Create GUI
        self.create_widgets()
        self.load_credentials()
        
        # Configure logging
        if self.logger:
            self.logger.info("Unified GUI initialized")
    
    def create_widgets(self):
        """Create the main GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="🚀 Gmail AI Manager - Unified Edition", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Main processing tab
        self.main_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.main_tab, text="📧 Email Processing")
        self.setup_main_tab()
        
        # Analytics tab
        self.analytics_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.analytics_tab, text="📊 Analytics")
        self.setup_analytics_tab()
        
        # Settings tab
        self.settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_tab, text="⚙️ Settings")
        self.setup_settings_tab()
    
    def setup_main_tab(self):
        """Setup main email processing tab"""
        # Gmail Settings Frame
        settings_frame = ttk.LabelFrame(self.main_tab, text="📧 Gmail Settings", padding="10")
        settings_frame.pack(fill='x', padx=10, pady=10)
        
        # Gmail credentials
        ttk.Label(settings_frame, text="Gmail Address:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(settings_frame, textvariable=self.gmail_email, width=40).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        ttk.Label(settings_frame, text="App Password:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(settings_frame, textvariable=self.gmail_password, show="*", width=40).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        # Classification options
        ttk.Label(settings_frame, text="Classification Mode:").grid(row=2, column=0, sticky=tk.W, pady=2)
        mode_combo = ttk.Combobox(settings_frame, textvariable=self.classification_mode, 
                                 values=["Hybrid", "Rule-based", "Machine Learning"], 
                                 width=25, state="readonly")
        mode_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        # Email count
        ttk.Label(settings_frame, text="Email Count:").grid(row=3, column=0, sticky=tk.W, pady=2)
        count_combo = ttk.Combobox(settings_frame, textvariable=self.email_count, 
                                  values=["10", "25", "50", "100", "All Available"], 
                                  width=25, state="readonly")
        count_combo.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        # Dry run option
        ttk.Checkbutton(settings_frame, text="🔍 Dry Run (Preview Only - Recommended)", 
                       variable=self.dry_run).grid(row=4, column=0, columnspan=2, 
                                                  sticky=tk.W, pady=5)
        
        settings_frame.columnconfigure(1, weight=1)
        
        # Action buttons
        button_frame = ttk.Frame(self.main_tab)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="🔍 Test Connection", 
                  command=self.test_connection).pack(side='left', padx=10)
        ttk.Button(button_frame, text="📧 Preview Emails", 
                  command=self.preview_emails).pack(side='left', padx=10)
        ttk.Button(button_frame, text="🚀 Run Classification", 
                  command=self.run_classification).pack(side='left', padx=10)
        ttk.Button(button_frame, text="🧹 Clean Inbox", 
                  command=self.clean_inbox).pack(side='left', padx=10)
        ttk.Button(button_frame, text="🗑️ Clear Output", 
                  command=self.clear_output).pack(side='left', padx=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.main_tab, mode='indeterminate')
        self.progress.pack(fill='x', padx=20, pady=10)
        
        # Status label
        self.status_label = ttk.Label(self.main_tab, text="Ready")
        self.status_label.pack(pady=5)
        
        # Output text area
        output_frame = ttk.LabelFrame(self.main_tab, text="📝 System Output", padding="10")
        output_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, height=15, wrap=tk.WORD)
        self.output_text.pack(fill='both', expand=True)
        
        # Add welcome message
        self.log_message("🚀 Gmail AI Manager - Unified Edition Initialized!")
        self.log_message("✅ All systems ready for email processing")
    
    def setup_analytics_tab(self):
        """Setup analytics tab"""
        title = ttk.Label(self.analytics_tab, text="📊 Email Analytics Dashboard", 
                         font=('Arial', 14, 'bold'))
        title.pack(pady=20)
        
        # Analytics content placeholder
        analytics_frame = ttk.LabelFrame(self.analytics_tab, text="Analytics Data", padding="20")
        analytics_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        ttk.Label(analytics_frame, text="📈 Analytics features coming soon...", 
                 font=('Arial', 12)).pack(pady=50)
        
        # Analytics buttons
        button_frame = ttk.Frame(analytics_frame)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="📊 Generate Report", 
                  command=self.generate_analytics).pack(side='left', padx=10)
        ttk.Button(button_frame, text="📈 Update Charts", 
                  command=self.update_charts).pack(side='left', padx=10)
    
    def setup_settings_tab(self):
        """Setup settings tab"""
        title = ttk.Label(self.settings_tab, text="⚙️ System Settings", 
                         font=('Arial', 14, 'bold'))
        title.pack(pady=20)
        
        # Settings content
        settings_frame = ttk.LabelFrame(self.settings_tab, text="Configuration", padding="20")
        settings_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Settings options
        ttk.Label(settings_frame, text="🔧 Settings management coming soon...", 
                 font=('Arial', 12)).pack(pady=50)
        
        # Settings buttons
        button_frame = ttk.Frame(settings_frame)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="💾 Save Settings", 
                  command=self.save_settings).pack(side='left', padx=10)
        ttk.Button(button_frame, text="🔄 Reset to Defaults", 
                  command=self.reset_settings).pack(side='left', padx=10)
    
    def load_credentials(self):
        """Load Gmail credentials"""
        if not utilities_available:
            self.log_message("⚠️ Credential loading not available - please enter manually")
            return
        
        try:
            email, password = get_gmail_credentials()
            self.gmail_email.set(email)
            self.gmail_password.set(password)
            self.log_message(f"✅ Loaded credentials for: {email}")
        except Exception as e:
            self.log_message(f"⚠️ Could not load credentials: {e}")
            self.log_message("💡 Please enter credentials manually")
    
    def log_message(self, message: str):
        """Add message to output area"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.output_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.output_text.see(tk.END)
        self.root.update_idletasks()
        
        # Also log to file if logger available
        if self.logger:
            self.logger.info(message)
    
    def clear_output(self):
        """Clear the output text area"""
        self.output_text.delete(1.0, tk.END)
        self.log_message("🗑️ Output cleared")
    
    def update_status(self, message: str):
        """Update the status label"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def start_progress(self):
        """Start the progress bar"""
        self.progress.start(10)
    
    def stop_progress(self):
        """Stop the progress bar"""
        self.progress.stop()
    
    def test_connection(self):
        """Test Gmail connection"""
        if not self.gmail_email.get() or not self.gmail_password.get():
            messagebox.showerror("Error", "Please enter Gmail credentials")
            return
        
        def test_thread():
            try:
                self.start_progress()
                self.update_status("Testing Gmail connection...")
                self.log_message("🔗 Testing Gmail connection...")
                
                import imaplib
                mail = imaplib.IMAP4_SSL("imap.gmail.com")
                mail.login(self.gmail_email.get(), self.gmail_password.get())
                mail.select("inbox")
                
                # Get inbox info
                _, data = mail.search(None, "ALL")
                total_emails = len(data[0].split()) if data[0] else 0
                
                _, unread_data = mail.search(None, "UNSEEN")
                unread_emails = len(unread_data[0].split()) if unread_data[0] else 0
                
                mail.logout()
                
                self.log_message(f"✅ Connection successful!")
                self.log_message(f"📊 Total emails in inbox: {total_emails}")
                self.log_message(f"📩 Unread emails: {unread_emails}")
                self.update_status("Connection successful")
                
            except Exception as e:
                self.log_message(f"❌ Connection failed: {str(e)}")
                self.update_status("Connection failed")
                messagebox.showerror("Connection Error", f"Failed to connect: {str(e)}")
            finally:
                self.stop_progress()
        
        threading.Thread(target=test_thread, daemon=True).start()
    
    def preview_emails(self):
        """Preview recent emails with classification"""
        if not self.gmail_email.get() or not self.gmail_password.get():
            messagebox.showerror("Error", "Please enter Gmail credentials")
            return
        
        def preview_thread():
            try:
                self.start_progress()
                self.update_status("Loading email preview...")
                self.log_message("📧 Loading email preview...")
                
                import imaplib
                import email
                from email.header import decode_header
                
                mail = imaplib.IMAP4_SSL("imap.gmail.com")
                mail.login(self.gmail_email.get(), self.gmail_password.get())
                mail.select("inbox")
                
                # Get recent emails
                count_str = self.email_count.get()
                if count_str == "All Available":
                    _, data = mail.search(None, "UNSEEN")
                else:
                    count = int(count_str)
                    _, data = mail.search(None, "ALL")
                    email_ids = data[0].split()
                    data = [b' '.join(email_ids[-count:])] if email_ids else [b'']
                
                email_ids = data[0].split() if data[0] else []
                
                if not email_ids:
                    self.log_message("📭 No emails found")
                    self.update_status("No emails found")
                    mail.logout()
                    return
                
                self.log_message(f"📊 Found {len(email_ids)} emails to preview")
                self.log_message("-" * 60)
                
                for i, email_id in enumerate(email_ids[-5:], 1):  # Show last 5
                    try:
                        # Fetch email
                        _, msg_data = mail.fetch(email_id, "(RFC822)")
                        email_message = email.message_from_bytes(msg_data[0][1])
                        
                        # Extract email information
                        subject = email_message.get("Subject", "No Subject")
                        sender = email_message.get("From", "Unknown Sender")
                        
                        # Decode headers
                        try:
                            if subject.startswith('=?'):
                                subject = str(email.header.make_header(email.header.decode_header(subject)))
                            if sender.startswith('=?'):
                                sender = str(email.header.make_header(email.header.decode_header(sender)))
                        except:
                            pass
                        
                        # Get body
                        body = ""
                        try:
                            if email_message.is_multipart():
                                for part in email_message.walk():
                                    if part.get_content_type() == "text/plain":
                                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')[:200]
                                        break
                            else:
                                body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')[:200]
                        except:
                            body = "Email body (processing error)"
                        
                        # Classify email
                        if utilities_available:
                            result = classify_email(subject, sender, body, f"preview_{email_id}")
                            classification = result.label
                            confidence = result.confidence
                            reason = result.reason
                        else:
                            # Fallback classification
                            classification = "Unknown"
                            confidence = 0.0
                            reason = "Classification not available"
                        
                        # Display results
                        self.log_message(f"{i}. 📧 {subject[:50]}...")
                        self.log_message(f"   From: {sender[:40]}")
                        self.log_message(f"   🤖 Classification: {classification}")
                        self.log_message(f"   📊 Confidence: {confidence:.2f}")
                        self.log_message(f"   💡 Reason: {reason}")
                        self.log_message("")
                        
                    except Exception as e:
                        self.log_message(f"⚠️ Error processing email {i}: {e}")
                        continue
                
                mail.logout()
                self.log_message("✅ Email preview completed!")
                self.update_status("Preview completed")
                
            except Exception as e:
                self.log_message(f"❌ Preview failed: {str(e)}")
                self.update_status("Preview failed")
                messagebox.showerror("Preview Error", f"Failed to preview emails: {str(e)}")
            finally:
                self.stop_progress()
        
        threading.Thread(target=preview_thread, daemon=True).start()
    
    def run_classification(self):
        """Run email classification"""
        if not self.gmail_email.get() or not self.gmail_password.get():
            messagebox.showerror("Error", "Please enter Gmail credentials")
            return
        
        # Confirm if not dry run
        if not self.dry_run.get():
            result = messagebox.askyesno("Confirm", 
                                       "This will apply labels to your emails. Continue?")
            if not result:
                return
        
        def classify_thread():
            try:
                self.start_progress()
                dry_run_text = " (DRY RUN)" if self.dry_run.get() else ""
                mode = self.classification_mode.get()
                
                self.update_status(f"Running {mode} classification{dry_run_text}...")
                self.log_message(f"🚀 Starting {mode} classification{dry_run_text}...")
                
                # Import required modules
                import imaplib
                import email
                from email.header import decode_header
                
                # Connect to Gmail
                mail = imaplib.IMAP4_SSL("imap.gmail.com")
                mail.login(self.gmail_email.get(), self.gmail_password.get())
                mail.select("inbox")
                
                # Get emails
                count_str = self.email_count.get()
                if count_str == "All Available":
                    _, data = mail.search(None, "UNSEEN")
                else:
                    count = int(count_str)
                    _, data = mail.search(None, "UNSEEN")
                    email_ids = data[0].split()
                    data = [b' '.join(email_ids[-count:])] if email_ids else [b'']
                
                email_ids = data[0].split() if data[0] else []
                
                if not email_ids:
                    self.log_message("📭 No emails found to process")
                    mail.logout()
                    return
                
                self.log_message(f"📧 Processing {len(email_ids)} emails...")
                
                classified_count = 0
                categories = {}
                
                for i, email_id in enumerate(email_ids, 1):
                    try:
                        # Fetch email
                        _, msg_data = mail.fetch(email_id, "(RFC822)")
                        email_message = email.message_from_bytes(msg_data[0][1])
                        
                        # Extract email information
                        subject = email_message.get("Subject", "No Subject")
                        sender = email_message.get("From", "Unknown Sender")
                        
                        # Decode headers
                        try:
                            if subject.startswith('=?'):
                                subject = str(email.header.make_header(email.header.decode_header(subject)))
                            if sender.startswith('=?'):
                                sender = str(email.header.make_header(email.header.decode_header(sender)))
                        except:
                            pass
                        
                        # Get body
                        body = ""
                        try:
                            if email_message.is_multipart():
                                for part in email_message.walk():
                                    if part.get_content_type() == "text/plain":
                                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')[:500]
                                        break
                            else:
                                body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')[:500]
                        except:
                            body = ""
                        
                        # Classify email
                        if utilities_available:
                            result = classify_email(subject, sender, body, f"classify_{email_id}")
                            classification = result.label
                            confidence = result.confidence
                            action = result.action
                            importance = result.importance
                        else:
                            # Fallback classification
                            classification = "Unknown"
                            confidence = 0.0
                            action = "archive"
                            importance = "low"
                        
                        categories[classification] = categories.get(classification, 0) + 1
                        
                        if classification != 'Unknown':
                            classified_count += 1
                            
                            if not self.dry_run.get():
                                try:
                                    # Apply classification action
                                    if action == 'trash':
                                        mail.store(email_id, '+FLAGS', '\\Deleted')
                                        self.log_message(f"🗑️ Trashed: {subject[:40]}... (Spam)")
                                    elif action == 'archive':
                                        mail.store(email_id, '-FLAGS', '\\Inbox')
                                        self.log_message(f"📁 Archived: {subject[:40]}... (Unimportant)")
                                    elif action == 'label':
                                        # Create and apply Gmail label
                                        label_name = f"AI-{classification}"
                                        try:
                                            mail.create(label_name)
                                        except:
                                            pass  # Label might already exist
                                        
                                        mail.store(email_id, '+X-GM-LABELS', f'"{label_name}"')
                                        self.log_message(f"🏷️ Labeled: {subject[:40]}... → {label_name}")
                                    
                                except Exception as e:
                                    self.log_message(f"⚠️ Failed to process email: {e}")
                            else:
                                # Dry run preview
                                if action == 'trash':
                                    self.log_message(f"🔍 Would TRASH: {subject[:40]}... (Spam)")
                                elif action == 'archive':
                                    self.log_message(f"🔍 Would ARCHIVE: {subject[:40]}... (Unimportant)")
                                else:
                                    self.log_message(f"🔍 Would LABEL: {subject[:40]}... → AI-{classification}")
                        
                        # Progress update
                        if i % 5 == 0:
                            self.log_message(f"⏳ Processed {i}/{len(email_ids)} emails...")
                    
                    except Exception as e:
                        self.log_message(f"⚠️ Error processing email {i}: {e}")
                        continue
                
                # Apply changes if not dry run
                if not self.dry_run.get():
                    try:
                        mail.expunge()
                        self.log_message("🔄 Applied all changes")
                    except Exception as e:
                        self.log_message(f"⚠️ Warning: Could not apply some changes: {e}")
                
                mail.logout()
                
                # Summary
                self.log_message(f"✅ Classification complete!")
                self.log_message(f"📊 Successfully classified {classified_count}/{len(email_ids)} emails")
                
                # Show category breakdown
                for category, count in categories.items():
                    self.log_message(f"  🏷️ {category}: {count} emails")
                
                self.update_status("Classification completed")
                
            except Exception as e:
                self.log_message(f"❌ Classification failed: {str(e)}")
                self.update_status("Classification failed")
                messagebox.showerror("Classification Error", f"Failed to run classification: {str(e)}")
            finally:
                self.stop_progress()
        
        threading.Thread(target=classify_thread, daemon=True).start()
    
    def clean_inbox(self):
        """Clean inbox by archiving and trashing emails"""
        self.log_message("🧹 Inbox cleaning feature coming soon...")
        self.log_message("💡 This will automatically archive unimportant emails and trash spam")
    
    def generate_analytics(self):
        """Generate analytics report"""
        self.log_message("📊 Analytics generation coming soon...")
        self.log_message("💡 This will create detailed reports of your email patterns")
    
    def update_charts(self):
        """Update analytics charts"""
        self.log_message("📈 Chart updates coming soon...")
        self.log_message("💡 This will refresh visual analytics")
    
    def save_settings(self):
        """Save current settings"""
        self.log_message("💾 Settings saving coming soon...")
        self.log_message("💡 This will save your preferences and configuration")
    
    def reset_settings(self):
        """Reset settings to defaults"""
        self.log_message("🔄 Settings reset coming soon...")
        self.log_message("💡 This will restore default configuration")

def main():
    """Main function to run the unified GUI"""
    print("🚀 Starting Gmail AI Manager - Unified Edition...")
    
    try:
        root = tk.Tk()
        app = UnifiedGmailGUI(root)
        
        # Handle window closing
        def on_closing():
            print("🚪 Window closing...")
            root.quit()
            root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        print("✅ Unified GUI initialized successfully")
        root.mainloop()
        print("✅ Unified GUI closed successfully")
        
    except Exception as e:
        print(f"❌ Error starting unified GUI: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
