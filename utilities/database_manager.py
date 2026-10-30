#!/usr/bin/env python3
"""
Unified Database Manager
Consolidates all database operations into a single, well-organized system
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

class DatabaseManager:
    """Unified database management for all Gmail AI components"""
    
    def __init__(self, db_path: str = "gmail_ai_unified.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the unified database with all required tables"""
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
                user_feedback TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Smart learning feedback
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_content TEXT,
                predicted_category TEXT,
                user_category TEXT,
                confidence REAL,
                feedback_date DATETIME,
                email_sender TEXT,
                email_subject TEXT,
                is_correction INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Custom categories
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS custom_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                keywords TEXT,
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Business intelligence data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS business_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_id TEXT,
                data_type TEXT,  -- 'rate_sheet', 'invoice', 'dot_compliance'
                data_json TEXT,
                extracted_at DATETIME,
                processed BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Rate sheets
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rate_sheets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                load_id TEXT,
                origin TEXT,
                destination TEXT,
                rate REAL,
                weight INTEGER,
                pickup_date TEXT,
                delivery_date TEXT,
                equipment_type TEXT,
                contact_info TEXT,
                broker TEXT,
                email_id TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Invoices
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT UNIQUE,
                amount REAL,
                due_date TEXT,
                vendor TEXT,
                description TEXT,
                payment_terms TEXT,
                email_id TEXT,
                status TEXT DEFAULT 'pending',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # DOT compliance
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dot_compliance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                violation_type TEXT,
                inspection_date TEXT,
                driver_name TEXT,
                truck_number TEXT,
                fine_amount REAL,
                due_date TEXT,
                email_id TEXT,
                status TEXT DEFAULT 'open',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Automation rules
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS automation_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                trigger_type TEXT,
                trigger_value TEXT,
                action_type TEXT,
                action_value TEXT,
                conditions TEXT,  -- JSON
                enabled BOOLEAN DEFAULT TRUE,
                priority INTEGER DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Security alerts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_id TEXT,
                alert_type TEXT,
                risk_score INTEGER,
                description TEXT,
                details TEXT,  -- JSON
                resolved BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Analytics data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT,
                metric_value REAL,
                metric_data TEXT,  -- JSON
                date_recorded DATE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_email_log_message_id ON email_log(message_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_email_log_date ON email_log(date_processed)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_learning_feedback_date ON learning_feedback(feedback_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_business_data_type ON business_data(data_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_rate_sheets_load_id ON rate_sheets(load_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_invoices_number ON invoices(invoice_number)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_security_alerts_resolved ON security_alerts(resolved)')
        
        conn.commit()
        conn.close()
        print(f"✅ Unified database initialized: {self.db_path}")
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """Execute query and return results as list of dictionaries"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, params)
            results = [dict(row) for row in cursor.fetchall()]
            return results
        finally:
            conn.close()
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute update query and return number of affected rows"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()
    
    def insert_email_log(self, email_data: Dict[str, Any]) -> int:
        """Insert email processing log entry"""
        query = '''
            INSERT INTO email_log 
            (message_id, subject, sender, recipient, date_received, date_processed, 
             classification, confidence, action_taken, processing_time, user_feedback)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        params = (
            email_data.get('message_id'),
            email_data.get('subject'),
            email_data.get('sender'),
            email_data.get('recipient'),
            email_data.get('date_received'),
            email_data.get('date_processed'),
            email_data.get('classification'),
            email_data.get('confidence'),
            email_data.get('action_taken'),
            email_data.get('processing_time'),
            email_data.get('user_feedback')
        )
        return self.execute_update(query, params)
    
    def insert_learning_feedback(self, feedback_data: Dict[str, Any]) -> int:
        """Insert learning feedback entry"""
        query = '''
            INSERT INTO learning_feedback 
            (email_content, predicted_category, user_category, confidence, 
             feedback_date, email_sender, email_subject, is_correction)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        params = (
            feedback_data.get('email_content'),
            feedback_data.get('predicted_category'),
            feedback_data.get('user_category'),
            feedback_data.get('confidence'),
            feedback_data.get('feedback_date'),
            feedback_data.get('email_sender'),
            feedback_data.get('email_subject'),
            feedback_data.get('is_correction', 0)
        )
        return self.execute_update(query, params)
    
    def insert_rate_sheet(self, rate_data: Dict[str, Any]) -> int:
        """Insert rate sheet data"""
        query = '''
            INSERT INTO rate_sheets 
            (load_id, origin, destination, rate, weight, pickup_date, 
             delivery_date, equipment_type, contact_info, broker, email_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        params = (
            rate_data.get('load_id'),
            rate_data.get('origin'),
            rate_data.get('destination'),
            rate_data.get('rate'),
            rate_data.get('weight'),
            rate_data.get('pickup_date'),
            rate_data.get('delivery_date'),
            rate_data.get('equipment_type'),
            rate_data.get('contact_info'),
            rate_data.get('broker'),
            rate_data.get('email_id')
        )
        return self.execute_update(query, params)
    
    def insert_invoice(self, invoice_data: Dict[str, Any]) -> int:
        """Insert invoice data"""
        query = '''
            INSERT INTO invoices 
            (invoice_number, amount, due_date, vendor, description, 
             payment_terms, email_id, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        params = (
            invoice_data.get('invoice_number'),
            invoice_data.get('amount'),
            invoice_data.get('due_date'),
            invoice_data.get('vendor'),
            invoice_data.get('description'),
            invoice_data.get('payment_terms'),
            invoice_data.get('email_id'),
            invoice_data.get('status', 'pending')
        )
        return self.execute_update(query, params)
    
    def get_analytics_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get analytics summary for the last N days"""
        query = '''
            SELECT 
                COUNT(*) as total_emails,
                COUNT(CASE WHEN classification IS NOT NULL THEN 1 END) as classified_emails,
                AVG(confidence) as avg_confidence,
                COUNT(CASE WHEN action_taken = 'label' THEN 1 END) as labeled_emails,
                COUNT(CASE WHEN action_taken = 'archive' THEN 1 END) as archived_emails
            FROM email_log 
            WHERE date_processed >= datetime('now', '-{} days')
        '''.format(days)
        
        results = self.execute_query(query)
        return results[0] if results else {}
    
    def get_classification_performance(self) -> Dict[str, Any]:
        """Get classification performance metrics"""
        query = '''
            SELECT 
                predicted_category,
                user_category,
                COUNT(*) as count,
                AVG(confidence) as avg_confidence
            FROM learning_feedback 
            WHERE feedback_date >= datetime('now', '-30 days')
            GROUP BY predicted_category, user_category
        '''
        
        return self.execute_query(query)
    
    def migrate_old_databases(self):
        """Migrate data from old separate databases"""
        print("🔄 Migrating data from old databases...")
        
        # List of old database files to migrate
        old_dbs = [
            "email_analytics.db",
            "smart_learning.db", 
            "business_intelligence.db",
            "automation.db",
            "security_compliance.db",
            "data/email_analytics.db",
            "data/smart_learning.db",
            "data/business_intelligence.db",
            "data/automation.db",
            "data/security_compliance.db"
        ]
        
        migrated_count = 0
        for db_path in old_dbs:
            if os.path.exists(db_path):
                try:
                    self._migrate_database(db_path)
                    migrated_count += 1
                    print(f"✅ Migrated: {db_path}")
                except Exception as e:
                    print(f"⚠️ Failed to migrate {db_path}: {e}")
        
        print(f"🔄 Migration complete: {migrated_count} databases processed")
    
    def _migrate_database(self, old_db_path: str):
        """Migrate individual database"""
        # This would contain specific migration logic for each old database
        # For now, just a placeholder
        pass

# Global database manager instance
db_manager = DatabaseManager()

def get_database_manager() -> DatabaseManager:
    """Get the global database manager instance"""
    return db_manager

if __name__ == "__main__":
    # Initialize and test database
    db = DatabaseManager()
    print("✅ Database manager initialized successfully")
    
    # Test analytics summary
    summary = db.get_analytics_summary()
    print(f"📊 Analytics summary: {summary}")
