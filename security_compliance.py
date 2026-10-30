#!/usr/bin/env python3
"""
Security & Compliance Monitor
Advanced security monitoring and compliance tracking for Gmail AI
"""

import sqlite3
import json
import hashlib
import re
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Optional
import logging

@dataclass
class SecurityAlert:
    id: int
    alert_type: str
    severity: str  # low, medium, high, critical
    description: str
    email_id: str
    detected_at: datetime
    resolved: bool = False
    resolution_notes: str = None

@dataclass
class ComplianceCheck:
    check_name: str
    description: str
    status: str  # pass, fail, warning
    details: str
    last_check: datetime

class SecurityComplianceMonitor:
    def __init__(self, db_path="security_compliance.db"):
        self.db_path = db_path
        self.init_database()
        
        # Security patterns
        self.security_patterns = {
            'phishing_indicators': [
                r'urgent\s+action\s+required',
                r'verify\s+your\s+account',
                r'click\s+here\s+immediately',
                r'suspended\s+account',
                r'security\s+alert',
                r'confirm\s+identity'
            ],
            'suspicious_links': [
                r'bit\.ly',
                r'tinyurl\.com',
                r'short\.link',
                r'suspicious-domain\.com'
            ],
            'data_breach_indicators': [
                r'password\s+compromised',
                r'data\s+breach',
                r'unauthorized\s+access',
                r'security\s+incident'
            ],
            'financial_fraud': [
                r'wire\s+transfer\s+urgently',
                r'send\s+money\s+immediately',
                r'invoice\s+payment\s+overdue',
                r'bank\s+account\s+verification'
            ]
        }
        
        # DOT compliance patterns for freight business
        self.dot_compliance_patterns = {
            'hours_violations': [
                r'hours\s+of\s+service\s+violation',
                r'logbook\s+violation',
                r'driving\s+time\s+exceeded'
            ],
            'inspection_failures': [
                r'failed\s+inspection',
                r'out\s+of\s+service',
                r'vehicle\s+defect'
            ],
            'documentation_issues': [
                r'missing\s+documentation',
                r'incomplete\s+paperwork',
                r'permit\s+expired'
            ]
        }
    
    def init_database(self):
        """Initialize security and compliance database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Security alerts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_type TEXT,
                severity TEXT,
                description TEXT,
                email_id TEXT,
                email_subject TEXT,
                email_sender TEXT,
                detected_at DATETIME,
                resolved INTEGER DEFAULT 0,
                resolution_notes TEXT,
                false_positive INTEGER DEFAULT 0
            )
        ''')
        
        # Compliance checks
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS compliance_checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                check_name TEXT,
                check_type TEXT,
                status TEXT,
                details TEXT,
                last_check DATETIME,
                next_check DATETIME,
                auto_check INTEGER DEFAULT 1
            )
        ''')
        
        # Security metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_date DATE,
                total_emails_scanned INTEGER,
                threats_detected INTEGER,
                phishing_attempts INTEGER,
                malware_detected INTEGER,
                compliance_violations INTEGER,
                false_positives INTEGER
            )
        ''')
        
        # Data access log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS access_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                action TEXT,
                resource TEXT,
                timestamp DATETIME,
                ip_address TEXT,
                success INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Initialize compliance checks
        self.init_compliance_checks()
    
    def init_compliance_checks(self):
        """Initialize default compliance checks"""
        default_checks = [
            {
                'check_name': 'DOT Hours of Service',
                'check_type': 'regulatory',
                'description': 'Monitor for hours of service violations',
                'auto_check': True
            },
            {
                'check_name': 'Data Retention Policy',
                'check_type': 'data_protection',
                'description': 'Ensure email data retention compliance',
                'auto_check': True
            },
            {
                'check_name': 'PII Detection',
                'check_type': 'privacy',
                'description': 'Detect and protect personally identifiable information',
                'auto_check': True
            },
            {
                'check_name': 'Financial Data Security',
                'check_type': 'financial',
                'description': 'Monitor financial information security',
                'auto_check': True
            }
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for check in default_checks:
            cursor.execute('''
                INSERT OR IGNORE INTO compliance_checks 
                (check_name, check_type, status, details, last_check, auto_check)
                VALUES (?, ?, 'pending', 'Initial setup', ?, ?)
            ''', (
                check['check_name'],
                check['check_type'],
                datetime.now(),
                1 if check['auto_check'] else 0
            ))
        
        conn.commit()
        conn.close()
    
    def scan_email_security(self, email_data: Dict) -> List[SecurityAlert]:
        """Scan email for security threats"""
        alerts = []
        
        email_id = email_data.get('message_id', '')
        subject = email_data.get('subject', '').lower()
        sender = email_data.get('sender', '').lower()
        body = email_data.get('body', '').lower()
        content = f"{subject} {body}"
        
        # Check for phishing indicators
        phishing_score = 0
        phishing_indicators = []
        
        for pattern in self.security_patterns['phishing_indicators']:
            if re.search(pattern, content, re.IGNORECASE):
                phishing_score += 1
                phishing_indicators.append(pattern)
        
        if phishing_score >= 2:
            alert = self.create_security_alert(
                alert_type='phishing',
                severity='high' if phishing_score >= 3 else 'medium',
                description=f'Potential phishing email detected. Indicators: {", ".join(phishing_indicators)}',
                email_id=email_id,
                email_data=email_data
            )
            alerts.append(alert)
        
        # Check for suspicious links
        for pattern in self.security_patterns['suspicious_links']:
            if re.search(pattern, content, re.IGNORECASE):
                alert = self.create_security_alert(
                    alert_type='suspicious_link',
                    severity='medium',
                    description=f'Suspicious link detected: {pattern}',
                    email_id=email_id,
                    email_data=email_data
                )
                alerts.append(alert)
        
        # Check for data breach indicators
        for pattern in self.security_patterns['data_breach_indicators']:
            if re.search(pattern, content, re.IGNORECASE):
                alert = self.create_security_alert(
                    alert_type='data_breach',
                    severity='critical',
                    description=f'Potential data breach notification: {pattern}',
                    email_id=email_id,
                    email_data=email_data
                )
                alerts.append(alert)
        
        # Check for financial fraud
        for pattern in self.security_patterns['financial_fraud']:
            if re.search(pattern, content, re.IGNORECASE):
                alert = self.create_security_alert(
                    alert_type='financial_fraud',
                    severity='high',
                    description=f'Potential financial fraud attempt: {pattern}',
                    email_id=email_id,
                    email_data=email_data
                )
                alerts.append(alert)
        
        # Check sender reputation (basic implementation)
        if self.is_suspicious_sender(sender):
            alert = self.create_security_alert(
                alert_type='suspicious_sender',
                severity='medium',
                description=f'Email from suspicious sender: {sender}',
                email_id=email_id,
                email_data=email_data
            )
            alerts.append(alert)
        
        return alerts
    
    def check_dot_compliance(self, email_data: Dict) -> List[Dict]:
        """Check DOT compliance issues"""
        compliance_issues = []
        
        email_id = email_data.get('message_id', '')
        subject = email_data.get('subject', '').lower()
        body = email_data.get('body', '').lower()
        content = f"{subject} {body}"
        
        # Hours of service violations
        for pattern in self.dot_compliance_patterns['hours_violations']:
            if re.search(pattern, content, re.IGNORECASE):
                compliance_issues.append({
                    'type': 'hours_violation',
                    'severity': 'high',
                    'description': f'Hours of service violation detected: {pattern}',
                    'email_id': email_id
                })
        
        # Inspection failures
        for pattern in self.dot_compliance_patterns['inspection_failures']:
            if re.search(pattern, content, re.IGNORECASE):
                compliance_issues.append({
                    'type': 'inspection_failure',
                    'severity': 'critical',
                    'description': f'Vehicle inspection failure: {pattern}',
                    'email_id': email_id
                })
        
        # Documentation issues
        for pattern in self.dot_compliance_patterns['documentation_issues']:
            if re.search(pattern, content, re.IGNORECASE):
                compliance_issues.append({
                    'type': 'documentation_issue',
                    'severity': 'medium',
                    'description': f'Documentation issue: {pattern}',
                    'email_id': email_id
                })
        
        return compliance_issues
    
    def detect_pii(self, email_data: Dict) -> List[Dict]:
        """Detect personally identifiable information"""
        pii_findings = []
        
        content = f"{email_data.get('subject', '')} {email_data.get('body', '')}"
        
        # SSN pattern
        ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
        if re.search(ssn_pattern, content):
            pii_findings.append({
                'type': 'ssn',
                'severity': 'high',
                'description': 'Social Security Number detected',
                'pattern': ssn_pattern
            })
        
        # Credit card pattern (basic)
        cc_pattern = r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
        if re.search(cc_pattern, content):
            pii_findings.append({
                'type': 'credit_card',
                'severity': 'critical',
                'description': 'Credit card number detected',
                'pattern': cc_pattern
            })
        
        # Phone number pattern
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        phone_matches = re.findall(phone_pattern, content)
        if len(phone_matches) > 2:  # Multiple phone numbers might indicate PII
            pii_findings.append({
                'type': 'phone_numbers',
                'severity': 'medium',
                'description': f'Multiple phone numbers detected: {len(phone_matches)}',
                'pattern': phone_pattern
            })
        
        # Driver license patterns (state-specific examples)
        dl_patterns = [
            r'\bDL[#:\s]*[A-Z0-9]{8,}\b',  # Generic
            r'\b[A-Z]\d{7}\b',  # California style
            r'\b\d{3}-\d{2}-\d{4}\b'  # Some states use SSN format
        ]
        
        for pattern in dl_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                pii_findings.append({
                    'type': 'drivers_license',
                    'severity': 'high',
                    'description': 'Driver license number detected',
                    'pattern': pattern
                })
                break
        
        return pii_findings
    
    def create_security_alert(self, alert_type: str, severity: str, 
                            description: str, email_id: str, email_data: Dict) -> SecurityAlert:
        """Create and save security alert"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO security_alerts 
            (alert_type, severity, description, email_id, email_subject, 
             email_sender, detected_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            alert_type, severity, description, email_id,
            email_data.get('subject', ''),
            email_data.get('sender', ''),
            datetime.now()
        ))
        
        alert_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return SecurityAlert(
            id=alert_id,
            alert_type=alert_type,
            severity=severity,
            description=description,
            email_id=email_id,
            detected_at=datetime.now()
        )
    
    def is_suspicious_sender(self, sender: str) -> bool:
        """Check if sender is suspicious (basic implementation)"""
        suspicious_domains = [
            'tempmail.com',
            '10minutemail.com',
            'guerrillamail.com',
            'mailinator.com'
        ]
        
        suspicious_patterns = [
            r'[0-9]{8,}@',  # Numeric usernames
            r'noreply.*random',  # Suspicious noreply addresses
            r'[a-z]{20,}@'  # Very long random usernames
        ]
        
        # Check domains
        if '@' in sender:
            domain = sender.split('@')[1]
            if domain in suspicious_domains:
                return True
        
        # Check patterns
        for pattern in suspicious_patterns:
            if re.search(pattern, sender, re.IGNORECASE):
                return True
        
        return False
    
    def run_comprehensive_scan(self, email_data: Dict) -> Dict:
        """Run comprehensive security and compliance scan"""
        results = {
            'email_id': email_data.get('message_id'),
            'scan_timestamp': datetime.now().isoformat(),
            'security_alerts': [],
            'compliance_issues': [],
            'pii_findings': [],
            'risk_score': 0
        }
        
        # Security scan
        security_alerts = self.scan_email_security(email_data)
        results['security_alerts'] = [
            {
                'type': alert.alert_type,
                'severity': alert.severity,
                'description': alert.description
            }
            for alert in security_alerts
        ]
        
        # DOT compliance check
        compliance_issues = self.check_dot_compliance(email_data)
        results['compliance_issues'] = compliance_issues
        
        # PII detection
        pii_findings = self.detect_pii(email_data)
        results['pii_findings'] = pii_findings
        
        # Calculate risk score
        risk_score = 0
        for alert in security_alerts:
            if alert.severity == 'critical':
                risk_score += 10
            elif alert.severity == 'high':
                risk_score += 7
            elif alert.severity == 'medium':
                risk_score += 4
            elif alert.severity == 'low':
                risk_score += 1
        
        for issue in compliance_issues:
            if issue['severity'] == 'critical':
                risk_score += 8
            elif issue['severity'] == 'high':
                risk_score += 5
            elif issue['severity'] == 'medium':
                risk_score += 3
        
        for finding in pii_findings:
            if finding['severity'] == 'critical':
                risk_score += 9
            elif finding['severity'] == 'high':
                risk_score += 6
            elif finding['severity'] == 'medium':
                risk_score += 3
        
        results['risk_score'] = min(risk_score, 100)  # Cap at 100
        
        return results
    
    def get_security_dashboard(self) -> Dict:
        """Get security dashboard data"""
        conn = sqlite3.connect(self.db_path)
        
        dashboard = {}
        
        # Recent alerts
        cursor = conn.cursor()
        cursor.execute('''
            SELECT alert_type, severity, COUNT(*) as count
            FROM security_alerts
            WHERE detected_at >= datetime('now', '-30 days') AND resolved = 0
            GROUP BY alert_type, severity
            ORDER BY count DESC
        ''')
        
        dashboard['recent_alerts'] = [
            {
                'type': row[0],
                'severity': row[1],
                'count': row[2]
            }
            for row in cursor.fetchall()
        ]
        
        # Alert summary
        cursor.execute('''
            SELECT 
                COUNT(*) as total_alerts,
                SUM(CASE WHEN severity = 'critical' THEN 1 ELSE 0 END) as critical,
                SUM(CASE WHEN severity = 'high' THEN 1 ELSE 0 END) as high,
                SUM(CASE WHEN severity = 'medium' THEN 1 ELSE 0 END) as medium,
                SUM(CASE WHEN resolved = 0 THEN 1 ELSE 0 END) as unresolved
            FROM security_alerts
            WHERE detected_at >= datetime('now', '-30 days')
        ''')
        
        row = cursor.fetchone()
        dashboard['alert_summary'] = {
            'total': row[0],
            'critical': row[1],
            'high': row[2],
            'medium': row[3],
            'unresolved': row[4]
        }
        
        # Compliance status
        cursor.execute('''
            SELECT check_name, status, last_check
            FROM compliance_checks
            WHERE auto_check = 1
            ORDER BY last_check DESC
        ''')
        
        dashboard['compliance_checks'] = [
            {
                'name': row[0],
                'status': row[1],
                'last_check': row[2]
            }
            for row in cursor.fetchall()
        ]
        
        conn.close()
        return dashboard
    
    def resolve_alert(self, alert_id: int, resolution_notes: str = None, 
                     false_positive: bool = False):
        """Resolve a security alert"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE security_alerts 
            SET resolved = 1, resolution_notes = ?, false_positive = ?
            WHERE id = ?
        ''', (resolution_notes, 1 if false_positive else 0, alert_id))
        
        conn.commit()
        conn.close()
    
    def log_access(self, user_id: str, action: str, resource: str, 
                   ip_address: str = None, success: bool = True):
        """Log access attempts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO access_log 
            (user_id, action, resource, timestamp, ip_address, success)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, action, resource, datetime.now(), ip_address, 1 if success else 0))
        
        conn.commit()
        conn.close()

