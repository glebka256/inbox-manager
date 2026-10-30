#!/usr/bin/env python3
"""
Master Gmail AI Integration System
Brings together all advanced features into a unified system
"""

import threading
import time
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Import all our advanced modules
from smart_learning_classifier import SmartLearningClassifier
from email_analytics import EmailAnalytics
from business_intelligence import BusinessIntelligenceProcessor
from email_automation import EmailAutomation
from security_compliance import SecurityComplianceMonitor

class MasterGmailAI:
    """Master Gmail AI system integrating all advanced features"""
    
    def __init__(self, config_file="master_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        
        # Initialize all components
        print("Initializing Gmail AI Master System...")
        
        self.smart_classifier = SmartLearningClassifier()
        self.analytics = EmailAnalytics()
        self.business_intel = BusinessIntelligenceProcessor()
        self.automation = EmailAutomation()
        self.security_monitor = SecurityComplianceMonitor()
        
        # System state
        self.running = False
        self.processed_emails = 0
        self.last_health_check = None
        
        print("✓ All components initialized successfully")
    
    def load_config(self) -> Dict:
        """Load master configuration"""
        default_config = {
            "processing": {
                "batch_size": 10,
                "processing_interval": 300,  # 5 minutes
                "max_emails_per_batch": 50
            },
            "features": {
                "smart_learning": True,
                "analytics": True,
                "business_intelligence": True,
                "automation": True,
                "security_monitoring": True
            },
            "thresholds": {
                "confidence_threshold": 0.7,
                "security_risk_threshold": 50,
                "auto_retrain_feedback_count": 15
            },
            "notifications": {
                "high_risk_security": True,
                "dot_compliance_issues": True,
                "overdue_invoices": True,
                "system_errors": True
            },
            "automation": {
                "auto_label": True,
                "auto_star_important": True,
                "auto_archive_spam": True,
                "create_tasks": True
            }
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    default_config.update(loaded_config)
            else:
                self.save_config(default_config)
        except Exception as e:
            print(f"Error loading config, using defaults: {e}")
        
        return default_config
    
    def save_config(self, config: Dict = None):
        """Save configuration"""
        if config is None:
            config = self.config
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def process_email_comprehensive(self, email_data: Dict) -> Dict:
        """Comprehensive email processing with all features"""
        email_id = email_data.get('message_id')
        processing_start = time.time()
        
        results = {
            'email_id': email_id,
            'timestamp': datetime.now().isoformat(),
            'processing_time': 0,
            'classification': None,
            'confidence': 0,
            'security_scan': None,
            'business_data': None,
            'automation_actions': [],
            'errors': []
        }
        
        try:
            # 1. Security Scan (first priority)
            if self.config['features']['security_monitoring']:
                try:
                    security_results = self.security_monitor.run_comprehensive_scan(email_data)
                    results['security_scan'] = security_results
                    
                    # High-risk security alert
                    if security_results['risk_score'] > self.config['thresholds']['security_risk_threshold']:
                        self.send_security_alert(email_data, security_results)
                        
                except Exception as e:
                    results['errors'].append(f"Security scan error: {str(e)}")
            
            # 2. Smart Classification
            if self.config['features']['smart_learning']:
                try:
                    prediction, confidence = self.smart_classifier.classify_email(
                        email_data.get('body', ''),
                        email_data.get('subject', ''),
                        email_data.get('sender', '')
                    )
                    
                    results['classification'] = prediction
                    results['confidence'] = confidence
                    
                    # Update email data with classification
                    email_data['classification'] = prediction
                    email_data['confidence'] = confidence
                    
                except Exception as e:
                    results['errors'].append(f"Classification error: {str(e)}")
            
            # 3. Business Intelligence Extraction
            if self.config['features']['business_intelligence']:
                try:
                    bi_results = self.business_intel.process_business_email(
                        email_id,
                        email_data.get('body', ''),
                        email_data.get('subject', ''),
                        email_data.get('sender', '')
                    )
                    
                    results['business_data'] = bi_results
                    email_data['business_data'] = bi_results
                    
                    # Check for DOT compliance issues
                    if bi_results.get('dot_compliance'):
                        self.send_compliance_alert(email_data, bi_results['dot_compliance'])
                    
                except Exception as e:
                    results['errors'].append(f"Business intelligence error: {str(e)}")
            
            # 4. Analytics Logging
            if self.config['features']['analytics']:
                try:
                    analytics_data = {
                        'message_id': email_id,
                        'subject': email_data.get('subject'),
                        'sender': email_data.get('sender'),
                        'recipient': email_data.get('recipient', 'me'),
                        'date_received': email_data.get('date_received'),
                        'classification': results.get('classification'),
                        'confidence': results.get('confidence'),
                        'action_taken': 'processed',
                        'processing_time': 0  # Will be updated below
                    }
                    
                    self.analytics.log_email_processing(analytics_data)
                    
                    # Update sender stats
                    if email_data.get('sender') and results.get('classification'):
                        self.analytics.update_sender_stats(
                            email_data['sender'],
                            email_data['sender'].split('@')[0],
                            results['classification']
                        )
                    
                except Exception as e:
                    results['errors'].append(f"Analytics error: {str(e)}")
            
            # 5. Automation Processing
            if self.config['features']['automation']:
                try:
                    # Process through automation rules
                    self.automation.process_email_automation(email_data)
                    
                    # Record automation actions (simplified)
                    actions = []
                    
                    if self.config['automation']['auto_label'] and results.get('classification'):
                        actions.append(f"Applied label: {results['classification']}")
                    
                    if (self.config['automation']['auto_star_important'] and 
                        results.get('classification') in ['Important', 'RateConfirmation']):
                        actions.append("Starred email")
                    
                    if (self.config['automation']['auto_archive_spam'] and 
                        results.get('classification') == 'Spam'):
                        actions.append("Archived spam")
                    
                    results['automation_actions'] = actions
                    
                except Exception as e:
                    results['errors'].append(f"Automation error: {str(e)}")
        
        except Exception as e:
            results['errors'].append(f"Critical processing error: {str(e)}")
        
        finally:
            # Calculate processing time
            processing_time = time.time() - processing_start
            results['processing_time'] = processing_time
            
            # Update analytics with processing time
            if self.config['features']['analytics'] and not results['errors']:
                try:
                    # Update the logged data with actual processing time
                    pass  # Implementation would update the database
                except:
                    pass
        
        return results
    
    def send_security_alert(self, email_data: Dict, security_results: Dict):
        """Send security alert notification"""
        if not self.config['notifications']['high_risk_security']:
            return
        
        alert_message = f"""
        HIGH RISK SECURITY ALERT
        
        Email: {email_data.get('subject', 'No Subject')}
        From: {email_data.get('sender', 'Unknown')}
        Risk Score: {security_results['risk_score']}/100
        
        Security Issues:
        {json.dumps(security_results['security_alerts'], indent=2)}
        
        Action Required: Review email immediately
        """
        
        print(f"🚨 SECURITY ALERT: {alert_message}")
        # Could extend to send email, Slack, etc.
    
    def send_compliance_alert(self, email_data: Dict, dot_compliance):
        """Send DOT compliance alert"""
        if not self.config['notifications']['dot_compliance_issues']:
            return
        
        alert_message = f"""
        DOT COMPLIANCE ISSUE DETECTED
        
        Email: {email_data.get('subject', 'No Subject')}
        From: {email_data.get('sender', 'Unknown')}
        
        Compliance Data:
        Violation: {dot_compliance.violation_type}
        Driver: {dot_compliance.driver_name}
        Fine: ${dot_compliance.fine_amount or 0}
        
        Action Required: Review compliance issue
        """
        
        print(f"⚠️ COMPLIANCE ALERT: {alert_message}")
    
    def run_system_health_check(self) -> Dict:
        """Run comprehensive system health check"""
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'components': {},
            'metrics': {},
            'recommendations': []
        }
        
        try:
            # Check smart learning system
            learning_stats = self.smart_classifier.get_learning_stats()
            health_status['components']['smart_learning'] = {
                'status': 'healthy' if learning_stats['correction_rate'] < 0.3 else 'warning',
                'total_feedback': learning_stats['total_feedback'],
                'correction_rate': learning_stats['correction_rate']
            }
            
            if learning_stats['correction_rate'] > 0.4:
                health_status['recommendations'].append(
                    "High correction rate detected - consider retraining the model"
                )
            
            # Check analytics system
            try:
                analytics_report = self.analytics.generate_daily_report()
                health_status['components']['analytics'] = {
                    'status': 'healthy',
                    'emails_processed': analytics_report.get('total_processed', 0)
                }
            except Exception as e:
                health_status['components']['analytics'] = {
                    'status': 'error',
                    'error': str(e)
                }
            
            # Check business intelligence
            try:
                business_report = self.business_intel.generate_business_report()
                health_status['components']['business_intelligence'] = {
                    'status': 'healthy',
                    'rate_sheets': len(business_report.get('rate_sheets', {})),
                    'invoices': len(business_report.get('invoices', {}))
                }
            except Exception as e:
                health_status['components']['business_intelligence'] = {
                    'status': 'error',
                    'error': str(e)
                }
            
            # Check automation system
            try:
                automation_stats = self.automation.get_automation_stats()
                health_status['components']['automation'] = {
                    'status': 'healthy',
                    'active_rules': automation_stats.get('rules', {}).get('total_rules', 0),
                    'total_executions': automation_stats.get('rules', {}).get('total_executions', 0)
                }
            except Exception as e:
                health_status['components']['automation'] = {
                    'status': 'error',
                    'error': str(e)
                }
            
            # Check security monitoring
            try:
                security_dashboard = self.security_monitor.get_security_dashboard()
                unresolved_alerts = security_dashboard.get('alert_summary', {}).get('unresolved', 0)
                
                health_status['components']['security_monitoring'] = {
                    'status': 'warning' if unresolved_alerts > 5 else 'healthy',
                    'unresolved_alerts': unresolved_alerts
                }
                
                if unresolved_alerts > 5:
                    health_status['recommendations'].append(
                        f"High number of unresolved security alerts: {unresolved_alerts}"
                    )
            except Exception as e:
                health_status['components']['security_monitoring'] = {
                    'status': 'error',
                    'error': str(e)
                }
            
            # Overall system metrics
            health_status['metrics'] = {
                'total_emails_processed': self.processed_emails,
                'uptime_hours': self.get_uptime_hours(),
                'last_health_check': self.last_health_check
            }
            
            # Determine overall status
            component_statuses = [comp['status'] for comp in health_status['components'].values()]
            if 'error' in component_statuses:
                health_status['overall_status'] = 'error'
            elif 'warning' in component_statuses:
                health_status['overall_status'] = 'warning'
            
        except Exception as e:
            health_status['overall_status'] = 'error'
            health_status['error'] = str(e)
        
        self.last_health_check = datetime.now()
        return health_status
    
    def get_uptime_hours(self) -> float:
        """Get system uptime in hours"""
        if not hasattr(self, 'start_time'):
            self.start_time = datetime.now()
        
        return (datetime.now() - self.start_time).total_seconds() / 3600
    
    def generate_master_report(self) -> Dict:
        """Generate comprehensive master report"""
        report = {
            'generated_at': datetime.now().isoformat(),
            'system_overview': {
                'total_emails_processed': self.processed_emails,
                'uptime_hours': self.get_uptime_hours(),
                'configuration': self.config
            }
        }
        
        try:
            # Analytics summary
            report['analytics'] = self.analytics.generate_daily_report()
            
            # Business intelligence summary
            report['business_intelligence'] = self.business_intel.generate_business_report()
            
            # Learning system stats
            report['smart_learning'] = self.smart_classifier.get_learning_stats()
            
            # Automation statistics
            report['automation'] = self.automation.get_automation_stats()
            
            # Security dashboard
            report['security'] = self.security_monitor.get_security_dashboard()
            
            # System health
            report['health_check'] = self.run_system_health_check()
            
            # Business insights
            insights = self.analytics.get_business_insights()
            report['business_insights'] = insights
            
            # Overdue items
            overdue = self.business_intel.get_overdue_items()
            report['overdue_items'] = overdue
            
        except Exception as e:
            report['error'] = f"Error generating report: {str(e)}"
        
        return report
    
    def start_master_system(self):
        """Start the master Gmail AI system"""
        print("\n🚀 Starting Master Gmail AI System...")
        
        self.running = True
        self.start_time = datetime.now()
        
        # Start automation scheduler
        if self.config['features']['automation']:
            self.automation.start_scheduler()
            print("✓ Automation scheduler started")
        
        # Run initial health check
        health = self.run_system_health_check()
        print(f"✓ System health check: {health['overall_status']}")
        
        print(f"\n🎯 Master Gmail AI System is now running!")
        print(f"   Configuration: {self.config_file}")
        print(f"   Features enabled: {sum(self.config['features'].values())}/5")
        print(f"   Processing ready...")
        
        return True
    
    def stop_master_system(self):
        """Stop the master system"""
        print("\n🛑 Stopping Master Gmail AI System...")
        
        self.running = False
        
        if self.config['features']['automation']:
            self.automation.stop_scheduler()
            print("✓ Automation scheduler stopped")
        
        # Generate final report
        try:
            final_report = self.generate_master_report()
            report_filename = f"final_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_filename, 'w') as f:
                json.dump(final_report, f, indent=2, default=str)
            print(f"✓ Final report saved: {report_filename}")
        except Exception as e:
            print(f"Error generating final report: {e}")
        
        print("✓ Master Gmail AI System stopped")
    
    def process_email_batch(self, emails: List[Dict]) -> List[Dict]:
        """Process a batch of emails"""
        results = []
        
        print(f"Processing batch of {len(emails)} emails...")
        
        for i, email in enumerate(emails):
            try:
                result = self.process_email_comprehensive(email)
                results.append(result)
                self.processed_emails += 1
                
                # Progress update
                if (i + 1) % 5 == 0:
                    print(f"  Processed {i + 1}/{len(emails)} emails...")
                
            except Exception as e:
                print(f"Error processing email {i}: {e}")
                results.append({
                    'email_id': email.get('message_id', f'unknown_{i}'),
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        print(f"✓ Batch processing complete: {len(results)} emails processed")
        return results

def create_sample_master_config():
    """Create a sample master configuration file"""
    config = {
        "processing": {
            "batch_size": 10,
            "processing_interval": 300,
            "max_emails_per_batch": 50
        },
        "features": {
            "smart_learning": True,
            "analytics": True,
            "business_intelligence": True,
            "automation": True,
            "security_monitoring": True
        },
        "thresholds": {
            "confidence_threshold": 0.7,
            "security_risk_threshold": 50,
            "auto_retrain_feedback_count": 15
        },
        "notifications": {
            "high_risk_security": True,
            "dot_compliance_issues": True,
            "overdue_invoices": True,
            "system_errors": True
        },
        "automation": {
            "auto_label": True,
            "auto_star_important": True,
            "auto_archive_spam": True,
            "create_tasks": True
        },
        "business_rules": {
            "rate_confirmation_priority": "high",
            "dot_compliance_escalation": True,
            "invoice_tracking": True,
            "linkedin_auto_archive": True
        }
    }
    
    with open('master_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✓ Sample master configuration created: master_config.json")

def main():
    """Demo the master Gmail AI system"""
    
    # Create sample config
    create_sample_master_config()
    
    # Initialize master system
    master_ai = MasterGmailAI()
    
    # Test with sample emails
    sample_emails = [
        {
            'message_id': 'master_test_1',
            'subject': 'Rate confirmation for load ABC123',
            'sender': 'dispatch@freightcompany.com',
            'recipient': 'sean@apexfreightcapital.com',
            'body': 'Rate: $2,500 for load ABC123 from Chicago, IL to Atlanta, GA. 45,000 lbs pickup Monday.',
            'date_received': datetime.now() - timedelta(hours=2)
        },
        {
            'message_id': 'master_test_2',
            'subject': 'URGENT: Account verification required',
            'sender': 'security@suspicious-bank.com',
            'recipient': 'sean@apexfreightcapital.com',
            'body': 'Your account has been suspended. Click here immediately to verify your identity.',
            'date_received': datetime.now() - timedelta(hours=1)
        },
        {
            'message_id': 'master_test_3',
            'subject': 'LinkedIn: New connection request',
            'sender': 'noreply@linkedin.com',
            'recipient': 'sean@apexfreightcapital.com',
            'body': 'John Smith wants to connect with you on LinkedIn.',
            'date_received': datetime.now() - timedelta(minutes=30)
        }
    ]
    
    # Start master system
    master_ai.start_master_system()
    
    try:
        # Process sample emails
        results = master_ai.process_email_batch(sample_emails)
        
        print("\n📊 PROCESSING RESULTS:")
        print("=" * 60)
        
        for result in results:
            print(f"\nEmail ID: {result['email_id']}")
            print(f"Classification: {result.get('classification', 'None')} (confidence: {result.get('confidence', 0):.3f})")
            print(f"Processing Time: {result.get('processing_time', 0):.3f}s")
            
            if result.get('security_scan'):
                print(f"Security Risk Score: {result['security_scan']['risk_score']}/100")
            
            if result.get('business_data'):
                if result['business_data'].get('rate_sheet'):
                    print("✓ Rate sheet detected")
                if result['business_data'].get('invoice'):
                    print("✓ Invoice detected")
                if result['business_data'].get('dot_compliance'):
                    print("⚠️ DOT compliance issue detected")
            
            if result.get('automation_actions'):
                print(f"Automation actions: {', '.join(result['automation_actions'])}")
            
            if result.get('errors'):
                print(f"Errors: {result['errors']}")
        
        # Generate master report
        print("\n📈 GENERATING MASTER REPORT...")
        report = master_ai.generate_master_report()
        
        # Save report
        report_file = f"master_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"✓ Master report saved: {report_file}")
        
        # System health check
        print("\n🏥 SYSTEM HEALTH CHECK:")
        health = master_ai.run_system_health_check()
        print(f"Overall Status: {health['overall_status']}")
        
        for component, status in health['components'].items():
            print(f"  {component}: {status['status']}")
        
        if health.get('recommendations'):
            print("\nRecommendations:")
            for rec in health['recommendations']:
                print(f"  • {rec}")
        
        print(f"\n📋 SUMMARY:")
        print(f"  Total emails processed: {master_ai.processed_emails}")
        print(f"  System uptime: {master_ai.get_uptime_hours():.2f} hours")
        print(f"  Features enabled: {sum(master_ai.config['features'].values())}/5")
        
        # Keep system running for a moment
        print("\n⏱️ System running... (press Ctrl+C to stop)")
        time.sleep(5)
        
    except KeyboardInterrupt:
        print("\nReceived shutdown signal...")
    
    finally:
        # Stop master system
        master_ai.stop_master_system()

if __name__ == "__main__":
    main()