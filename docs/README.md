# 🤖 Gmail AI Manager - Intelligent Email Organization System

**An AI-powered Gmail management system that automatically classifies and organizes your emails using advanced machine learning and rule-based algorithms.**

This intelligent system acts as your personal AI assistant for Gmail, learning from your email patterns and automatically categorizing incoming messages. No more manual email sorting - let AI do the work for you!

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Gmail](https://img.shields.io/badge/Gmail-AI-red.svg)
![AI](https://img.shields.io/badge/AI-Machine%20Learning-orange.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🤖 AI Features

- 🧠 **Hybrid AI Classification**: Combines machine learning and rule-based intelligence for optimal accuracy
- 🔮 **Automatic Email Organization**: AI automatically labels and categorizes your emails
- 🎯 **Smart Pattern Recognition**: Learns from your existing Gmail labels and email patterns
- 📚 **Adaptive Intelligence**: Improves classification accuracy over time
- ✅ **Confidence-Based Decisions**: Only applies labels when AI is confident about the classification
- 🤖 **Multi-Algorithm Approach**: Uses TF-IDF vectorization with Naive Bayes ML + keyword pattern matching
- 🔄 **Intelligent Fallback System**: Seamlessly switches between AI methods for best results
- ⚡ **Fast AI Processing**: Efficient batch processing of emails with real-time classification
- � **AI Analytics**: Detailed AI performance reports and statistics

## � What This AI System Does

**Think of this as your personal AI assistant for Gmail.** 

This system:
- 🤖 **Learns** from your existing email organization patterns
- 🧠 **Analyzes** incoming emails using advanced AI algorithms
- 🏷️ **Automatically** applies appropriate Gmail labels
- 📊 **Improves** its accuracy over time through machine learning
- ⚡ **Saves** you hours of manual email sorting

**Example**: When you receive an email from "orders@amazon.com" with subject "Your order has shipped", the AI will automatically label it as "Shopping" and file it appropriately. No manual work required!

## 🏗️ AI System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Gmail Inbox    │────│  Email Scraper   │────│  Classification │
│  (IMAP)         │    │  (IMAP Client)   │    │  Engine         │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │  Training Data   │    │  Rule Engine &  │
                       │  Collector       │    │  ML Model       │
                       └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │  ML Training     │    │  Label          │
                       │  Pipeline        │    │  Application    │
                       └──────────────────┘    └─────────────────┘
```

## 📋 Table of Contents

- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Components](#-components)
- [Customization](#-customization)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- Gmail account with 2-Factor Authentication enabled
- Gmail App Password (see setup guide below)

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/gmail-email-classifier.git
cd gmail-email-classifier
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Gmail App Password

1. **Enable 2-Factor Authentication** on your Google Account
   - Go to [Google Account Settings](https://myaccount.google.com)
   - Navigate to Security → 2-Step Verification
   - Follow the setup process

2. **Generate App Password**
   - In Security settings, go to 2-Step Verification
   - Click "App passwords"
   - Select "Mail" and "Other (Custom name)"
   - Name it "Email Classifier"
   - Copy the 16-character password

3. **Configure Gmail Credentials**
   
   **📁 IMPORTANT: Use the Credentials Folder**
   
   ```bash
   cd credentials/
   cp gmail_credentials_template.env gmail_credentials.env
   # Edit gmail_credentials.env with your actual credentials
   ```
   
   **See detailed setup guide**: `credentials/README.md`
   
   Your file should look like:
   ```env
   GMAIL_USER=your.email@gmail.com
   GMAIL_PASS=your-16-character-app-password
   ```

### 4. Initial Configuration

```bash
# Test your Gmail connection
python test_gmail_connection.py

# Collect training data from existing labels
python training_data_collector.py

# Train the ML model
python ml_email_classifier.py
```

## ⚡ Quick Start

### Basic Email Classification

```bash
# Test classification without applying labels
python rule_based_classifier.py

# Apply labels to new emails (dry run)
python Gmail_scraper.py --dry-run

# Apply labels to new emails (live)
python Gmail_scraper.py --apply
```

### Training Your Model

```bash
# Collect training data from your existing Gmail labels
python training_data_collector.py

# Train the machine learning model
python ml_email_classifier.py

# View training results
cat email_training_data.csv
```

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# Gmail Credentials
GMAIL_EMAIL=your.email@gmail.com
GMAIL_PASSWORD=your_16_character_app_password

# Optional: Classification Settings
MAX_EMAILS_PER_RUN=50
CONFIDENCE_THRESHOLD=0.6
```

### Classification Rules

Edit the rules in `rule_based_classifier.py`:

```python
CLASSIFICATION_RULES = {
    'Work': {
        'keywords': ['meeting', 'project', 'deadline'],
        'senders': ['boss@company.com'],
        'domains': ['company.com']
    },
    # Add more rules...
}
```

## 🎯 Usage

### Command Line Interface

```bash
# Basic usage
python Gmail_scraper.py

# Options
python Gmail_scraper.py --help
python Gmail_scraper.py --dry-run              # Test without applying labels
python Gmail_scraper.py --max-emails 20       # Limit processing
python Gmail_scraper.py --retrain             # Retrain model first
```

### Programmatic Usage

```python
from rule_based_classifier import RuleBasedClassifier
from ml_email_classifier import EmailMLClassifier

# Initialize classifiers
rule_classifier = RuleBasedClassifier()
ml_classifier = EmailMLClassifier()

# Classify an email
subject = "Meeting tomorrow at 2 PM"
sender = "boss@company.com"

# Rule-based classification
label, confidence = rule_classifier.classify_email(subject, sender)
print(f"Rule-based: {label} (confidence: {confidence})")

# ML classification
ml_classifier.load_model()
prediction = ml_classifier.predict([f"{subject} {sender}"])
print(f"ML prediction: {prediction}")
```

## 🔧 Components

### Core Scripts

| Script | Description |
|--------|-------------|
| `Gmail_scraper.py` | Main email processing and labeling script |
| `rule_based_classifier.py` | Keyword and pattern-based classification |
| `ml_email_classifier.py` | Machine learning model training and prediction |
| `training_data_collector.py` | Extracts training data from existing Gmail labels |
| `test_gmail_connection.py` | Tests Gmail connectivity and permissions |

### Generated Files

| File | Description |
|------|-------------|
| `email_classifier.pkl` | Trained machine learning model |
| `vectorizer.pkl` | TF-IDF vectorizer for text processing |
| `label_mappings.pkl` | Label encoding mappings |
| `email_training_data.csv` | Collected training dataset |

### Configuration Files

| File | Description |
|------|-------------|
| `.env` | Environment variables (credentials) |
| `requirements.txt` | Python dependencies |
| `.gitignore` | Git ignore patterns |

## 🎨 Customization

### Adding New Label Rules

1. **Edit Classification Rules**
   ```python
   # In rule_based_classifier.py
   CLASSIFICATION_RULES['NewLabel'] = {
       'keywords': ['keyword1', 'keyword2'],
       'senders': ['sender@domain.com'],
       'domains': ['domain.com']
   }
   ```

2. **Retrain ML Model**
   ```bash
   python training_data_collector.py
   python ml_email_classifier.py
   ```

### Adjusting Classification Logic

Edit the decision logic in `Gmail_scraper.py`:

```python
def classify_email(self, subject, sender):
    rule_label, rule_score = self.rule_based_classify(subject, sender)
    ml_label, ml_confidence = self.ml_classify(subject, sender)
    
    # Custom decision logic
    if rule_score >= 5:  # Very strong rule match
        return rule_label, "rule"
    elif ml_confidence > 0.8:  # High ML confidence
        return ml_label, "ml"
    # Add more logic...
```

### Performance Optimization

```python
# Limit email processing
MAX_EMAILS_PER_RUN = 100

# Adjust confidence thresholds
ML_CONFIDENCE_THRESHOLD = 0.7
RULE_CONFIDENCE_THRESHOLD = 3

# Enable batch processing
BATCH_SIZE = 50
```

## 📊 Analytics & Monitoring

### Classification Reports

```bash
# Generate detailed classification report
python -c "
from ml_email_classifier import EmailMLClassifier
classifier = EmailMLClassifier()
classifier.load_training_data()
classifier.analyze_training_data()
"
```

### Performance Metrics

The system tracks:
- Classification accuracy per method (rule-based vs ML)
- Processing speed (emails per minute)
- Label distribution
- Confidence scores
- Error rates

### Logs

Check logs for debugging:
```bash
tail -f classification.log
```

## 🚨 Troubleshooting

### Common Issues

**1. Authentication Errors**
```
Error: Authentication failed
```
- Verify 2FA is enabled
- Check App Password is correct (16 characters)
- Ensure no extra spaces in .env file

**2. No Training Data**
```
Error: No valid training data after filtering
```
- Run `training_data_collector.py` first
- Ensure you have existing Gmail labels with emails
- Check Gmail label names match classification rules

**3. Model Loading Errors**
```
Error: email_classifier.pkl not found
```
- Run `ml_email_classifier.py` to train model
- Check file permissions
- Ensure sufficient training data

**4. IMAP Connection Issues**
```
Error: IMAP connection failed
```
- Check internet connection
- Verify Gmail IMAP is enabled
- Try regenerating App Password

### Debug Mode

Enable verbose logging:
```bash
export DEBUG=true
python Gmail_scraper.py
```

### Performance Issues

If processing is slow:
1. Reduce `MAX_EMAILS_PER_RUN`
2. Use `--dry-run` for testing
3. Process emails in smaller batches
4. Check network connection speed

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md).

### Development Setup

```bash
# Clone and setup development environment
git clone https://github.com/your-username/gmail-email-classifier.git
cd gmail-email-classifier

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Code formatting
black .
flake8 .
```

### Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [scikit-learn](https://scikit-learn.org/) for machine learning
- Uses [python-dotenv](https://github.com/theskumar/python-dotenv) for configuration
- Inspired by email automation needs of busy professionals

## 📞 Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/your-username/gmail-email-classifier/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/your-username/gmail-email-classifier/discussions)
- 📧 **Email Support**: support@yoursite.com

---

⭐ **Star this repo** if you find it helpful!

**Happy Email Organizing!** 📧✨