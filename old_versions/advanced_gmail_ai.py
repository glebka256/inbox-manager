#!/usr/bin/env python3
"""
Advanced Gmail AI Manager GUI
Comprehensive email management with analytics, learning, and business intelligence
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import json
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

# Import our modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # Add parent directory to path
from smart_learning_classifier import SmartLearningClassifier
from email_analytics import EmailAnalytics
from business_intelligence import BusinessIntelligenceProcessor
from gmail_ai_gui import GmailAIGUI  # Extend existing GUI

class AdvancedGmailAI(GmailAIGUI):
    """Advanced Gmail AI Manager with analytics and business intelligence"""
    
    def __init__(self, root):
        super().__init__(root)
        
        # Initialize advanced components
        self.smart_classifier = SmartLearningClassifier()
        self.analytics = EmailAnalytics()
        self.business_intel = BusinessIntelligenceProcessor()
        
        # Add advanced features to existing GUI
        self.setup_advanced_features()
        
        # Analytics dashboard window
        self.analytics_window = None
        self.business_window = None
        
    def setup_advanced_features(self):
        """Add advanced features to the existing GUI"""
        
        # Create advanced notebook
        self.advanced_notebook = ttk.Notebook(self.root)
        self.advanced_notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=5)
        
        # Move existing main frame to notebook
        self.main_frame.grid_forget()
        self.advanced_notebook.add(self.main_frame, text="Email Processing")
        
        # Analytics tab
        self.analytics_frame = ttk.Frame(self.advanced_notebook)
        self.advanced_notebook.add(self.analytics_frame, text="Analytics")
        self.setup_analytics_tab()
        
        # Business Intelligence tab
        self.business_frame = ttk.Frame(self.advanced_notebook)
        self.advanced_notebook.add(self.business_frame, text="Business Intelligence")
        self.setup_business_tab()
        
        # Smart Learning tab
        self.learning_frame = ttk.Frame(self.advanced_notebook)
        self.advanced_notebook.add(self.learning_frame, text="Smart Learning")
        self.setup_learning_tab()
        
        # Settings tab
        self.settings_frame = ttk.Frame(self.advanced_notebook)
        self.advanced_notebook.add(self.settings_frame, text="Advanced Settings")
        self.setup_advanced_settings_tab()
    
    def setup_analytics_tab(self):
        """Setup the analytics dashboard tab"""
        
        # Analytics controls
        controls_frame = ttk.LabelFrame(self.analytics_frame, text="Analytics Controls")
        controls_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(controls_frame, text="Generate Daily Report", 
                  command=self.generate_daily_report).pack(side='left', padx=5, pady=5)
        ttk.Button(controls_frame, text="Create Visual Dashboard", 
                  command=self.create_visual_dashboard).pack(side='left', padx=5, pady=5)
        ttk.Button(controls_frame, text="Export Analytics", 
                  command=self.export_analytics).pack(side='left', padx=5, pady=5)
        
        # Time range selector
        time_frame = ttk.LabelFrame(self.analytics_frame, text="Time Range")
        time_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(time_frame, text="Period:").pack(side='left', padx=5)
        self.time_period = ttk.Combobox(time_frame, values=["7 days", "30 days", "90 days", "1 year"])
        self.time_period.set("30 days")
        self.time_period.pack(side='left', padx=5)
        
        # Analytics display
        self.analytics_text = tk.Text(self.analytics_frame, height=20, wrap='word')
        analytics_scroll = ttk.Scrollbar(self.analytics_frame, orient='vertical', 
                                       command=self.analytics_text.yview)
        self.analytics_text.configure(yscrollcommand=analytics_scroll.set)
        
        self.analytics_text.pack(side='left', fill='both', expand=True, padx=10, pady=5)
        analytics_scroll.pack(side='right', fill='y', pady=5)
    
    def setup_business_tab(self):
        """Setup the business intelligence tab"""
        
        # Business controls
        controls_frame = ttk.LabelFrame(self.business_frame, text="Business Intelligence")
        controls_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(controls_frame, text="Generate Business Report", 
                  command=self.generate_business_report).pack(side='left', padx=5, pady=5)
        ttk.Button(controls_frame, text="Check Overdue Items", 
                  command=self.check_overdue_items).pack(side='left', padx=5, pady=5)
        ttk.Button(controls_frame, text="Rate Sheet Analysis", 
                  command=self.analyze_rate_sheets).pack(side='left', padx=5, pady=5)
        
        # Business metrics frame
        metrics_frame = ttk.LabelFrame(self.business_frame, text="Key Metrics")
        metrics_frame.pack(fill='x', padx=10, pady=5)
        
        # Create metrics display
        self.metrics_labels = {}
        metrics = ["Total Loads", "Revenue", "Pending Invoices", "DOT Violations"]
        for i, metric in enumerate(metrics):
            row = i // 2
            col = i % 2
            
            label_frame = ttk.Frame(metrics_frame)
            label_frame.grid(row=row, column=col, padx=10, pady=5, sticky='w')
            
            ttk.Label(label_frame, text=f"{metric}:").pack(side='left')
            self.metrics_labels[metric] = ttk.Label(label_frame, text="0", font=('Arial', 12, 'bold'))
            self.metrics_labels[metric].pack(side='left', padx=10)
        
        # Business display
        self.business_text = tk.Text(self.business_frame, height=15, wrap='word')
        business_scroll = ttk.Scrollbar(self.business_frame, orient='vertical', 
                                      command=self.business_text.yview)
        self.business_text.configure(yscrollcommand=business_scroll.set)
        
        self.business_text.pack(side='left', fill='both', expand=True, padx=10, pady=5)
        business_scroll.pack(side='right', fill='y', pady=5)
    
    def setup_learning_tab(self):
        """Setup the smart learning tab"""
        
        # Learning controls
        controls_frame = ttk.LabelFrame(self.learning_frame, text="Smart Learning Controls")
        controls_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(controls_frame, text="View Learning Stats", 
                  command=self.show_learning_stats).pack(side='left', padx=5, pady=5)
        ttk.Button(controls_frame, text="Retrain Model", 
                  command=self.retrain_model).pack(side='left', padx=5, pady=5)
        ttk.Button(controls_frame, text="Add Custom Category", 
                  command=self.add_custom_category).pack(side='left', padx=5, pady=5)
        
        # Feedback section
        feedback_frame = ttk.LabelFrame(self.learning_frame, text="Provide Feedback")
        feedback_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(feedback_frame, text="Email Content:").pack(anchor='w')
        self.feedback_email = tk.Text(feedback_frame, height=5, wrap='word')
        self.feedback_email.pack(fill='x', padx=5, pady=2)
        
        # Feedback controls
        feedback_controls = ttk.Frame(feedback_frame)
        feedback_controls.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(feedback_controls, text="Correct Category:").pack(side='left')
        self.feedback_category = ttk.Combobox(feedback_controls)
        self.feedback_category.pack(side='left', padx=5)
        
        ttk.Button(feedback_controls, text="Submit Feedback", 
                  command=self.submit_feedback).pack(side='left', padx=10)
        
        # Learning stats display
        self.learning_text = tk.Text(self.learning_frame, height=10, wrap='word')
        learning_scroll = ttk.Scrollbar(self.learning_frame, orient='vertical', 
                                      command=self.learning_text.yview)
        self.learning_text.configure(yscrollcommand=learning_scroll.set)
        
        self.learning_text.pack(side='left', fill='both', expand=True, padx=10, pady=5)
        learning_scroll.pack(side='right', fill='y', pady=5)
        
        # Load categories for feedback
        self.load_categories()
    
    def setup_advanced_settings_tab(self):
        """Setup advanced settings tab"""
        
        # Confidence threshold
        confidence_frame = ttk.LabelFrame(self.settings_frame, text="Classification Settings")
        confidence_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(confidence_frame, text="Confidence Threshold:").pack(side='left')
        self.confidence_var = tk.DoubleVar(value=0.7)
        self.confidence_scale = ttk.Scale(confidence_frame, from_=0.5, to=0.95, 
                                        variable=self.confidence_var, orient='horizontal')
        self.confidence_scale.pack(side='left', padx=10, fill='x', expand=True)
        self.confidence_label = ttk.Label(confidence_frame, text="0.70")
        self.confidence_label.pack(side='right', padx=5)
        
        self.confidence_scale.configure(command=self.update_confidence_label)
        
        # Auto-retraining settings
        retrain_frame = ttk.LabelFrame(self.settings_frame, text="Auto-Retraining")
        retrain_frame.pack(fill='x', padx=10, pady=5)
        
        self.auto_retrain = tk.BooleanVar(value=True)
        ttk.Checkbutton(retrain_frame, text="Enable automatic retraining", 
                       variable=self.auto_retrain).pack(anchor='w')
        
        ttk.Label(retrain_frame, text="Retrain after feedback count:").pack(anchor='w')
        self.retrain_threshold = tk.IntVar(value=10)
        ttk.Spinbox(retrain_frame, from_=5, to=50, textvariable=self.retrain_threshold).pack(anchor='w')
        
        # Analytics settings
        analytics_settings_frame = ttk.LabelFrame(self.settings_frame, text="Analytics Settings")
        analytics_settings_frame.pack(fill='x', padx=10, pady=5)
        
        self.auto_analytics = tk.BooleanVar(value=True)
        ttk.Checkbutton(analytics_settings_frame, text="Generate daily analytics reports", 
                       variable=self.auto_analytics).pack(anchor='w')
        
        self.business_intel_enabled = tk.BooleanVar(value=True)
        ttk.Checkbutton(analytics_settings_frame, text="Enable business intelligence extraction", 
                       variable=self.business_intel_enabled).pack(anchor='w')
        
        # Save settings button
        ttk.Button(self.settings_frame, text="Save Settings", 
                  command=self.save_advanced_settings).pack(pady=10)
    
    def generate_daily_report(self):
        """Generate and display daily analytics report"""
        def run_report():
            try:
                report = self.analytics.generate_daily_report()
                
                self.analytics_text.delete(1.0, tk.END)
                self.analytics_text.insert(tk.END, f"Daily Analytics Report - {report['date']}\n")
                self.analytics_text.insert(tk.END, "=" * 50 + "\n\n")
                
                self.analytics_text.insert(tk.END, f"Total Emails Processed: {report['total_processed']}\n\n")
                
                if report['email_volume']:
                    self.analytics_text.insert(tk.END, "Email Volume by Category:\n")
                    for item in report['email_volume']:
                        self.analytics_text.insert(tk.END, f"  {item['classification']}: {item['count']}\n")
                    self.analytics_text.insert(tk.END, "\n")
                
                if report['top_senders']:
                    self.analytics_text.insert(tk.END, "Top Senders:\n")
                    for sender in report['top_senders'][:5]:
                        self.analytics_text.insert(tk.END, f"  {sender['sender']}: {sender['email_count']} emails\n")
                    self.analytics_text.insert(tk.END, "\n")
                
                if report['classification_accuracy']:
                    self.analytics_text.insert(tk.END, "Classification Performance:\n")
                    for item in report['classification_accuracy']:
                        self.analytics_text.insert(tk.END, 
                            f"  {item['classification']}: {item['avg_confidence']:.3f} avg confidence ({item['total_count']} emails)\n")
                
                messagebox.showinfo("Success", "Daily report generated successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
        
        threading.Thread(target=run_report, daemon=True).start()
    
    def create_visual_dashboard(self):
        """Create visual analytics dashboard"""
        def create_dashboard():
            try:
                result = self.analytics.create_analytics_dashboard()
                messagebox.showinfo("Success", f"Visual dashboard created: {result}")
                
                # Open the analytics folder
                import subprocess
                subprocess.Popen(['explorer', 'analytics_output'])
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create dashboard: {str(e)}")
        
        threading.Thread(target=create_dashboard, daemon=True).start()
    
    def generate_business_report(self):
        """Generate business intelligence report"""
        def run_business_report():
            try:
                report = self.business_intel.generate_business_report()
                
                self.business_text.delete(1.0, tk.END)
                self.business_text.insert(tk.END, "Business Intelligence Report\n")
                self.business_text.insert(tk.END, "=" * 40 + "\n\n")
                
                if 'rate_sheets' in report:
                    rs = report['rate_sheets']
                    self.business_text.insert(tk.END, f"RATE SHEETS (Last 30 Days):\n")
                    self.business_text.insert(tk.END, f"  Total Loads: {rs['total_loads']}\n")
                    self.business_text.insert(tk.END, f"  Total Revenue: ${rs['total_revenue']:,.2f}\n")
                    self.business_text.insert(tk.END, f"  Average Rate: ${rs['avg_rate']:,.2f}\n\n")
                    
                    # Update metrics
                    self.metrics_labels["Total Loads"].config(text=str(rs['total_loads']))
                    self.metrics_labels["Revenue"].config(text=f"${rs['total_revenue']:,.0f}")
                
                if 'invoices' in report:
                    inv = report['invoices']
                    self.business_text.insert(tk.END, f"INVOICES:\n")
                    self.business_text.insert(tk.END, f"  Total Invoices: {inv['total_invoices']}\n")
                    self.business_text.insert(tk.END, f"  Pending: {inv['pending_count']} (${inv['pending_amount']:,.2f})\n\n")
                    
                    # Update metrics
                    self.metrics_labels["Pending Invoices"].config(text=str(inv['pending_count']))
                
                if 'dot_compliance' in report:
                    dot = report['dot_compliance']
                    self.business_text.insert(tk.END, f"DOT COMPLIANCE:\n")
                    self.business_text.insert(tk.END, f"  Total Violations: {dot['total_violations']}\n")
                    self.business_text.insert(tk.END, f"  Total Fines: ${dot['total_fines']:,.2f}\n")
                    self.business_text.insert(tk.END, f"  Open Violations: {dot['open_violations']}\n\n")
                    
                    # Update metrics
                    self.metrics_labels["DOT Violations"].config(text=str(dot['open_violations']))
                
                messagebox.showinfo("Success", "Business report generated successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to generate business report: {str(e)}")
        
        threading.Thread(target=run_business_report, daemon=True).start()
    
    def show_learning_stats(self):
        """Display smart learning statistics"""
        try:
            stats = self.smart_classifier.get_learning_stats()
            
            self.learning_text.delete(1.0, tk.END)
            self.learning_text.insert(tk.END, "Smart Learning Statistics\n")
            self.learning_text.insert(tk.END, "=" * 30 + "\n\n")
            
            self.learning_text.insert(tk.END, f"Total Feedback Received: {stats['total_feedback']}\n")
            self.learning_text.insert(tk.END, f"Correction Rate: {stats['correction_rate']:.1%}\n")
            self.learning_text.insert(tk.END, f"Recent Feedback (7 days): {stats['recent_feedback']}\n")
            self.learning_text.insert(tk.END, f"Total Categories: {stats['total_categories']}\n\n")
            
            if stats['category_distribution']:
                self.learning_text.insert(tk.END, "Category Usage:\n")
                for category, count in stats['category_distribution'].items():
                    self.learning_text.insert(tk.END, f"  {category}: {count}\n")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get learning stats: {str(e)}")
    
    def add_custom_category(self):
        """Add a new custom category"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Custom Category")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Category Name:").pack(pady=5)
        name_entry = ttk.Entry(dialog, width=40)
        name_entry.pack(pady=5)
        
        ttk.Label(dialog, text="Description:").pack(pady=5)
        desc_text = tk.Text(dialog, height=5, width=50)
        desc_text.pack(pady=5)
        
        ttk.Label(dialog, text="Keywords (comma-separated):").pack(pady=5)
        keywords_entry = ttk.Entry(dialog, width=40)
        keywords_entry.pack(pady=5)
        
        def save_category():
            name = name_entry.get().strip()
            description = desc_text.get(1.0, tk.END).strip()
            keywords = [k.strip() for k in keywords_entry.get().split(',') if k.strip()]
            
            if not name:
                messagebox.showerror("Error", "Category name is required")
                return
            
            success = self.smart_classifier.add_custom_category(name, description, keywords)
            if success:
                messagebox.showinfo("Success", f"Category '{name}' added successfully!")
                self.load_categories()
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Category already exists or failed to add")
        
        ttk.Button(dialog, text="Save Category", command=save_category).pack(pady=10)
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).pack(pady=5)
    
    def submit_feedback(self):
        """Submit user feedback for learning"""
        email_content = self.feedback_email.get(1.0, tk.END).strip()
        category = self.feedback_category.get()
        
        if not email_content or not category:
            messagebox.showerror("Error", "Please provide both email content and category")
            return
        
        try:
            # Get prediction first
            prediction, confidence = self.smart_classifier.classify_email(email_content)
            
            # Record feedback
            self.smart_classifier.record_user_feedback(
                email_content, prediction, category, confidence, 
                "feedback@user.com", "User Feedback"
            )
            
            messagebox.showinfo("Success", "Feedback submitted successfully!")
            self.feedback_email.delete(1.0, tk.END)
            self.feedback_category.set("")
            
            # Update learning stats
            self.show_learning_stats()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to submit feedback: {str(e)}")
    
    def load_categories(self):
        """Load available categories for feedback"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.smart_classifier.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT category_name FROM custom_categories ORDER BY category_name')
            categories = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            self.feedback_category['values'] = categories
            
        except Exception as e:
            print(f"Failed to load categories: {e}")
    
    def update_confidence_label(self, value):
        """Update confidence threshold label"""
        self.confidence_label.config(text=f"{float(value):.2f}")
        self.smart_classifier.confidence_threshold = float(value)
    
    def retrain_model(self):
        """Manually trigger model retraining"""
        def retrain():
            try:
                self.smart_classifier.retrain_model()
                messagebox.showinfo("Success", "Model retrained successfully!")
                self.show_learning_stats()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to retrain model: {str(e)}")
        
        threading.Thread(target=retrain, daemon=True).start()
    
    def check_overdue_items(self):
        """Check for overdue business items"""
        def check_overdue():
            try:
                overdue = self.business_intel.get_overdue_items()
                
                self.business_text.delete(1.0, tk.END)
                self.business_text.insert(tk.END, "OVERDUE ITEMS REPORT\n")
                self.business_text.insert(tk.END, "=" * 25 + "\n\n")
                
                if overdue['overdue_invoices']:
                    self.business_text.insert(tk.END, "OVERDUE INVOICES:\n")
                    for invoice in overdue['overdue_invoices']:
                        self.business_text.insert(tk.END, 
                            f"  {invoice['invoice_number']}: ${invoice['amount']:.2f} (due: {invoice['due_date']})\n")
                    self.business_text.insert(tk.END, "\n")
                
                if overdue['overdue_compliance']:
                    self.business_text.insert(tk.END, "OVERDUE DOT COMPLIANCE:\n")
                    for item in overdue['overdue_compliance']:
                        self.business_text.insert(tk.END, 
                            f"  {item['violation_type']}: ${item['fine_amount']:.2f} (due: {item['due_date']})\n")
                
                if not overdue['overdue_invoices'] and not overdue['overdue_compliance']:
                    self.business_text.insert(tk.END, "No overdue items found!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to check overdue items: {str(e)}")
        
        threading.Thread(target=check_overdue, daemon=True).start()
    
    def analyze_rate_sheets(self):
        """Analyze rate sheet trends"""
        messagebox.showinfo("Coming Soon", "Rate sheet analysis feature coming soon!")
    
    def export_analytics(self):
        """Export analytics data"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                report = self.analytics.generate_daily_report()
                with open(filename, 'w') as f:
                    json.dump(report, f, indent=2, default=str)
                messagebox.showinfo("Success", f"Analytics exported to {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export analytics: {str(e)}")
    
    def save_advanced_settings(self):
        """Save advanced settings"""
        settings = {
            'confidence_threshold': self.confidence_var.get(),
            'auto_retrain': self.auto_retrain.get(),
            'retrain_threshold': self.retrain_threshold.get(),
            'auto_analytics': self.auto_analytics.get(),
            'business_intel_enabled': self.business_intel_enabled.get()
        }
        
        try:
            with open('advanced_settings.json', 'w') as f:
                json.dump(settings, f, indent=2)
            messagebox.showinfo("Success", "Advanced settings saved!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
    
    def run_advanced_classification(self):
        """Run classification with advanced features"""
        def classify_advanced():
            try:
                self.output_text.delete(1.0, tk.END)
                self.output_text.insert(tk.END, "Starting Advanced Gmail AI Classification...\n\n")
                
                # Use existing connection logic but with advanced processing
                if hasattr(self, 'gmail_service') and self.gmail_service:
                    # Get recent emails
                    results = self.gmail_service.users().messages().list(
                        userId='me', maxResults=10, q='in:inbox'
                    ).execute()
                    
                    messages = results.get('messages', [])
                    
                    for i, message in enumerate(messages):
                        msg = self.gmail_service.users().messages().get(
                            userId='me', id=message['id']
                        ).execute()
                        
                        # Extract email data
                        subject = self.get_header(msg, 'Subject') or 'No Subject'
                        sender = self.get_header(msg, 'From') or 'Unknown Sender'
                        body = self.get_email_body(msg)
                        
                        self.output_text.insert(tk.END, f"Processing email {i+1}: {subject[:50]}...\n")
                        
                        # Smart classification
                        prediction, confidence = self.smart_classifier.classify_email(
                            body, subject, sender
                        )
                        
                        # Business intelligence extraction
                        if self.business_intel_enabled.get():
                            bi_results = self.business_intel.process_business_email(
                                message['id'], body, subject, sender
                            )
                            
                            if bi_results['rate_sheet']:
                                self.output_text.insert(tk.END, f"  ✓ Rate sheet detected!\n")
                            if bi_results['invoice']:
                                self.output_text.insert(tk.END, f"  ✓ Invoice detected!\n")
                            if bi_results['dot_compliance']:
                                self.output_text.insert(tk.END, f"  ⚠ DOT compliance issue!\n")
                        
                        # Log for analytics
                        self.analytics.log_email_processing({
                            'message_id': message['id'],
                            'subject': subject,
                            'sender': sender,
                            'recipient': 'me',
                            'date_received': datetime.now(),
                            'classification': prediction,
                            'confidence': confidence,
                            'action_taken': 'labeled',
                            'processing_time': 0.5
                        })
                        
                        self.output_text.insert(tk.END, 
                            f"  Classification: {prediction} (confidence: {confidence:.3f})\n")
                        
                        # Apply Gmail label
                        self.apply_gmail_label(message['id'], prediction)
                        
                        self.output_text.insert(tk.END, f"  ✓ Labeled as '{prediction}'\n\n")
                        
                        # Update progress
                        self.progress['value'] = ((i + 1) / len(messages)) * 100
                        self.root.update_idletasks()
                    
                    self.output_text.insert(tk.END, "Advanced classification completed!\n")
                    messagebox.showinfo("Success", "Advanced email classification completed!")
                    
                else:
                    messagebox.showerror("Error", "Please connect to Gmail first")
                    
            except Exception as e:
                self.output_text.insert(tk.END, f"Error: {str(e)}\n")
                messagebox.showerror("Error", f"Classification failed: {str(e)}")
            
            finally:
                self.progress['value'] = 0
        
        threading.Thread(target=classify_advanced, daemon=True).start()

def main():
    """Launch the Advanced Gmail AI Manager"""
    root = tk.Tk()
    root.title("🚀 ADVANCED Gmail AI Manager - Ultimate Edition 🚀")
    root.geometry("1200x800")
    
    app = AdvancedGmailAI(root)
    
    root.mainloop()

if __name__ == "__main__":
    main()