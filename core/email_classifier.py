#!/usr/bin/env python3
"""
Unified Email Classifier
Consolidates all email classification logic into a single, maintainable system
"""

import re
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import sys
from pathlib import Path

# Add utilities to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir.parent / "utilities"))

try:
    from logger import get_logger, log_classification
    from config_manager import get_config
except ImportError:
    # Fallback if utilities not available
    def get_logger(name): return None
    def log_classification(*args, **kwargs): pass
    def get_config(): return None

class ClassificationType(Enum):
    """Types of classification methods"""
    RULE_BASED = "rule_based"
    MACHINE_LEARNING = "ml"
    HYBRID = "hybrid"

@dataclass
class ClassificationResult:
    """Email classification result"""
    label: str
    confidence: float
    method: str
    reason: str
    action: str = "label"  # label, archive, trash, star
    importance: str = "medium"  # high, medium, low, junk
    keywords_matched: List[str] = None
    business_data: Dict[str, Any] = None

class EmailClassifier:
    """Unified email classifier with multiple classification methods"""
    
    def __init__(self, classification_type: ClassificationType = ClassificationType.HYBRID):
        self.classification_type = classification_type
        self.logger = get_logger("email_classifier")
        self.config = get_config()
        
        # Classification rules
        self.rules = self._load_classification_rules()
        
        # Business-specific patterns
        self.business_patterns = self._load_business_patterns()
        
        # Spam indicators
        self.spam_indicators = self._load_spam_indicators()
    
    def _load_classification_rules(self) -> Dict[str, List[str]]:
        """Load classification rules"""
        return {
            'LinkedIn': [
                'linkedin', 'inmail', 'connection request', 'jobs-listings@linkedin',
                'linkedin.com', 'professional network', 'career opportunity'
            ],
            'Freight/Leads': [
                'freight', 'shipping', 'logistics', 'trucking', 'load',
                'dispatch', 'carrier', 'rate confirmation', 'ratecon',
                'bulkloads', 'freightquote', 'truckstop'
            ],
            'RateConfirmation': [
                'rate confirmation', 'ratecon', 'confirmation', 'ops briefing',
                'fema', 'load confirmation', 'rate sheet', 'pricing'
            ],
            'API/Developer': [
                'api', 'developer', 'github', 'stackoverflow', 'accounting',
                'apex freight', 'technical', 'code', 'programming'
            ],
            'E-commerce': [
                'order', 'purchase', 'receipt', 'invoice', 'payment due',
                'amazon', 'ebay', 'shopify', 'stripe', 'paypal'
            ],
            'Finance': [
                'bank', 'payment', 'statement', 'finance', 'account',
                'credit card', 'loan', 'mortgage', 'investment'
            ],
            'Newsletter': [
                'newsletter', 'unsubscribe', 'weekly', 'monthly',
                'digest', 'update', 'news', 'blog'
            ],
            'Social': [
                'facebook', 'twitter', 'instagram', 'notification',
                'social media', 'follow', 'like', 'share'
            ],
            'Promotional': [
                'sale', 'discount', 'coupon', 'offer expires', 'limited time',
                'special offer', 'promotional', 'marketing', 'advertisement'
            ]
        }
    
    def _load_business_patterns(self) -> Dict[str, List[str]]:
        """Load business-specific patterns"""
        return {
            'rate_sheet': [
                r'rate[:\s]*\$?[\d,]+\.?\d*',
                r'load[:\s]*[A-Z0-9]+',
                r'origin[:\s]*[A-Za-z\s,]+',
                r'destination[:\s]*[A-Za-z\s,]+',
                r'pickup[:\s]*\d{1,2}/\d{1,2}/\d{4}',
                r'delivery[:\s]*\d{1,2}/\d{1,2}/\d{4}'
            ],
            'invoice': [
                r'invoice[:\s]*#?[A-Z0-9-]+',
                r'amount[:\s]*\$?[\d,]+\.?\d*',
                r'due[:\s]*date[:\s]*\d{1,2}/\d{1,2}/\d{4}',
                r'payment[:\s]*terms'
            ],
            'dot_compliance': [
                r'dot[:\s]*violation',
                r'inspection[:\s]*date',
                r'driver[:\s]*[A-Za-z\s]+',
                r'truck[:\s]*#?[A-Z0-9-]+',
                r'fine[:\s]*\$?[\d,]+\.?\d*'
            ]
        }
    
    def _load_spam_indicators(self) -> List[str]:
        """Load spam indicators"""
        return [
            'viagra', 'cialis', 'pills', 'weight loss', 'lose weight fast',
            'make money fast', 'work from home', 'free money', 'lottery winner',
            'congratulations winner', 'urgent reply needed', 'click here now',
            'limited time offer', 'act now', 'free trial', 'no credit check',
            'debt relief', 'credit repair', 'consolidate debt', 'refinance now',
            'earn extra cash', 'home business', 'mlm', 'pyramid scheme'
        ]
    
    def classify_email(self, subject: str, sender: str, body: str, 
                      email_id: Optional[str] = None) -> ClassificationResult:
        """Classify email using the specified method"""
        
        # Clean and prepare text
        subject_clean = self._clean_text(subject or "")
        sender_clean = self._clean_text(sender or "")
        body_clean = self._clean_text(body or "")
        combined_text = f"{subject_clean} {sender_clean} {body_clean}"
        
        # Choose classification method
        if self.classification_type == ClassificationType.RULE_BASED:
            result = self._classify_rule_based(subject_clean, sender_clean, body_clean, combined_text)
        elif self.classification_type == ClassificationType.MACHINE_LEARNING:
            result = self._classify_ml(subject_clean, sender_clean, body_clean, combined_text)
        else:  # HYBRID
            result = self._classify_hybrid(subject_clean, sender_clean, body_clean, combined_text)
        
        # Log classification
        if email_id:
            log_classification(email_id, result.label, result.confidence, 
                             method=result.method, sender=sender)
        
        return result
    
    def _classify_rule_based(self, subject: str, sender: str, body: str, 
                           combined_text: str) -> ClassificationResult:
        """Rule-based classification"""
        
        # Check for spam first (highest priority)
        spam_score = self._calculate_spam_score(combined_text)
        if spam_score > 0.8:
            return ClassificationResult(
                label="Spam",
                confidence=spam_score,
                method="rule_based",
                reason="Spam indicators detected",
                action="trash",
                importance="junk"
            )
        
        # Check business patterns
        business_data = self._extract_business_data(combined_text)
        
        # Check classification rules
        best_match = self._find_best_rule_match(combined_text)
        
        if best_match:
            return ClassificationResult(
                label=best_match['label'],
                confidence=best_match['confidence'],
                method="rule_based",
                reason=best_match['reason'],
                action=self._determine_action(best_match['label']),
                importance=self._determine_importance(best_match['label']),
                keywords_matched=best_match['keywords'],
                business_data=business_data
            )
        
        # Default classification
        return ClassificationResult(
            label="Unknown",
            confidence=0.0,
            method="rule_based",
            reason="No specific patterns matched",
            action="archive",
            importance="low"
        )
    
    def _classify_ml(self, subject: str, sender: str, body: str, 
                    combined_text: str) -> ClassificationResult:
        """Machine learning classification (placeholder)"""
        # This would integrate with your existing ML models
        # For now, fall back to rule-based
        return self._classify_rule_based(subject, sender, body, combined_text)
    
    def _classify_hybrid(self, subject: str, sender: str, body: str, 
                        combined_text: str) -> ClassificationResult:
        """Hybrid classification combining multiple methods"""
        # Get rule-based result
        rule_result = self._classify_rule_based(subject, sender, body, combined_text)
        
        # Get ML result (if available)
        ml_result = self._classify_ml(subject, sender, body, combined_text)
        
        # Combine results (simple voting for now)
        if rule_result.confidence > ml_result.confidence:
            return rule_result
        else:
            return ml_result
    
    def _calculate_spam_score(self, text: str) -> float:
        """Calculate spam score"""
        text_lower = text.lower()
        spam_count = sum(1 for indicator in self.spam_indicators if indicator in text_lower)
        return min(spam_count / len(self.spam_indicators) * 2, 1.0)
    
    def _find_best_rule_match(self, text: str) -> Optional[Dict[str, Any]]:
        """Find the best rule match"""
        text_lower = text.lower()
        best_match = None
        best_score = 0
        
        for label, keywords in self.rules.items():
            matched_keywords = [kw for kw in keywords if kw.lower() in text_lower]
            if matched_keywords:
                score = len(matched_keywords) / len(keywords)
                if score > best_score:
                    best_match = {
                        'label': label,
                        'confidence': min(score * 2, 1.0),  # Scale to 0-1
                        'reason': f"Matched {len(matched_keywords)} keywords",
                        'keywords': matched_keywords
                    }
                    best_score = score
        
        return best_match
    
    def _extract_business_data(self, text: str) -> Dict[str, Any]:
        """Extract business-specific data"""
        business_data = {}
        
        for data_type, patterns in self.business_patterns.items():
            matches = []
            for pattern in patterns:
                found = re.findall(pattern, text, re.IGNORECASE)
                matches.extend(found)
            
            if matches:
                business_data[data_type] = matches
        
        return business_data
    
    def _determine_action(self, label: str) -> str:
        """Determine action based on label"""
        action_map = {
            'Spam': 'trash',
            'Promotional': 'archive',
            'Newsletter': 'archive',
            'Unknown': 'archive',
            'LinkedIn': 'label',
            'Freight/Leads': 'label',
            'RateConfirmation': 'label',
            'E-commerce': 'label',
            'Finance': 'label'
        }
        return action_map.get(label, 'label')
    
    def _determine_importance(self, label: str) -> str:
        """Determine importance based on label"""
        importance_map = {
            'Spam': 'junk',
            'Promotional': 'low',
            'Newsletter': 'medium',
            'Unknown': 'low',
            'LinkedIn': 'high',
            'Freight/Leads': 'high',
            'RateConfirmation': 'high',
            'E-commerce': 'high',
            'Finance': 'high'
        }
        return importance_map.get(label, 'medium')
    
    def _clean_text(self, text: str) -> str:
        """Clean text for processing"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s@.-]', ' ', text)
        
        return text.strip()
    
    def add_custom_rule(self, label: str, keywords: List[str]):
        """Add custom classification rule"""
        if label not in self.rules:
            self.rules[label] = []
        self.rules[label].extend(keywords)
        self.logger.info(f"Added custom rule for {label} with {len(keywords)} keywords")
    
    def get_classification_stats(self) -> Dict[str, Any]:
        """Get classification statistics"""
        return {
            'total_rules': sum(len(keywords) for keywords in self.rules.values()),
            'categories': list(self.rules.keys()),
            'spam_indicators': len(self.spam_indicators),
            'business_patterns': len(self.business_patterns)
        }

# Global classifier instance
classifier = EmailClassifier()

def get_classifier() -> EmailClassifier:
    """Get the global classifier instance"""
    return classifier

def classify_email(subject: str, sender: str, body: str, 
                  email_id: Optional[str] = None) -> ClassificationResult:
    """Convenience function for email classification"""
    return classifier.classify_email(subject, sender, body, email_id)

if __name__ == "__main__":
    # Test classifier
    classifier = EmailClassifier()
    
    # Test emails
    test_emails = [
        {
            'subject': 'Rate confirmation for load ABC123',
            'sender': 'dispatch@freightcompany.com',
            'body': 'Rate: $2,500 for load ABC123 from Chicago, IL to Atlanta, GA.'
        },
        {
            'subject': 'LinkedIn: New connection request',
            'sender': 'noreply@linkedin.com',
            'body': 'John Smith wants to connect with you on LinkedIn.'
        },
        {
            'subject': 'URGENT: Account verification required',
            'sender': 'security@suspicious-bank.com',
            'body': 'Your account has been suspended. Click here immediately.'
        }
    ]
    
    print("🧠 Testing Email Classifier")
    print("=" * 50)
    
    for i, email in enumerate(test_emails, 1):
        result = classifier.classify_email(
            email['subject'], 
            email['sender'], 
            email['body'],
            f"test_email_{i}"
        )
        
        print(f"\n📧 Email {i}: {email['subject']}")
        print(f"   From: {email['sender']}")
        print(f"   Classification: {result.label}")
        print(f"   Confidence: {result.confidence:.2f}")
        print(f"   Action: {result.action}")
        print(f"   Importance: {result.importance}")
        print(f"   Reason: {result.reason}")
    
    print(f"\n📊 Classifier Stats: {classifier.get_classification_stats()}")
