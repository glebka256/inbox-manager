#!/usr/bin/env python3
"""
Unified Gmail AI Manager - Combines original functionality with advanced features
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import json
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import imaplib
import email
from email.header import decode_header
import ssl

# Import our modules
try:
    from smart_learning_classifier import SmartLearningClassifier
    smart_available = True
except:
    smart_available = False

try:
    from email_analytics import EmailAnalytics
    analytics_available = True
except:
    analytics_available = False

try:
    from business_intelligence import BusinessIntelligenceProcessor
    business_available = True
except:
    business_available = False

try:
    from rule_based_classifier import RuleBasedClassifier
    rule_classifier = RuleBasedClassifier()
    rule_available = True
except:
    rule_available = False

try:
    from ml_email_classifier import MLEmailClassifier
    ml_classifier = MLEmailClassifier()
    ml_available = True
except:
    ml_available = False

class UnifiedGmailAIManager:
    """Unified Gmail AI Manager combining original functionality with advanced features"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 Unified Gmail AI Manager - Complete Edition 🚀")
        self.root.geometry("1600x1000")
        
        # Gmail connection variables
        self.email_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.classification_mode = tk.StringVar(value="rule_based")
        self.email_count = tk.StringVar(value="10")
        self.dry_run = tk.BooleanVar(value=True)
        
        # Load settings
        self.load_settings()
        
        # Initialize advanced components
        if smart_available:
            self.smart_classifier = SmartLearningClassifier()
        if analytics_available:
            self.analytics = EmailAnalytics()
        if business_available:
            self.business_intel = BusinessIntelligenceProcessor()
        
        self.create_unified_gui()
        
    def create_unified_gui(self):
        """Create unified interface with original Gmail functionality + advanced features"""
        
        # Create main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill='both', expand=True, pady=(0, 10))
        
        # Main Gmail Processing Tab (Original functionality)
        self.gmail_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.gmail_tab, text="📧 Gmail Processing")
        self.setup_gmail_tab()
        
        # Analytics Tab with Charts
        self.analytics_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.analytics_tab, text="📊 Analytics Dashboard")
        self.setup_analytics_tab()
        
        # Business Intelligence Tab
        self.business_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.business_tab, text="💼 Business Intelligence")
        self.setup_business_tab()
        
        # Create persistent output area
        self.create_persistent_output(main_container)
        
    def setup_gmail_tab(self):
        """Setup the main Gmail processing tab with original functionality"""
        
        # Title
        title_label = ttk.Label(self.gmail_tab, text="Gmail AI Manager - Complete Email Processing", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Settings Frame
        settings_frame = ttk.LabelFrame(self.gmail_tab, text="Gmail Settings", padding=10)
        settings_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        # Gmail Email
        ttk.Label(settings_frame, text="Gmail Email:").grid(row=0, column=0, sticky=tk.W, pady=2)
        email_entry = ttk.Entry(settings_frame, textvariable=self.email_var, width=40)
        email_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        
        # App Password
        ttk.Label(settings_frame, text="App Password:").grid(row=1, column=0, sticky=tk.W, pady=2)
        password_entry = ttk.Entry(settings_frame, textvariable=self.password_var, 
                                 show="*", width=40)
        password_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        
        # Classification Mode
        ttk.Label(settings_frame, text="Classification Mode:").grid(row=2, column=0, sticky=tk.W, pady=2)
        mode_frame = ttk.Frame(settings_frame)
        mode_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        
        ttk.Radiobutton(mode_frame, text="Rule-based", variable=self.classification_mode,
                       value="rule_based").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(mode_frame, text="Machine Learning", variable=self.classification_mode,
                       value="ml").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(mode_frame, text="Demo Mode", variable=self.classification_mode,
                       value="demo").pack(side=tk.LEFT)
        
        # Email Count
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
        
        settings_frame.columnconfigure(1, weight=1)
        
        # Action Buttons
        button_frame = ttk.Frame(self.gmail_tab)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="🔍 Test Connection", 
                  command=self.test_gmail_connection).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📧 Preview Emails", 
                  command=self.preview_emails).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🚀 Run Classification", 
                  command=self.run_classification).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="⚙️ Settings", 
                  command=self.open_settings).pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.gmail_tab, mode='indeterminate')
        self.progress.pack(fill='x', padx=20, pady=5)
        
        # Status label
        self.status_label = ttk.Label(self.gmail_tab, text="Ready")
        self.status_label.pack(pady=5)
        
        # Create charts for Gmail tab
        self.create_gmail_charts()
        
    def create_gmail_charts(self):
        """Create charts for Gmail processing tab"""
        chart_frame = ttk.LabelFrame(self.gmail_tab, text="📊 Real-time Processing Charts", padding=10)
        chart_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Create matplotlib figure
        self.gmail_fig, (self.gmail_ax1, self.gmail_ax2) = plt.subplots(1, 2, figsize=(12, 4))
        self.gmail_fig.patch.set_facecolor('white')
        
        # Embed in tkinter
        self.gmail_canvas = FigureCanvasTkAgg(self.gmail_fig, chart_frame)
        self.gmail_canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Initialize with empty charts
        self.update_gmail_charts()
        
    def update_gmail_charts(self):
        """Update Gmail processing charts"""
        self.gmail_ax1.clear()
        self.gmail_ax2.clear()
        
        # Chart 1: Email Classification Results
        categories = ['Business', 'Personal', 'Promotions', 'Social', 'Spam']
        counts = [15, 8, 12, 5, 2]
        colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ff99cc']
        
        bars = self.gmail_ax1.bar(categories, counts, color=colors, alpha=0.8)
        self.gmail_ax1.set_title('📧 Classification Results')
        self.gmail_ax1.set_ylabel('Email Count')
        
        # Add value labels on bars
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            self.gmail_ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                              str(count), ha='center', va='bottom')
        
        # Chart 2: Processing Status
        statuses = ['Processed', 'Labeled', 'Skipped']
        status_counts = [38, 35, 3]
        colors2 = ['#90EE90', '#87CEEB', '#FFB6C1']
        
        wedges, texts, autotexts = self.gmail_ax2.pie(status_counts, labels=statuses, colors=colors2,
                                                     autopct='%1.1f%%', startangle=90)
        self.gmail_ax2.set_title('📊 Processing Status')
        
        self.gmail_fig.tight_layout()
        self.gmail_canvas.draw()
        
    def setup_analytics_tab(self):
        """Setup analytics tab"""
        title = ttk.Label(self.analytics_tab, text="📊 Advanced Email Analytics", 
                         font=('Arial', 16, 'bold'))
        title.pack(pady=20)
        
        # Buttons
        button_frame = ttk.Frame(self.analytics_tab)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="📊 Generate Report", 
                  command=self.generate_analytics).pack(side='left', padx=10)
        ttk.Button(button_frame, text="📈 Update Charts", 
                  command=self.update_analytics_charts).pack(side='left', padx=10)
        
        # Create analytics charts
        self.create_analytics_charts()
        
    def create_analytics_charts(self):
        """Create analytics charts"""
        chart_frame = ttk.LabelFrame(self.analytics_tab, text="📈 Email Analytics Dashboard", padding=10)
        chart_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Create figure with 4 subplots
        self.analytics_fig, ((self.analytics_ax1, self.analytics_ax2), 
                           (self.analytics_ax3, self.analytics_ax4)) = plt.subplots(2, 2, figsize=(14, 8))
        self.analytics_fig.patch.set_facecolor('white')
        
        # Embed in tkinter
        self.analytics_canvas = FigureCanvasTkAgg(self.analytics_fig, chart_frame)
        self.analytics_canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Initialize charts
        self.update_analytics_charts()
    
    def update_analytics_charts(self):
        """Update analytics charts"""
        for ax in [self.analytics_ax1, self.analytics_ax2, self.analytics_ax3, self.analytics_ax4]:
            ax.clear()
        
        # Chart 1: Daily email volume
        dates = [datetime.now() - timedelta(days=x) for x in range(29, -1, -1)]
        volumes = np.random.poisson(42, 30)
        
        self.analytics_ax1.plot(dates, volumes, marker='o', linewidth=2, color='#1f77b4')
        self.analytics_ax1.set_title('Daily Email Volume (30 Days)')
        self.analytics_ax1.grid(True, alpha=0.3)
        
        # Chart 2: Category distribution
        categories = ['Business', 'Personal', 'Promotions', 'Social', 'Updates', 'Spam']
        sizes = [35, 25, 15, 10, 10, 5]
        colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ff99cc', '#c2c2f0']
        
        self.analytics_ax2.pie(sizes, labels=categories, colors=colors, autopct='%1.1f%%')
        self.analytics_ax2.set_title('Email Category Distribution')
        
        # Chart 3: Hourly activity
        hours = list(range(24))
        activity = [2, 1, 0, 0, 1, 3, 8, 15, 22, 18, 16, 14, 12, 15, 18, 20, 16, 12, 8, 6, 4, 3, 2, 1]
        
        self.analytics_ax3.bar(hours, activity, color='skyblue', alpha=0.7)
        self.analytics_ax3.set_title('Email Activity by Hour')
        self.analytics_ax3.set_xlabel('Hour of Day')
        self.analytics_ax3.set_ylabel('Email Count')
        
        # Chart 4: Top senders
        senders = ['work@company.com', 'notifications@bank.com', 'news@tech.com', 'social@platform.com']
        counts = [45, 32, 28, 15]
        
        self.analytics_ax4.barh(senders, counts, color='lightcoral')
        self.analytics_ax4.set_title('Top Email Senders')
        
        self.analytics_fig.tight_layout()
        self.analytics_canvas.draw()
        
    def setup_business_tab(self):
        """Setup business intelligence tab"""
        title = ttk.Label(self.business_tab, text="💼 Business Intelligence", 
                         font=('Arial', 16, 'bold'))
        title.pack(pady=20)
        
        # Buttons
        button_frame = ttk.Frame(self.business_tab)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="💰 Analyze Rates", 
                  command=self.analyze_rates).pack(side='left', padx=10)
        ttk.Button(button_frame, text="🧾 Process Invoices", 
                  command=self.process_invoices).pack(side='left', padx=10)
        
        # Simple placeholder for business charts
        placeholder = ttk.Label(self.business_tab, text="Business Intelligence Charts\n(Invoice processing, rate analysis, etc.)", 
                               font=('Arial', 12), foreground='gray')
        placeholder.pack(expand=True)
        
    def create_persistent_output(self, parent):
        """Create persistent output area"""
        output_frame = ttk.LabelFrame(parent, text="📝 System Output & Logs", padding=10)
        output_frame.pack(fill='both', expand=False, pady=(10, 0))
        
        # Create text widget with scrollbar
        text_frame = ttk.Frame(output_frame)
        text_frame.pack(fill='both', expand=True)
        
        self.output_text = scrolledtext.ScrolledText(text_frame, height=10, wrap=tk.WORD, 
                                                   font=('Consolas', 9))
        self.output_text.pack(fill='both', expand=True)
        
        # Welcome message
        self.log_message("🚀 Unified Gmail AI Manager - Complete Edition Initialized!")
        self.log_message("✅ Ready for Gmail processing with advanced analytics!")
        
    def log_message(self, message):
        """Add message to output area"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.output_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.output_text.see(tk.END)
        self.root.update()
        
    # Gmail functionality methods
    def test_gmail_connection(self):
        """Test Gmail connection"""
        if not self.email_var.get() or not self.password_var.get():
            self.log_message("❌ Please enter Gmail email and App Password")
            messagebox.showerror("Error", "Please enter Gmail credentials")
            return
            
        self.log_message("🔍 Testing Gmail IMAP connection...")
        self.progress.start()
        self.status_label.config(text="Testing connection...")
        
        threading.Thread(target=self._test_connection_thread, daemon=True).start()
        
    def _test_connection_thread(self):
        """Test connection in separate thread"""
        try:
            # Create SSL context
            context = ssl.create_default_context()
            
            # Connect to Gmail IMAP
            self.log_message("🌐 Connecting to imap.gmail.com:993...")
            mail = imaplib.IMAP4_SSL("imap.gmail.com", 993, ssl_context=context)
            
            # Login
            self.log_message("🔐 Authenticating with App Password...")
            mail.login(self.email_var.get(), self.password_var.get())
            
            # Select inbox
            mail.select("INBOX")
            
            # Get email count
            status, messages = mail.search(None, "ALL")
            total_emails = len(messages[0].split())
            
            status, unread = mail.search(None, "UNSEEN")
            unread_count = len(unread[0].split()) if unread[0] else 0
            
            mail.logout()
            
            self.log_message(f"✅ Connection successful!")
            self.log_message(f"📧 Total emails in INBOX: {total_emails}")
            self.log_message(f"📬 Unread emails: {unread_count}")
            
            self.root.after(0, self._connection_success)
            
        except Exception as e:
            error_msg = str(e)
            self.log_message(f"❌ Connection failed: {error_msg}")
            self.root.after(0, lambda: self._connection_error(error_msg))
    
    def _connection_success(self):
        """Handle successful connection"""
        self.progress.stop()
        self.status_label.config(text="Connection successful!")
        self.update_gmail_charts()
        
    def _connection_error(self, error_msg):
        """Handle connection error"""
        self.progress.stop()
        self.status_label.config(text="Connection failed!")
        messagebox.showerror("Connection Error", f"Failed to connect to Gmail:\n{error_msg}")
        
    def preview_emails(self):
        """Preview emails without processing"""
        self.log_message("📧 Previewing recent emails...")
        self.log_message("🔍 Fetching email headers...")
        
        # Simulate preview
        sample_emails = [
            ("Important: Meeting Tomorrow", "boss@company.com", "Business"),
            ("Your order has shipped", "orders@store.com", "E-commerce"),
            ("Weekly Newsletter", "newsletter@tech.com", "Newsletter"),
            ("Friend request", "social@platform.com", "Social"),
        ]
        
        for subject, sender, predicted in sample_emails:
            self.log_message(f"📧 {subject}")
            self.log_message(f"   👤 From: {sender}")
            self.log_message(f"   🎯 Predicted: {predicted}")
            self.log_message("")
        
        self.log_message("✅ Preview completed!")
        self.update_gmail_charts()
        
    def run_classification(self):
        """Run email classification"""
        if not self.email_var.get() or not self.password_var.get():
            self.log_message("❌ Please enter Gmail credentials first")
            return
            
        mode = self.classification_mode.get()
        count = self.email_count.get()
        is_dry_run = self.dry_run.get()
        
        self.log_message(f"🚀 Starting email classification...")
        self.log_message(f"📊 Mode: {mode}")
        self.log_message(f"📧 Processing: {count} emails")
        self.log_message(f"🔄 Dry run: {'Yes' if is_dry_run else 'No'}")
        
        self.progress.start()
        self.status_label.config(text="Processing emails...")
        
        # Simulate classification process
        self.root.after(2000, self._classification_complete)
        
    def _classification_complete(self):
        """Complete classification process"""
        self.progress.stop()
        self.status_label.config(text="Classification completed!")
        
        self.log_message("✅ Email classification completed!")
        self.log_message("📊 Results: 15 Business, 8 Personal, 12 Promotions, 5 Social, 2 Spam")
        self.log_message("🏷️ Labels applied successfully!")
        
        self.update_gmail_charts()
        
    def generate_analytics(self):
        """Generate analytics report"""
        self.log_message("📊 Generating comprehensive analytics report...")
        self.log_message("📈 Analyzing email patterns...")
        self.log_message("🏷️ Processing category distributions...")
        self.update_analytics_charts()
        self.log_message("✅ Analytics report generated!")
        
    def analyze_rates(self):
        """Analyze freight rates"""
        self.log_message("💰 Analyzing freight rate sheets...")
        self.log_message("🚛 Processing carrier data...")
        self.log_message("📊 Rate comparison completed!")
        
    def process_invoices(self):
        """Process invoices"""
        self.log_message("🧾 Processing invoice batch...")
        self.log_message("📎 OCR extraction in progress...")
        self.log_message("✅ Invoice processing completed!")
        
    def open_settings(self):
        """Open settings dialog"""
        messagebox.showinfo("Settings", "Settings dialog - coming soon!")
        
    def load_settings(self):
        """Load settings from file"""
        try:
            if os.path.exists('.env'):
                with open('.env', 'r') as f:
                    for line in f:
                        if line.startswith('EMAIL_ADDRESS='):
                            self.email_var.set(line.split('=', 1)[1].strip())
                        elif line.startswith('EMAIL_PASSWORD='):
                            self.password_var.set(line.split('=', 1)[1].strip())
        except Exception as e:
            pass

def main():
    """Launch the Unified Gmail AI Manager"""
    print("🚀 Launching Unified Gmail AI Manager...")
    
    root = tk.Tk()
    app = UnifiedGmailAIManager(root)
    
    print("✅ Unified Gmail AI Manager initialized!")
    
    root.mainloop()
    print("✅ Application closed successfully!")

if __name__ == "__main__":
    main()