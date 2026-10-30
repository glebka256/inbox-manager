#!/usr/bin/env python3
"""
Business Intelligence Email Processor
Specialized processor for freight and business email analysis
"""

import re
import json
import sqlite3
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import pandas as pd

@dataclass
class RateSheet:
    """Rate sheet information extracted from email"""
    load_id: str
    origin: str
    destination: str
    rate: float
    weight: Optional[int] = None
    pickup_date: Optional[str] = None
    delivery_date: Optional[str] = None
    equipment_type: Optional[str] = None
    contact_info: Optional[str] = None
    broker: Optional[str] = None

@dataclass
class Invoice:
    """Invoice information extracted from email"""
    invoice_number: str
    amount: float
    due_date: Optional[str] = None
    vendor: Optional[str] = None
    description: Optional[str] = None
    payment_terms: Optional[str] = None

@dataclass
class DOTCompliance:
    """DOT compliance information"""
    violation_type: Optional[str] = None
    inspection_date: Optional[str] = None
    driver_name: Optional[str] = None
    truck_number: Optional[str] = None
    fine_amount: Optional[float] = None
    due_date: Optional[str] = None

class BusinessIntelligenceProcessor:
    def __init__(self, db_path="business_intelligence.db"):
        self.db_path = db_path
        self.init_database()
        
        # Regex patterns for data extraction
        self.patterns = {
            'rate': [
                r'\$[\d,]+\.?\d*',
                r'rate[:\s]+\$?[\d,]+\.?\d*',
                r'pay[:\s]+\$?[\d,]+\.?\d*'
            ],
            'load_id': [
                r'load[#\s:]*([A-Z0-9]+)',
                r'reference[#\s:]*([A-Z0-9]+)',
                r'job[#\s:]*([A-Z0-9]+)'
            ],
            'weight': [
                r'(\d{1,3}(?:,\d{3})*)\s*(?:lbs?|pounds?)',
                r'weight[:\s]+(\d{1,3}(?:,\d{3})*)'
            ],
            'dates': [
                r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}',
                r'\d{4}-\d{2}-\d{2}',
                r'(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}'
            ],
            'cities': [
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z]{2})',
                r'from\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'to\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
            ],
            'invoice_number': [
                r'invoice[#\s:]*([A-Z0-9\-]+)',
                r'inv[#\s:]*([A-Z0-9\-]+)',
                r'bill[#\s:]*([A-Z0-9\-]+)'
            ],
            'dot_violations': [
                r'violation[:\s]+([A-Za-z0-9\s]+)',
                r'fine[:\s]+\$?([\d,]+\.?\d*)',
                r'CSA\s+score[:\s]+([\d.]+)'
            ]
        }
    
    def init_database(self):
        """Initialize business intelligence database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Rate sheets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rate_sheets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_id TEXT,
                load_id TEXT,
                origin TEXT,
                destination TEXT,
                rate REAL,
                weight INTEGER,
                pickup_date TEXT,
                delivery_date TEXT,
                equipment_type TEXT,
                broker TEXT,
                contact_info TEXT,
                extracted_date DATETIME,
                email_sender TEXT,
                confidence_score REAL
            )
        ''')
        
        # Invoices table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_id TEXT,
                invoice_number TEXT,
                amount REAL,
                due_date TEXT,
                vendor TEXT,
                description TEXT,
                payment_terms TEXT,
                extracted_date DATETIME,
                email_sender TEXT,
                status TEXT DEFAULT 'pending'
            )
        ''')
        
        # DOT compliance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dot_compliance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_id TEXT,
                violation_type TEXT,
                inspection_date TEXT,
                driver_name TEXT,
                truck_number TEXT,
                fine_amount REAL,
                due_date TEXT,
                extracted_date DATETIME,
                status TEXT DEFAULT 'open'
            )
        ''')
        
        # Business metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS business_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_date DATE,
                total_loads INTEGER,
                total_revenue REAL,
                avg_rate_per_mile REAL,
                pending_invoices INTEGER,
                outstanding_amount REAL,
                dot_violations INTEGER,
                compliance_score REAL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def extract_rate_sheet(self, email_content: str, subject: str, sender: str) -> Optional[RateSheet]:
        """Extract rate sheet information from email"""
        content = f"{subject} {email_content}".lower()
        
        # Check if this looks like a rate sheet
        rate_indicators = ['rate', 'load', 'pickup', 'delivery', 'freight', 'miles']
        if not any(indicator in content for indicator in rate_indicators):
            return None
        
        rate_sheet = RateSheet("", "", "", 0.0)
        
        # Extract rate
        for pattern in self.patterns['rate']:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                rate_str = matches[0].replace('$', '').replace(',', '')
                try:
                    rate_sheet.rate = float(rate_str)
                    break
                except ValueError:
                    continue
        
        # Extract load ID
        for pattern in self.patterns['load_id']:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                rate_sheet.load_id = matches[0]
                break
        
        # Extract weight
        for pattern in self.patterns['weight']:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                try:
                    rate_sheet.weight = int(matches[0].replace(',', ''))
                    break
                except ValueError:
                    continue
        
        # Extract cities (origin/destination)
        city_matches = re.findall(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z]{2})', email_content)
        if len(city_matches) >= 2:
            rate_sheet.origin = f"{city_matches[0][0]}, {city_matches[0][1]}"
            rate_sheet.destination = f"{city_matches[1][0]}, {city_matches[1][1]}"
        elif len(city_matches) == 1:
            rate_sheet.origin = f"{city_matches[0][0]}, {city_matches[0][1]}"
        
        # Extract dates
        date_matches = re.findall(self.patterns['dates'][0], email_content)
        if len(date_matches) >= 2:
            rate_sheet.pickup_date = date_matches[0]
            rate_sheet.delivery_date = date_matches[1]
        elif len(date_matches) == 1:
            rate_sheet.pickup_date = date_matches[0]
        
        # Extract equipment type
        equipment_types = ['van', 'reefer', 'flatbed', 'step deck', 'lowboy', 'tanker']
        for equip_type in equipment_types:
            if equip_type in content:
                rate_sheet.equipment_type = equip_type
                break
        
        # Set broker from sender
        if '@' in sender:
            rate_sheet.broker = sender.split('@')[1]
        
        # Only return if we found meaningful data
        if rate_sheet.rate > 0 or rate_sheet.load_id:
            return rate_sheet
        
        return None
    
    def extract_invoice(self, email_content: str, subject: str, sender: str) -> Optional[Invoice]:
        """Extract invoice information from email"""
        content = f"{subject} {email_content}".lower()
        
        # Check if this looks like an invoice
        invoice_indicators = ['invoice', 'bill', 'payment', 'due', 'amount']
        if not any(indicator in content for indicator in invoice_indicators):
            return None
        
        invoice = Invoice("", 0.0)
        
        # Extract invoice number
        for pattern in self.patterns['invoice_number']:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                invoice.invoice_number = matches[0]
                break
        
        # Extract amount
        amount_patterns = [
            r'amount[:\s]+\$?([\d,]+\.?\d*)',
            r'total[:\s]+\$?([\d,]+\.?\d*)',
            r'\$[\d,]+\.?\d*'
        ]
        for pattern in amount_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                try:
                    amount_str = matches[0].replace('$', '').replace(',', '')
                    invoice.amount = float(amount_str)
                    break
                except ValueError:
                    continue
        
        # Extract due date
        due_date_patterns = [
            r'due[:\s]+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'payment\s+due[:\s]+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})'
        ]
        for pattern in due_date_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                invoice.due_date = matches[0]
                break
        
        # Extract vendor from sender
        if '@' in sender:
            invoice.vendor = sender
        
        # Extract payment terms
        terms_patterns = [
            r'net\s+(\d+)',
            r'payment\s+terms[:\s]+([^.\n]+)'
        ]
        for pattern in terms_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                invoice.payment_terms = matches[0]
                break
        
        if invoice.amount > 0 or invoice.invoice_number:
            return invoice
        
        return None
    
    def extract_dot_compliance(self, email_content: str, subject: str, sender: str) -> Optional[DOTCompliance]:
        """Extract DOT compliance information from email"""
        content = f"{subject} {email_content}".lower()
        
        # Check if this is DOT related
        dot_indicators = ['dot', 'inspection', 'violation', 'compliance', 'csa', 'fmcsa']
        if not any(indicator in content for indicator in dot_indicators):
            return None
        
        dot_info = DOTCompliance()
        
        # Extract violation type
        violation_patterns = [
            r'violation[:\s]+([A-Za-z0-9\s\-]+)(?:\n|\.)',
            r'cited\s+for[:\s]+([A-Za-z0-9\s\-]+)(?:\n|\.)',
            r'infraction[:\s]+([A-Za-z0-9\s\-]+)(?:\n|\.)'
        ]
        for pattern in violation_patterns:
            matches = re.findall(pattern, email_content, re.IGNORECASE)
            if matches:
                dot_info.violation_type = matches[0].strip()
                break
        
        # Extract fine amount
        fine_patterns = [
            r'fine[:\s]+\$?([\d,]+\.?\d*)',
            r'penalty[:\s]+\$?([\d,]+\.?\d*)',
            r'amount\s+due[:\s]+\$?([\d,]+\.?\d*)'
        ]
        for pattern in fine_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                try:
                    fine_str = matches[0].replace(',', '')
                    dot_info.fine_amount = float(fine_str)
                    break
                except ValueError:
                    continue
        
        # Extract driver and truck info
        driver_patterns = [
            r'driver[:\s]+([A-Za-z\s]+)(?:\n|,)',
            r'operator[:\s]+([A-Za-z\s]+)(?:\n|,)'
        ]
        for pattern in driver_patterns:
            matches = re.findall(pattern, email_content, re.IGNORECASE)
            if matches:
                dot_info.driver_name = matches[0].strip()
                break
        
        truck_patterns = [
            r'truck[#\s:]*([A-Z0-9\-]+)',
            r'vehicle[#\s:]*([A-Z0-9\-]+)',
            r'unit[#\s:]*([A-Z0-9\-]+)'
        ]
        for pattern in truck_patterns:
            matches = re.findall(pattern, email_content, re.IGNORECASE)
            if matches:
                dot_info.truck_number = matches[0]
                break
        
        # Extract dates
        date_matches = re.findall(self.patterns['dates'][0], email_content)
        if date_matches:
            dot_info.inspection_date = date_matches[0]
            if len(date_matches) > 1:
                dot_info.due_date = date_matches[1]
        
        if dot_info.violation_type or dot_info.fine_amount:
            return dot_info
        
        return None
    
    def process_business_email(self, email_id: str, email_content: str, 
                             subject: str, sender: str) -> Dict:
        """Process email for business intelligence extraction"""
        results = {
            'rate_sheet': None,
            'invoice': None,
            'dot_compliance': None,
            'extracted_data': {}
        }
        
        # Try to extract rate sheet
        rate_sheet = self.extract_rate_sheet(email_content, subject, sender)
        if rate_sheet:
            self.save_rate_sheet(email_id, rate_sheet, sender)
            results['rate_sheet'] = rate_sheet
        
        # Try to extract invoice
        invoice = self.extract_invoice(email_content, subject, sender)
        if invoice:
            self.save_invoice(email_id, invoice, sender)
            results['invoice'] = invoice
        
        # Try to extract DOT compliance
        dot_info = self.extract_dot_compliance(email_content, subject, sender)
        if dot_info:
            self.save_dot_compliance(email_id, dot_info)
            results['dot_compliance'] = dot_info
        
        return results
    
    def save_rate_sheet(self, email_id: str, rate_sheet: RateSheet, sender: str):
        """Save rate sheet to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO rate_sheets 
            (email_id, load_id, origin, destination, rate, weight, pickup_date, 
             delivery_date, equipment_type, broker, contact_info, extracted_date, 
             email_sender, confidence_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            email_id, rate_sheet.load_id, rate_sheet.origin, rate_sheet.destination,
            rate_sheet.rate, rate_sheet.weight, rate_sheet.pickup_date,
            rate_sheet.delivery_date, rate_sheet.equipment_type, rate_sheet.broker,
            rate_sheet.contact_info, datetime.now(), sender, 0.8
        ))
        
        conn.commit()
        conn.close()
    
    def save_invoice(self, email_id: str, invoice: Invoice, sender: str):
        """Save invoice to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO invoices 
            (email_id, invoice_number, amount, due_date, vendor, description, 
             payment_terms, extracted_date, email_sender)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            email_id, invoice.invoice_number, invoice.amount, invoice.due_date,
            invoice.vendor, invoice.description, invoice.payment_terms,
            datetime.now(), sender
        ))
        
        conn.commit()
        conn.close()
    
    def save_dot_compliance(self, email_id: str, dot_info: DOTCompliance):
        """Save DOT compliance info to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO dot_compliance 
            (email_id, violation_type, inspection_date, driver_name, truck_number, 
             fine_amount, due_date, extracted_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            email_id, dot_info.violation_type, dot_info.inspection_date,
            dot_info.driver_name, dot_info.truck_number, dot_info.fine_amount,
            dot_info.due_date, datetime.now()
        ))
        
        conn.commit()
        conn.close()
    
    def generate_business_report(self) -> Dict:
        """Generate comprehensive business intelligence report"""
        conn = sqlite3.connect(self.db_path)
        
        report = {}
        
        # Rate sheet analytics
        df_rates = pd.read_sql_query('''
            SELECT * FROM rate_sheets 
            WHERE extracted_date >= datetime('now', '-30 days')
        ''', conn)
        
        if not df_rates.empty:
            report['rate_sheets'] = {
                'total_loads': len(df_rates),
                'total_revenue': df_rates['rate'].sum(),
                'avg_rate': df_rates['rate'].mean(),
                'avg_weight': df_rates['weight'].mean() if 'weight' in df_rates else 0,
                'top_brokers': df_rates['broker'].value_counts().head().to_dict(),
                'equipment_breakdown': df_rates['equipment_type'].value_counts().to_dict()
            }
        
        # Invoice analytics
        df_invoices = pd.read_sql_query('''
            SELECT * FROM invoices 
            WHERE extracted_date >= datetime('now', '-30 days')
        ''', conn)
        
        if not df_invoices.empty:
            pending_invoices = df_invoices[df_invoices['status'] == 'pending']
            report['invoices'] = {
                'total_invoices': len(df_invoices),
                'total_amount': df_invoices['amount'].sum(),
                'pending_count': len(pending_invoices),
                'pending_amount': pending_invoices['amount'].sum(),
                'avg_invoice_amount': df_invoices['amount'].mean()
            }
        
        # DOT compliance
        df_dot = pd.read_sql_query('''
            SELECT * FROM dot_compliance 
            WHERE extracted_date >= datetime('now', '-90 days')
        ''', conn)
        
        if not df_dot.empty:
            report['dot_compliance'] = {
                'total_violations': len(df_dot),
                'total_fines': df_dot['fine_amount'].sum(),
                'open_violations': len(df_dot[df_dot['status'] == 'open']),
                'violation_types': df_dot['violation_type'].value_counts().to_dict(),
                'avg_fine': df_dot['fine_amount'].mean()
            }
        
        conn.close()
        return report
    
    def get_overdue_items(self) -> Dict:
        """Get overdue invoices and compliance items"""
        conn = sqlite3.connect(self.db_path)
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Overdue invoices
        overdue_invoices = pd.read_sql_query('''
            SELECT * FROM invoices 
            WHERE due_date < ? AND status = 'pending'
            ORDER BY due_date
        ''', conn, params=[today])
        
        # Overdue DOT compliance
        overdue_dot = pd.read_sql_query('''
            SELECT * FROM dot_compliance 
            WHERE due_date < ? AND status = 'open'
            ORDER BY due_date
        ''', conn, params=[today])
        
        conn.close()
        
        return {
            'overdue_invoices': overdue_invoices.to_dict('records'),
            'overdue_compliance': overdue_dot.to_dict('records')
        }

def main():
    """Demo the business intelligence processor"""
    processor = BusinessIntelligenceProcessor()
    
    # Test rate sheet extraction
    rate_email = """
    Subject: Rate Confirmation - Load #ABC123
    
    Rate: $2,500
    Load ID: ABC123
    From: Chicago, IL
    To: Atlanta, GA
    Weight: 45,000 lbs
    Pickup: 12/15/2024
    Equipment: Van
    """
    
    result = processor.process_business_email(
        "test1", rate_email, "Rate Confirmation - Load #ABC123", 
        "dispatch@freightbroker.com"
    )
    
    print("Extracted Rate Sheet:")
    if result['rate_sheet']:
        print(f"Load ID: {result['rate_sheet'].load_id}")
        print(f"Rate: ${result['rate_sheet'].rate}")
        print(f"Route: {result['rate_sheet'].origin} -> {result['rate_sheet'].destination}")
    
    # Generate business report
    report = processor.generate_business_report()
    print("\nBusiness Intelligence Report:")
    print(json.dumps(report, indent=2, default=str))

if __name__ == "__main__":
    main()