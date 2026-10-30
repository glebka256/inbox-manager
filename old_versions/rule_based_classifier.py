import imaplib
import email
import os
import re
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Get email credentials from environment variables
GMAIL_EMAIL = os.getenv('GMAIL_EMAIL', '').strip()
GMAIL_PASSWORD = os.getenv('GMAIL_PASSWORD', '').strip().replace(' ', '').replace('\xa0', '')

# Validate that credentials are loaded
if not GMAIL_EMAIL or not GMAIL_PASSWORD:
    raise ValueError("Please set GMAIL_EMAIL and GMAIL_PASSWORD in your .env file")

# Rule-based classification patterns based on your Gmail labels
CLASSIFICATION_RULES = {
    'API': {
        'keywords': ['api', 'endpoint', 'rest', 'json', 'webhook', 'integration', 'developer', 'postman'],
        'senders': ['api@', 'developer@', 'noreply@github.com', 'notifications@github.com'],
        'domains': ['github.com', 'stripe.com', 'twilio.com', 'sendgrid.com']
    },
    'LinkedIn': {
        'keywords': ['linkedin', 'connection', 'network', 'professional', 'job alert', 'messaged you'],
        'senders': ['linkedin.com', 'messaging-digest-noreply@linkedin.com', 'noreply@linkedin.com'],
        'domains': ['linkedin.com']
    },
    'Coding': {
        'keywords': ['github', 'stackoverflow', 'programming', 'python', 'javascript', 'code', 'repository', 'commit', 'pull request'],
        'senders': ['github.com', 'stackoverflow.com', 'codecademy.com'],
        'domains': ['github.com', 'stackoverflow.com', 'codepen.io']
    },
    'Gov.com': {
        'keywords': ['government', 'federal', 'contract', 'bid', 'rfp', 'proposal', 'sam.gov', 'gsa'],
        'senders': ['sam.gov', 'gsa.gov', 'sba.gov'],
        'domains': ['.gov']
    },
    'leads': {
        'keywords': ['freight', 'trucking', 'shipping', 'logistics', 'load', 'cargo', 'transportation', 'quote'],
        'senders': ['loadboard', 'truckstop', 'dat.com'],
        'domains': ['freightquote.com', 'uship.com']
    },
    'Bonfire': {
        'keywords': ['bonfire', 'apparel', 'custom shirts', 'fundraising', 'merchandise'],
        'senders': ['bonfire.com', 'noreply@bonfire.com'],
        'domains': ['bonfire.com']
    },
    'Ratecon': {
        'keywords': ['rate confirmation', 'ratecon', 'load confirmation', 'dispatch', 'pickup', 'delivery'],
        'senders': ['dispatch@', 'operations@'],
        'domains': []
    }
}

class RuleBasedClassifier:
    def __init__(self):
        self.rules = CLASSIFICATION_RULES
    
    def classify_email(self, subject, sender, body_preview=""):
        """Classify email based on rules"""
        subject_lower = (subject or "").lower()
        sender_lower = (sender or "").lower()
        body_lower = (body_preview or "").lower()
        
        # Combine all text for analysis
        full_text = f"{subject_lower} {sender_lower} {body_lower}"
        
        scores = {}
        
        for label, rules in self.rules.items():
            score = 0
            
            # Check keywords
            for keyword in rules['keywords']:
                if keyword.lower() in full_text:
                    score += 2  # Keywords get higher weight
            
            # Check sender patterns
            for sender_pattern in rules['senders']:
                if sender_pattern.lower() in sender_lower:
                    score += 3  # Sender matches get highest weight
            
            # Check domains
            for domain in rules['domains']:
                if domain.lower() in sender_lower:
                    score += 3  # Domain matches get highest weight
            
            if score > 0:
                scores[label] = score
        
        # Return the label with highest score, or None if no matches
        if scores:
            best_label = max(scores.items(), key=lambda x: x[1])
            return best_label[0], best_label[1]
        
        return None, 0
    
    def add_rule(self, label, keywords=None, senders=None, domains=None):
        """Add new classification rules"""
        if label not in self.rules:
            self.rules[label] = {'keywords': [], 'senders': [], 'domains': []}
        
        if keywords:
            self.rules[label]['keywords'].extend(keywords)
        if senders:
            self.rules[label]['senders'].extend(senders)
        if domains:
            self.rules[label]['domains'].extend(domains)

def apply_label_to_email(mail, email_num, label_name):
    """Apply a Gmail label to a specific email"""
    try:
        # Gmail IMAP uses the STORE command to add labels
        mail.store(email_num, '+X-GM-LABELS', f'({label_name})')
        return True
    except Exception as e:
        print(f"❌ Error applying label '{label_name}': {e}")
        return False

