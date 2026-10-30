#!/usr/bin/env python3
"""
Gmail AI Mobile API
REST API for mobile app integration
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import sqlite3
from datetime import datetime, timedelta
import threading
import os

# Import our modules
from smart_learning_classifier import SmartLearningClassifier
from email_analytics import EmailAnalytics
from business_intelligence import BusinessIntelligenceProcessor
from email_automation import EmailAutomation

app = Flask(__name__)
CORS(app)  # Enable CORS for mobile apps

# Initialize components
smart_classifier = SmartLearningClassifier()
analytics = EmailAnalytics()
business_intel = BusinessIntelligenceProcessor()
automation = EmailAutomation()

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status"""
    return jsonify({
        'status': 'running',
        'version': '2.0.0',
        'timestamp': datetime.now().isoformat(),
        'components': {
            'smart_learning': True,
            'analytics': True,
            'business_intelligence': True,
            'automation': True
        }
    })

@app.route('/api/dashboard', methods=['GET'])
def dashboard_summary():
    """Get dashboard summary for mobile app"""
    try:
        # Get analytics report
        analytics_report = analytics.generate_daily_report()
        
        # Get business metrics
        business_report = business_intel.generate_business_report()
        
        # Get learning stats
        learning_stats = smart_classifier.get_learning_stats()
        
        # Get automation stats
        automation_stats = automation.get_automation_stats()
        
        # Get overdue items
        overdue_items = business_intel.get_overdue_items()
        
        dashboard = {
            'summary': {
                'total_emails_today': analytics_report.get('total_processed', 0),
                'total_loads': business_report.get('rate_sheets', {}).get('total_loads', 0),
                'pending_invoices': business_report.get('invoices', {}).get('pending_count', 0),
                'open_violations': business_report.get('dot_compliance', {}).get('open_violations', 0),
                'learning_accuracy': 1 - learning_stats.get('correction_rate', 0)
            },
            'alerts': {
                'overdue_invoices': len(overdue_items.get('overdue_invoices', [])),
                'overdue_compliance': len(overdue_items.get('overdue_compliance', [])),
                'high_priority_emails': 0  # TODO: Implement
            },
            'recent_activity': {
                'classifications_today': analytics_report.get('classification_accuracy', []),
                'automation_executions': automation_stats.get('recent_executions', {}),
                'top_senders': analytics_report.get('top_senders', [])[:5]
            }
        }
        
        return jsonify(dashboard)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/daily', methods=['GET'])
def daily_analytics():
    """Get daily analytics report"""
    try:
        days = request.args.get('days', 7, type=int)
        report = analytics.generate_daily_report()
        return jsonify(report)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/business/report', methods=['GET'])
def business_report():
    """Get business intelligence report"""
    try:
        report = business_intel.generate_business_report()
        return jsonify(report)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/business/overdue', methods=['GET'])
def overdue_items():
    """Get overdue business items"""
    try:
        overdue = business_intel.get_overdue_items()
        return jsonify(overdue)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/learning/stats', methods=['GET'])
def learning_stats():
    """Get smart learning statistics"""
    try:
        stats = smart_classifier.get_learning_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/learning/feedback', methods=['POST'])
