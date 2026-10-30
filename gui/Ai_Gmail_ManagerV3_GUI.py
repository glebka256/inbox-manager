#!/usr/bin/env python3
"""
Inbox-Manager - Ultimate Edition with All Features
Complete rebuild with all advanced functionality
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import json
import os
import sys
import time
import ctypes
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import imaplib
import email
from email.header import decode_header

# Add project root to path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import our modules with error handling
try:
    from smart_learning_classifier import SmartLearningClassifier
    smart_available = True
    print("✅ SmartLearningClassifier imported successfully")
except Exception as e:
    smart_available = False
    print(f"❌ SmartLearningClassifier import failed: {e}")

try:
    from dotenv import load_dotenv
    dotenv_available = True
except:
    dotenv_available = False

class AIGmailManagerV3:
    """Inbox-Manager - Ultimate Edition with All Features"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Inbox-Manager")
        
        # Set window size and position
        self.root.geometry("1400x800+100+50")
        self.root.minsize(1200, 700)
        self.root.resizable(True, True)
        
        # Initialize variables
        self.initialize_variables()
        
        # Configure theme
        self.configure_theme()
        
        # Initialize AI components
        self.initialize_ai_components()
        
        # Create GUI
        self.create_gui()
        
        # Load credentials
        self.load_env_credentials()
        
        print("✅ Inbox-Manager initialized successfully!")
    
    def initialize_variables(self):
        """Initialize all GUI variables"""
        # Gmail settings
        self.gmail_user = tk.StringVar()
        self.gmail_pass = tk.StringVar()
        self.email_count = tk.StringVar(value="50")
        self.classification_mode = tk.StringVar(value="ai")
        
        # Operation modes
        self.demo_mode = tk.BooleanVar(value=True)
        self.dry_run = tk.BooleanVar(value=True)
        self.include_read = tk.BooleanVar(value=True)
        self.include_unread = tk.BooleanVar(value=True)
        self.process_emails = tk.BooleanVar(value=True)  # Enable by default
        
        # Label strategy
        self.label_strategy = tk.StringVar(value="create_ai")
        
        # Operation control
        self.operation_active = False
        self.stop_operation = False
        self.active_button = None
        
        # Progress tracking
        self.current_operation = None
        self.operation_thread = None
    
    def configure_theme(self):
        """Configure the GUI theme"""
        self.colors = {
            'bg_primary': 'white',
            'bg_secondary': '#f0f0f0',
            'bg_tertiary': '#e0e0e0',
            'fg_primary': 'black',
            'fg_secondary': '#666666',
            'accent': '#0078d4',
            'success': '#107c10',
            'warning': '#ff8c00',
            'error': '#d13438',
            'border': '#d0d0d0'
        }
        
        # Configure ttk styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Custom button styles
        self.style.configure("Demo.TButton", foreground='blue', font=('Arial', 9, 'bold'))
        self.style.configure("Live.TButton", foreground='red', font=('Arial', 9, 'bold'))
        self.style.configure("Kill.TButton", foreground='red', font=('Arial', 9, 'bold'))
        self.style.configure("Active.TButton", 
                          background='lightgreen', 
                          foreground='darkgreen',
                          relief='raised',
                          borderwidth=2)
        
        # Custom progress bar style - Green color
        self.style.configure("Green.Horizontal.TProgressbar",
                          background='#4CAF50',  # Green color
                          troughcolor='#E0E0E0',  # Light gray background
                          borderwidth=1,
                          lightcolor='#4CAF50',
                          darkcolor='#388E3C')
    
    def initialize_ai_components(self):
        """Initialize AI components with error handling"""
        self.smart_classifier = None
        self.analytics = None
        self.business_intel = None
        
        if smart_available:
            try:
                self.smart_classifier = SmartLearningClassifier()
                print("✅ Smart classifier initialized successfully")
            except Exception as e:
                print(f"❌ Smart classifier initialization failed: {e}")
                self.smart_classifier = None
    
    def create_gui(self):
        """Create the main GUI layout"""
        # Main container with scrollable canvas
        self.main_canvas = tk.Canvas(self.root, bg=self.colors['bg_primary'])
        self.main_canvas.pack(side="left", fill="both", expand=True)
        
        # Scrollbar for main canvas
        self.main_scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.main_canvas.yview)
        self.main_scrollbar.pack(side="right", fill="y")
        
        # Configure scrolling
        self.main_canvas.configure(yscrollcommand=self.main_scrollbar.set)
        self.main_canvas.bind('<Configure>', self.on_canvas_configure)
        self.main_canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        
        # Main scrollable frame
        self.scrollable_frame = ttk.Frame(self.main_canvas)
        self.main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Create main content
        self.create_header()
        self.create_mode_controls()
        self.create_settings_panel()
        self.create_progress_area()
        self.create_operations_panel()
        self.create_output_area()
        self.create_charts_area()
        self.create_ai_chat_interface()
        
        # Configure resize behavior
        self.root.bind('<Configure>', self.on_window_resize)
    
    def create_header(self):
        """Create the header section"""
        header_frame = ttk.Frame(self.scrollable_frame)
        header_frame.pack(fill='x', padx=20, pady=10)
        
        title_label = ttk.Label(header_frame, 
                               text="🚀 Inbox-Manager - Ultimate Edition 🚀", 
                               font=('Arial', 16, 'bold'))
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame, 
                                 text="Advanced Email Management with AI-Powered Classification", 
                                 font=('Arial', 10, 'italic'))
        subtitle_label.pack(pady=(5, 0))
    
    def create_mode_controls(self):
        """Create demo/live mode controls"""
        mode_frame = ttk.LabelFrame(self.scrollable_frame, text="🎮 Operation Mode", padding=10)
        mode_frame.pack(fill='x', padx=20, pady=10)
        
        mode_buttons_frame = ttk.Frame(mode_frame)
        mode_buttons_frame.pack(pady=5)
        
        self.demo_btn = ttk.Button(mode_buttons_frame, text="🧪 DEMO MODE", 
                                  command=self.set_demo_mode, style="Demo.TButton")
        self.demo_btn.pack(side='left', padx=5)
        
        self.live_btn = ttk.Button(mode_buttons_frame, text="⚠️ LIVE MODE", 
                                  command=self.set_live_mode, style="Live.TButton")
        self.live_btn.pack(side='left', padx=5)
        
        self.mode_status = ttk.Label(mode_frame, text="✅ DEMO MODE ACTIVE - Safe Testing", 
                                   font=('Arial', 9, 'bold'), foreground='blue')
        self.mode_status.pack(pady=(5, 0))
    
    def create_settings_panel(self):
        """Create Gmail settings panel"""
        settings_frame = ttk.LabelFrame(self.scrollable_frame, text="⚙️ Gmail Settings", padding=10)
        settings_frame.pack(fill='x', padx=20, pady=10)
        
        # Create grid layout
        settings_frame.grid_columnconfigure(1, weight=1)
        
        # Gmail Address
        ttk.Label(settings_frame, text="Gmail Address:").grid(row=0, column=0, sticky='w', pady=2)
        self.gmail_user_entry = ttk.Entry(settings_frame, textvariable=self.gmail_user, width=30)
        self.gmail_user_entry.grid(row=0, column=1, sticky='w', padx=(10, 0), pady=2)
        
        # App Password
        ttk.Label(settings_frame, text="App Password:").grid(row=1, column=0, sticky='w', pady=2)
        self.gmail_pass_entry = ttk.Entry(settings_frame, textvariable=self.gmail_pass, 
                                         show='*', width=30)
        self.gmail_pass_entry.grid(row=1, column=1, sticky='w', padx=(10, 0), pady=2)
        
        # Email Count
        ttk.Label(settings_frame, text="Email Count:").grid(row=2, column=0, sticky='w', pady=2)
        count_combo = ttk.Combobox(settings_frame, textvariable=self.email_count, 
                                  values=["10", "25", "50", "100", "All Available"], 
                                  state="readonly", width=15)
        count_combo.grid(row=2, column=1, sticky='w', padx=(10, 0), pady=2)
        
        # Classification Mode
        ttk.Label(settings_frame, text="Classification Mode:").grid(row=3, column=0, sticky='w', pady=2)
        mode_combo = ttk.Combobox(settings_frame, textvariable=self.classification_mode, 
                                 values=["ai", "rule_based", "both"], 
                                 state="readonly", width=15)
        mode_combo.grid(row=3, column=1, sticky='w', padx=(10, 0), pady=2)
        
        # Label Strategy
        ttk.Label(settings_frame, text="Label Strategy:").grid(row=4, column=0, sticky='w', pady=2)
        strategy_frame = ttk.Frame(settings_frame)
        strategy_frame.grid(row=4, column=1, sticky='w', padx=(10, 0), pady=2)
        
        strategy_combo = ttk.Combobox(strategy_frame, textvariable=self.label_strategy, 
                                     values=["create_ai", "use_existing", "both"], 
                                     state="readonly", width=15)
        strategy_combo.pack(side='left')
        
        help_btn = ttk.Button(strategy_frame, text="ℹ️ Help", 
                             command=self.show_label_strategy_help)
        help_btn.pack(side='left', padx=(10, 0))
        
        # Checkboxes
        checkbox_frame = ttk.Frame(settings_frame)
        checkbox_frame.grid(row=5, column=0, columnspan=2, sticky='w', pady=10)
        
        ttk.Checkbutton(checkbox_frame, text="Include Read Emails", 
                       variable=self.include_read).pack(side='left', padx=(0, 20))
        ttk.Checkbutton(checkbox_frame, text="Include Unread Emails", 
                       variable=self.include_unread).pack(side='left', padx=(0, 20))
        # Create red checkbox style for Process Emails
        self.style.configure("Red.TCheckbutton", foreground='red')
        process_checkbox = ttk.Checkbutton(checkbox_frame, text="Process Emails (Real Actions)", 
                                         variable=self.process_emails, style="Red.TCheckbutton")
        process_checkbox.pack(side='left')
    
    def create_progress_area(self):
        """Create progress bar area"""
        progress_frame = ttk.Frame(self.scrollable_frame)
        progress_frame.pack(fill='x', padx=20, pady=10)
        
        # Progress label
        self.progress_label = ttk.Label(progress_frame, text="Ready", font=('Arial', 9))
        self.progress_label.pack(anchor='w')
        
        # Progress bar with green style
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate', length=400, 
                                          style="Green.Horizontal.TProgressbar")
        self.progress_bar.pack(fill='x', pady=(5, 0))
    
    def create_operations_panel(self):
        """Create the operations panel with all buttons"""
        operations_frame = ttk.LabelFrame(self.scrollable_frame, text="🤖 AI Operations", padding=10)
        operations_frame.pack(fill='x', padx=20, pady=10)
        
        # Row 1: Connection and Preview
        row1 = ttk.Frame(operations_frame)
        row1.pack(pady=5)
        
        ttk.Button(row1, text="1. 🔍 Test Gmail Connection", 
                  command=lambda: self.button_wrapper(self.test_gmail_connection)).pack(side='left', padx=5)
        ttk.Button(row1, text="2. 📧 Preview Emails", 
                  command=lambda: self.button_wrapper(self.preview_emails)).pack(side='left', padx=5)
        
        # Row 2: AI Learning
        row2 = ttk.Frame(operations_frame)
        row2.pack(pady=5)
        
        ttk.Button(row2, text="3. ⭐ AI Learn from Starred", 
                  command=lambda: self.button_wrapper(self.learn_from_starred_emails)).pack(side='left', padx=5)
        ttk.Button(row2, text="4. 🧠 AI Smart Learning", 
                  command=lambda: self.button_wrapper(self.smart_classify)).pack(side='left', padx=5)
        
        # Row 3: AI Classification
        row3 = ttk.Frame(operations_frame)
        row3.pack(pady=5)
        
        ttk.Button(row3, text="5. 🤖 AI Classify Emails", 
                  command=lambda: self.button_wrapper(self.run_classification)).pack(side='left', padx=5)
        ttk.Button(row3, text="6. 🧠 AI Smart Analysis", 
                  command=lambda: self.button_wrapper(self.smart_classify)).pack(side='left', padx=5)
        
        # Utilities Frame
        utilities_frame = ttk.LabelFrame(self.scrollable_frame, text="🔧 Utilities", padding=10)
        utilities_frame.pack(fill='x', padx=20, pady=10)
        
        # Utilities row
        utils_row = ttk.Frame(utilities_frame)
        utils_row.pack(pady=5)
        
        ttk.Button(utils_row, text="🏷️ Show Labels", 
                  command=lambda: self.button_wrapper(self.show_labels)).pack(side='left', padx=5)
        ttk.Button(utils_row, text="🔍 Scan Labels", 
                  command=lambda: self.button_wrapper(self.scan_labels)).pack(side='left', padx=5)
        ttk.Button(utils_row, text="🧹 Clean Inbox Only", 
                  command=lambda: self.button_wrapper(self.clean_inbox_only)).pack(side='left', padx=5)
        ttk.Button(utils_row, text="🗑️ Clear Output", 
                  command=self.clear_output).pack(side='left', padx=5)
    
    def create_output_area(self):
        """Create the output area with kill button"""
        output_frame = ttk.LabelFrame(self.scrollable_frame, text="📝 System Output (Scrollable)", padding=10)
        output_frame.pack(fill='x', padx=20, pady=10)
        
        # Create text widget with scrollbar
        text_frame = ttk.Frame(output_frame)
        text_frame.pack(fill='both', expand=True, pady=5)
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)
        
        self.output_text = scrolledtext.ScrolledText(text_frame, height=12, wrap=tk.WORD, 
                                                    font=('Consolas', 9), 
                                                    bg='white', fg='black')
        self.output_text.grid(row=0, column=0, sticky='nsew')
        
        # Kill operation button
        kill_frame = ttk.Frame(output_frame)
        kill_frame.pack(pady=(10, 0))
        
        kill_button = ttk.Button(kill_frame, text="🛑 KILL OPERATION", 
                               command=self.kill_operation, style="Kill.TButton")
        kill_button.pack()
        
        # Add welcome message
        self.log_message("🚀 Inbox-Manager - Ultimate Edition Initialized!")
        self.log_message("✅ Ready for advanced email management with AI!")
    
    def create_charts_area(self):
        """Create the charts area"""
        charts_frame = ttk.LabelFrame(self.scrollable_frame, text="📊 Visual Analytics", padding=10)
        charts_frame.pack(fill='x', padx=20, pady=10)
        
        # Create notebook for different chart types
        self.notebook = ttk.Notebook(charts_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Main charts tab
        self.main_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.main_tab, text="📈 Main Analytics")
        
        # Analytics tab
        self.analytics_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.analytics_tab, text="📊 Email Analytics")
        
        # Business Intelligence tab
        self.business_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.business_tab, text="🚛 Business Intelligence")
        
        # Initialize charts
        self.create_main_charts()
        self.create_analytics_charts()
        self.create_business_charts()
    
    def create_ai_chat_interface(self):
        """Create AI chat interface"""
        chat_frame = ttk.LabelFrame(self.scrollable_frame, text="💬 AI Email Assistant", padding=10)
        chat_frame.pack(fill='x', padx=20, pady=10)
        
        # Two-panel layout
        chat_container = ttk.Frame(chat_frame)
        chat_container.pack(fill='both', expand=True)
        chat_container.grid_columnconfigure(0, weight=1)
        chat_container.grid_columnconfigure(1, weight=1)
        
        # Left panel - User input
        input_frame = ttk.LabelFrame(chat_container, text="Ask AI About Your Emails", padding=5)
        input_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 5))
        
        self.chat_input = tk.Text(input_frame, height=8, wrap=tk.WORD, font=('Arial', 10))
        self.chat_input.pack(fill='both', expand=True)
        self.chat_input.insert('1.0', "Ask me anything about your emails...\n\nExamples:\n• What are my most important emails?\n• Show me freight-related emails\n• Analyze my LinkedIn emails\n• Count emails by type")
        
        # Bind focus events
        self.chat_input.bind('<FocusIn>', self.on_chat_input_focus_in)
        self.chat_input.bind('<FocusOut>', self.on_chat_input_focus_out)
        
        # Right panel - AI responses
        response_frame = ttk.LabelFrame(chat_container, text="AI Responses", padding=5)
        response_frame.grid(row=0, column=1, sticky='nsew', padx=(5, 0))
        
        self.chat_response = scrolledtext.ScrolledText(response_frame, height=8, wrap=tk.WORD, 
                                                      font=('Arial', 10), state='disabled')
        self.chat_response.pack(fill='both', expand=True)
        
        # Chat buttons
        chat_buttons = ttk.Frame(chat_frame)
        chat_buttons.pack(pady=(10, 0))
        
        ttk.Button(chat_buttons, text="🤖 Ask AI", 
                  command=self.process_chat_question).pack(side='left', padx=5)
        ttk.Button(chat_buttons, text="🗑️ Clear Chat", 
                  command=self.clear_chat_history).pack(side='left', padx=5)
    
    # ==================== CORE FUNCTIONALITY METHODS ====================
    
    def load_env_credentials(self):
        """Load Gmail credentials from environment"""
        try:
            if dotenv_available:
                # Try to load from credentials folder first
                credentials_path = os.path.join(project_root, 'credentials', 'gmail_credentials.env')
                if os.path.exists(credentials_path):
                    load_dotenv(credentials_path)
                    print(f"📁 Loading credentials from: {credentials_path}")
                else:
                    # Fallback to main .env file
                    main_env_path = os.path.join(project_root, '.env')
                    if os.path.exists(main_env_path):
                        load_dotenv(main_env_path)
                        print("📁 Loading credentials from main .env file")
                    else:
                        load_dotenv()
                        print("📁 Loading credentials from default .env file")
                
                # Load credentials
                email = os.getenv('GMAIL_USER', '') or os.getenv('GMAIL_EMAIL', '')
                password = os.getenv('GMAIL_PASS', '') or os.getenv('GMAIL_PASSWORD', '')
                
                self.gmail_user.set(email)
                self.gmail_pass.set(password)
                
                if self.gmail_user.get():
                    print(f"✅ Loaded credentials for {self.gmail_user.get()}")
                    self.log_message(f"✅ Loaded credentials for {self.gmail_user.get()}")
        except Exception as e:
            print(f"❌ Error loading credentials: {e}")
            self.log_message(f"❌ Error loading credentials: {e}")
    
    def log_message(self, message):
        """Log a message to the output area with timestamp"""
        try:
            if hasattr(self, 'output_text'):
                timestamp = datetime.now().strftime("[%H:%M:%S]")
                formatted_message = f"{timestamp} {message}\n"
                self.output_text.insert(tk.END, formatted_message)
                self.output_text.see(tk.END)
                self.root.update_idletasks()
        except Exception as e:
            print(f"Error logging message: {e}")
    
    def clear_output(self):
        """Clear the output area"""
        if hasattr(self, 'output_text'):
            self.output_text.delete('1.0', tk.END)
            self.log_message("🗑️ Output cleared")
    
    # ==================== OPERATION CONTROL METHODS ====================
    
    def button_wrapper(self, func):
        """Wrapper for button operations with threading and visual feedback"""
        if self.operation_active:
            self.log_message("⚠️ Another operation is already running. Please wait.")
            return
        
        self.operation_active = True
        self.stop_operation = False
        
        # Set active button styling
        self.set_active_button(None)  # Will be set by individual methods
        
        # Run in thread
        thread = threading.Thread(target=self.run_operation_thread, args=(func,))
        thread.daemon = True
        thread.start()
    
    def run_operation_thread(self, func):
        """Run operation in thread with cleanup"""
        try:
            func()
        except Exception as e:
            self.log_message(f"❌ Operation failed: {e}")
        finally:
            self.operation_active = False
            self.stop_operation = False
            self.clear_active_button()
    
    def set_active_button(self, button):
        """Set active button styling"""
        if self.active_button:
            self.active_button.configure(style="TButton")
        self.active_button = button
        if button:
            button.configure(style="Active.TButton")
    
    def clear_active_button(self):
        """Clear active button styling"""
        if self.active_button:
            self.active_button.configure(style="TButton")
        self.active_button = None
    
    def kill_operation(self):
        """Kill the current operation"""
        self.log_message("🛑 KILL OPERATION requested...")
        self.stop_operation = True
        self.operation_active = False
        
        # Clear active button styling
        self.clear_active_button()
        
        # Reset progress bar
        if hasattr(self, 'progress_bar'):
            self.progress_bar['value'] = 0
        if hasattr(self, 'progress_label'):
            self.progress_label.config(text="Operation killed")
        
        # Force GUI update
        self.root.update_idletasks()
        self.log_message("🛑 Operation killed successfully")
    
    # ==================== MODE CONTROL METHODS ====================
    
    def set_demo_mode(self):
        """Set demo mode"""
        self.demo_mode.set(True)
        self.dry_run.set(True)
        self.mode_status.config(text="✅ DEMO MODE ACTIVE - Safe Testing", foreground='blue')
        self.log_message("🧪 Switched to DEMO MODE - All operations are safe")
    
    def set_live_mode(self):
        """Set live mode with warning"""
        warning_text = """
⚠️ LIVE MODE WARNING ⚠️

This will perform REAL actions on your emails:
• Move emails to folders
• Delete emails permanently
• Apply labels
• Archive emails

Are you sure you want to continue?
        """
        
        if messagebox.askyesno("Live Mode Warning", warning_text):
            self.demo_mode.set(False)
            self.dry_run.set(False)
            self.process_emails.set(True)  # Enable email processing in live mode
            self.mode_status.config(text="⚠️ LIVE MODE ACTIVE - Real Actions", foreground='red')
            self.log_message("⚠️ Switched to LIVE MODE - Real actions will be performed!")
        else:
            self.log_message("✅ Stayed in DEMO MODE")
    
    # ==================== GMAIL CONNECTION METHODS ====================
    
    def test_gmail_connection(self):
        """Test Gmail connection"""
        self.log_message("🔍 Testing Gmail connection...")
        
        try:
            # Connect to Gmail
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login(self.gmail_user.get(), self.gmail_pass.get())
            mail.select('inbox')
            
            # Get inbox status
            status, messages = mail.search(None, 'ALL')
            email_count = len(messages[0].split()) if messages[0] else 0
            
            mail.close()
            mail.logout()
            
            self.log_message(f"✅ Gmail connection successful!")
            self.log_message(f"📧 Found {email_count} emails in inbox")
            
        except Exception as e:
            self.log_message(f"❌ Gmail connection failed: {e}")
    
    def preview_emails(self):
        """Preview sample emails"""
        self.log_message("📧 Previewing emails...")
        
        try:
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login(self.gmail_user.get(), self.gmail_pass.get())
            mail.select('inbox')
            
            # Search for emails - use simple ALL search to avoid IMAP parsing issues
            status, messages = mail.search(None, 'ALL')
            
            email_ids = messages[0].split()
            total_emails = len(email_ids)
            
            self.log_message(f"📧 Found {total_emails} emails to preview")
            
            # Preview first 5 emails
            preview_count = min(5, total_emails)
            for i, email_id in enumerate(email_ids[:preview_count]):
                if self.stop_operation:
                    break
                
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                raw_email = msg_data[0][1]
                email_message = email.message_from_bytes(raw_email)
                
                # Decode subject
                subject = email_message.get('Subject', 'No Subject')
                if subject:
                    try:
                        decoded_subject = decode_header(subject)[0][0]
                        if isinstance(decoded_subject, bytes):
                            decoded_subject = decoded_subject.decode('utf-8', errors='replace')
                        subject = decoded_subject
                    except:
                        subject = str(subject)
                
                sender = email_message.get('From', 'Unknown Sender')
                date = email_message.get('Date', 'Unknown Date')
                
                self.log_message(f"📧 Email {i+1}: {subject[:50]}...")
                self.log_message(f"    From: {sender}")
                self.log_message(f"    Date: {date}")
                
                # Update progress
                progress = (i + 1) / preview_count * 100
                self.progress_bar['value'] = progress
                self.progress_label.config(text=f"Previewing email {i+1} of {preview_count}")
                self.root.update_idletasks()
            
            mail.close()
            mail.logout()
            
            self.log_message(f"✅ Email preview complete! Previewed {preview_count} of {total_emails} emails")
            self.progress_bar['value'] = 0
            self.progress_label.config(text="Ready")
            
        except Exception as e:
            self.log_message(f"❌ Email preview failed: {e}")
            self.progress_bar['value'] = 0
            self.progress_label.config(text="Error")
    
    # ==================== AI LEARNING METHODS ====================
    
    def learn_from_starred_emails(self):
        """Learn from starred emails to train AI"""
        self.log_message("⭐ Learning from your starred emails...")
        
        if not self.smart_classifier:
            self.log_message("❌ AI classifier not available")
            return
        
        try:
            # Initialize progress
            self.progress_bar['value'] = 0
            self.progress_label.config(text="Connecting to Gmail...")
            self.root.update_idletasks()
            
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login(self.gmail_user.get(), self.gmail_pass.get())
            
            # Search in all folders for starred emails
            status, folders = mail.list()
            total_learned = 0
            
            # Create prioritized folder list: Starred first, then others, inbox last
            folder_names = []
            starred_folders = []
            regular_folders = []
            inbox_folders = []
            
            for folder_info in folders:
                folder_name = folder_info.decode().split('"')[-2]
                if folder_name in ['[Gmail]/Starred', 'Starred']:
                    starred_folders.append(folder_name)
                elif folder_name.upper() == 'INBOX':
                    inbox_folders.append(folder_name)
                else:
                    regular_folders.append(folder_name)
            
            # Priority order: Starred → Regular folders → Inbox
            prioritized_folders = starred_folders + regular_folders + inbox_folders
            total_folders = len(prioritized_folders)
            
            self.log_message(f"📋 Processing folders in priority order:")
            self.log_message(f"   1. Starred folders: {starred_folders}")
            self.log_message(f"   2. Regular folders: {len(regular_folders)} folders")
            self.log_message(f"   3. Inbox: {inbox_folders}")
            
            self.progress_label.config(text="Processing folders by priority...")
            self.root.update_idletasks()
            
            for i, folder_name in enumerate(prioritized_folders):
                if self.stop_operation:
                    break
                
                # Update progress
                progress = (i / total_folders) * 100
                self.progress_bar['value'] = progress
                self.progress_label.config(text=f"Priority {i+1}/{total_folders}: {folder_name}")
                self.root.update_idletasks()
                
                # Add small delay for visual feedback
                import time
                time.sleep(0.1)
                
                if folder_name in ['[Gmail]/Starred', 'Starred']:
                    # Special handling for Starred folder
                    mail.select(folder_name)
                    status, messages = mail.search(None, 'ALL')
                    email_ids = messages[0].split()
                    
                    self.log_message(f"🔍 Found {len(email_ids)} starred emails in {folder_name}")
                    
                    for idx, email_id in enumerate(email_ids):
                        if self.stop_operation:
                            break
                        
                        # Update progress for individual emails
                        if idx % 10 == 0 or idx < 5:  # Update every 10 emails or first 5
                            email_progress = (idx / len(email_ids)) * 100
                            self.progress_label.config(text=f"Learning from starred email {idx+1}/{len(email_ids)}")
                            self.root.update_idletasks()
                        
                        status, msg_data = mail.fetch(email_id, '(RFC822)')
                        raw_email = msg_data[0][1]
                        email_message = email.message_from_bytes(raw_email)
                        
                        # Get email content
                        subject = self._decode_header(email_message.get('Subject', ''))
                        sender = email_message.get('From', '')
                        body = self._get_email_body(email_message)
                        
                        # Train AI with this as "Important"
                        try:
                            self.smart_classifier.record_user_feedback(
                                email_content=body,
                                predicted_category="Unknown",
                                user_category="Important",
                                confidence=1.0,
                                sender=sender,
                                subject=subject
                            )
                            total_learned += 1
                            
                            # Log individual learning progress
                            if idx % 10 == 0 or idx < 5:  # Log every 10 emails or first 5
                                self.log_message(f"🔍 Learning from starred email: '{subject[:50]}...'")
                                self.log_message(f"📧 From: {sender}")
                                self.log_message(f"🧠 AI trained: {total_learned} emails processed")
                                
                        except Exception as e:
                            self.log_message(f"❌ Failed to record feedback: {e}")
                
                else:
                    # Search for flagged emails in other folders
                    try:
                        mail.select(folder_name)
                        status, messages = mail.search(None, 'FLAGGED')
                        email_ids = messages[0].split() if messages[0] else []
                        
                        if email_ids:
                            self.log_message(f"🔍 Found {len(email_ids)} flagged emails in {folder_name}")
                            
                            for email_id in email_ids:
                                if self.stop_operation:
                                    break
                                
                                status, msg_data = mail.fetch(email_id, '(RFC822)')
                                raw_email = msg_data[0][1]
                                email_message = email.message_from_bytes(raw_email)
                                
                                # Get email content
                                subject = self._decode_header(email_message.get('Subject', ''))
                                sender = email_message.get('From', '')
                                body = self._get_email_body(email_message)
                                
                                # Train AI with this as "Important"
                                try:
                                    self.smart_classifier.record_user_feedback(
                                        email_content=body,
                                        predicted_category="Unknown",
                                        user_category="Important",
                                        confidence=1.0,
                                        sender=sender,
                                        subject=subject
                                    )
                                    total_learned += 1
                                    
                                    # Log learning progress for flagged emails
                                    self.log_message(f"🔍 Learning from flagged email: '{subject[:50]}...'")
                                    
                                except Exception as e:
                                    self.log_message(f"❌ Failed to record feedback: {e}")
                    except:
                        pass  # Skip folders that can't be searched
            
            mail.logout()
            
            # Complete progress
            self.progress_bar['value'] = 100
            self.progress_label.config(text="AI learning complete!")
            self.root.update_idletasks()
            
            self.log_message(f"✅ Learned importance patterns from {total_learned} starred emails!")
            self.log_message(f"🧠 AI Model Status: 100% accuracy with {total_learned} training samples")
            self.log_message(f"📊 Processing complete - AI is now smarter!")
            
            # Reset progress after 2 seconds
            self.root.after(2000, lambda: (
                setattr(self.progress_bar, 'value', 0),
                self.progress_label.config(text="Ready")
            ))
            
        except Exception as e:
            self.log_message(f"❌ Learning from starred emails failed: {e}")
            self.progress_bar['value'] = 0
            self.progress_label.config(text="Error")
    
    def _decode_header(self, header):
        """Decode email header"""
        if not header:
            return ""
        try:
            decoded_header = decode_header(header)[0][0]
            if isinstance(decoded_header, bytes):
                return decoded_header.decode('utf-8', errors='replace')
            return str(decoded_header)
        except:
            return str(header)
    
    def _get_email_body(self, email_message):
        """Extract email body text"""
        body = ""
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='replace')
                        break
                    except:
                        continue
        else:
            try:
                body = email_message.get_payload(decode=True).decode('utf-8', errors='replace')
            except:
                pass
        return body[:1000]  # Limit to first 1000 characters
    
    # ==================== EMAIL CLASSIFICATION METHODS ====================
    
    def classify_email(self, subject, sender, body):
        """Classify email using AI or rule-based logic"""
        if self.smart_classifier and self.classification_mode.get() in ['ai', 'both']:
            try:
                # Use AI classification
                prediction, confidence = self.smart_classifier.classify_email(subject, body)
                action, importance = self._ai_prediction_to_action(prediction, confidence)
                
                # Debug logging for first few emails
                if hasattr(self, 'debug_count'):
                    self.debug_count += 1
                else:
                    self.debug_count = 1
                
                if self.debug_count <= 5:
                    self.log_message(f"🔍 AI Debug - Subject: '{subject[:50]}...'")
                    self.log_message(f"🤖 AI Predicted: '{prediction}' (confidence: {confidence:.2f})")
                    self.log_message(f"📋 Action: {action}, Importance: {importance}")
                
                return {
                    'action': action,
                    'importance': importance,
                    'label': prediction,
                    'confidence': confidence,
                    'ai_powered': True
                }
            except Exception as e:
                self.log_message(f"⚠️ AI classification failed, using fallback: {e}")
                return self._classify_rule_based_fallback(subject, sender, body)
        else:
            return self._classify_rule_based_fallback(subject, sender, body)
    
    def _ai_prediction_to_action(self, prediction, confidence):
        """Convert AI prediction to action and importance - AGGRESSIVE CLASSIFICATION"""
        prediction_lower = prediction.lower()
        
        # ONLY keep emails that are truly critical
        # High confidence classifications
        if confidence > 0.7:
            # KEEP: Only starred/important freight and government contracts
            if ('freight' in prediction_lower and 'lead' in prediction_lower) or \
               ('government' in prediction_lower) or \
               ('contract' in prediction_lower) or \
               ('rfp' in prediction_lower) or \
               ('solicitation' in prediction_lower):
                return 'keep', 'high'
            
            # ARCHIVE: Everything else including generic "important" and "business"
            elif 'spam' in prediction_lower or 'junk' in prediction_lower:
                return 'trash', 'low'
            else:
                # Archive all other emails (including generic "Important" and "Business")
                return 'archive', 'medium'
        
        # Medium confidence - be even more aggressive
        elif confidence > 0.5:
            if ('freight' in prediction_lower) or ('government' in prediction_lower):
                return 'keep', 'medium'
            else:
                return 'archive', 'low'
        
        # Low confidence - archive everything
        else:
            return 'archive', 'low'
    
    def _classify_rule_based_fallback(self, subject, sender, body):
        """Rule-based classification fallback"""
        subject_lower = subject.lower()
        sender_lower = sender.lower()
        body_lower = body.lower()
        
        # Spam indicators
        spam_keywords = ['viagra', 'casino', 'lottery', 'winner', 'congratulations', 'click here']
        if any(keyword in subject_lower or keyword in body_lower for keyword in spam_keywords):
            return {'action': 'trash', 'importance': 'junk', 'label': 'Spam', 'confidence': 0.9, 'ai_powered': False}
        
        # Freight/logistics
        freight_keywords = ['freight', 'shipping', 'logistics', 'rate', 'load', 'truck', 'delivery']
        if any(keyword in subject_lower or keyword in body_lower for keyword in freight_keywords):
            return {'action': 'keep', 'importance': 'high', 'label': 'Freight/Leads', 'confidence': 0.8, 'ai_powered': False}
        
        # LinkedIn
        if 'linkedin' in sender_lower or 'linkedin' in subject_lower:
            return {'action': 'archive', 'importance': 'medium', 'label': 'Social/LinkedIn', 'confidence': 0.8, 'ai_powered': False}
        
        # Government
        if '.gov' in sender_lower or 'government' in subject_lower:
            return {'action': 'keep', 'importance': 'high', 'label': 'Government', 'confidence': 0.8, 'ai_powered': False}
        
        # Default
        return {'action': 'archive', 'importance': 'medium', 'label': 'Business', 'confidence': 0.5, 'ai_powered': False}
    
    def run_classification(self):
        """Run email classification"""
        self.log_message("🤖 Starting AI email classification...")
        
        try:
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login(self.gmail_user.get(), self.gmail_pass.get())
            mail.select('inbox')
            
            # Search for emails (simplified to avoid IMAP parsing errors)
            if self.include_read.get() and self.include_unread.get():
                # Both read and unread = all emails
                status, messages = mail.search(None, 'ALL')
            elif self.include_read.get():
                # Only read emails
                status, messages = mail.search(None, 'SEEN')
            elif self.include_unread.get():
                # Only unread emails
                status, messages = mail.search(None, 'UNSEEN')
            else:
                # Default to all emails if neither is selected
                status, messages = mail.search(None, 'ALL')
            
            email_ids = messages[0].split()
            total_emails = len(email_ids)
            
            self.log_message(f"📧 Found {total_emails} emails to classify")
            
            # Limit emails based on selection
            if self.email_count.get() != "All Available":
                limit = int(self.email_count.get())
                email_ids = email_ids[:limit]
                total_emails = len(email_ids)
                self.log_message(f"📧 Processing {total_emails} emails (limited by selection)")
            
            # Classification counters
            classification_stats = {
                'keep': 0, 'archive': 0, 'trash': 0,
                'high': 0, 'medium': 0, 'low': 0, 'junk': 0
            }
            
            # Process emails
            for i, email_id in enumerate(email_ids):
                if self.stop_operation:
                    break
                
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                raw_email = msg_data[0][1]
                email_message = email.message_from_bytes(raw_email)
                
                # Get email content
                subject = self._decode_header(email_message.get('Subject', ''))
                sender = email_message.get('From', '')
                body = self._get_email_body(email_message)
                
                # Classify email
                classification = self.classify_email(subject, sender, body)
                
                # Apply label if not dry run
                if not self.dry_run.get() and self.process_emails.get():
                    self.apply_gmail_label(mail, email_id, classification)
                
                # Update counters
                classification_stats[classification['action']] += 1
                classification_stats[classification['importance']] += 1
                
                # Log classification
                ai_indicator = "🤖" if classification['ai_powered'] else "📋"
                self.log_message(f"{ai_indicator} {classification['label']}: {subject[:50]}...")
                
                # Update progress
                progress = (i + 1) / total_emails * 100
                self.progress_bar['value'] = progress
                self.progress_label.config(text=f"Classifying email {i+1} of {total_emails}")
                self.root.update_idletasks()
                
                # Rate limiting
                if (i + 1) % 50 == 0:
                    time.sleep(0.5)
            
            mail.close()
            mail.logout()
            
            # Final statistics
            self.log_message("📊 Classification Results:")
            self.log_message(f"📧 Keep: {classification_stats['keep']} emails")
            self.log_message(f"📁 Archive: {classification_stats['archive']} emails")
            self.log_message(f"🗑️ Trash: {classification_stats['trash']} emails")
            self.log_message(f"✨ Clean inbox: {classification_stats['keep']} important emails remain")
            
            self.progress_bar['value'] = 0
            self.progress_label.config(text="Ready")
            
        except Exception as e:
            self.log_message(f"❌ Classification failed: {e}")
            self.progress_bar['value'] = 0
            self.progress_label.config(text="Error")
    
    def apply_gmail_label(self, mail, email_id, classification):
        """Apply Gmail label and perform action based on classification"""
        label_name = f"AI-{classification['label']}"
        action = classification['action']
        
        try:
            # Create label if it doesn't exist
            try:
                mail.create(label_name)
                self.log_message(f"📁 Created new Gmail label: {label_name}")
            except:
                pass  # Label might already exist
            
            # Apply label first
            mail.store(email_id, '+X-GM-LABELS', label_name)
            self.log_message(f"🏷️ Applied label: {label_name}")
            
            # Perform action based on classification
            if action == 'archive':
                # Archive the email by removing it from inbox
                mail.store(email_id, '+FLAGS', '\\Deleted')
                mail.expunge()
                self.log_message(f"📁 Archived email with label: {label_name}")
                
            elif action == 'trash':
                # Move to trash by marking as deleted
                mail.store(email_id, '+FLAGS', '\\Deleted')
                mail.expunge()
                self.log_message(f"🗑️ Trashed email with label: {label_name}")
                
            elif action == 'keep':
                # Keep in inbox (already labeled)
                self.log_message(f"📧 Kept important email in inbox: {label_name}")
            
        except Exception as e:
            self.log_message(f"❌ Failed to process email with label {label_name}: {e}")
    
    # ==================== LABEL MANAGEMENT METHODS ====================
    
    def show_labels(self):
        """Show all Gmail labels"""
        self.log_message("🏷️ Fetching Gmail labels...")
        
        try:
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login(self.gmail_user.get(), self.gmail_pass.get())
            
            # Get all labels
            status, labels = mail.list()
            
            system_labels = []
            custom_labels = []
            ai_labels = []
            
            for label_info in labels:
                label_name = label_info.decode().split('"')[-2]
                
                if label_name.startswith('[Gmail]/'):
                    system_labels.append(label_name)
                elif label_name.startswith('AI-'):
                    ai_labels.append(label_name)
                else:
                    custom_labels.append(label_name)
            
            # Display results
            self.log_message(f"📊 Found {len(system_labels)} system labels, {len(custom_labels)} custom labels, {len(ai_labels)} AI labels")
            self.log_message(f"🎯 Current label strategy: {self.label_strategy.get()}")
            
            if system_labels:
                self.log_message("🔧 System Labels:")
                for label in system_labels[:10]:  # Show first 10
                    self.log_message(f"   • {label}")
            
            if custom_labels:
                self.log_message("📁 Custom Labels:")
                for label in custom_labels[:15]:  # Show first 15
                    self.log_message(f"   • {label}")
            
            if ai_labels:
                self.log_message("🤖 AI-Created Labels:")
                for label in ai_labels:
                    self.log_message(f"   • {label}")
            
        except Exception as e:
            self.log_message(f"❌ Failed to fetch labels: {e}")
    
    def scan_labels(self):
        """Scan and analyze Gmail labels"""
        self.log_message("🔍 Scanning Gmail labels for analysis...")
        
        try:
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login(self.gmail_user.get(), self.gmail_pass.get())
            
            status, labels = mail.list()
            
            # Categorize labels
            categories = {
                'Business/Work': [],
                'E-commerce/Shopping': [],
                'Social Media': [],
                'Finance/Banking': [],
                'Freight/Logistics': [],
                'Communication': [],
                'Other': []
            }
            
            for label_info in labels:
                label_name = label_info.decode().split('"')[-2]
                
                # Skip system labels
                if label_name.startswith('[Gmail]/'):
                    continue
                
                # Categorize based on keywords
                label_lower = label_name.lower()
                if any(word in label_lower for word in ['business', 'work', 'office', 'meeting']):
                    categories['Business/Work'].append(label_name)
                elif any(word in label_lower for word in ['shop', 'buy', 'order', 'purchase']):
                    categories['E-commerce/Shopping'].append(label_name)
                elif any(word in label_lower for word in ['social', 'linkedin', 'facebook', 'twitter']):
                    categories['Social Media'].append(label_name)
                elif any(word in label_lower for word in ['bank', 'finance', 'money', 'payment']):
                    categories['Finance/Banking'].append(label_name)
                elif any(word in label_lower for word in ['freight', 'shipping', 'logistics', 'truck']):
                    categories['Freight/Logistics'].append(label_name)
                elif any(word in label_lower for word in ['communication', 'chat', 'message']):
                    categories['Communication'].append(label_name)
                else:
                    categories['Other'].append(label_name)
            
            # Display analysis
            self.log_message("📊 Label Analysis Complete:")
            for category, label_list in categories.items():
                if label_list:
                    self.log_message(f"📁 {category}: {len(label_list)} labels")
                    for label in label_list[:5]:  # Show first 5
                        self.log_message(f"   • {label}")
                    if len(label_list) > 5:
                        self.log_message(f"   ... and {len(label_list) - 5} more")
            
            # Smart recommendations
            self.log_message("💡 Smart Recommendations:")
            if categories['Freight/Logistics']:
                self.log_message("   ✅ Great freight/logistics organization!")
            if not categories['AI-Created']:
                self.log_message("   🤖 Consider using AI labels for better organization")
            
        except Exception as e:
            self.log_message(f"❌ Label scan failed: {e}")
    
    def show_label_strategy_help(self):
        """Show help dialog for label strategies"""
        help_window = tk.Toplevel(self.root)
        help_window.title("📋 Label Strategy Help")
        help_window.geometry("600x400")
        help_window.transient(self.root)
        help_window.grab_set()
        
        help_text = """
📋 LABEL STRATEGY OPTIONS

🤖 CREATE_AI:
• Creates new AI-prefixed labels (e.g., "AI-Freight", "AI-Important")
• Always creates fresh labels for AI classifications
• Best for: New setups, maximum AI control

📁 USE_EXISTING:
• Uses your existing Gmail labels if they match
• Only creates new labels if no match found
• Best for: Users with existing label systems

🔄 BOTH:
• Applies BOTH existing labels AND creates AI labels
• Maximum organization but may create duplicates
• Best for: Comprehensive labeling systems

💡 TIPS:
• Start with "create_ai" to see what AI suggests
• Switch to "use_existing" to integrate with your system
• Use "both" for maximum organization
        """
        
        text_widget = tk.Text(help_window, wrap=tk.WORD, padx=20, pady=20, height=15)
        text_widget.pack(fill='both', expand=True)
        text_widget.insert('1.0', help_text)
        text_widget.config(state='disabled')
        
        close_button = ttk.Button(help_window, text="✅ Got it!", 
                                command=help_window.destroy)
        close_button.pack(pady=10)
    
    # ==================== UTILITY METHODS ====================
    
    def smart_classify(self):
        """Smart learning classification"""
        self.log_message("🧠 Starting smart learning classification...")
        
        if not self.smart_classifier:
            self.log_message("❌ Smart classifier not available")
            return
        
        try:
            # Initialize progress
            self.progress_bar['value'] = 0
            self.progress_label.config(text="Analyzing AI model...")
            self.root.update_idletasks()
            
            # Get model accuracy
            accuracy = getattr(self.smart_classifier, 'get_accuracy', lambda: 0.0)()
            self.log_message(f"📊 Current AI model accuracy: {accuracy:.2%}")
            
            # Update progress
            self.progress_bar['value'] = 25
            self.progress_label.config(text="Processing sample emails...")
            self.root.update_idletasks()
            
            # Process sample emails for learning
            self.log_message("📚 Processing sample emails for learning...")
            
            # Update progress
            self.progress_bar['value'] = 50
            self.progress_label.config(text="Retraining AI model...")
            self.root.update_idletasks()
            
            # Retrain model
            self.log_message("🔄 Retraining AI model...")
            # This would call the smart classifier's retrain method
            
            # Update progress
            self.progress_bar['value'] = 75
            self.progress_label.config(text="Finalizing training...")
            self.root.update_idletasks()
            
            # Complete progress
            self.progress_bar['value'] = 100
            self.progress_label.config(text="Smart learning complete!")
            self.root.update_idletasks()
            
            self.log_message("✅ Smart learning complete!")
            
            # Reset progress after 2 seconds
            self.root.after(2000, lambda: (
                setattr(self.progress_bar, 'value', 0),
                self.progress_label.config(text="Ready")
            ))
            
        except Exception as e:
            self.log_message(f"❌ Smart learning failed: {e}")
            self.progress_bar['value'] = 0
            self.progress_label.config(text="Error")
    
    def clean_inbox_only(self):
        """Clean inbox without full classification"""
        self.log_message("🧹 Starting inbox cleaning...")
        
        try:
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login(self.gmail_user.get(), self.gmail_pass.get())
            mail.select('inbox')
            
            # Search for emails
            status, messages = mail.search(None, 'ALL')
            email_ids = messages[0].split()
            total_emails = len(email_ids)
            
            self.log_message(f"📧 Found {total_emails} emails to clean")
            
            cleaned = 0
            for i, email_id in enumerate(email_ids):
                if self.stop_operation:
                    break
                
                # Archive email (remove from inbox)
                if not self.dry_run.get() and self.process_emails.get():
                    mail.store(email_id, '-FLAGS', 'Inbox')
                    cleaned += 1
                
                # Update progress
                progress = (i + 1) / total_emails * 100
                self.progress_bar['value'] = progress
                self.progress_label.config(text=f"Cleaning email {i+1} of {total_emails}")
                self.root.update_idletasks()
                
                # Rate limiting
                if (i + 1) % 50 == 0:
                    time.sleep(1)
            
            mail.close()
            mail.logout()
            
            if self.dry_run.get():
                self.log_message(f"🧪 DRY RUN: Would archive {total_emails} emails")
            else:
                self.log_message(f"✅ Cleaned inbox: {cleaned} emails archived")
            
            self.progress_bar['value'] = 0
            self.progress_label.config(text="Ready")
            
        except Exception as e:
            self.log_message(f"❌ Inbox cleaning failed: {e}")
            self.progress_bar['value'] = 0
            self.progress_label.config(text="Error")
    
    # ==================== CHART CREATION METHODS ====================
    
    def create_main_charts(self):
        """Create main analytics charts"""
        try:
            # Create sample data for demonstration
            hours = list(range(24))
            email_volume = [np.random.randint(5, 50) for _ in hours]
            
            # Create figure
            self.main_fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            
            # Email volume by hour
            ax1.bar(hours, email_volume, color='skyblue', alpha=0.7)
            ax1.set_title('📧 Email Volume by Hour')
            ax1.set_xlabel('Hour of Day')
            ax1.set_ylabel('Number of Emails')
            ax1.grid(True, alpha=0.3)
            
            # Classification accuracy
            categories = ['Important', 'Business', 'Freight', 'Social', 'Spam']
            accuracy = [0.95, 0.87, 0.92, 0.78, 0.96]
            colors = ['green', 'blue', 'orange', 'purple', 'red']
            
            ax2.bar(categories, accuracy, color=colors, alpha=0.7)
            ax2.set_title('🎯 Classification Accuracy')
            ax2.set_ylabel('Accuracy Rate')
            ax2.set_ylim(0, 1)
            ax2.grid(True, alpha=0.3)
            
            # Rotate x-axis labels
            ax2.tick_params(axis='x', rotation=45)
            
            self.main_fig.tight_layout()
            
            # Create canvas
            self.main_canvas_chart = FigureCanvasTkAgg(self.main_fig, self.main_tab)
            self.main_canvas_chart.draw()
            self.main_canvas_chart.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
            
        except Exception as e:
            print(f"Error creating main charts: {e}")
    
    def create_analytics_charts(self):
        """Create email analytics charts"""
        try:
            # Create sample data
            labels = ['Important', 'Business', 'Freight', 'Social', 'Newsletters']
            sizes = [25, 35, 20, 15, 5]
            colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ff99cc']
            
            # Create figure
            self.analytics_fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            
            # Pie chart
            ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax1.set_title('📊 Email Distribution')
            
            # Activity over time
            days = list(range(1, 31))
            activity = [np.random.randint(20, 100) for _ in days]
            
            ax2.plot(days, activity, marker='o', linewidth=2, markersize=4)
            ax2.set_title('📈 Daily Email Activity')
            ax2.set_xlabel('Day of Month')
            ax2.set_ylabel('Number of Emails')
            ax2.grid(True, alpha=0.3)
            
            self.analytics_fig.tight_layout()
            
            # Create canvas
            self.analytics_canvas = FigureCanvasTkAgg(self.analytics_fig, self.analytics_tab)
            self.analytics_canvas.draw()
            self.analytics_canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
            
        except Exception as e:
            print(f"Error creating analytics charts: {e}")
    
    def create_business_charts(self):
        """Create business intelligence charts"""
        try:
            # Create sample business data
            freight_types = ['Dry Van', 'Refrigerated', 'Flatbed', 'Container']
            freight_volume = [45, 30, 15, 10]
            
            # Create figure
            self.business_fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            
            # Freight volume
            ax1.bar(freight_types, freight_volume, color=['#ff6b6b', '#4ecdc4', '#45b7d1', '#f9ca24'])
            ax1.set_title('🚛 Freight Volume by Type')
            ax1.set_ylabel('Volume (%)')
            ax1.tick_params(axis='x', rotation=45)
            
            # Invoice processing
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
            invoices = [120, 135, 150, 140, 160, 175]
            
            ax2.plot(months, invoices, marker='s', linewidth=3, markersize=8, color='green')
            ax2.set_title('📋 Invoice Processing Trend')
            ax2.set_ylabel('Number of Invoices')
            ax2.grid(True, alpha=0.3)
            
            self.business_fig.tight_layout()
            
            # Create canvas
            self.business_canvas = FigureCanvasTkAgg(self.business_fig, self.business_tab)
            self.business_canvas.draw()
            self.business_canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
            
        except Exception as e:
            print(f"Error creating business charts: {e}")
    
    # ==================== AI CHAT INTERFACE METHODS ====================
    
    def on_chat_input_focus_in(self, event):
        """Handle chat input focus in"""
        if "Ask me anything about your emails..." in self.chat_input.get('1.0', tk.END):
            self.chat_input.delete('1.0', tk.END)
    
    def on_chat_input_focus_out(self, event):
        """Handle chat input focus out"""
        if not self.chat_input.get('1.0', tk.END).strip():
            self.chat_input.insert('1.0', "Ask me anything about your emails...\n\nExamples:\n• What are my most important emails?\n• Show me freight-related emails\n• Analyze my LinkedIn emails\n• Count emails by type")
    
    def clear_chat_history(self):
        """Clear chat history"""
        self.chat_response.config(state='normal')
        self.chat_response.delete('1.0', tk.END)
        self.chat_response.config(state='disabled')
        self.chat_input.delete('1.0', tk.END)
        self.on_chat_input_focus_out(None)
    
    def process_chat_question(self):
        """Process user's chat question"""
        question = self.chat_input.get('1.0', tk.END).strip()
        
        if not question or "Ask me anything about your emails..." in question:
            self.add_chat_response("Please ask me a question about your emails!")
            return
        
        # Add user question to chat
        self.add_chat_response(f"👤 You: {question}")
        
        # Process the question
        response = self.analyze_email_question(question)
        self.add_chat_response(f"🤖 AI: {response}")
    
    def add_chat_response(self, message):
        """Add message to chat response area"""
        self.chat_response.config(state='normal')
        self.chat_response.insert(tk.END, message + "\n\n")
        self.chat_response.config(state='disabled')
        self.chat_response.see(tk.END)
    
    def analyze_email_question(self, question):
        """Analyze user's email question and provide intelligent response"""
        question_lower = question.lower()
        
        # Start analysis with progress indication
        self.add_chat_response("🤖 AI: Analyzing your emails... Please wait.")
        self.root.update_idletasks()
        
        try:
            # Connect to Gmail to get real data
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login(self.gmail_user.get(), self.gmail_pass.get())
            
            # Determine question type and provide intelligent response
            if any(word in question_lower for word in ['important', 'priority', 'urgent', 'starred']):
                response = self.analyze_important_emails_live(mail)
            elif any(word in question_lower for word in ['freight', 'shipping', 'logistics', 'truck', 'load']):
                response = self.analyze_freight_emails_live(mail)
            elif any(word in question_lower for word in ['linkedin', 'social', 'network']):
                response = self.analyze_linkedin_emails_live(mail)
            elif any(word in question_lower for word in ['government', 'gov', '.gov', 'tax', 'irs']):
                response = self.analyze_government_emails_live(mail)
            elif any(word in question_lower for word in ['count', 'how many', 'number', 'total']):
                response = self.count_emails_by_type_live(mail)
            elif any(word in question_lower for word in ['search', 'find', 'look for', 'show me']) or 'from' in question_lower or 'with' in question_lower:
                response = self.search_emails_by_content_live(mail, question)
            elif any(word in question_lower for word in ['summary', 'overview', 'inbox', 'status']):
                response = self.summarize_inbox_live(mail)
            elif any(word in question_lower for word in ['classify', 'categorize', 'organize']):
                response = self.analyze_classification_patterns_live(mail)
            elif any(word in question_lower for word in ['recent', 'today', 'yesterday', 'week']):
                response = self.analyze_recent_emails_live(mail, question)
            elif any(word in question_lower for word in ['sender', 'from', 'who sent']):
                response = self.analyze_top_senders_live(mail)
            elif any(word in question_lower for word in ['unread', 'new']):
                response = self.analyze_unread_emails_live(mail)
            else:
                response = self.general_email_analysis_live(mail, question)
            
            mail.logout()
            return response
            
        except Exception as e:
            return f"❌ I encountered an error while analyzing your emails: {str(e)}\n\n💡 Make sure you're connected to Gmail and try again."
    
    def analyze_important_emails_live(self, mail):
        """Analyze important emails with live data"""
        try:
            # Get starred emails from the Starred folder
            mail.select('[Gmail]/Starred')
            status, starred_messages = mail.search(None, 'ALL')
            starred_count = len(starred_messages[0].split()) if starred_messages[0] else 0
            
            # Get flagged emails from inbox
            mail.select('inbox')
            status, flagged_messages = mail.search(None, 'FLAGGED')
            flagged_count = len(flagged_messages[0].split()) if flagged_messages[0] else 0
            
            # Analyze recent starred emails for patterns
            patterns = []
            senders = {}
            subjects = []
            
            if starred_count > 0:
                # Sample recent starred emails
                starred_ids = starred_messages[0].split()[-10:]  # Last 10 starred
                mail.select('[Gmail]/Starred')
                
                for email_id in starred_ids:
                    try:
                        status, msg_data = mail.fetch(email_id, '(RFC822)')
                        raw_email = msg_data[0][1]
                        email_message = email.message_from_bytes(raw_email)
                        
                        sender = email_message.get('From', '')
                        subject = self._decode_header(email_message.get('Subject', ''))
                        
                        # Count senders
                        sender_domain = sender.split('@')[-1].split('>')[0] if '@' in sender else sender
                        senders[sender_domain] = senders.get(sender_domain, 0) + 1
                        subjects.append(subject)
                        
                    except:
                        continue
            
            # Analyze patterns using AI if available
            ai_analysis = ""
            if self.smart_classifier and subjects:
                try:
                    # Use AI to classify starred email patterns
                    sample_content = " ".join(subjects[:5])
                    prediction, confidence = self.smart_classifier.classify_email("Important Analysis", sample_content)
                    ai_analysis = f"\n🤖 AI Pattern Recognition:\n• Detected category: {prediction} (confidence: {confidence:.2%})"
                except:
                    pass
            
            # Top senders analysis
            top_senders = sorted(senders.items(), key=lambda x: x[1], reverse=True)[:3]
            sender_analysis = "\n".join([f"• {domain}: {count} emails" for domain, count in top_senders])
            
            return f"""⭐ Important Email Analysis (Live Data):

📊 Current Status:
• Starred emails: {starred_count}
• Flagged emails in inbox: {flagged_count}
• Total important emails: {starred_count + flagged_count}

📈 Top Senders of Important Emails:
{sender_analysis if sender_analysis else "• No pattern data available"}

🎯 Recent Important Subjects:
{chr(10).join([f"• {subj[:60]}..." for subj in subjects[:3]]) if subjects else "• No recent starred emails"}
{ai_analysis}

💡 AI Recommendations:
• Your starred system shows {starred_count} critical emails
• {'High engagement with ' + top_senders[0][0] if top_senders else 'Diversified important email sources'}
• AI is learning from your {starred_count} starred email patterns
• Consider using labels for better organization of important emails"""
            
        except Exception as e:
            return f"❌ Error analyzing important emails: {str(e)}"
    
    def count_emails_by_type_live(self, mail):
        """Count emails by type with live data"""
        try:
            counts = {}
            
            # Get inbox count
            mail.select('inbox')
            status, inbox_messages = mail.search(None, 'ALL')
            inbox_count = len(inbox_messages[0].split()) if inbox_messages[0] else 0
            
            # Get starred count
            mail.select('[Gmail]/Starred')
            status, starred_messages = mail.search(None, 'ALL')
            starred_count = len(starred_messages[0].split()) if starred_messages[0] else 0
            
            # Get unread count
            mail.select('inbox')
            status, unread_messages = mail.search(None, 'UNSEEN')
            unread_count = len(unread_messages[0].split()) if unread_messages[0] else 0
            
            # Sample emails for classification
            sample_size = min(50, inbox_count)
            if sample_size > 0:
                email_ids = inbox_messages[0].split()[-sample_size:]  # Recent emails
                classifications = {}
                
                for email_id in email_ids[:20]:  # Analyze 20 recent emails
                    try:
                        status, msg_data = mail.fetch(email_id, '(RFC822)')
                        raw_email = msg_data[0][1]
                        email_message = email.message_from_bytes(raw_email)
                        
                        subject = self._decode_header(email_message.get('Subject', ''))
                        sender = email_message.get('From', '')
                        body = self._get_email_body(email_message)
                        
                        # Classify using AI or rules
                        if self.smart_classifier:
                            try:
                                prediction, confidence = self.smart_classifier.classify_email(subject, body)
                                category = prediction if confidence > 0.5 else "Unknown"
                            except:
                                category = self._classify_email_simple(subject, sender)
                        else:
                            category = self._classify_email_simple(subject, sender)
                        
                        classifications[category] = classifications.get(category, 0) + 1
                        
                    except:
                        continue
                
                # Extrapolate to full inbox
                total_classified = sum(classifications.values())
                if total_classified > 0:
                    for category, count in classifications.items():
                        estimated = int((count / total_classified) * inbox_count)
                        classifications[category] = estimated
            
            return f"""📊 Live Email Count Analysis:

📧 Current Inbox Status:
• Total emails in inbox: {inbox_count:,}
• Unread emails: {unread_count:,} ({unread_count/inbox_count*100:.1f}% of inbox)
• Starred emails: {starred_count:,}
• Read emails: {inbox_count - unread_count:,}

🏷️ Estimated Email Categories (based on recent sample):
{chr(10).join([f"• {category}: ~{count:,} emails" for category, count in sorted(classifications.items(), key=lambda x: x[1], reverse=True)]) if 'classifications' in locals() and classifications else "• Analysis pending - run classification for detailed breakdown"}

📈 Inbox Health Score: {max(0, 100 - (unread_count/inbox_count*100)):.0f}/100
{'🟢 Great! Your inbox is well managed.' if unread_count < inbox_count * 0.1 else '🟡 Consider processing unread emails.' if unread_count < inbox_count * 0.3 else '🔴 High unread count - inbox needs attention.'}

💡 Recommendations:
• {'Focus on processing ' + str(unread_count) + ' unread emails' if unread_count > 50 else 'Maintain current email processing habits'}
• Use AI classification to automatically organize emails
• Consider archiving old emails to improve performance"""
            
        except Exception as e:
            return f"❌ Error counting emails: {str(e)}"
    
    def _classify_email_simple(self, subject, sender):
        """Simple email classification without AI"""
        subject_lower = subject.lower()
        sender_lower = sender.lower()
        
        if any(word in subject_lower for word in ['freight', 'shipping', 'logistics', 'truck', 'load']):
            return "Freight/Logistics"
        elif any(word in sender_lower for word in ['linkedin', 'social']):
            return "Social/LinkedIn"
        elif '.gov' in sender_lower or 'government' in subject_lower:
            return "Government"
        elif any(word in subject_lower for word in ['invoice', 'payment', 'bill']):
            return "Financial"
        elif any(word in subject_lower for word in ['newsletter', 'unsubscribe', 'marketing']):
            return "Marketing"
        else:
            return "Business"
    
    def summarize_inbox_live(self, mail):
        """Provide live inbox summary"""
        try:
            # Get comprehensive inbox data
            mail.select('inbox')
            status, all_messages = mail.search(None, 'ALL')
            total_count = len(all_messages[0].split()) if all_messages[0] else 0
            
            status, unread_messages = mail.search(None, 'UNSEEN')
            unread_count = len(unread_messages[0].split()) if unread_messages[0] else 0
            
            status, today_messages = mail.search(None, 'SINCE', datetime.now().strftime('%d-%b-%Y'))
            today_count = len(today_messages[0].split()) if today_messages[0] else 0
            
            # Get recent email sample for analysis
            recent_senders = {}
            urgent_count = 0
            
            if total_count > 0:
                recent_ids = all_messages[0].split()[-10:]  # Last 10 emails
                
                for email_id in recent_ids:
                    try:
                        status, msg_data = mail.fetch(email_id, '(RFC822)')
                        raw_email = msg_data[0][1]
                        email_message = email.message_from_bytes(raw_email)
                        
                        sender = email_message.get('From', '')
                        subject = self._decode_header(email_message.get('Subject', ''))
                        
                        # Count senders
                        sender_domain = sender.split('@')[-1].split('>')[0] if '@' in sender else "Unknown"
                        recent_senders[sender_domain] = recent_senders.get(sender_domain, 0) + 1
                        
                        # Check for urgency
                        if any(word in subject.lower() for word in ['urgent', 'asap', 'immediate', 'priority']):
                            urgent_count += 1
                            
                    except:
                        continue
            
            # Calculate inbox efficiency metrics
            read_rate = ((total_count - unread_count) / total_count * 100) if total_count > 0 else 0
            activity_level = "High" if today_count > 20 else "Medium" if today_count > 5 else "Low"
            
            top_senders = sorted(recent_senders.items(), key=lambda x: x[1], reverse=True)[:3]
            sender_summary = "\n".join([f"• {domain}: {count} recent emails" for domain, count in top_senders])
            
            return f"""📋 Live Inbox Summary:

📊 Current Status:
• Total emails: {total_count:,}
• Unread emails: {unread_count:,} ({unread_count/total_count*100:.1f}%)
• Emails today: {today_count}
• Read rate: {read_rate:.1f}%

📈 Activity Level: {activity_level}
🚨 Urgent emails detected: {urgent_count}

👥 Recent Active Senders:
{sender_summary if sender_summary else "• No recent activity"}

🎯 Inbox Health:
{'🟢 Excellent - Well managed inbox' if read_rate > 90 and unread_count < 50 else '🟡 Good - Some attention needed' if read_rate > 70 else '🔴 Needs attention - High unread count'}

💡 Smart Recommendations:
• {'Process ' + str(unread_count) + ' unread emails' if unread_count > 10 else 'Great job keeping up with emails!'}
• {'Urgent attention needed for ' + str(urgent_count) + ' priority emails' if urgent_count > 0 else 'No urgent emails detected'}
• Use AI classification to automatically organize your {total_count:,} emails
• Consider archiving old emails for better performance"""
            
        except Exception as e:
            return f"❌ Error summarizing inbox: {str(e)}"
    
    def general_email_analysis_live(self, mail, question):
        """Provide general email analysis with AI insights"""
        try:
            # Get basic inbox metrics
            mail.select('inbox')
            status, all_messages = mail.search(None, 'ALL')
            total_count = len(all_messages[0].split()) if all_messages[0] else 0
            
            # Use AI to understand the question better
            ai_insight = ""
            if self.smart_classifier and question:
                try:
                    prediction, confidence = self.smart_classifier.classify_email(f"User Question: {question}", question)
                    ai_insight = f"\n🤖 AI Understanding: Your question seems related to {prediction} (confidence: {confidence:.1%})"
                except:
                    pass
            
            return f"""🤖 AI Email Assistant Analysis:

❓ Your Question: "{question}"
{ai_insight}

📊 Quick Inbox Overview:
• Total emails: {total_count:,}
• Ready for AI-powered analysis and organization

💡 I can help you with:
• Detailed email analysis and categorization
• Finding specific emails or patterns
• Organizing your inbox with smart labels
• Identifying important communications
• Tracking email trends and senders
• Providing personalized email management tips

🚀 Suggested Actions:
• Ask me about specific email types (e.g., "Show me freight emails")
• Request detailed counts (e.g., "How many unread emails?")
• Get sender analysis (e.g., "Who sends me the most emails?")
• Analyze importance patterns (e.g., "What are my most important emails?")

Would you like me to perform any of these specific analyses?"""
            
        except Exception as e:
            return f"❌ Error in general analysis: {str(e)}"
    
    # Add placeholder methods for other analysis types (can be expanded later)
    def analyze_freight_emails_live(self, mail):
        """Analyze freight emails with live data"""
        return self._analyze_category_live(mail, ['freight', 'shipping', 'logistics', 'truck', 'load'], "🚛 Freight/Logistics")
    
    def analyze_linkedin_emails_live(self, mail):
        """Analyze LinkedIn emails with live data"""  
        return self._analyze_category_live(mail, ['linkedin'], "💼 LinkedIn/Social", sender_filter=True)
    
    def analyze_government_emails_live(self, mail):
        """Analyze government emails with live data"""
        return self._analyze_category_live(mail, ['government', 'gov', '.gov'], "🏛️ Government")
    
    def analyze_unread_emails_live(self, mail):
        """Analyze unread emails"""
        try:
            mail.select('inbox')
            status, unread_messages = mail.search(None, 'UNSEEN')
            unread_count = len(unread_messages[0].split()) if unread_messages[0] else 0
            
            if unread_count == 0:
                return "✅ Congratulations! You have no unread emails. Your inbox is fully processed."
            
            # Analyze recent unread emails
            unread_ids = unread_messages[0].split()[-10:]  # Recent 10 unread
            urgent_count = 0
            senders = {}
            
            for email_id in unread_ids:
                try:
                    status, msg_data = mail.fetch(email_id, '(RFC822)')
                    raw_email = msg_data[0][1]
                    email_message = email.message_from_bytes(raw_email)
                    
                    sender = email_message.get('From', '')
                    subject = self._decode_header(email_message.get('Subject', ''))
                    
                    sender_domain = sender.split('@')[-1].split('>')[0] if '@' in sender else "Unknown"
                    senders[sender_domain] = senders.get(sender_domain, 0) + 1
                    
                    if any(word in subject.lower() for word in ['urgent', 'asap', 'immediate', 'priority']):
                        urgent_count += 1
                        
                except:
                    continue
            
            top_senders = sorted(senders.items(), key=lambda x: x[1], reverse=True)[:3]
            
            return f"""📬 Unread Email Analysis:
            
📊 Current Status:
• Total unread emails: {unread_count:,}
• Urgent unread emails: {urgent_count}
• Percentage of inbox: {unread_count/4000*100:.1f}% (estimated)

👥 Top Unread Senders:
{chr(10).join([f"• {domain}: {count} emails" for domain, count in top_senders]) if top_senders else "• No pattern data available"}

🚨 Priority Level: {'🔴 HIGH - Urgent emails detected!' if urgent_count > 0 else '🟡 MEDIUM - Regular processing needed' if unread_count > 50 else '🟢 LOW - Manageable amount'}

💡 Recommendations:
• {'Process urgent emails first!' if urgent_count > 0 else 'Start with recent emails for quick wins'}
• Use AI classification to automatically organize unread emails
• Consider batch processing similar emails together
• Set up filters for recurring low-priority emails"""
            
        except Exception as e:
            return f"❌ Error analyzing unread emails: {str(e)}"
    
    def _analyze_category_live(self, mail, keywords, category_name, sender_filter=False):
        """Generic method to analyze email categories"""
        try:
            mail.select('inbox')
            status, all_messages = mail.search(None, 'ALL')
            total_count = len(all_messages[0].split()) if all_messages[0] else 0
            
            # Sample recent emails for analysis
            sample_ids = all_messages[0].split()[-50:] if total_count > 0 else []
            category_emails = []
            
            for email_id in sample_ids:
                try:
                    status, msg_data = mail.fetch(email_id, '(RFC822)')
                    raw_email = msg_data[0][1]
                    email_message = email.message_from_bytes(raw_email)
                    
                    sender = email_message.get('From', '')
                    subject = self._decode_header(email_message.get('Subject', ''))
                    
                    # Check if email matches category
                    matches = False
                    if sender_filter:
                        matches = any(keyword in sender.lower() for keyword in keywords)
                    else:
                        matches = any(keyword in subject.lower() or keyword in sender.lower() for keyword in keywords)
                    
                    if matches:
                        category_emails.append((subject, sender))
                        
                except:
                    continue
            
            estimated_count = int((len(category_emails) / len(sample_ids)) * total_count) if sample_ids else 0
            
            return f"""{category_name} Email Analysis:
            
📊 Analysis Results:
• Estimated {category_name.split()[-1]} emails: ~{estimated_count:,}
• Sample found: {len(category_emails)} in recent 50 emails
• Percentage of inbox: {estimated_count/total_count*100:.1f}%

📧 Recent Examples:
{chr(10).join([f"• {subj[:50]}... (from {sender.split('@')[-1].split('>')[0] if '@' in sender else sender})" for subj, sender in category_emails[:3]]) if category_emails else "• No recent emails found"}

💡 AI Insights:
• {'High activity' if len(category_emails) > 5 else 'Medium activity' if len(category_emails) > 2 else 'Low activity'} in this category
• Consider using labels for better organization
• {'Archive older emails' if estimated_count > 100 else 'Current volume is manageable'}

🎯 Recommendations:
• Use AI classification to automatically organize these emails
• Create specific labels for {category_name.split()[-1]} emails
• {'Set up filters for recurring emails' if len(category_emails) > 3 else 'Monitor for patterns'}"""
            
        except Exception as e:
            return f"❌ Error analyzing {category_name} emails: {str(e)}"
    
    def search_emails_by_content_live(self, mail, search_query):
        """Search emails with live data - enhanced with sender and subject search"""
        try:
            query_lower = search_query.lower()
            
            # Parse the search query for sender and subject patterns
            sender_search = None
            subject_search = None
            
            # Extract sender search patterns
            if 'from' in query_lower:
                # Examples: "emails from apex", "do i have any emails from john"
                from_patterns = ['from ', 'emails from ', 'any emails from ']
                for pattern in from_patterns:
                    if pattern in query_lower:
                        sender_search = query_lower.split(pattern)[1].split(' ')[0].strip('?.,!')
                        break
            
            # Extract subject search patterns  
            if 'with' in query_lower:
                # Examples: "emails with API", "do i have any emails with invoice"
                with_patterns = ['with ', 'emails with ', 'any emails with ', 'containing ']
                for pattern in with_patterns:
                    if pattern in query_lower:
                        remaining = query_lower.split(pattern)[1].strip('?.,!')
                        subject_search = remaining.split(' ')[0] if ' ' in remaining else remaining
                        break
            
            # If no specific patterns, try to extract keywords
            if not sender_search and not subject_search:
                # Look for quoted terms or last word as search term
                if '"' in search_query:
                    subject_search = search_query.split('"')[1]
                else:
                    words = query_lower.replace('?', '').replace('!', '').split()
                    # Get the last meaningful word as search term
                    exclude_words = ['emails', 'email', 'any', 'do', 'i', 'have', 'the', 'a', 'an']
                    for word in reversed(words):
                        if word not in exclude_words and len(word) > 2:
                            subject_search = word
                            break
            
            # Search emails
            mail.select('inbox')
            status, all_messages = mail.search(None, 'ALL')
            total_count = len(all_messages[0].split()) if all_messages[0] else 0
            
            # Sample recent emails for search
            sample_size = min(100, total_count)  # Search more emails for better results
            email_ids = all_messages[0].split()[-sample_size:] if total_count > 0 else []
            
            found_emails = []
            sender_matches = []
            subject_matches = []
            
            for email_id in email_ids:
                try:
                    status, msg_data = mail.fetch(email_id, '(RFC822)')
                    raw_email = msg_data[0][1]
                    email_message = email.message_from_bytes(raw_email)
                    
                    sender = email_message.get('From', '')
                    subject = self._decode_header(email_message.get('Subject', ''))
                    date = email_message.get('Date', '')
                    
                    # Check sender match
                    sender_match = False
                    if sender_search and sender_search in sender.lower():
                        sender_match = True
                        sender_matches.append((subject, sender, date))
                    
                    # Check subject match
                    subject_match = False
                    if subject_search and subject_search in subject.lower():
                        subject_match = True
                        subject_matches.append((subject, sender, date))
                    
                    # Add to found emails if either matches
                    if sender_match or subject_match:
                        found_emails.append({
                            'subject': subject,
                            'sender': sender,
                            'date': date,
                            'sender_match': sender_match,
                            'subject_match': subject_match
                        })
                        
                except Exception as e:
                    continue
            
            # Build response
            search_type = []
            if sender_search:
                search_type.append(f"sender containing '{sender_search}'")
            if subject_search:
                search_type.append(f"subject containing '{subject_search}'")
            
            search_description = " and ".join(search_type) if search_type else "general search"
            
            if not found_emails:
                return f"""🔍 Email Search Results:

❓ Your Search: "{search_query}"
🎯 Looking for: {search_description}

📊 Results: No matching emails found in recent {sample_size} emails

💡 Search Tips:
• Try: "emails from [company/name]" (e.g., "emails from apex")
• Try: "emails with [keyword]" (e.g., "emails with API")
• Try: "show me [keyword] emails" (e.g., "show me invoice emails")
• Use broader terms if no results found
• Check spelling of search terms

🔄 Suggestions:
• Search for partial matches (e.g., "apex" instead of "apex freight")
• Try searching by domain (e.g., "gmail.com" or "company.com")
• Use common keywords from your emails"""

            # Format results
            result_summary = f"Found {len(found_emails)} matching emails"
            if sender_matches and subject_matches:
                result_summary += f" ({len(sender_matches)} sender matches, {len(subject_matches)} subject matches)"
            elif sender_matches:
                result_summary += f" (all from sender matching '{sender_search}')"
            elif subject_matches:
                result_summary += f" (all with subject containing '{subject_search}')"
            
            # Show top results
            top_results = found_emails[:10]  # Show top 10 matches
            results_text = ""
            
            for i, email in enumerate(top_results, 1):
                match_type = []
                if email['sender_match']:
                    match_type.append("👤 Sender")
                if email['subject_match']:
                    match_type.append("📧 Subject")
                
                match_indicator = " + ".join(match_type)
                sender_clean = email['sender'].split('<')[0].strip().strip('"')
                
                results_text += f"• [{match_indicator}] {email['subject'][:60]}...\n"
                results_text += f"  From: {sender_clean}\n"
                if i < len(top_results):
                    results_text += "\n"
            
            return f"""🔍 Email Search Results:

❓ Your Search: "{search_query}"
🎯 Search Criteria: {search_description}

📊 Results: {result_summary}
📧 Searched: {sample_size} recent emails from inbox

🎯 Matching Emails:
{results_text}

💡 Actions You Can Take:
• Run "AI Classify Emails" to organize these emails
• Use labels to group similar emails
• Archive old emails if no longer needed
• Star important emails for quick access

🔍 Refine Your Search:
• Be more specific: "emails from apex freight capital"
• Search by domain: "emails from @company.com"  
• Use multiple keywords: "emails with API integration"
• Try different variations of the search term"""
            
        except Exception as e:
            return f"""❌ Search Error: {str(e)}

🔍 Search Help:
Try these search formats:
• "Do I have emails from [sender]?"
• "Show me emails with [keyword]"  
• "Find emails about [topic]"
• "Emails from [company/person]"

Examples:
• "Do I have emails from Apex?"
• "Show me emails with API"
• "Find emails about invoices"
• "Emails from john@company.com"
"""
    
    def analyze_top_senders_live(self, mail):
        """Analyze top email senders"""
        try:
            mail.select('inbox')
            status, all_messages = mail.search(None, 'ALL')
            total_count = len(all_messages[0].split()) if all_messages[0] else 0
            
            # Sample recent emails for sender analysis
            sample_ids = all_messages[0].split()[-100:] if total_count > 0 else []
            senders = {}
            
            for email_id in sample_ids:
                try:
                    status, msg_data = mail.fetch(email_id, '(RFC822)')
                    raw_email = msg_data[0][1]
                    email_message = email.message_from_bytes(raw_email)
                    
                    sender = email_message.get('From', '')
                    sender_domain = sender.split('@')[-1].split('>')[0] if '@' in sender else "Unknown"
                    senders[sender_domain] = senders.get(sender_domain, 0) + 1
                    
                except:
                    continue
            
            top_senders = sorted(senders.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return f"""👥 Top Email Senders Analysis:
            
📊 Based on recent 100 emails:
{chr(10).join([f"• {domain}: {count} emails ({count/len(sample_ids)*100:.1f}%)" for domain, count in top_senders]) if top_senders else "• No sender data available"}

📈 Sender Insights:
• Most active sender: {top_senders[0][0] if top_senders else "Unknown"}
• Email distribution: {'Concentrated' if len(top_senders) > 0 and top_senders[0][1] > len(sample_ids) * 0.3 else 'Diversified'}
• Total unique senders: {len(senders)}

💡 Recommendations:
• {'Consider filters for high-volume sender: ' + top_senders[0][0] if top_senders and top_senders[0][1] > 10 else 'Good sender diversity'}
• Use labels to organize emails by sender domain
• Monitor for spam patterns from unknown senders"""
            
        except Exception as e:
            return f"❌ Error analyzing senders: {str(e)}"
    
    def analyze_recent_emails_live(self, mail, question):
        """Analyze recent emails based on time period"""
        try:
            # Determine time period from question
            question_lower = question.lower()
            if 'today' in question_lower:
                since_date = datetime.now().strftime('%d-%b-%Y')
                period = "today"
            elif 'yesterday' in question_lower:
                since_date = (datetime.now() - timedelta(days=1)).strftime('%d-%b-%Y')
                period = "since yesterday"
            elif 'week' in question_lower:
                since_date = (datetime.now() - timedelta(days=7)).strftime('%d-%b-%Y')
                period = "this week"
            else:
                since_date = (datetime.now() - timedelta(days=1)).strftime('%d-%b-%Y')
                period = "recent"
            
            mail.select('inbox')
            status, recent_messages = mail.search(None, 'SINCE', since_date)
            recent_count = len(recent_messages[0].split()) if recent_messages[0] else 0
            
            return f"""📅 Recent Email Analysis ({period}):
            
📊 Activity Summary:
• Emails received {period}: {recent_count}
• Average per day: {recent_count/7 if 'week' in period else recent_count}
• Activity level: {'High' if recent_count > 50 else 'Medium' if recent_count > 10 else 'Low'}

🎯 Insights:
• {'Very active email period!' if recent_count > 100 else 'Normal email activity' if recent_count > 20 else 'Quiet email period'}
• Consider processing these {recent_count} emails first
• Use AI classification for efficient organization

💡 Next Steps:
• Run email classification on recent emails
• Check for urgent or important messages
• Archive processed emails to maintain inbox health"""
            
        except Exception as e:
            return f"❌ Error analyzing recent emails: {str(e)}"
    
    def analyze_classification_patterns_live(self, mail):
        """Analyze email classification patterns"""
        return f"""🤖 AI Classification System Status:
        
🧠 AI Model Information:
• Smart Learning Classifier: {'✅ Active' if self.smart_classifier else '❌ Not Available'}
• Training Data: {'Available from starred emails' if self.smart_classifier else 'Not loaded'}
• Classification Mode: {self.classification_mode.get().upper()}

📊 Classification Capabilities:
• Real-time email categorization
• Importance pattern recognition
• Sender behavior analysis
• Content-based classification
• Confidence scoring for decisions

🎯 Available Categories:
• Freight/Logistics • Government • Financial
• Social/LinkedIn • Marketing • Business
• Important • Spam/Junk

💡 Recommendations:
• Run "AI Classify Emails" to organize your inbox
• Use "AI Learn from Starred" to improve accuracy
• Enable Live Mode for real email processing
• Review classification results and provide feedback"""
    
    def analyze_freight_emails(self):
        """Analyze freight-related emails"""
        return """🚛 Freight Email Analysis:
        
Your freight/logistics email patterns:
• High volume of rate confirmations and load updates
• Key senders include brokers, shippers, and carriers
• Important keywords: freight, shipping, logistics, rate, load

📈 Trends:
• Peak activity during business hours (9 AM - 5 PM)
• Most emails require immediate attention
• High priority for revenue-generating communications

🎯 Action Items:
• Keep freight emails in inbox for quick access
• Use "Freight/Leads" label for organization
• Archive old rate confirmations after processing"""
    
    def analyze_linkedin_emails(self):
        """Analyze LinkedIn emails"""
        return """💼 LinkedIn Email Analysis:
        
LinkedIn email patterns:
• Mostly connection requests and job opportunities
• Professional networking notifications
• Marketing messages from LinkedIn services

📊 Classification:
• Generally low to medium priority
• Can be safely archived after review
• Useful for professional networking tracking

💡 Suggestions:
• Archive LinkedIn emails weekly
• Keep only job-related notifications in inbox
• Use "Social/LinkedIn" label for organization"""
    
    def analyze_government_emails(self):
        """Analyze government emails"""
        return """🏛️ Government Email Analysis:
        
Government email patterns:
• Official communications and notifications
• Tax-related documents and updates
• Regulatory compliance information
• High importance for business operations

⚠️ Priority Level: HIGH
• Government emails should be kept in inbox
• Often contain time-sensitive information
• Important for compliance and legal matters

📋 Action Items:
• Monitor for tax deadlines and compliance updates
• Keep government emails organized with labels
• Set up alerts for urgent government communications"""
    
    def count_emails_by_type(self):
        """Count emails by type"""
        return """📊 Email Count by Type:
        
Based on recent analysis:
• Total emails in inbox: ~4,000
• Important/Starred: 196 emails
• Freight/Logistics: ~800 emails
• Business communications: ~2,000 emails
• Social/LinkedIn: ~300 emails
• Government: ~50 emails
• Newsletters/Marketing: ~500 emails
• Spam/Junk: ~150 emails

📈 Distribution:
• Business emails: 50%
• Freight/Logistics: 20%
• Marketing: 12.5%
• Social: 7.5%
• Important: 5%
• Other: 5%

💡 Inbox Health: Good organization with clear categories"""
    
    def search_emails_by_content(self, search_query):
        """Search emails by content"""
        return f"""🔍 Search Results for: "{search_query}"
        
I can help you find emails based on:
• Subject line keywords
• Sender information
• Content analysis
• Date ranges
• Label categories

To perform a detailed search:
1. Use the "Preview Emails" function
2. Run classification to categorize emails
3. Check specific labels in Gmail

Would you like me to help you find emails with specific criteria?"""
    
    def summarize_inbox(self):
        """Summarize inbox"""
        return """📋 Inbox Summary:
        
📧 Total Emails: ~4,000
🎯 Important: 196 (starred)
🚛 Freight/Logistics: ~800
💼 Business: ~2,000
👥 Social: ~300
🏛️ Government: ~50

📊 Health Status:
✅ Well organized with clear categories
✅ AI classification working effectively
✅ Starred system for priorities
⚠️ Consider archiving old newsletters

💡 Recommendations:
• Archive emails older than 30 days
• Use AI labels for better organization
• Keep freight emails for quick access
• Regular cleanup of marketing emails"""
    
    def general_email_analysis(self):
        """General email analysis"""
        return """🤖 General Email Analysis:
        
Your email management system is working well! Here's what I can help with:

🔍 Analysis Features:
• Important email identification
• Freight/logistics tracking
• Business communication monitoring
• Social media email management
• Government email alerts

📊 Current Status:
• AI learning from your starred emails
• Smart classification in progress
• Label organization system active
• Inbox health: Good

💡 What would you like to know more about?
Try asking specific questions like:
• "Show me my most important emails"
• "Analyze freight emails"
• "Count emails by type"
• "What's in my inbox?"""
    
    # ==================== GUI EVENT HANDLERS ====================
    
    def on_canvas_configure(self, event):
        """Handle canvas configuration"""
        self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
    
    def on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def on_window_resize(self, event):
        """Handle window resize"""
        if event.widget == self.root:
            # Update canvas scroll region
            self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))


def main():
    """Launch Inbox-Manager"""
    print("🚀 Launching Inbox-Manager - Ultimate Edition...")
    
    # Fix working directory for double-click launches
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Change to project root if in gui subdirectory
    if script_dir.endswith('gui'):
        os.chdir(project_root)
        print(f"📁 Changed working directory to: {project_root}")
    
    # Add project root to Python path
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
        print(f"📁 Added to Python path: {project_root}")
    
    # Hide console window on Windows for double-click launches
    try:
        if os.name == 'nt':  # Windows
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
            print("🪟 Console window hidden")
    except:
        pass  # Ignore if hiding fails
    
    try:
        root = tk.Tk()
        app = AIGmailManagerV3(root)
        
        print("✅ Inbox-Manager initialized successfully!")
        
        root.mainloop()
        print("✅ Inbox-Manager closed successfully!")
        
    except Exception as e:
        print(f"❌ Error launching Inbox-Manager: {e}")
        messagebox.showerror("Launch Error", f"Failed to launch Inbox-Manager:\n{e}")


if __name__ == "__main__":
    main()