def get_email_labels(mail, email_num):
    """Get existing labels for an email"""
    try:
        _, msg_data = mail.fetch(email_num, '(X-GM-LABELS)')
        if msg_data and msg_data[0]:
            labels_info = msg_data[0].decode('utf-8')
            # Extract labels from the response
            labels_match = re.search(r'X-GM-LABELS \((.*?)\)', labels_info)
            if labels_match:
                labels = labels_match.group(1).replace('"', '').split()
                return labels
        return []
    except Exception as e:
        print(f"⚠️ Error getting labels: {e}")
        return []

def get_email_body_preview(msg, max_length=200):
    """Extract a preview of email body for classification"""
    try:
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    break
        else:
            body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
        
        # Clean and truncate
        body = re.sub(r'\s+', ' ', body).strip()
        return body[:max_length]
    except:
        return ""

def classify_and_label_emails(dry_run=True):
    """Main function to classify and label emails"""
    classifier = RuleBasedClassifier()
    
    try:
        print(f"🔗 Connecting to Gmail for: {GMAIL_EMAIL}")
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(GMAIL_EMAIL, GMAIL_PASSWORD)
        mail.select("inbox")
        
        # Get unread emails
        _, data = mail.search(None, "UNSEEN")
        
        if not data[0]:
            print("📭 No unread emails found.")
            mail.logout()
            return
        
        email_ids = data[0].split()
        print(f"📧 Found {len(email_ids)} unread emails to classify")
        print("=" * 80)
        
        classified_count = 0
        
        for i, num in enumerate(email_ids, 1):
            try:
                # Fetch email message
                _, msg_data = mail.fetch(num, '(RFC822)')
                msg = email.message_from_bytes(msg_data[0][1])
                
                # Extract email details
                subject = msg["subject"] or 'No Subject'
                sender = msg["from"] or 'Unknown Sender'
                date = msg["date"] or 'Unknown Date'
                
                # Get body preview for better classification
                body_preview = get_email_body_preview(msg)
                
                # Get current labels
                current_labels = get_email_labels(mail, num)
                
                # Classify email
                predicted_label, confidence = classifier.classify_email(subject, sender, body_preview)
                
                print(f"{i}. 📧 Email Analysis:")
                print(f"   Subject: {subject}")
                print(f"   From: {sender}")
                print(f"   Current Labels: {current_labels}")
                
                if predicted_label:
                    print(f"   🤖 Predicted: {predicted_label} (confidence: {confidence})")
                    
                    # Check if label should be applied
                    if predicted_label not in current_labels:
                        if dry_run:
                            print(f"   🔄 [DRY RUN] Would apply label: {predicted_label}")
                        else:
                            if apply_label_to_email(mail, num, predicted_label):
                                print(f"   ✅ Applied label: {predicted_label}")
                                classified_count += 1
                            else:
                                print(f"   ❌ Failed to apply label: {predicted_label}")
                    else:
                        print(f"   ℹ️ Label '{predicted_label}' already exists")
                else:
                    print(f"   ❓ No classification rule matched")
                
                print("-" * 80)
                
            except Exception as e:
                print(f"❌ Error processing email {num}: {e}")
                print("-" * 80)
        
        mail.logout()
        
        if dry_run:
            print(f"\n🔍 DRY RUN COMPLETE - No labels were actually applied")
            print(f"📊 {classified_count} emails would have been classified")
            print(f"💡 Run with dry_run=False to apply labels")
        else:
            print(f"\n✅ CLASSIFICATION COMPLETE")
            print(f"📊 Successfully classified and labeled {classified_count} emails")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def show_classification_rules():
    """Display current classification rules"""
    print("📋 Current Classification Rules:")
    print("=" * 50)
    
    for label, rules in CLASSIFICATION_RULES.items():
        print(f"\n🏷️ {label}:")
        print(f"   Keywords: {', '.join(rules['keywords'])}")
        print(f"   Senders: {', '.join(rules['senders'])}")
        print(f"   Domains: {', '.join(rules['domains'])}")

if __name__ == "__main__":
    print("🚀 Rule-Based Email Classifier")
    print("=" * 50)
    
    # Show current rules
    show_classification_rules()
    
    print("\n" + "=" * 50)
    print("🔍 Starting classification (DRY RUN mode)")
    print("=" * 50)
    
    # Run in dry-run mode first
    classify_and_label_emails(dry_run=True)