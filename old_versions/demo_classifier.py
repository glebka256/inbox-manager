#!/usr/bin/env python3
"""
Gmail AI Manager Demo - Process Recent Emails
This demo version processes your 10 most recent emails to show you how the AI classification works.
"""

import os
import imaplib
import email
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

GMAIL_EMAIL = os.getenv('GMAIL_EMAIL')
GMAIL_PASSWORD = os.getenv('GMAIL_PASSWORD')

if not GMAIL_EMAIL or not GMAIL_PASSWORD:
    print("❌ Please configure your .env file with Gmail credentials")
    exit(1)

# Ensure credentials are properly encoded
try:
    GMAIL_EMAIL = GMAIL_EMAIL.encode('ascii', errors='ignore').decode('ascii')
    GMAIL_PASSWORD = GMAIL_PASSWORD.encode('ascii', errors='ignore').decode('ascii')
except:
    pass  # If there's any issue, use as-is

def demo_email_classification():
    """Demo function to show email classification on recent emails"""
    print("🚀 Gmail AI Manager - Demo Classification")
    print("=" * 60)
    print("This demo will analyze your 10 most recent emails and show")
    print("how the AI would classify them (without applying labels).")
    print()
    
    try:
        print("🔗 Connecting to Gmail...")
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(GMAIL_EMAIL, GMAIL_PASSWORD)
        mail.select("inbox")
        
        # Get recent emails (last 10)
        _, data = mail.search(None, "ALL")
        email_ids = data[0].split()
        
        if not email_ids:
            print("📭 No emails found in inbox.")
            mail.logout()
            return
        
        # Get the 10 most recent emails
        recent_emails = email_ids[-10:]
        print(f"📧 Analyzing {len(recent_emails)} most recent emails...")
        print("=" * 80)
        
        for i, email_id in enumerate(recent_emails, 1):
            try:
                # Fetch email
                _, msg_data = mail.fetch(email_id, "(RFC822)")
                email_message = email.message_from_bytes(msg_data[0][1])
                
                # Extract email information
                subject = email_message.get("Subject", "No Subject")
                sender = email_message.get("From", "Unknown Sender")
                date = email_message.get("Date", "Unknown Date")
                
                # Clean up subject and sender for display
                if subject:
                    # Remove any problematic characters
                    subject = str(subject).encode('ascii', errors='ignore').decode('ascii')
                if sender:
                    sender = str(sender).encode('ascii', errors='ignore').decode('ascii')
                
                # Get email body (simplified)
                body = ""
                if email_message.is_multipart():
                    for part in email_message.walk():
                        if part.get_content_type() == "text/plain":
                            try:
                                body_bytes = part.get_payload(decode=True)
                                if body_bytes:
                                    body = body_bytes.decode('utf-8', errors='ignore')[:200]
                                    break
                            except:
                                continue
                else:
                    try:
                        body_bytes = email_message.get_payload(decode=True)
                        if body_bytes:
                            body = body_bytes.decode('utf-8', errors='ignore')[:200]
                    except:
                        body = "Could not decode body"
                
                # Simple classification based on keywords and sender
                classification = classify_email_simple(subject, sender, body)
                
                print(f"{i:2d}. 📧 Email Analysis:")
                print(f"   Subject: {subject[:60]}...")
                print(f"   From: {sender[:50]}")
                print(f"   Date: {date}")
                print(f"   🤖 AI Classification: {classification['label']}")
                print(f"   📊 Confidence: {classification['confidence']}/5")
                print(f"   💡 Reason: {classification['reason']}")
                print("-" * 80)
                
            except Exception as e:
                print(f"⚠️ Error processing email {i}: {e}")
                continue
        
        mail.logout()
        print("✅ Demo classification completed!")
        print()
        print("🎯 To actually apply labels to emails:")
        print("   1. Edit rule_based_classifier.py")
        print("   2. Change 'dry_run=True' to 'dry_run=False'")
        print("   3. Run: python rule_based_classifier.py")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()

def classify_email_simple(subject, sender, body):
    """Simple email classification logic"""
    subject_lower = subject.lower()
    sender_lower = sender.lower()
    body_lower = body.lower()
    
    # LinkedIn detection
    if any(keyword in subject_lower + sender_lower + body_lower for keyword in 
           ['linkedin', 'connection', 'network', 'professional', 'job alert']):
        return {
            'label': 'LinkedIn',
            'confidence': 5,
            'reason': 'LinkedIn keywords detected'
        }
    
    # API/Developer detection
    if any(keyword in subject_lower + sender_lower + body_lower for keyword in 
           ['api', 'github', 'developer', 'webhook', 'json', 'endpoint']):
        return {
            'label': 'API',
            'confidence': 4,
            'reason': 'API/Developer keywords detected'
        }
    
    # Government contracts
    if any(keyword in subject_lower + sender_lower + body_lower for keyword in 
           ['government', 'federal', 'contract', 'bid', 'rfp', 'cage', 'sam.gov']):
        return {
            'label': 'Gov.com',
            'confidence': 5,
            'reason': 'Government contract keywords detected'
        }
    
    # Freight/Logistics
    if any(keyword in subject_lower + sender_lower + body_lower for keyword in 
           ['freight', 'trucking', 'shipping', 'logistics', 'load', 'cargo', 'transportation']):
        return {
            'label': 'leads',
            'confidence': 4,
            'reason': 'Freight/logistics keywords detected'
        }
    
    # Bonfire
    if any(keyword in subject_lower + sender_lower + body_lower for keyword in 
           ['bonfire', 'apparel', 'custom shirts', 'fundraising']):
        return {
            'label': 'Bonfire',
            'confidence': 5,
            'reason': 'Bonfire keywords detected'
        }
    
    # Rate confirmation
    if any(keyword in subject_lower + sender_lower + body_lower for keyword in 
           ['rate confirmation', 'ratecon', 'dispatch', 'pickup', 'delivery']):
        return {
            'label': 'Ratecon',
            'confidence': 5,
            'reason': 'Rate confirmation keywords detected'
        }
    
    # Default classification
    return {
        'label': 'Unknown',
        'confidence': 1,
        'reason': 'No specific keywords matched'
    }

if __name__ == "__main__":
    demo_email_classification()