def submit_learning_feedback():
    """Submit feedback for smart learning"""
    try:
        data = request.json
        
        email_content = data.get('email_content')
        predicted_category = data.get('predicted_category')
        correct_category = data.get('correct_category')
        confidence = data.get('confidence', 0.5)
        sender = data.get('sender', 'api@mobile.com')
        subject = data.get('subject', 'Mobile Feedback')
        
        if not all([email_content, correct_category]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        smart_classifier.record_user_feedback(
            email_content, predicted_category, correct_category,
            confidence, sender, subject
        )
        
        return jsonify({'message': 'Feedback submitted successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/classify', methods=['POST'])
def classify_email():
    """Classify email content"""
    try:
        data = request.json
        
        email_content = data.get('content', '')
        subject = data.get('subject', '')
        sender = data.get('sender', '')
        
        if not email_content:
            return jsonify({'error': 'Email content is required'}), 400
        
        prediction, confidence = smart_classifier.classify_email(
            email_content, subject, sender
        )
        
        # Get suggestions if confidence is low
        suggestions = smart_classifier.get_category_suggestions(email_content)
        
        result = {
            'classification': prediction,
            'confidence': confidence,
            'suggestions': [
                {'category': cat, 'confidence': conf}
                for cat, conf in suggestions
            ]
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/automation/rules', methods=['GET'])
def get_automation_rules():
    """Get automation rules"""
    try:
        automation.load_rules_and_workflows()
        
        rules = [
            {
                'id': rule.id,
                'name': rule.name,
                'trigger_type': rule.trigger_type.value,
                'trigger_value': rule.trigger_value,
                'action_type': rule.action_type.value,
                'action_value': rule.action_value,
                'enabled': rule.enabled,
                'priority': rule.priority
            }
            for rule in automation.rules
        ]
        
        return jsonify({'rules': rules})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/automation/rules', methods=['POST'])
def add_automation_rule():
    """Add new automation rule"""
    try:
        data = request.json
        
        success = automation.add_automation_rule(
            name=data.get('name'),
            trigger_type=data.get('trigger_type'),
            trigger_value=data.get('trigger_value'),
            action_type=data.get('action_type'),
            action_value=data.get('action_value'),
            conditions=data.get('conditions', {}),
            priority=data.get('priority', 1)
        )
        
        if success:
            return jsonify({'message': 'Rule added successfully'})
        else:
            return jsonify({'error': 'Failed to add rule'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/automation/stats', methods=['GET'])
def automation_statistics():
    """Get automation statistics"""
    try:
        stats = automation.get_automation_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get available categories"""
    try:
        conn = sqlite3.connect(smart_classifier.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT category_name, description, usage_count FROM custom_categories ORDER BY usage_count DESC')
        
        categories = [
            {
                'name': row[0],
                'description': row[1],
                'usage_count': row[2]
            }
            for row in cursor.fetchall()
        ]
        
        conn.close()
        return jsonify({'categories': categories})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/categories', methods=['POST'])
def add_category():
    """Add new category"""
    try:
        data = request.json
        
        success = smart_classifier.add_custom_category(
            name=data.get('name'),
            description=data.get('description', ''),
            keywords=data.get('keywords', []),
            rules=data.get('rules', {})
        )
        
        if success:
            return jsonify({'message': 'Category added successfully'})
        else:
            return jsonify({'error': 'Category already exists'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    """Get recent notifications/alerts"""
    try:
        # Get overdue items as notifications
        overdue = business_intel.get_overdue_items()
        
        notifications = []
        
        # Overdue invoices
        for invoice in overdue.get('overdue_invoices', []):
            notifications.append({
                'id': f"invoice_{invoice['id']}",
                'type': 'overdue_invoice',
                'title': f"Overdue Invoice: {invoice['invoice_number']}",
                'message': f"Amount: ${invoice['amount']:.2f}, Due: {invoice['due_date']}",
                'priority': 'high',
                'timestamp': datetime.now().isoformat()
            })
        
        # Overdue compliance
        for compliance in overdue.get('overdue_compliance', []):
            notifications.append({
                'id': f"compliance_{compliance['id']}",
                'type': 'dot_compliance',
                'title': f"DOT Compliance Issue",
                'message': f"{compliance['violation_type']}, Fine: ${compliance['fine_amount']:.2f}",
                'priority': 'critical',
                'timestamp': datetime.now().isoformat()
            })
        
        # Sort by priority and timestamp
        notifications.sort(key=lambda x: (x['priority'] == 'critical', x['timestamp']), reverse=True)
        
        return jsonify({'notifications': notifications[:20]})  # Limit to 20
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search', methods=['GET'])
def search_emails():
    """Search processed emails"""
    try:
        query = request.args.get('q', '')
        category = request.args.get('category', '')
        limit = request.args.get('limit', 20, type=int)
        
        # Search in analytics database
        conn = sqlite3.connect(analytics.db_path)
        
        sql = '''
            SELECT message_id, subject, sender, classification, confidence, date_processed
            FROM email_log
            WHERE 1=1
        '''
        params = []
        
        if query:
            sql += ' AND (subject LIKE ? OR sender LIKE ?)'
            params.extend([f'%{query}%', f'%{query}%'])
        
        if category:
            sql += ' AND classification = ?'
            params.append(category)
        
        sql += ' ORDER BY date_processed DESC LIMIT ?'
        params.append(limit)
        
        cursor = conn.cursor()
        cursor.execute(sql, params)
        
        emails = [
            {
                'message_id': row[0],
                'subject': row[1],
                'sender': row[2],
                'classification': row[3],
                'confidence': row[4],
                'date_processed': row[5]
            }
            for row in cursor.fetchall()
        ]
        
        conn.close()
        return jsonify({'emails': emails})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

def create_api_documentation():
    """Create API documentation"""
    docs = {
        'title': 'Gmail AI Mobile API',
        'version': '2.0.0',
        'description': 'REST API for Gmail AI Manager mobile integration',
        'base_url': 'http://localhost:5000/api',
        'endpoints': {
            'GET /status': 'Get system status',
            'GET /dashboard': 'Get dashboard summary',
            'GET /analytics/daily': 'Get daily analytics',
            'GET /business/report': 'Get business intelligence report',
            'GET /business/overdue': 'Get overdue items',
            'GET /learning/stats': 'Get learning statistics',
            'POST /learning/feedback': 'Submit learning feedback',
            'POST /classify': 'Classify email content',
            'GET /automation/rules': 'Get automation rules',
            'POST /automation/rules': 'Add automation rule',
            'GET /automation/stats': 'Get automation statistics',
            'GET /categories': 'Get available categories',
            'POST /categories': 'Add new category',
            'GET /notifications': 'Get notifications/alerts',
            'GET /search': 'Search processed emails'
        }
    }
    
    with open('api_documentation.json', 'w') as f:
        json.dump(docs, f, indent=2)
    
    return docs

def start_api_server(host='0.0.0.0', port=5000, debug=False):
    """Start the API server"""
    print(f"Starting Gmail AI Mobile API server on {host}:{port}")
    
    # Create API documentation
    create_api_documentation()
    
    # Start automation scheduler in background
    automation.start_scheduler()
    
    try:
        app.run(host=host, port=port, debug=debug, threaded=True)
    finally:
        automation.stop_scheduler()

if __name__ == '__main__':
    start_api_server(debug=True)