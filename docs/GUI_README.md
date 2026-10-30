# Gmail AI Manager - GUI User Guide

## 🚀 Quick Start

### Method 1: Double-click to start
1. Double-click `start_gui.bat` 
2. The GUI will open automatically

### Method 2: Command line
```powershell
cd "c:\Users\Sean Fitz\OneDrive\Desktop\Email_Scraper"
.\gmail_ai_env\Scripts\Activate.ps1
python gmail_ai_gui.py
```

## 📋 GUI Features

### 🔧 Settings Panel
- **Gmail Email**: Your Gmail address
- **App Password**: Your Gmail App Password (not regular password)
- **Classification Mode**: 
  - **Rule-Based**: Fast keyword matching
  - **Machine Learning**: AI-powered classification (77.8% accuracy)
  - **Demo Only**: Preview without making changes
- **Emails to Process**: 10, 25, 50, 100, or All Unread
- **Dry Run**: Preview mode (safe - no changes made)

### 🎛️ Action Buttons
- **🔍 Test Connection**: Verify Gmail credentials work
- **📧 Preview Emails**: See how emails would be classified
- **🚀 Run Classification**: Actually apply labels to emails
- **⚙️ Settings**: Advanced configuration

### 📊 Output Window
- Real-time progress updates
- Detailed classification results
- Error messages and debugging info
- Timestamped activity log

## 🛡️ Safety Features

### Dry Run Mode (Recommended for first use)
- ✅ **Enabled by default**
- Shows what would happen without making changes
- Safe to test with your real emails
- Disable only when you're confident

### Test Connection
- Verifies credentials before processing
- Shows inbox statistics
- Catches authentication issues early

## 📧 Daily Workflow

### First Time Setup
1. **Test Connection** to verify credentials
2. **Preview Emails** to see classifications
3. Review the output to ensure accuracy
4. When satisfied, uncheck "Dry Run"
5. **Run Classification** to apply labels

### Daily Use
1. Open GUI with `start_gui.bat`
2. Click **Run Classification**
3. Check your Gmail - emails are organized!

## 🎯 Classification Types

The AI automatically detects and labels:
- **📱 LinkedIn**: Messages and notifications
- **🚚 Freight/Leads**: Logistics and business opportunities  
- **📄 Rate Confirmations**: Shipping documents
- **🔧 API/Developer**: Technical emails
- **❓ Unknown**: Emails that don't match patterns

## ⚙️ Advanced Settings

### Credentials Management
- Use the **Settings** button to save credentials to `.env` file
- More secure than entering every time
- Credentials are stored locally on your computer

### Classification Rules
- View current keyword rules in Settings
- Modify `rule_based_classifier.py` to customize
- Add new categories and keywords as needed

## 🚨 Troubleshooting

### Connection Issues
- Verify Gmail App Password (not regular password)
- Check internet connection
- Ensure Gmail IMAP is enabled

### No Emails Processed
- Check "Emails to Process" setting
- Verify you have unread emails
- Try "Preview Emails" first

### GUI Won't Start
- Run `start_gui.bat` as Administrator
- Check if virtual environment is properly set up
- Install missing packages: `pip install -r requirements.txt`

## 💡 Tips

- **Start with Dry Run** enabled for safety
- **Test Connection** before processing emails
- **Preview Emails** to verify accuracy
- Use **smaller email counts** (10-25) for faster processing
- Check Gmail labels after processing to see results
- Review classification accuracy and adjust rules as needed

## 🔄 Updates and Maintenance

- The AI learns from your email patterns
- Periodically review and update classification rules
- Use Machine Learning mode for more advanced classification
- Back up your `.env` file for credential security

---

**Need help?** Check the main `README.md` for detailed technical information and troubleshooting guides.