def main():
    """Demo the security and compliance monitor"""
    monitor = SecurityComplianceMonitor()
    
    # Test email data
    test_emails = [
        {
            'message_id': 'test_phishing',
            'subject': 'URGENT: Verify your account immediately!',
            'sender': 'security@suspicious-bank.com',
            'body': 'Your account has been suspended. Click here immediately to verify your identity and prevent permanent closure.',
            'date_received': datetime.now()
        },
        {
            'message_id': 'test_dot',
            'subject': 'DOT Inspection Failure Notice',
            'sender': 'dot@transportation.gov',
            'body': 'Vehicle unit #123 failed inspection due to brake violations. Driver John Smith exceeded hours of service limits.',
            'date_received': datetime.now()
        },
        {
            'message_id': 'test_pii',
            'subject': 'Driver Information Update',
            'sender': 'hr@company.com',
            'body': 'Please update driver John Smith SSN: 123-45-6789, DL: CA12345678, Phone: 555-123-4567',
            'date_received': datetime.now()
        }
    ]
    
    print("Running Security & Compliance Scans...")
    print("=" * 50)
    
    for email in test_emails:
        print(f"\nScanning: {email['subject']}")
        results = monitor.run_comprehensive_scan(email)
        
        print(f"Risk Score: {results['risk_score']}/100")
        
        if results['security_alerts']:
            print("Security Alerts:")
            for alert in results['security_alerts']:
                print(f"  - {alert['type']}: {alert['description']} ({alert['severity']})")
        
        if results['compliance_issues']:
            print("Compliance Issues:")
            for issue in results['compliance_issues']:
                print(f"  - {issue['type']}: {issue['description']} ({issue['severity']})")
        
        if results['pii_findings']:
            print("PII Detected:")
            for finding in results['pii_findings']:
                print(f"  - {finding['type']}: {finding['description']} ({finding['severity']})")
    
    print("\n" + "=" * 50)
    print("Security Dashboard:")
    dashboard = monitor.get_security_dashboard()
    print(json.dumps(dashboard, indent=2, default=str))

if __name__ == "__main__":
    main()