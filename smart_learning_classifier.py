#!/usr/bin/env python3
"""
Smart Learning Email Classifier
Adaptive ML system that learns from user feedback
"""

import sqlite3
import json
import pickle
import time
import numpy as np
from datetime import datetime, timedelta
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import pandas as pd

class SmartLearningClassifier:
    def __init__(self, db_path="smart_learning.db", model_path="smart_model.pkl"):
        self.db_path = db_path
        self.model_path = model_path
        self.confidence_threshold = 0.7
        self.init_database()
        self.load_or_create_model()
    
    def init_database(self):
        """Initialize the learning database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Training data with user feedback
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS training_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_content TEXT,
                predicted_category TEXT,
                user_category TEXT,
                confidence REAL,
                feedback_date DATETIME,
                email_sender TEXT,
                email_subject TEXT,
                is_correction INTEGER  -- 1 if user corrected, 0 if confirmed
            )
        ''')
        
        # Category management
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS custom_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_name TEXT UNIQUE,
                description TEXT,
                keywords TEXT,  -- JSON list of keywords
                rules TEXT,     -- JSON rules for classification
                created_date DATETIME,
                usage_count INTEGER DEFAULT 0,
                accuracy REAL DEFAULT 0.0
            )
        ''')
        
        # Model performance tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_version TEXT,
                accuracy REAL,
                training_size INTEGER,
                test_date DATETIME,
                categories_count INTEGER,
                notes TEXT
            )
        ''')
        
        # Insert default categories if not exist
        default_categories = [
            ('Important', 'High priority emails requiring immediate attention', 
             '["urgent", "asap", "deadline", "critical", "emergency"]', 
             '{"priority": "high", "response_time": "immediate"}'),
            ('Business', 'General business correspondence', 
             '["meeting", "proposal", "contract", "invoice"]', 
             '{"priority": "medium", "response_time": "24h"}'),
            ('LinkedIn', 'LinkedIn notifications and messages', 
             '["linkedin", "connection", "profile", "network"]', 
             '{"priority": "low", "response_time": "weekly"}'),
            ('Spam', 'Unwanted promotional emails', 
             '["unsubscribe", "free", "limited time", "act now"]', 
             '{"priority": "none", "action": "archive"}'),
            ('RateConfirmation', 'Freight rate confirmations', 
             '["rate", "confirmation", "load", "pickup", "delivery"]', 
             '{"priority": "high", "response_time": "2h", "business_critical": true}')
        ]
        
        for category, desc, keywords, rules in default_categories:
            cursor.execute('''
                INSERT OR IGNORE INTO custom_categories 
                (category_name, description, keywords, rules, created_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (category, desc, keywords, rules, datetime.now()))
        
        conn.commit()
        conn.close()
    
    def add_custom_category(self, name, description, keywords=None, rules=None):
        """Add a new custom category"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        keywords_json = json.dumps(keywords or [])
        rules_json = json.dumps(rules or {})
        
        try:
            cursor.execute('''
                INSERT INTO custom_categories 
                (category_name, description, keywords, rules, created_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, description, keywords_json, rules_json, datetime.now()))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Category already exists
        finally:
            conn.close()
    
    def record_user_feedback(self, email_content, predicted_category, user_category, 
                           confidence, sender, subject):
        """Record user feedback for learning"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        is_correction = 1 if predicted_category != user_category else 0
        
        cursor.execute('''
            INSERT INTO training_feedback 
            (email_content, predicted_category, user_category, confidence, 
             feedback_date, email_sender, email_subject, is_correction)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (email_content, predicted_category, user_category, confidence,
              datetime.now(), sender, subject, is_correction))
        
        # Update category usage
        cursor.execute('''
            UPDATE custom_categories 
            SET usage_count = usage_count + 1 
            WHERE category_name = ?
        ''', (user_category,))
        
        conn.commit()
        conn.close()
        
        # Only check for retraining occasionally, not after every feedback
        # This prevents the constant retraining issue
        if not hasattr(self, '_feedback_count'):
            self._feedback_count = 0
        self._feedback_count += 1
        
        # Only check retraining trigger every 50 feedback records to prevent constant retraining
        if self._feedback_count % 50 == 0:
            self.check_retrain_trigger()
    
    def check_retrain_trigger(self):
        """Check if model should be retrained based on new feedback"""
        # Check if we recently retrained to avoid constant retraining
        if hasattr(self, '_last_retrain_time'):
            time_since_last = time.time() - self._last_retrain_time
            if time_since_last < 300:  # Don't retrain more than once every 5 minutes
                return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check how much new feedback we have since last retrain
        cursor.execute('''
            SELECT COUNT(*) FROM training_feedback 
            WHERE feedback_date > datetime('now', '-1 hour')
        ''')
        recent_feedback = cursor.fetchone()[0]
        
        # Check correction rate
        cursor.execute('''
            SELECT COUNT(*) FROM training_feedback 
            WHERE is_correction = 1 AND feedback_date > datetime('now', '-1 hour')
        ''')
        recent_corrections = cursor.fetchone()[0]
        
        conn.close()
        
        # Only retrain if we have significant feedback AND high correction rate
        # Very conservative thresholds to prevent constant retraining
        if recent_feedback >= 100 or (recent_corrections >= 10 and recent_corrections / max(recent_feedback, 1) > 0.6):
            print("Triggering model retraining based on user feedback...")
            self._last_retrain_time = time.time()
            self.retrain_model()
    
    def force_retrain(self):
        """Force a manual retrain regardless of thresholds"""
        print("Manual retraining requested...")
        self._last_retrain_time = time.time()
        self.retrain_model()
    
    def load_or_create_model(self):
        """Load existing model or create new one"""
        try:
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            print("Loaded existing smart learning model")
        except (FileNotFoundError, EOFError):
            self.create_initial_model()
    
    def create_initial_model(self):
        """Create initial model with basic training data"""
        # Load any existing training data
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query('''
            SELECT email_content, user_category 
            FROM training_feedback
        ''', conn)
        conn.close()
        
        if len(df) < 5:  # Not enough data, use defaults
            # Create basic model with minimal training
            self.model = Pipeline([
                ('tfidf', TfidfVectorizer(max_features=1000, stop_words='english')),
                ('classifier', MultinomialNB())
            ])
            
            # Minimal training data
            sample_texts = [
                "urgent meeting tomorrow deadline",
                "linkedin connection request profile",
                "rate confirmation load pickup delivery",
                "business proposal contract invoice",
                "spam free offer limited time"
            ]
            sample_labels = ["Important", "LinkedIn", "RateConfirmation", "Business", "Spam"]
            
            self.model.fit(sample_texts, sample_labels)
        else:
            self.train_model_from_data(df)
        
        self.save_model()
    
    def train_model_from_data(self, df):
        """Train model from feedback data"""
        if len(df) < 5:
            print("Not enough training data for smart learning")
            return
        
        # Prepare data
        X = df['email_content'].values
        y = df['user_category'].values
        
        # Create and train model
        self.model = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=1000, stop_words='english')),
            ('classifier', MultinomialNB())
        ])
        
        if len(df) > 20:  # Enough for train/test split
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            self.model.fit(X_train, y_train)
            
            # Evaluate
            predictions = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, predictions)
            
            # Log performance
            self.log_model_performance(accuracy, len(X_train), len(set(y)))
            
            print(f"Smart learning model retrained with accuracy: {accuracy:.3f}")
        else:
            self.model.fit(X, y)
            print("Smart learning model trained with limited data")
    
    def retrain_model(self):
        """Retrain the model with all available feedback"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query('''
            SELECT email_content, user_category 
            FROM training_feedback
            ORDER BY feedback_date DESC
        ''', conn)
        conn.close()
        
        if len(df) >= 5:
            self.train_model_from_data(df)
            self.save_model()
            print("Model successfully retrained with user feedback")
        else:
            print("Not enough feedback data for retraining")
    
    def classify_email(self, email_content, subject="", sender=""):
        """Classify email with confidence scoring"""
        if not hasattr(self, 'model') or self.model is None:
            return "Unknown", 0.0
        
        try:
            # Combine email content with subject for better classification
            full_content = f"{subject} {email_content}".strip()
            
            # Get prediction and probabilities
            prediction = self.model.predict([full_content])[0]
            probabilities = self.model.predict_proba([full_content])[0]
            confidence = max(probabilities)
            
            # Apply business rules for confidence adjustment
            confidence = self.adjust_confidence_with_rules(
                full_content, prediction, confidence, sender
            )
            
            return prediction, confidence
        
        except Exception as e:
            print(f"Classification error: {e}")
            return "Unknown", 0.0
    
    def adjust_confidence_with_rules(self, content, prediction, confidence, sender):
        """Apply business rules to adjust confidence"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get category rules
        cursor.execute('''
            SELECT keywords, rules FROM custom_categories 
            WHERE category_name = ?
        ''', (prediction,))
        
        result = cursor.fetchone()
        if result:
            keywords = json.loads(result[0])
            rules = json.loads(result[1])
            
            # Boost confidence if keywords match
            content_lower = content.lower()
            keyword_matches = sum(1 for keyword in keywords if keyword.lower() in content_lower)
            if keyword_matches > 0:
                confidence += 0.1 * keyword_matches
                confidence = min(confidence, 1.0)
            
            # Apply sender-based rules
            if sender and '@' in sender:
                domain = sender.split('@')[1]
                if prediction == 'LinkedIn' and 'linkedin' in domain:
                    confidence += 0.2
                elif prediction == 'RateConfirmation' and any(
                    freight_term in domain.lower() 
                    for freight_term in ['freight', 'transport', 'logistics']
                ):
                    confidence += 0.15
        
        conn.close()
        return min(confidence, 1.0)
    
    def get_learning_stats(self):
        """Get statistics about the learning system"""
        conn = sqlite3.connect(self.db_path)
        
        stats = {}
        
        # Total feedback
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM training_feedback')
        stats['total_feedback'] = cursor.fetchone()[0]
        
        # Correction rate
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(is_correction) as corrections
            FROM training_feedback
        ''')
        result = cursor.fetchone()
        if result[0] > 0:
            stats['correction_rate'] = result[1] / result[0]
        else:
            stats['correction_rate'] = 0
        
        # Category distribution
        cursor.execute('''
            SELECT user_category, COUNT(*) as count
            FROM training_feedback
            GROUP BY user_category
            ORDER BY count DESC
        ''')
        stats['category_distribution'] = {
            row[0]: row[1] for row in cursor.fetchall()
        }
        
        # Recent activity
        cursor.execute('''
            SELECT COUNT(*) FROM training_feedback
            WHERE feedback_date >= datetime('now', '-7 days')
        ''')
        stats['recent_feedback'] = cursor.fetchone()[0]
        
        # Custom categories
        cursor.execute('SELECT COUNT(*) FROM custom_categories')
        stats['total_categories'] = cursor.fetchone()[0]
        
        conn.close()
        return stats
    
    def log_model_performance(self, accuracy, training_size, categories_count):
        """Log model performance metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        version = f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        cursor.execute('''
            INSERT INTO model_performance 
            (model_version, accuracy, training_size, test_date, categories_count)
            VALUES (?, ?, ?, ?, ?)
        ''', (version, accuracy, training_size, datetime.now(), categories_count))
        
        conn.commit()
        conn.close()
    
    def save_model(self):
        """Save the trained model"""
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)
    
    def get_category_suggestions(self, email_content):
        """Get category suggestions for uncertain classifications"""
        prediction, confidence = self.classify_email(email_content)
        
        if confidence < self.confidence_threshold:
            # Get all possible categories with their probabilities
            probabilities = self.model.predict_proba([email_content])[0]
            classes = self.model.classes_
            
            # Get top 3 suggestions
            top_indices = np.argsort(probabilities)[-3:][::-1]
            suggestions = [
                (classes[i], probabilities[i]) 
                for i in top_indices
            ]
            
            return suggestions
        
        return [(prediction, confidence)]

def main():
    """Demo the smart learning system"""
    classifier = SmartLearningClassifier()
    
    # Test classification
    test_email = """
    Subject: Rate confirmation for load #ABC123
    
    Please confirm the rate of $2,500 for pickup on Monday.
    Load details: 45,000 lbs from Chicago to Atlanta.
    """
    
    prediction, confidence = classifier.classify_email(test_email)
    print(f"Classification: {prediction} (confidence: {confidence:.3f})")
    
    # Simulate user feedback
    classifier.record_user_feedback(
        test_email, prediction, "RateConfirmation", 
        confidence, "dispatch@freightco.com", "Rate confirmation for load #ABC123"
    )
    
    # Get learning stats
    stats = classifier.get_learning_stats()
    print("\nLearning Statistics:")
    print(json.dumps(stats, indent=2))
    
    # Add custom category
    success = classifier.add_custom_category(
        "DOTCompliance", 
        "Department of Transportation compliance emails",
        ["DOT", "compliance", "inspection", "violation", "CSA"],
        {"priority": "high", "department": "safety"}
    )
    print(f"\nCustom category added: {success}")

if __name__ == "__main__":
    main()