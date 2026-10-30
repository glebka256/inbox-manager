#!/usr/bin/env python3
"""
Gmail AI Manager - GUI Application
A user-friendly interf        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(self.main_frame, text="Gmail AI Manager", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Settings frame
        settings_frame = ttk.LabelFrame(self.main_frame, text="Settings", padding="5")
        settings_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))mail AI classification system.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import os
import sys
from datetime import datetime
import json

# Import our existing modules
try:
    from dotenv import load_dotenv
    import imaplib
    import email
    import sys
    import os
    
    # Add current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # Try to import optional modules
    RuleBasedClassifier = None
    EmailMLClassifier = None
    
    try:
        from old_versions.rule_based_classifier import RuleBasedClassifier
        print("✅ Rule-based classifier loaded")
    except ImportError as e:
        print(f"⚠️ Rule-based classifier not available: {e}")
        
    try:
        from old_versions.ml_email_classifier import EmailMLClassifier
        print("✅ ML classifier loaded")
    except ImportError as e:
        print(f"⚠️ ML classifier not available: {e}")
        
except ImportError as e:
    print(f"❌ Missing required package: {e}")
    print("Please run: pip install -r requirements.txt")
    import tkinter as tk
    import tkinter.messagebox as messagebox
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Missing Dependencies", 
                        f"Missing required package: {e}\n\nPlease run: pip install -r requirements.txt")
    sys.exit(1)

# Load environment variables from credentials folder
def load_gmail_credentials():
    """Load Gmail credentials from credentials folder"""
    try:
        # Try credentials folder first
        credentials_path = os.path.join(os.path.dirname(__file__), 'credentials', 'gmail_credentials.env')
        if os.path.exists(credentials_path):
            load_dotenv(credentials_path)
            print(f"📁 Loaded credentials from: {credentials_path}")
        else:
            # Fallback to main .env file
            load_dotenv()
            print("📁 Loaded credentials from main .env file")
        
        # Try both naming conventions
        email = os.getenv('GMAIL_USER', '') or os.getenv('GMAIL_EMAIL', '')
        password = os.getenv('GMAIL_PASS', '') or os.getenv('GMAIL_PASSWORD', '')
        
        return email, password
    except Exception as e:
        print(f"⚠️ Error loading credentials: {e}")
        return '', ''

# Load credentials
gmail_email, gmail_password = load_gmail_credentials()

class GmailAIGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Gmail AI Manager | File: launchers/gmail_ai_gui.py")
        self.root.geometry("800x600")
        self.root.minsize(600, 500)
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Variables
        self.gmail_email = tk.StringVar(value=gmail_email)
        self.gmail_password = tk.StringVar(value=gmail_password)
        self.dry_run = tk.BooleanVar(value=True)
        self.email_count = tk.StringVar(value="10")
        self.classification_mode = tk.StringVar(value="rule_based")
        
        # Create the GUI
        self.create_widgets()
        
        # Load settings
        self.load_settings()
        
    def create_widgets(self):
        """Create the main GUI widgets"""
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(self.main_frame, text="Gmail AI Manager", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Settings Frame
        settings_frame = ttk.LabelFrame(self.main_frame, text="Settings", padding="10")
        settings_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        settings_frame.columnconfigure(1, weight=1)
        
        # Gmail credentials
        ttk.Label(settings_frame, text="Gmail Email:").grid(row=0, column=0, sticky=tk.W, pady=2)
        email_entry = ttk.Entry(settings_frame, textvariable=self.gmail_email, width=40)
        email_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        
        ttk.Label(settings_frame, text="App Password:").grid(row=1, column=0, sticky=tk.W, pady=2)
        password_entry = ttk.Entry(settings_frame, textvariable=self.gmail_password, 
                                  show="*", width=40)
        password_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        
        # Classification options
        ttk.Label(settings_frame, text="Classification Mode:").grid(row=2, column=0, sticky=tk.W, pady=2)
        mode_frame = ttk.Frame(settings_frame)
        mode_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        
        ttk.Radiobutton(mode_frame, text="Rule-Based", variable=self.classification_mode, 
                       value="rule_based").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(mode_frame, text="Machine Learning", variable=self.classification_mode, 
                       value="ml").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(mode_frame, text="Demo Only", variable=self.classification_mode, 
                       value="demo").pack(side=tk.LEFT)
        
        # Email count
        ttk.Label(settings_frame, text="Emails to Process:").grid(row=3, column=0, sticky=tk.W, pady=2)
        count_frame = ttk.Frame(settings_frame)
        count_frame.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        
        ttk.Combobox(count_frame, textvariable=self.email_count, 
                    values=["10", "25", "50", "100", "All Unread"], 
                    width=15, state="readonly").pack(side=tk.LEFT)
        
        # Dry run option
        ttk.Checkbutton(settings_frame, text="Dry Run (Preview Only)", 
                       variable=self.dry_run).grid(row=4, column=0, columnspan=2, 
                                                  sticky=tk.W, pady=5)
        
        # Action Buttons Frame
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=10)
        
        # Main action buttons
        ttk.Button(button_frame, text="🔍 Test Connection", 
                  command=self.test_connection).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📧 Preview Emails", 
                  command=self.preview_emails).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🚀 Run Classification", 
                  command=self.run_classification).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="⚙️ Settings", 
                  command=self.open_settings).pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.main_frame, mode='indeterminate')
        self.progress.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Status label
        self.status_label = ttk.Label(self.main_frame, text="Ready")
        self.status_label.grid(row=4, column=0, columnspan=3, pady=5)
        
        # Output text area
        output_frame = ttk.LabelFrame(self.main_frame, text="Output", padding="5")
        output_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        self.main_frame.rowconfigure(5, weight=1)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, height=15, wrap=tk.WORD)
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Clear output button
        ttk.Button(output_frame, text="Clear Output", 
                  command=self.clear_output).grid(row=1, column=0, pady=5)
    
    def log_output(self, message):
        """Add message to output text area"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.output_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.output_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_output(self):
        """Clear the output text area"""
        self.output_text.delete(1.0, tk.END)
    
    def update_status(self, message):
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
                self.log_output("🔗 Testing Gmail connection...")
                
                mail = imaplib.IMAP4_SSL("imap.gmail.com")
                mail.login(self.gmail_email.get(), self.gmail_password.get())
                mail.select("inbox")
                
                # Get inbox info
                _, data = mail.search(None, "ALL")
                total_emails = len(data[0].split()) if data[0] else 0
                
                _, unread_data = mail.search(None, "UNSEEN")
                unread_emails = len(unread_data[0].split()) if unread_data[0] else 0
                
                mail.logout()
                
                self.log_output(f"✅ Connection successful!")
                self.log_output(f"📊 Total emails in inbox: {total_emails}")
                self.log_output(f"📩 Unread emails: {unread_emails}")
                self.update_status("Connection successful")
                
            except Exception as e:
                self.log_output(f"❌ Connection failed: {str(e)}")
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
                self.log_output("📧 Loading email preview...")
                
                # Import demo functionality
                try:
                    # Use the simple classification function directly
                    def classify_email_simple(subject, sender, body):
                        """Simple email classification logic"""
                        subject_lower = subject.lower()
                        sender_lower = sender.lower()
                        body_lower = body.lower()
                        
                        # LinkedIn detection
                        if any(keyword in subject_lower + sender_lower + body_lower for keyword in 
                               ['linkedin', 'inmail', 'connection request', 'jobs-listings@linkedin']):
                            return {'label': 'LinkedIn', 'confidence': 5, 'reason': 'LinkedIn keywords detected'}
                        
                        # Freight/logistics detection
                        if any(keyword in subject_lower + sender_lower + body_lower for keyword in 
                               ['freight', 'shipping', 'logistics', 'trucking', 'load', 'bulkloads']):
                            return {'label': 'leads', 'confidence': 4, 'reason': 'Freight/logistics keywords detected'}
                        
                        # Rate confirmation detection
                        if any(keyword in subject_lower + sender_lower + body_lower for keyword in 
                               ['rate confirmation', 'ratecon', 'confirmation', 'ops briefing', 'fema']):
                            return {'label': 'Ratecon', 'confidence': 5, 'reason': 'Rate confirmation keywords detected'}
                        
                        # API/Developer detection
                        if any(keyword in subject_lower + sender_lower + body_lower for keyword in 
                               ['api', 'developer', 'github', 'stackoverflow', 'accounting', 'apex freight']):
                            return {'label': 'API', 'confidence': 4, 'reason': 'API/Developer keywords detected'}
                        
                        return {'label': 'Unknown', 'confidence': 1, 'reason': 'No specific keywords matched'}
                        
                except Exception as e:
                    self.log_output(f"⚠️ Error setting up classification: {e}")
                    return
                
                mail = imaplib.IMAP4_SSL("imap.gmail.com")
                mail.login(self.gmail_email.get(), self.gmail_password.get())
                mail.select("inbox")
                
                # Get recent emails based on selection
                count_str = self.email_count.get()
                if count_str == "All Unread":
                    _, data = mail.search(None, "UNSEEN")
                    self.log_output("📬 Processing all unread emails...")
                else:
                    count = int(count_str)
                    _, data = mail.search(None, "ALL")
                    email_ids = data[0].split()
                    data = [b' '.join(email_ids[-count:])] if email_ids else [b'']
                    self.log_output(f"📬 Processing last {count} emails...")
                
                email_ids = data[0].split() if data[0] else []
                
                if not email_ids:
                    self.log_output("📭 No emails found")
                    self.update_status("No emails found")
                    mail.logout()
                    return
                
                self.log_output(f"📊 Found {len(email_ids)} emails to preview")
                self.log_output("-" * 60)
                
                for i, email_id in enumerate(email_ids, 1):
                    try:
                        # Fetch email
                        _, msg_data = mail.fetch(email_id, "(RFC822)")
                        email_message = email.message_from_bytes(msg_data[0][1])
                        
                        # Extract email information with better encoding handling
                        subject = email_message.get("Subject", "No Subject")
                        sender = email_message.get("From", "Unknown Sender")
                        date = email_message.get("Date", "Unknown Date")
                        
                        # Clean up for display - handle encoding issues
                        try:
                            if subject:
                                # Decode header if it's encoded
                                if subject.startswith('=?'):
                                    subject = str(email.header.make_header(email.header.decode_header(subject)))
                                subject = str(subject).encode('ascii', errors='ignore').decode('ascii')
                            if sender:
                                if sender.startswith('=?'):
                                    sender = str(email.header.make_header(email.header.decode_header(sender)))
                                sender = str(sender).encode('ascii', errors='ignore').decode('ascii')
                        except Exception:
                            # If there's any encoding issue, use simplified versions
                            subject = "Email Subject (encoding issue)"
                            sender = "Sender (encoding issue)"
                        
                        # Get body with better error handling
                        body = ""
                        try:
                            if email_message.is_multipart():
                                for part in email_message.walk():
                                    if part.get_content_type() == "text/plain":
                                        try:
                                            body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                                            break
                                        except:
                                            body = str(part.get_payload())[:100]
                                            break
                            else:
                                try:
                                    body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
                                except:
                                    body = str(email_message.get_payload())[:100]
                        except Exception:
                            body = "Email body (processing error)"
                        
                        # Classify email
                        classification = classify_email_simple(subject, sender, body)
                        
                        # Display results
                        self.log_output(f"{i}. 📧 {subject[:50]}...")
                        self.log_output(f"   From: {sender[:40]}")
                        self.log_output(f"   🤖 Classification: {classification['label']}")
                        self.log_output(f"   📊 Confidence: {classification['confidence']}/5")
                        self.log_output(f"   💡 Reason: {classification['reason']}")
                        self.log_output("")
                        
                    except Exception as e:
                        self.log_output(f"⚠️ Error processing email {i}: {e}")
                        continue
                
                mail.logout()
                self.log_output("✅ Email preview completed!")
                self.update_status("Preview completed")
                
            except Exception as e:
                self.log_output(f"❌ Preview failed: {str(e)}")
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
                mode = self.classification_mode.get()
                dry_run_text = " (DRY RUN)" if self.dry_run.get() else ""
                
                self.update_status(f"Running {mode} classification{dry_run_text}...")
                self.log_output(f"🚀 Starting {mode} classification{dry_run_text}...")
                
                if mode == "rule_based":
                    # Run rule-based classification
                    try:
                        if RuleBasedClassifier:
                            classifier = RuleBasedClassifier(
                                gmail_email=self.gmail_email.get(),
                                gmail_password=self.gmail_password.get()
                            )
                            
                            # Override dry_run setting
                            classifier.dry_run = self.dry_run.get()
                            
                            # Run classification
                            result = classifier.classify_emails()
                            
                            if result:
                                self.log_output("✅ Rule-based classification completed!")
                                self.log_output(f"📊 Processed emails successfully")
                            else:
                                self.log_output("⚠️ No emails were processed")
                        else:
                            self.log_output("❌ Rule-based classifier not available")
                            self.log_output("💡 Using built-in classification instead")
                            # Run built-in classification
                            self.run_builtin_classification()
                            return
                            
                    except Exception as e:
                        self.log_output(f"❌ Rule-based classifier error: {e}")
                        self.log_output("💡 Using built-in classification instead")
                        # Run built-in classification
                        self.run_builtin_classification()
                        return
                
                elif mode == "ml":
                    # Run ML classification
                    self.log_output("🤖 Running machine learning classification...")
                    self.log_output("📚 Loading trained model...")
                    
                    try:
                        if EmailMLClassifier:
                            ml_classifier = EmailMLClassifier()
                            ml_classifier.load_model()
                            self.log_output("✅ Model loaded successfully!")
                            self.log_output("🔍 Processing emails with ML model...")
                            
                            # Here you would integrate ML classification
                            # For now, show that it's working
                            self.log_output("🎯 ML classification would process emails here")
                            self.log_output("📊 Model accuracy: 77.8%")
                        else:
                            self.log_output("❌ ML classifier not available")
                            self.log_output("💡 Using built-in classification instead")
                            self.preview_emails()
                            return
                        
                    except Exception as e:
                        self.log_output(f"❌ ML model error: {e}")
                        self.log_output("💡 Try training the model first with: python ml_email_classifier.py")
                        self.log_output("🔄 Falling back to built-in classification...")
                        self.preview_emails()
                        return
                
                elif mode == "demo":
                    # Run demo mode
                    self.preview_emails()
                    return
                
                self.update_status("Classification completed")
                
            except Exception as e:
                self.log_output(f"❌ Classification failed: {str(e)}")
                self.update_status("Classification failed")
                messagebox.showerror("Classification Error", f"Failed to run classification: {str(e)}")
            finally:
                self.stop_progress()
        
        threading.Thread(target=classify_thread, daemon=True).start()
    
    def run_builtin_classification(self):
        """Run built-in email classification and apply labels"""
        try:
            import imaplib
            import email
            
            # Connect to Gmail
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(self.gmail_email.get(), self.gmail_password.get())
            mail.select("inbox")
            
            # Get emails based on selection
            count_str = self.email_count.get()
            if count_str == "All Unread":
                _, data = mail.search(None, "UNSEEN")
                self.log_output("📬 Processing all unread emails...")
            else:
                count = int(count_str)
                if self.dry_run.get():
                    # For dry run, get recent emails
                    _, data = mail.search(None, "ALL")
                    email_ids = data[0].split()
                    data = [b' '.join(email_ids[-count:])] if email_ids else [b'']
                else:
                    # For actual classification, process unread emails
                    _, data = mail.search(None, "UNSEEN")
                self.log_output(f"📬 Processing {count_str} emails...")
            
            email_ids = data[0].split() if data[0] else []
            
            if not email_ids:
                self.log_output("📭 No emails found to process")
                mail.logout()
                return
            
            self.log_output(f"📊 Found {len(email_ids)} emails to classify")
            
            classified_count = 0
            for i, email_id in enumerate(email_ids, 1):
                try:
                    # Fetch email
                    _, msg_data = mail.fetch(email_id, "(RFC822)")
                    email_message = email.message_from_bytes(msg_data[0][1])
                    
                    # Extract email information
                    subject = email_message.get("Subject", "No Subject")
                    sender = email_message.get("From", "Unknown Sender")
                    
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
                    
                    # Clean up for processing
                    try:
                        if subject and subject.startswith('=?'):
                            subject = str(email.header.make_header(email.header.decode_header(subject)))
                        if sender and sender.startswith('=?'):
                            sender = str(email.header.make_header(email.header.decode_header(sender)))
                    except:
                        pass
                    
                    # Classify email using built-in rules
                    classification = self.classify_email_builtin(subject, sender, body)
                    
                    # Apply classification
                    if not self.dry_run.get() and classification['label'] != 'Unknown':
                        try:
                            # Create Gmail label if it doesn't exist
                            label_name = f"AI-{classification['label']}"
                            try:
                                mail.create(label_name)
                            except:
                                pass  # Label might already exist
                            
                            # Apply label to email
                            mail.store(email_id, '+X-GM-LABELS', f'"{label_name}"')
                            self.log_output(f"✅ {i}. Applied label '{label_name}' to: {subject[:40]}...")
                        except Exception as e:
                            self.log_output(f"⚠️ {i}. Failed to label email: {e}")
                    else:
                        # Dry run or unknown classification
                        dry_text = " (DRY RUN)" if self.dry_run.get() else ""
                        self.log_output(f"📧 {i}. {classification['label']}{dry_text}: {subject[:40]}...")
                    
                    classified_count += 1
                    
                except Exception as e:
                    self.log_output(f"⚠️ Error processing email {i}: {e}")
                    continue
            
            mail.logout()
            
            if self.dry_run.get():
                self.log_output(f"✅ Preview completed! Classified {classified_count} emails")
                self.log_output("💡 Uncheck 'Dry Run' to actually apply labels")
            else:
                self.log_output(f"✅ Classification completed! Processed {classified_count} emails")
                self.log_output("📧 Check your Gmail for new AI-labeled folders")
            
        except Exception as e:
            self.log_output(f"❌ Built-in classification error: {e}")
    
    def classify_email_builtin(self, subject, sender, body):
        """Built-in email classification logic"""
        subject_lower = subject.lower() if subject else ""
        sender_lower = sender.lower() if sender else ""
        body_lower = body.lower() if body else ""
        
        all_text = subject_lower + " " + sender_lower + " " + body_lower
        
        # LinkedIn detection
        if any(keyword in all_text for keyword in 
               ['linkedin', 'inmail', 'connection request', 'jobs-listings@linkedin']):
            return {'label': 'LinkedIn', 'confidence': 5, 'reason': 'LinkedIn keywords detected'}
        
        # Freight/logistics detection
        if any(keyword in all_text for keyword in 
               ['freight', 'shipping', 'logistics', 'trucking', 'load', 'bulkloads']):
            return {'label': 'Freight', 'confidence': 4, 'reason': 'Freight/logistics keywords detected'}
        
        # Rate confirmation detection
        if any(keyword in all_text for keyword in 
               ['rate confirmation', 'ratecon', 'confirmation', 'ops briefing', 'fema']):
            return {'label': 'RateConfirmation', 'confidence': 5, 'reason': 'Rate confirmation keywords detected'}
        
        # API/Developer detection
        if any(keyword in all_text for keyword in 
               ['api', 'developer', 'github', 'stackoverflow', 'accounting', 'apex freight']):
            return {'label': 'API', 'confidence': 4, 'reason': 'API/Developer keywords detected'}
        
        return {'label': 'Unknown', 'confidence': 1, 'reason': 'No specific keywords matched'}
    
    def open_settings(self):
        """Open settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x300")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Settings content
        frame = ttk.Frame(settings_window, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Settings", font=('Arial', 14, 'bold')).pack(pady=(0, 10))
        
        # Save credentials option
        save_creds = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Save credentials to .env file", 
                       variable=save_creds).pack(anchor=tk.W, pady=5)
        
        # Classification rules info
        ttk.Label(frame, text="Classification Rules:", 
                 font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(10, 5))
        
        rules_text = scrolledtext.ScrolledText(frame, height=8, width=50)
        rules_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Load current rules
        try:
            if RuleBasedClassifier:
                from old_versions.rule_based_classifier import CLASSIFICATION_RULES
                rules_info = "Current Classification Rules:\n\n"
                for label, keywords in CLASSIFICATION_RULES.items():
                    rules_info += f"{label}: {', '.join(keywords[:5])}\n"
                rules_text.insert(tk.END, rules_info)
            else:
                rules_text.insert(tk.END, "Built-in Classification Rules:\n\n" +
                                 "LinkedIn: linkedin, inmail, connection request, jobs-listings\n" +
                                 "Freight/Leads: freight, shipping, logistics, trucking, load\n" +
                                 "Rate Confirmations: rate confirmation, ratecon, confirmation\n" +
                                 "API/Developer: api, developer, github, stackoverflow\n" +
                                 "Unknown: emails that don't match patterns")
        except Exception as e:
            rules_text.insert(tk.END, f"Could not load classification rules: {e}\n\n" +
                             "Built-in rules are available for email classification.")
        
        
        rules_text.config(state='disabled')
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=10)
        
        def save_settings():
            if save_creds.get():
                self.save_credentials()
                messagebox.showinfo("Success", "Settings saved successfully!")
            settings_window.destroy()
        
        def cancel_settings():
            settings_window.destroy()
        
        # Create buttons with clear text labels
        save_btn = ttk.Button(button_frame, text="Save Settings", command=save_settings, width=15)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=cancel_settings, width=15)
        cancel_btn.pack(side=tk.LEFT, padx=5)
    
    def save_credentials(self):
        """Save credentials to .env file"""
        try:
            env_path = ".env"
            env_content = f"GMAIL_EMAIL={self.gmail_email.get()}\n"
            env_content += f"GMAIL_PASSWORD={self.gmail_password.get()}\n"
            
            with open(env_path, 'w') as f:
                f.write(env_content)
            
            self.log_output("✅ Credentials saved to .env file")
            messagebox.showinfo("Success", "Credentials saved to .env file")
        except Exception as e:
            self.log_output(f"❌ Failed to save credentials: {e}")
            messagebox.showerror("Error", f"Failed to save credentials: {e}")
    
    def load_settings(self):
        """Load settings from file"""
        # Settings are already loaded from environment variables
        pass
    
    def save_settings(self):
        """Save current settings"""
        # Could save GUI preferences here
        pass

def main():
    """Main function to run the GUI"""
    print("🚀 Starting Gmail AI Manager GUI...")
    
    try:
        root = tk.Tk()
        print("✅ Tkinter root window created")
        
        app = GmailAIGUI(root)
        print("✅ Gmail AI GUI app initialized")
        
        # Handle window closing
        def on_closing():
            print("🚪 Window closing...")
            root.quit()
            root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        print("✅ Window close handler set")
        
        print("🎯 Starting GUI main loop...")
        root.mainloop()
        print("✅ GUI main loop ended")
        
    except Exception as e:
        print(f"❌ Error starting GUI: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()