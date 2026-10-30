#!/usr/bin/env python3
"""
Unified Logging System
Centralized logging for all Gmail AI components
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
from logging.handlers import RotatingFileHandler

class GmailAILogger:
    """Unified logging system for Gmail AI"""
    
    def __init__(self, name: str = "gmail_ai", log_level: str = "INFO"):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup log handlers"""
        # Create logs directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # File handler with rotation
        log_file = log_dir / "gmail_ai.log"
        file_handler = RotatingFileHandler(
            log_file, 
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(self._format_message(message, **kwargs))
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(self._format_message(message, **kwargs))
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(self._format_message(message, **kwargs))
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self.logger.error(self._format_message(message, **kwargs))
    
    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self.logger.critical(self._format_message(message, **kwargs))
    
    def _format_message(self, message: str, **kwargs) -> str:
        """Format log message with additional context"""
        if not kwargs:
            return message
        
        context = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        return f"{message} | {context}"
    
    def log_email_processing(self, email_id: str, action: str, **kwargs):
        """Log email processing activity"""
        self.info(f"Email processing: {action}", email_id=email_id, **kwargs)
    
    def log_classification(self, email_id: str, classification: str, confidence: float, **kwargs):
        """Log classification activity"""
        self.info(f"Email classified: {classification}", 
                 email_id=email_id, 
                 classification=classification, 
                 confidence=confidence, 
                 **kwargs)
    
    def log_error(self, component: str, error: Exception, **kwargs):
        """Log error with component context"""
        self.error(f"Error in {component}: {str(error)}", 
                  component=component, 
                  error_type=type(error).__name__, 
                  **kwargs)
    
    def log_security_alert(self, alert_type: str, risk_score: int, **kwargs):
        """Log security alert"""
        self.warning(f"Security alert: {alert_type}", 
                    alert_type=alert_type, 
                    risk_score=risk_score, 
                    **kwargs)
    
    def log_business_data(self, data_type: str, **kwargs):
        """Log business data extraction"""
        self.info(f"Business data extracted: {data_type}", 
                 data_type=data_type, 
                 **kwargs)

# Global logger instances
main_logger = GmailAILogger("gmail_ai")
email_logger = GmailAILogger("gmail_ai.email")
classification_logger = GmailAILogger("gmail_ai.classification")
security_logger = GmailAILogger("gmail_ai.security")
business_logger = GmailAILogger("gmail_ai.business")

def get_logger(name: str = "gmail_ai") -> GmailAILogger:
    """Get logger instance"""
    return GmailAILogger(name)

def log_email_processing(email_id: str, action: str, **kwargs):
    """Convenience function for email processing logs"""
    email_logger.log_email_processing(email_id, action, **kwargs)

def log_classification(email_id: str, classification: str, confidence: float, **kwargs):
    """Convenience function for classification logs"""
    classification_logger.log_classification(email_id, classification, confidence, **kwargs)

def log_error(component: str, error: Exception, **kwargs):
    """Convenience function for error logs"""
    main_logger.log_error(component, error, **kwargs)

def log_security_alert(alert_type: str, risk_score: int, **kwargs):
    """Convenience function for security alerts"""
    security_logger.log_security_alert(alert_type, risk_score, **kwargs)

def log_business_data(data_type: str, **kwargs):
    """Convenience function for business data logs"""
    business_logger.log_business_data(data_type, **kwargs)

if __name__ == "__main__":
    # Test logging system
    logger = get_logger("test")
    
    logger.info("Testing logging system")
    logger.debug("Debug message", test_param="value")
    logger.warning("Warning message", warning_type="test")
    logger.error("Error message", error_code=500)
    
    # Test specialized loggers
    log_email_processing("test_email_123", "classified", classification="Business")
    log_classification("test_email_123", "Business", 0.85, sender="test@example.com")
    log_error("test_component", Exception("Test error"), additional_info="test")
    log_security_alert("phishing", 75, email_id="test_email_123")
    log_business_data("rate_sheet", load_id="ABC123")
    
    print("✅ Logging system test complete")
