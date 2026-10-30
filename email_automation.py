#!/usr/bin/env python3
"""
Email Automation & Workflow Manager
Automated email processing with custom workflows and rules
"""

import json
import sqlite3
import schedule
import time
import threading
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Optional, Callable
from enum import Enum

class ActionType(Enum):
    LABEL = "label"
    MOVE_TO_FOLDER = "move_to_folder"
    FORWARD = "forward"
    REPLY = "reply"
    DELETE = "delete"
    MARK_READ = "mark_read"
    MARK_UNREAD = "mark_unread"
    STAR = "star"
    ARCHIVE = "archive"
    CREATE_TASK = "create_task"
    SEND_NOTIFICATION = "send_notification"

class TriggerType(Enum):
    CLASSIFICATION = "classification"
    SENDER = "sender"
    SUBJECT_CONTAINS = "subject_contains"
    BODY_CONTAINS = "body_contains"
    TIME_BASED = "time_based"
    CONFIDENCE_THRESHOLD = "confidence_threshold"
    BUSINESS_DATA = "business_data"

@dataclass
class AutomationRule:
    id: int
    name: str
    trigger_type: TriggerType
    trigger_value: str
    action_type: ActionType
    action_value: str
    conditions: Dict = None
    enabled: bool = True
    priority: int = 1
    created_date: datetime = None

@dataclass
class WorkflowStep:
    step_id: int
    action_type: ActionType
    action_value: str
    delay_seconds: int = 0
    conditions: Dict = None

@dataclass
class Workflow:
    id: int
    name: str
    description: str
    trigger_type: TriggerType
    trigger_value: str
    steps: List[WorkflowStep]
    enabled: bool = True

