#!/usr/bin/env python3
"""
Example usage script for Gmail Email Classifier
Demonstrates different ways to use the email classification system
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def example_1_test_connection():
    """Example 1: Test Gmail connection"""
    print("Example 1: Testing Gmail Connection")
    print("=" * 40)
    
    try:
        from test_gmail_connection import test_gmail_connection
        test_gmail_connection()
        print("✅ Connection test completed")
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
    print()

def example_2_rule_based_classification():
    """Example 2: Rule-based email classification"""
    print("Example 2: Rule-based Classification")
    print("=" * 40)
    
    try:
        from rule_based_classifier import RuleBasedClassifier
        
        # Initialize classifier
        classifier = RuleBasedClassifier()
        
        # Example emails
        test_emails = [
            {
                'subject': 'Meeting tomorrow at 2 PM',
                'sender': 'colleague@company.com',
                'body': 'Hi, just confirming our meeting tomorrow at 2 PM in conference room A.'
            },
            {
                'subject': 'Your Amazon order has shipped',
                'sender': 'shipment-tracking@amazon.com',
                'body': 'Your order #123456789 has been shipped and will arrive tomorrow.'
            },
            {
                'subject': 'Weekly newsletter from TechCrunch',
                'sender': 'newsletter@techcrunch.com',
                'body': 'Here are this week\'s top tech stories...'
            }
        ]
        
        # Classify emails
        for i, email in enumerate(test_emails, 1):
            print(f"Email {i}:")
            print(f"  Subject: {email['subject']}")
            print(f"  From: {email['sender']}")
            
            # Get classification
            result = classifier.classify_email(
                email['subject'], 
                email['sender'], 
                email['body']
            )
            
            print(f"  Classification: {result['label']} (confidence: {result['confidence']:.2f})")
            print(f"  Reason: {result['reason']}")
            print()
        
        print("✅ Rule-based classification completed")
    except Exception as e:
        print(f"❌ Rule-based classification failed: {e}")
    print()

def example_3_ml_classification():
    """Example 3: Machine learning classification"""
    print("Example 3: ML Classification")
    print("=" * 40)
    
    try:
        from ml_email_classifier import EmailMLClassifier
        
        # Check if model exists
        if not os.path.exists('email_classifier.pkl'):
            print("⚠️ ML model not found. Please train the model first:")
            print("   python ml_email_classifier.py")
            return
        
        # Initialize classifier
        classifier = EmailMLClassifier()
        classifier.load_model()
        
        # Example emails
        test_emails = [
            "Meeting scheduled for tomorrow at 2 PM in the conference room",
            "Your Amazon order has been shipped and tracking information is available",
            "Weekly newsletter with the latest tech news and updates",
            "Social media notification: You have 5 new friend requests",
            "Bank statement for December 2024 is now available"
        ]
        
        # Classify emails
        for i, email_text in enumerate(test_emails, 1):
            print(f"Email {i}: {email_text[:50]}...")
            
            # Get classification
            result = classifier.predict(email_text)
            
            print(f"  Classification: {result['prediction']} (confidence: {result['confidence']:.2f})")
            print()
        
        print("✅ ML classification completed")
    except Exception as e:
        print(f"❌ ML classification failed: {e}")
    print()

def example_4_collect_training_data():
    """Example 4: Collect training data from Gmail"""
    print("Example 4: Collect Training Data")
    print("=" * 40)
    
    try:
        from training_data_collector import TrainingDataCollector
        
        print("This will collect labeled emails from your Gmail account")
        response = input("Continue? (y/N): ")
        
        if response.lower() == 'y':
            collector = TrainingDataCollector()
            collector.collect_training_data()
            print("✅ Training data collection completed")
        else:
            print("Skipped training data collection")
    except Exception as e:
        print(f"❌ Training data collection failed: {e}")
    print()

def example_5_train_model():
    """Example 5: Train the ML model"""
    print("Example 5: Train ML Model")
    print("=" * 40)
    
    try:
        from ml_email_classifier import EmailMLClassifier
        
        # Check if training data exists
        if not os.path.exists('email_training_data.csv'):
            print("⚠️ No training data found. Please collect training data first:")
            print("   python training_data_collector.py")
            return
        
        print("This will train a new ML model using your training data")
        response = input("Continue? (y/N): ")
        
        if response.lower() == 'y':
            classifier = EmailMLClassifier()
            classifier.train_model()
            print("✅ Model training completed")
        else:
            print("Skipped model training")
    except Exception as e:
        print(f"❌ Model training failed: {e}")
    print()

def example_6_hybrid_classification():
    """Example 6: Hybrid classification (rule-based + ML)"""
    print("Example 6: Hybrid Classification")
    print("=" * 40)
    
    try:
        # This would demonstrate the hybrid approach from Gmail_scraper.py
        print("This example would show the hybrid classification system")
        print("that combines rule-based and ML approaches.")
        print()
        print("To use the hybrid system:")
        print("1. Ensure both rule-based and ML models are ready")
        print("2. Run: python Gmail_scraper.py")
        print("3. The system will use rules first, then ML for uncertain cases")
        print()
        
        print("✅ Hybrid classification info provided")
    except Exception as e:
        print(f"❌ Hybrid classification demo failed: {e}")
    print()

def main():
    """Main function to run examples"""
    print("🚀 Gmail Email Classifier - Usage Examples")
    print("=" * 50)
    print()
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️ .env file not found!")
        print("Please copy .env.example to .env and configure your Gmail credentials")
        print("Run: python setup.py")
        return
    
    examples = [
        ("Test Gmail Connection", example_1_test_connection),
        ("Rule-based Classification", example_2_rule_based_classification),
        ("ML Classification", example_3_ml_classification),
        ("Collect Training Data", example_4_collect_training_data),
        ("Train ML Model", example_5_train_model),
        ("Hybrid Classification Info", example_6_hybrid_classification),
    ]
    
    print("Available examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    print(f"  {len(examples) + 1}. Run all examples")
    print("  0. Exit")
    print()
    
    while True:
        try:
            choice = input("Select an example (0-{}): ".format(len(examples) + 1))
            choice = int(choice)
            
            if choice == 0:
                print("Goodbye!")
                break
            elif choice == len(examples) + 1:
                # Run all examples
                for name, func in examples:
                    print(f"\n{'='*60}")
                    func()
                break
            elif 1 <= choice <= len(examples):
                # Run selected example
                print(f"\n{'='*60}")
                examples[choice - 1][1]()
                
                # Ask if user wants to continue
                cont = input("Run another example? (y/N): ")
                if cont.lower() != 'y':
                    print("Goodbye!")
                    break
            else:
                print("Invalid choice. Please try again.")
                
        except ValueError:
            print("Please enter a valid number.")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break

if __name__ == "__main__":
    main()