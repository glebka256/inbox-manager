#!/usr/bin/env python3
"""
Gmail AI Analytics Engine
Advanced email analytics and insights system
"""

import sqlite3
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import re
import os

class EmailAnalytics:
    def __init__(self, db_path="email_analytics.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the analytics database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Email processing log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT UNIQUE,
                subject TEXT,
                sender TEXT,
                recipient TEXT,
                date_received DATETIME,
                date_processed DATETIME,
                classification TEXT,
                confidence REAL,
                action_taken TEXT,
                processing_time REAL,
                user_feedback TEXT
            )
        ''')
        
        # Classification performance
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS classification_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATETIME,
                total_emails INTEGER,
                correct_classifications INTEGER,
                accuracy REAL,
                category TEXT
            )
        ''')
        
        # Sender analysis
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sender_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_email TEXT,
                sender_name TEXT,
                total_emails INTEGER,
                avg_response_time REAL,
                priority_score REAL,
                last_email_date DATETIME,
                categories TEXT  -- JSON list of categories
            )
        ''')
        
        # Business metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS business_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATETIME,
                metric_name TEXT,
                metric_value REAL,
                category TEXT,
                notes TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def log_email_processing(self, email_data):
        """Log email processing for analytics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO email_log 
            (message_id, subject, sender, recipient, date_received, date_processed, 
             classification, confidence, action_taken, processing_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            email_data.get('message_id'),
            email_data.get('subject'),
            email_data.get('sender'),
            email_data.get('recipient'),
            email_data.get('date_received'),
            datetime.now(),
            email_data.get('classification'),
            email_data.get('confidence'),
            email_data.get('action_taken'),
            email_data.get('processing_time', 0)
        ))
        
        conn.commit()
        conn.close()
    
    def update_sender_stats(self, sender_email, sender_name, category):
        """Update sender statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get existing stats
        cursor.execute('SELECT * FROM sender_stats WHERE sender_email = ?', (sender_email,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing
            total_emails = existing[3] + 1
            categories = json.loads(existing[7] or '[]')
            if category not in categories:
                categories.append(category)
            
            cursor.execute('''
                UPDATE sender_stats 
                SET total_emails = ?, categories = ?, last_email_date = ?
                WHERE sender_email = ?
            ''', (total_emails, json.dumps(categories), datetime.now(), sender_email))
        else:
            # Create new
            cursor.execute('''
                INSERT INTO sender_stats 
                (sender_email, sender_name, total_emails, categories, last_email_date)
                VALUES (?, ?, 1, ?, ?)
            ''', (sender_email, sender_name, json.dumps([category]), datetime.now()))
        
        conn.commit()
        conn.close()
    
    def generate_daily_report(self):
        """Generate daily email analytics report"""
        conn = sqlite3.connect(self.db_path)
        
        # Email volume by category
        df_emails = pd.read_sql_query('''
            SELECT classification, COUNT(*) as count, DATE(date_processed) as date
            FROM email_log 
            WHERE date_processed >= datetime('now', '-7 days')
            GROUP BY classification, DATE(date_processed)
        ''', conn)
        
        # Top senders
        df_senders = pd.read_sql_query('''
            SELECT sender, COUNT(*) as email_count
            FROM email_log 
            WHERE date_processed >= datetime('now', '-7 days')
            GROUP BY sender
            ORDER BY email_count DESC
            LIMIT 10
        ''', conn)
        
        # Classification accuracy
        df_accuracy = pd.read_sql_query('''
            SELECT classification, 
                   AVG(confidence) as avg_confidence,
                   COUNT(*) as total_count
            FROM email_log 
            WHERE date_processed >= datetime('now', '-7 days')
            GROUP BY classification
        ''', conn)
        
        conn.close()
        
        report = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'email_volume': df_emails.to_dict('records'),
            'top_senders': df_senders.to_dict('records'),
            'classification_accuracy': df_accuracy.to_dict('records'),
            'total_processed': len(df_emails)
        }
        
        return report
    
    def create_analytics_dashboard(self, output_dir="analytics_output"):
        """Create visual analytics dashboard"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        conn = sqlite3.connect(self.db_path)
        
        # Set style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # 1. Email Volume Over Time
        df_volume = pd.read_sql_query('''
            SELECT DATE(date_processed) as date, COUNT(*) as count
            FROM email_log 
            WHERE date_processed >= datetime('now', '-30 days')
            GROUP BY DATE(date_processed)
            ORDER BY date
        ''', conn)
        
        if not df_volume.empty:
            plt.figure(figsize=(12, 6))
            plt.plot(pd.to_datetime(df_volume['date']), df_volume['count'], marker='o')
            plt.title('Email Volume Over Time (Last 30 Days)')
            plt.xlabel('Date')
            plt.ylabel('Number of Emails')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(f'{output_dir}/email_volume.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        # 2. Classification Distribution
        df_categories = pd.read_sql_query('''
            SELECT classification, COUNT(*) as count
            FROM email_log 
            WHERE date_processed >= datetime('now', '-30 days')
            GROUP BY classification
            ORDER BY count DESC
        ''', conn)
        
        if not df_categories.empty:
            plt.figure(figsize=(10, 8))
            plt.pie(df_categories['count'], labels=df_categories['classification'], autopct='%1.1f%%')
            plt.title('Email Classification Distribution (Last 30 Days)')
            plt.axis('equal')
            plt.tight_layout()
            plt.savefig(f'{output_dir}/classification_pie.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        # 3. Top Senders Bar Chart
        df_senders = pd.read_sql_query('''
            SELECT sender, COUNT(*) as count
            FROM email_log 
            WHERE date_processed >= datetime('now', '-30 days')
            GROUP BY sender
            ORDER BY count DESC
            LIMIT 15
        ''', conn)
        
        if not df_senders.empty:
            plt.figure(figsize=(12, 8))
            # Truncate long sender names
            df_senders['sender_short'] = df_senders['sender'].str[:30] + '...'
            sns.barplot(data=df_senders, y='sender_short', x='count')
            plt.title('Top Email Senders (Last 30 Days)')
            plt.xlabel('Number of Emails')
            plt.ylabel('Sender')
            plt.tight_layout()
            plt.savefig(f'{output_dir}/top_senders.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        # 4. Classification Confidence Heatmap
        df_confidence = pd.read_sql_query('''
            SELECT classification, 
                   DATE(date_processed) as date,
                   AVG(confidence) as avg_confidence
            FROM email_log 
            WHERE date_processed >= datetime('now', '-14 days')
            GROUP BY classification, DATE(date_processed)
        ''', conn)
        
        if not df_confidence.empty:
            pivot_df = df_confidence.pivot(index='classification', columns='date', values='avg_confidence')
            
            plt.figure(figsize=(14, 8))
            sns.heatmap(pivot_df, annot=True, fmt='.2f', cmap='YlOrRd')
            plt.title('Classification Confidence Over Time')
            plt.xlabel('Date')
            plt.ylabel('Classification')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(f'{output_dir}/confidence_heatmap.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        conn.close()
        
        return f"Analytics dashboard created in {output_dir}/"
    
    def get_business_insights(self):
        """Generate business-specific insights"""
        conn = sqlite3.connect(self.db_path)
        
        insights = {}
        
        # Response time analysis
        cursor = conn.cursor()
        cursor.execute('''
            SELECT AVG(processing_time) as avg_time, classification
            FROM email_log 
            WHERE processing_time > 0
            GROUP BY classification
        ''')
        
        insights['processing_performance'] = {
            row[1]: row[0] for row in cursor.fetchall()
        }
        
        # Peak email times
        cursor.execute('''
            SELECT strftime('%H', date_received) as hour, COUNT(*) as count
            FROM email_log 
            WHERE date_received >= datetime('now', '-30 days')
            GROUP BY strftime('%H', date_received)
            ORDER BY count DESC
        ''')
        
        insights['peak_hours'] = {
            f"{row[0]}:00": row[1] for row in cursor.fetchall()
        }
        
        # Sender priority scoring
        cursor.execute('''
            SELECT sender, COUNT(*) as frequency, 
                   AVG(confidence) as avg_confidence
            FROM email_log 
            WHERE date_processed >= datetime('now', '-30 days')
            GROUP BY sender
            HAVING frequency >= 3
            ORDER BY frequency DESC, avg_confidence DESC
        ''')
        
        insights['priority_senders'] = [
            {
                'sender': row[0],
                'frequency': row[1],
                'avg_confidence': row[2],
                'priority_score': row[1] * row[2]  # Simple scoring
            }
            for row in cursor.fetchall()[:20]
        ]
        
        conn.close()
        return insights

def main():
    """Demo the analytics system"""
    analytics = EmailAnalytics()
    
    # Sample data for demonstration
    sample_emails = [
        {
            'message_id': 'test1@gmail.com',
            'subject': 'Rate confirmation for load ABC123',
            'sender': 'dispatch@freightcompany.com',
            'recipient': 'sean@apexfreightcapital.com',
            'date_received': datetime.now() - timedelta(days=1),
            'classification': 'RateConfirmation',
            'confidence': 0.95,
            'action_taken': 'labeled',
            'processing_time': 0.5
        },
        {
            'message_id': 'test2@gmail.com',
            'subject': 'LinkedIn connection request',
            'sender': 'noreply@linkedin.com',
            'recipient': 'sean@apexfreightcapital.com',
            'date_received': datetime.now() - timedelta(hours=6),
            'classification': 'LinkedIn',
            'confidence': 0.88,
            'action_taken': 'labeled',
            'processing_time': 0.3
        }
    ]
    
    # Log sample data
    for email in sample_emails:
        analytics.log_email_processing(email)
        analytics.update_sender_stats(
            email['sender'], 
            email['sender'].split('@')[0], 
            email['classification']
        )
    
    # Generate reports
    daily_report = analytics.generate_daily_report()
    print("Daily Report Generated:")
    print(json.dumps(daily_report, indent=2, default=str))
    
    # Create dashboard
    dashboard_path = analytics.create_analytics_dashboard()
    print(f"\nAnalytics dashboard created: {dashboard_path}")
    
    # Get business insights
    insights = analytics.get_business_insights()
    print("\nBusiness Insights:")
    print(json.dumps(insights, indent=2, default=str))

if __name__ == "__main__":
    main()