class EmailAutomation:
    def __init__(self, db_path="automation.db"):
        self.db_path = db_path
        self.rules = []
        self.workflows = []
        self.running = False
        self.init_database()
        self.load_rules_and_workflows()
        
    def init_database(self):
        """Initialize automation database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Automation rules
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS automation_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                trigger_type TEXT,
                trigger_value TEXT,
                action_type TEXT,
                action_value TEXT,
                conditions TEXT,  -- JSON
                enabled INTEGER DEFAULT 1,
                priority INTEGER DEFAULT 1,
                created_date DATETIME,
                last_executed DATETIME,
                execution_count INTEGER DEFAULT 0
            )
        ''')
        
        # Workflows
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workflows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                description TEXT,
                trigger_type TEXT,
                trigger_value TEXT,
                steps TEXT,  -- JSON array of steps
                enabled INTEGER DEFAULT 1,
                created_date DATETIME,
                last_executed DATETIME
            )
        ''')
        
        # Execution log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS execution_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_id INTEGER,
                workflow_id INTEGER,
                email_id TEXT,
                execution_date DATETIME,
                status TEXT,
                result TEXT,
                error_message TEXT
            )
        ''')
        
        # Scheduled tasks
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scheduled_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_name TEXT,
                task_type TEXT,
                schedule_pattern TEXT,  -- cron-like pattern
                next_run DATETIME,
                enabled INTEGER DEFAULT 1,
                task_data TEXT  -- JSON
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Add default rules
        self.add_default_rules()
    
    def add_default_rules(self):
        """Add default automation rules"""
        default_rules = [
            {
                'name': 'High Priority Rate Confirmations',
                'trigger_type': TriggerType.CLASSIFICATION.value,
                'trigger_value': 'RateConfirmation',
                'action_type': ActionType.STAR.value,
                'action_value': 'true',
                'conditions': {'confidence': 0.8},
                'priority': 1
            },
            {
                'name': 'Auto-Archive LinkedIn',
                'trigger_type': TriggerType.CLASSIFICATION.value,
                'trigger_value': 'LinkedIn',
                'action_type': ActionType.ARCHIVE.value,
                'action_value': 'true',
                'conditions': {'confidence': 0.7},
                'priority': 2
            },
            {
                'name': 'DOT Compliance Alerts',
                'trigger_type': TriggerType.BUSINESS_DATA.value,
                'trigger_value': 'dot_compliance',
                'action_type': ActionType.SEND_NOTIFICATION.value,
                'action_value': 'DOT compliance issue detected!',
                'conditions': {},
                'priority': 1
            },
            {
                'name': 'Overdue Invoice Reminders',
                'trigger_type': TriggerType.TIME_BASED.value,
                'trigger_value': 'daily_9am',
                'action_type': ActionType.CREATE_TASK.value,
                'action_value': 'Check overdue invoices',
                'conditions': {},
                'priority': 2
            }
        ]
        
        for rule_data in default_rules:
            self.add_automation_rule(**rule_data)
    
    def add_automation_rule(self, name: str, trigger_type: str, trigger_value: str,
                          action_type: str, action_value: str, conditions: Dict = None,
                          priority: int = 1) -> bool:
        """Add a new automation rule"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO automation_rules 
                (name, trigger_type, trigger_value, action_type, action_value, 
                 conditions, priority, created_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                name, trigger_type, trigger_value, action_type, action_value,
                json.dumps(conditions or {}), priority, datetime.now()
            ))
            
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            
            if success:
                self.load_rules_and_workflows()
            
            return success
            
        except Exception as e:
            print(f"Error adding automation rule: {e}")
            conn.close()
            return False
    
    def add_workflow(self, name: str, description: str, trigger_type: str,
                    trigger_value: str, steps: List[Dict]) -> bool:
        """Add a new workflow"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO workflows 
                (name, description, trigger_type, trigger_value, steps, created_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                name, description, trigger_type, trigger_value,
                json.dumps(steps), datetime.now()
            ))
            
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            
            if success:
                self.load_rules_and_workflows()
            
            return success
            
        except Exception as e:
            print(f"Error adding workflow: {e}")
            conn.close()
            return False
    
    def load_rules_and_workflows(self):
        """Load rules and workflows from database"""
        conn = sqlite3.connect(self.db_path)
        
        # Load rules
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, trigger_type, trigger_value, action_type, action_value,
                   conditions, enabled, priority, created_date
            FROM automation_rules
            WHERE enabled = 1
            ORDER BY priority
        ''')
        
        self.rules = []
        for row in cursor.fetchall():
            rule = AutomationRule(
                id=row[0],
                name=row[1],
                trigger_type=TriggerType(row[2]),
                trigger_value=row[3],
                action_type=ActionType(row[4]),
                action_value=row[5],
                conditions=json.loads(row[6] or '{}'),
                enabled=bool(row[7]),
                priority=row[8],
                created_date=datetime.fromisoformat(row[9]) if row[9] else None
            )
            self.rules.append(rule)
        
        # Load workflows
        cursor.execute('''
            SELECT id, name, description, trigger_type, trigger_value, steps, enabled
            FROM workflows
            WHERE enabled = 1
        ''')
        
        self.workflows = []
        for row in cursor.fetchall():
            steps_data = json.loads(row[5])
            steps = [
                WorkflowStep(
                    step_id=step['step_id'],
                    action_type=ActionType(step['action_type']),
                    action_value=step['action_value'],
                    delay_seconds=step.get('delay_seconds', 0),
                    conditions=step.get('conditions', {})
                )
                for step in steps_data
            ]
            
            workflow = Workflow(
                id=row[0],
                name=row[1],
                description=row[2],
                trigger_type=TriggerType(row[3]),
                trigger_value=row[4],
                steps=steps,
                enabled=bool(row[6])
            )
            self.workflows.append(workflow)
        
        conn.close()
    
    def process_email_automation(self, email_data: Dict):
        """Process email through automation rules and workflows"""
        email_id = email_data.get('message_id')
        classification = email_data.get('classification')
        confidence = email_data.get('confidence', 0)
        sender = email_data.get('sender', '')
        subject = email_data.get('subject', '')
        body = email_data.get('body', '')
        business_data = email_data.get('business_data', {})
        
        # Process automation rules
        for rule in self.rules:
            if self.check_rule_trigger(rule, email_data):
                if self.check_rule_conditions(rule, email_data):
                    self.execute_rule_action(rule, email_data)
        
        # Process workflows
        for workflow in self.workflows:
            if self.check_workflow_trigger(workflow, email_data):
                self.execute_workflow(workflow, email_data)
    
    def check_rule_trigger(self, rule: AutomationRule, email_data: Dict) -> bool:
        """Check if rule trigger condition is met"""
        if rule.trigger_type == TriggerType.CLASSIFICATION:
            return email_data.get('classification') == rule.trigger_value
        
        elif rule.trigger_type == TriggerType.SENDER:
            return rule.trigger_value.lower() in email_data.get('sender', '').lower()
        
        elif rule.trigger_type == TriggerType.SUBJECT_CONTAINS:
            return rule.trigger_value.lower() in email_data.get('subject', '').lower()
        
        elif rule.trigger_type == TriggerType.BODY_CONTAINS:
            return rule.trigger_value.lower() in email_data.get('body', '').lower()
        
        elif rule.trigger_type == TriggerType.CONFIDENCE_THRESHOLD:
            return email_data.get('confidence', 0) >= float(rule.trigger_value)
        
        elif rule.trigger_type == TriggerType.BUSINESS_DATA:
            business_data = email_data.get('business_data', {})
            return rule.trigger_value in business_data and business_data[rule.trigger_value]
        
        elif rule.trigger_type == TriggerType.TIME_BASED:
            # Time-based triggers handled by scheduler
            return False
        
        return False
    
    def check_rule_conditions(self, rule: AutomationRule, email_data: Dict) -> bool:
        """Check if additional rule conditions are met"""
        if not rule.conditions:
            return True
        
        # Check confidence condition
        if 'confidence' in rule.conditions:
            if email_data.get('confidence', 0) < rule.conditions['confidence']:
                return False
        
        # Check sender domain condition
        if 'sender_domain' in rule.conditions:
            sender = email_data.get('sender', '')
            if '@' in sender:
                domain = sender.split('@')[1]
                if rule.conditions['sender_domain'] not in domain:
                    return False
        
        # Check date conditions
        if 'max_age_hours' in rule.conditions:
            email_date = email_data.get('date_received')
            if email_date:
                age_hours = (datetime.now() - email_date).total_seconds() / 3600
                if age_hours > rule.conditions['max_age_hours']:
                    return False
        
        return True
    
    def execute_rule_action(self, rule: AutomationRule, email_data: Dict):
        """Execute the action defined by the rule"""
        try:
            email_id = email_data.get('message_id')
            
            if rule.action_type == ActionType.LABEL:
                self.apply_label(email_id, rule.action_value)
            
            elif rule.action_type == ActionType.STAR:
                self.star_email(email_id)
            
            elif rule.action_type == ActionType.ARCHIVE:
                self.archive_email(email_id)
            
            elif rule.action_type == ActionType.MARK_READ:
                self.mark_read(email_id)
            
            elif rule.action_type == ActionType.SEND_NOTIFICATION:
                self.send_notification(rule.action_value, email_data)
            
            elif rule.action_type == ActionType.CREATE_TASK:
                self.create_task(rule.action_value, email_data)
            
            # Log successful execution
            self.log_execution(rule.id, None, email_id, "success", 
                             f"Executed {rule.action_type.value}")
            
            # Update execution count
            self.update_rule_execution(rule.id)
            
        except Exception as e:
            self.log_execution(rule.id, None, email_id, "error", str(e))
            print(f"Error executing rule {rule.name}: {e}")
    
    def execute_workflow(self, workflow: Workflow, email_data: Dict):
        """Execute a workflow with multiple steps"""
        try:
            email_id = email_data.get('message_id')
            
            for step in workflow.steps:
                # Check step conditions
                if step.conditions and not self.check_step_conditions(step, email_data):
                    continue
                
                # Add delay if specified
                if step.delay_seconds > 0:
                    time.sleep(step.delay_seconds)
                
                # Execute step action
                self.execute_step_action(step, email_data)
            
            # Log workflow execution
            self.log_execution(None, workflow.id, email_id, "success", 
                             f"Executed workflow: {workflow.name}")
            
        except Exception as e:
            self.log_execution(None, workflow.id, email_id, "error", str(e))
            print(f"Error executing workflow {workflow.name}: {e}")
    
    def check_workflow_trigger(self, workflow: Workflow, email_data: Dict) -> bool:
        """Check if workflow trigger condition is met"""
        # Same logic as rule triggers
        if workflow.trigger_type == TriggerType.CLASSIFICATION:
            return email_data.get('classification') == workflow.trigger_value
        
        elif workflow.trigger_type == TriggerType.BUSINESS_DATA:
            business_data = email_data.get('business_data', {})
            return workflow.trigger_value in business_data and business_data[workflow.trigger_value]
        
        return False
    
    def check_step_conditions(self, step: WorkflowStep, email_data: Dict) -> bool:
        """Check if workflow step conditions are met"""
        if not step.conditions:
            return True
        
        # Similar to rule conditions but for individual steps
        return True
    
    def execute_step_action(self, step: WorkflowStep, email_data: Dict):
        """Execute a single workflow step"""
        email_id = email_data.get('message_id')
        
        if step.action_type == ActionType.LABEL:
            self.apply_label(email_id, step.action_value)
        
        elif step.action_type == ActionType.FORWARD:
            self.forward_email(email_id, step.action_value)
        
        elif step.action_type == ActionType.CREATE_TASK:
            self.create_task(step.action_value, email_data)
        
        # Add more step actions as needed
    
    def apply_label(self, email_id: str, label: str):
        """Apply Gmail label to email (stub - implement with Gmail API)"""
        print(f"Applying label '{label}' to email {email_id}")
    
    def star_email(self, email_id: str):
        """Star an email (stub - implement with Gmail API)"""
        print(f"Starring email {email_id}")
    
    def archive_email(self, email_id: str):
        """Archive an email (stub - implement with Gmail API)"""
        print(f"Archiving email {email_id}")
    
    def mark_read(self, email_id: str):
        """Mark email as read (stub - implement with Gmail API)"""
        print(f"Marking email {email_id} as read")
    
    def forward_email(self, email_id: str, to_address: str):
        """Forward email (stub - implement with Gmail API)"""
        print(f"Forwarding email {email_id} to {to_address}")
    
    def send_notification(self, message: str, email_data: Dict):
        """Send notification (can be extended for different notification types)"""
        print(f"NOTIFICATION: {message}")
        print(f"Email: {email_data.get('subject', 'No Subject')}")
        
        # Could extend to send:
        # - Desktop notifications
        # - Slack messages
        # - SMS alerts
        # - Email alerts
    
    def create_task(self, task_description: str, email_data: Dict):
        """Create a task (stub - integrate with task management systems)"""
        print(f"TASK CREATED: {task_description}")
        print(f"Related to email: {email_data.get('subject', 'No Subject')}")
        
        # Could integrate with:
        # - Todoist
        # - Asana
        # - Trello
        # - Microsoft To-Do
    
    def log_execution(self, rule_id: Optional[int], workflow_id: Optional[int],
                     email_id: str, status: str, result: str, error: str = None):
        """Log automation execution"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO execution_log 
            (rule_id, workflow_id, email_id, execution_date, status, result, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (rule_id, workflow_id, email_id, datetime.now(), status, result, error))
        
        conn.commit()
        conn.close()
    
    def update_rule_execution(self, rule_id: int):
        """Update rule execution statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE automation_rules 
            SET last_executed = ?, execution_count = execution_count + 1
            WHERE id = ?
        ''', (datetime.now(), rule_id))
        
        conn.commit()
        conn.close()
    
    def get_automation_stats(self) -> Dict:
        """Get automation statistics"""
        conn = sqlite3.connect(self.db_path)
        
        stats = {}
        
        # Rule execution stats
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) as total_rules,
                   SUM(execution_count) as total_executions,
                   AVG(execution_count) as avg_executions
            FROM automation_rules
            WHERE enabled = 1
        ''')
        
        row = cursor.fetchone()
        stats['rules'] = {
            'total_rules': row[0],
            'total_executions': row[1] or 0,
            'avg_executions': row[2] or 0
        }
        
        # Recent execution log
        cursor.execute('''
            SELECT status, COUNT(*) as count
            FROM execution_log
            WHERE execution_date >= datetime('now', '-7 days')
            GROUP BY status
        ''')
        
        stats['recent_executions'] = {
            row[0]: row[1] for row in cursor.fetchall()
        }
        
        # Top triggered rules
        cursor.execute('''
            SELECT ar.name, ar.execution_count
            FROM automation_rules ar
            WHERE ar.enabled = 1
            ORDER BY ar.execution_count DESC
            LIMIT 5
        ''')
        
        stats['top_rules'] = [
            {'name': row[0], 'executions': row[1]}
            for row in cursor.fetchall()
        ]
        
        conn.close()
        return stats
    
    def start_scheduler(self):
        """Start the automation scheduler"""
        self.running = True
        
        # Schedule time-based rules
        schedule.every().day.at("09:00").do(self.run_daily_tasks)
        schedule.every().hour.do(self.run_hourly_tasks)
        
        def run_scheduler():
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        print("Automation scheduler started")
    
    def stop_scheduler(self):
        """Stop the automation scheduler"""
        self.running = False
        print("Automation scheduler stopped")
    
    def run_daily_tasks(self):
        """Run daily automation tasks"""
        print("Running daily automation tasks...")
        
        # Execute time-based rules
        for rule in self.rules:
            if rule.trigger_type == TriggerType.TIME_BASED:
                if 'daily' in rule.trigger_value:
                    # Create synthetic email data for time-based triggers
                    email_data = {
                        'message_id': f'scheduled_{datetime.now().isoformat()}',
                        'trigger_type': 'scheduled',
                        'trigger_time': datetime.now()
                    }
                    self.execute_rule_action(rule, email_data)
    
    def run_hourly_tasks(self):
        """Run hourly automation tasks"""
        print("Running hourly automation tasks...")
        # Add hourly task logic here

def create_sample_workflows():
    """Create sample workflows for demonstration"""
    automation = EmailAutomation()
    
    # Sample workflow: Rate confirmation processing
    rate_workflow_steps = [
        {
            'step_id': 1,
            'action_type': ActionType.STAR.value,
            'action_value': 'true',
            'delay_seconds': 0
        },
        {
            'step_id': 2,
            'action_type': ActionType.LABEL.value,
            'action_value': 'HighPriority',
            'delay_seconds': 1
        },
        {
            'step_id': 3,
            'action_type': ActionType.CREATE_TASK.value,
            'action_value': 'Review rate confirmation',
            'delay_seconds': 2
        }
    ]
    
    automation.add_workflow(
        name="Rate Confirmation Workflow",
        description="Complete processing for rate confirmations",
        trigger_type=TriggerType.CLASSIFICATION.value,
        trigger_value="RateConfirmation",
        steps=rate_workflow_steps
    )
    
    return automation

def main():
    """Demo the automation system"""
    automation = create_sample_workflows()
    
    # Test email data
    test_email = {
        'message_id': 'test123',
        'classification': 'RateConfirmation',
        'confidence': 0.95,
        'sender': 'dispatch@freightcompany.com',
        'subject': 'Rate confirmation for load ABC123',
        'body': 'Please confirm the rate of $2,500...',
        'business_data': {
            'rate_sheet': True
        }
    }
    
    print("Processing test email through automation...")
    automation.process_email_automation(test_email)
    
    print("\nAutomation Statistics:")
    stats = automation.get_automation_stats()
    print(json.dumps(stats, indent=2))
    
    # Start scheduler for demo (stop after a few seconds)
    automation.start_scheduler()
    time.sleep(5)
    automation.stop_scheduler()

if __name__ == "__main__":
    main()