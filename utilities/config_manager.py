#!/usr/bin/env python3
"""
Unified Configuration Manager
Centralized configuration management for all Gmail AI components
"""

import json
import os
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, asdict

@dataclass
class ProcessingConfig:
    """Email processing configuration"""
    batch_size: int = 10
    processing_interval: int = 300  # 5 minutes
    max_emails_per_batch: int = 50
    confidence_threshold: float = 0.7
    max_processing_time: int = 30  # seconds per email

@dataclass
class FeaturesConfig:
    """Feature toggles"""
    smart_learning: bool = True
    analytics: bool = True
    business_intelligence: bool = True
    automation: bool = True
    security_monitoring: bool = True
    mobile_api: bool = True

@dataclass
class SecurityConfig:
    """Security settings"""
    encrypt_credentials: bool = True
    security_risk_threshold: int = 50
    auto_retrain_feedback_count: int = 15
    enable_audit_logging: bool = True

@dataclass
class NotificationConfig:
    """Notification settings"""
    high_risk_security: bool = True
    dot_compliance_issues: bool = True
    overdue_invoices: bool = True
    system_errors: bool = True
    email_notifications: bool = False

@dataclass
class AutomationConfig:
    """Automation settings"""
    auto_label: bool = True
    auto_star_important: bool = True
    auto_archive_spam: bool = True
    create_tasks: bool = True
    enable_scheduling: bool = True

@dataclass
class BusinessRulesConfig:
    """Business-specific rules"""
    rate_confirmation_priority: str = "high"
    dot_compliance_escalation: bool = True
    invoice_tracking: bool = True
    linkedin_auto_archive: bool = True
    freight_keywords: list = None

    def __post_init__(self):
        if self.freight_keywords is None:
            self.freight_keywords = [
                'freight', 'shipping', 'logistics', 'trucking', 'load',
                'dispatch', 'rate confirmation', 'ratecon', 'carrier'
            ]

class ConfigManager:
    """Unified configuration manager"""
    
    def __init__(self, config_file: str = "config/gmail_ai_config.json"):
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                return self._merge_with_defaults(config_data)
            except Exception as e:
                print(f"⚠️ Error loading config: {e}, using defaults")
        
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'processing': asdict(ProcessingConfig()),
            'features': asdict(FeaturesConfig()),
            'security': asdict(SecurityConfig()),
            'notifications': asdict(NotificationConfig()),
            'automation': asdict(AutomationConfig()),
            'business_rules': asdict(BusinessRulesConfig()),
            'database': {
                'path': 'gmail_ai_unified.db',
                'backup_enabled': True,
                'backup_interval': 24  # hours
            },
            'logging': {
                'level': 'INFO',
                'file': 'logs/gmail_ai.log',
                'max_size': 10,  # MB
                'backup_count': 5
            },
            'gui': {
                'theme': 'light',
                'window_size': [1200, 800],
                'auto_save': True
            }
        }
    
    def _merge_with_defaults(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Merge loaded config with defaults"""
        default_config = self._get_default_config()
        
        # Deep merge
        for key, value in config_data.items():
            if key in default_config and isinstance(value, dict) and isinstance(default_config[key], dict):
                default_config[key].update(value)
            else:
                default_config[key] = value
        
        return default_config
    
    def save_config(self, config: Optional[Dict[str, Any]] = None):
        """Save configuration to file"""
        if config is None:
            config = self.config
        
        # Ensure config directory exists
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"✅ Configuration saved to {self.config_file}")
        except Exception as e:
            print(f"❌ Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports dot notation)"""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """Set configuration value by key (supports dot notation)"""
        keys = key.split('.')
        config = self.config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
    
    def get_processing_config(self) -> ProcessingConfig:
        """Get processing configuration"""
        return ProcessingConfig(**self.config.get('processing', {}))
    
    def get_features_config(self) -> FeaturesConfig:
        """Get features configuration"""
        return FeaturesConfig(**self.config.get('features', {}))
    
    def get_security_config(self) -> SecurityConfig:
        """Get security configuration"""
        return SecurityConfig(**self.config.get('security', {}))
    
    def get_notification_config(self) -> NotificationConfig:
        """Get notification configuration"""
        return NotificationConfig(**self.config.get('notifications', {}))
    
    def get_automation_config(self) -> AutomationConfig:
        """Get automation configuration"""
        return AutomationConfig(**self.config.get('automation', {}))
    
    def get_business_rules_config(self) -> BusinessRulesConfig:
        """Get business rules configuration"""
        return BusinessRulesConfig(**self.config.get('business_rules', {}))
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a feature is enabled"""
        return self.config.get('features', {}).get(feature, False)
    
    def enable_feature(self, feature: str):
        """Enable a feature"""
        if 'features' not in self.config:
            self.config['features'] = {}
        self.config['features'][feature] = True
    
    def disable_feature(self, feature: str):
        """Disable a feature"""
        if 'features' not in self.config:
            self.config['features'] = {}
        self.config['features'][feature] = False
    
    def get_database_path(self) -> str:
        """Get database path"""
        return self.config.get('database', {}).get('path', 'gmail_ai_unified.db')
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return self.config.get('logging', {})
    
    def validate_config(self) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []
        
        # Validate processing config
        processing = self.get_processing_config()
        if processing.batch_size <= 0:
            issues.append("Batch size must be positive")
        if processing.confidence_threshold < 0 or processing.confidence_threshold > 1:
            issues.append("Confidence threshold must be between 0 and 1")
        
        # Validate security config
        security = self.get_security_config()
        if security.security_risk_threshold < 0 or security.security_risk_threshold > 100:
            issues.append("Security risk threshold must be between 0 and 100")
        
        return issues

# Global configuration manager instance
config_manager = ConfigManager()

def get_config() -> ConfigManager:
    """Get the global configuration manager instance"""
    return config_manager

def get_setting(key: str, default: Any = None) -> Any:
    """Convenience function to get a setting"""
    return config_manager.get(key, default)

def is_feature_enabled(feature: str) -> bool:
    """Convenience function to check if a feature is enabled"""
    return config_manager.is_feature_enabled(feature)

if __name__ == "__main__":
    # Test configuration manager
    config = ConfigManager()
    
    print("🔧 Configuration Manager Test")
    print(f"📁 Config file: {config.config_file}")
    print(f"🔧 Features enabled: {sum(config.get('features', {}).values())}")
    print(f"📊 Processing batch size: {config.get('processing.batch_size')}")
    print(f"🔒 Security threshold: {config.get('security.security_risk_threshold')}")
    
    # Validate config
    issues = config.validate_config()
    if issues:
        print(f"⚠️ Configuration issues: {issues}")
    else:
        print("✅ Configuration is valid")
