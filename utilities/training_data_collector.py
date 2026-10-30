import imaplib
import email
import os
import json
import csv
import re
from dotenv import load_dotenv
from datetime import datetime
import pandas as pd

# Load environment variables from .env file
load_dotenv()

# Get email credentials from environment variables
GMAIL_EMAIL = os.getenv('GMAIL_EMAIL', '').strip()
GMAIL_PASSWORD = os.getenv('GMAIL_PASSWORD', '').strip().replace(' ', '').replace('\xa0', '')

# Validate that credentials are loaded
if not GMAIL_EMAIL or not GMAIL_PASSWORD:
    raise ValueError("Please set GMAIL_EMAIL and GMAIL_PASSWORD in your .env file")

class TrainingDataCollector:
    def __init__(self):
        self.training_data = []
        
    def clean_text(self, text):
        """Clean and normalize text for training"""
        if not text:
            return ""
        
        # Decode any encoded subjects
        try:
            import email.header
            decoded = email.header.decode_header(text)
            text = ""
            for part, encoding in decoded:
                if isinstance(part, bytes):
                    if encoding:
                        text += part.decode(encoding, errors='ignore')
                    else:
                        text += part.decode('utf-8', errors='ignore')
                else:
                    text += part
        except:
            pass
        
        # Basic text cleaning
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single
        text = re.sub(r'[^\w\s@\.-]', ' ', text)  # Keep alphanumeric, @, ., -
        text = text.strip().lower()
        
        return text
    
    def extract_features_from_email(self, msg, sender, label):
        """Extract features from an email for training"""
        subject = msg.get("subject", "") or ""
        sender = sender or ""
        date_str = msg.get("date", "") or ""
        
        # Clean the texts
        clean_subject = self.clean_text(subject)
        clean_sender = self.clean_text(sender)
        
        # Extract domain from sender
        domain = ""
        if "@" in sender:
            try:
                domain = sender.split("@")[1].split(">")[0].strip().lower()
            except:
                domain = ""
        
        # Create feature text (combine subject and sender info)
        feature_text = f"{clean_subject} {clean_sender}"
        
        return {
            'original_subject': subject,
            'clean_subject': clean_subject,
            'sender': sender,
            'clean_sender': clean_sender,
            'domain': domain,
            'feature_text': feature_text,
            'label': label,
            'date': date_str
        }
    
    def collect_from_label(self, mail, label_name, max_emails=100):
        """Collect training data from a specific Gmail label"""
        print(f"📁 Collecting training data from label: {label_name}")
        
        try:
            # Select the label folder
            mail.select(f'"{label_name}"')
            
            # Search for emails in this label
            _, data = mail.search(None, "ALL")
            
            if not data[0]:
                print(f"   ❌ No emails found in label: {label_name}")
                return 0
            
            email_ids = data[0].split()
            total_emails = len(email_ids)
            
            # Limit the number of emails to process
            if total_emails > max_emails:
                email_ids = email_ids[-max_emails:]  # Get most recent emails
                print(f"   📊 Processing {max_emails} most recent emails out of {total_emails}")
            else:
                print(f"   📊 Processing all {total_emails} emails")
            
            processed = 0
            
            for email_id in email_ids:
                try:
                    # Fetch email
                    _, msg_data = mail.fetch(email_id, '(RFC822)')
                    msg = email.message_from_bytes(msg_data[0][1])
                    
                    sender = msg.get("from", "") or ""
                    
                    # Extract features
                    features = self.extract_features_from_email(msg, sender, label_name)
                    self.training_data.append(features)
                    processed += 1
                    
                except Exception as e:
                    print(f"   ⚠️ Error processing email {email_id}: {e}")
                    continue
            
            print(f"   ✅ Successfully processed {processed} emails from {label_name}")
            return processed
            
        except Exception as e:
            print(f"   ❌ Error accessing label {label_name}: {e}")
            return 0
    
    def collect_training_data(self, labels_to_collect=None, max_emails_per_label=50):
        """Collect training data from multiple Gmail labels"""
        
        if labels_to_collect is None:
            # Your main labels based on the classifier
            labels_to_collect = [
                'API', 'LinkedIn', 'Coding', 'Gov.com', 'leads', 
                'Bonfire', 'Ratecon', 'Shippers', 'Solmlbsm-Gov. Contracts'
            ]
        
        try:
            print(f"🔗 Connecting to Gmail for: {GMAIL_EMAIL}")
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(GMAIL_EMAIL, GMAIL_PASSWORD)
            
            print(f"📚 Collecting training data from {len(labels_to_collect)} labels")
            print("=" * 60)
            
            total_collected = 0
            
            for label in labels_to_collect:
                collected = self.collect_from_label(mail, label, max_emails_per_label)
                total_collected += collected
                print()
            
            mail.logout()
            
            print("=" * 60)
            print(f"📊 Training Data Collection Summary:")
            print(f"   Total emails collected: {total_collected}")
            print(f"   Labels covered: {len(labels_to_collect)}")
            print(f"   Average emails per label: {total_collected / len(labels_to_collect):.1f}")
            
            return total_collected
            
        except Exception as e:
            print(f"❌ Error during data collection: {e}")
            return 0
    
    def save_training_data(self, filename="email_training_data.csv"):
        """Save collected training data to CSV file"""
        if not self.training_data:
            print("❌ No training data to save")
            return False
        
        try:
            df = pd.DataFrame(self.training_data)
            df.to_csv(filename, index=False)
            
            print(f"💾 Training data saved to: {filename}")
            print(f"📊 Dataset statistics:")
            print(f"   Total samples: {len(df)}")
            print(f"   Label distribution:")
            
            label_counts = df['label'].value_counts()
            for label, count in label_counts.items():
                print(f"     {label}: {count} emails")
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving training data: {e}")
            return False
    
    def analyze_training_data(self):
        """Analyze the collected training data"""
        if not self.training_data:
            print("❌ No training data to analyze")
            return
        
        df = pd.DataFrame(self.training_data)
        
        print("🔍 Training Data Analysis:")
        print("=" * 50)
        
        print(f"📊 Dataset Overview:")
        print(f"   Total samples: {len(df)}")
        print(f"   Unique labels: {df['label'].nunique()}")
        print(f"   Average subject length: {df['clean_subject'].str.len().mean():.1f} characters")
        
        print(f"\n📈 Label Distribution:")
        label_counts = df['label'].value_counts()
        for label, count in label_counts.items():
            percentage = (count / len(df)) * 100
            print(f"   {label}: {count} emails ({percentage:.1f}%)")
        
        print(f"\n📧 Top Domains by Label:")
        for label in df['label'].unique():
            label_df = df[df['label'] == label]
            top_domains = label_df['domain'].value_counts().head(3)
            print(f"   {label}:")
            for domain, count in top_domains.items():
                if domain:  # Skip empty domains
                    print(f"     {domain}: {count} emails")
        
        print(f"\n🔤 Sample Subjects by Label:")
        for label in df['label'].unique():
            label_df = df[df['label'] == label]
            sample_subjects = label_df['original_subject'].head(2).tolist()
            print(f"   {label}:")
            for subject in sample_subjects:
                print(f"     \"{subject[:60]}...\"")

def main():
    collector = TrainingDataCollector()
    
    print("🚀 Email Training Data Collector")
    print("=" * 50)
    
    # Collect training data
    total_collected = collector.collect_training_data(max_emails_per_label=30)
    
    if total_collected > 0:
        # Analyze the data
        print("\n" + "=" * 50)
        collector.analyze_training_data()
        
        # Save the training data
        print("\n" + "=" * 50)
        collector.save_training_data("email_training_data.csv")
        
        # Also save as JSON for backup
        with open("email_training_data.json", "w") as f:
            json.dump(collector.training_data, f, indent=2)
        print("💾 Backup saved as: email_training_data.json")
        
    else:
        print("❌ No training data was collected")

if __name__ == "__main__":
    main()