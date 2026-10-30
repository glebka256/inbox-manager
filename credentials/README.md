# Gmail AI Manager - Credentials Setup Guide

## 📧 Setting Up Gmail Credentials

### Step 1: Generate Gmail App Password

**IMPORTANT**: You CANNOT use your regular Gmail password. You must create an App Password.

1. **Enable 2-Factor Authentication** on your Gmail account first:
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Enable 2-Step Verification if not already enabled

2. **Generate App Password**:
   - Go to [Google App Passwords](https://myaccount.google.com/apppasswords)
   - Select "Mail" as the app
   - Select "Other" as the device and name it "Gmail AI Manager"
   - Google will generate a 16-character password like: `abcd efgh ijkl mnop`

### Step 2: Configure Credentials

1. **Navigate to credentials folder**:
   ```
   Email_Scraper/credentials/
   ```

2. **Copy the template**:
   - Copy `gmail_credentials_template.env`
   - Rename it to `gmail_credentials.env`

3. **Edit the credentials file**:
   ```env
   GMAIL_USER=your.email@gmail.com
   GMAIL_PASS=your-16-character-app-password
   ```

### Step 3: Security Notes

- ✅ **DO** use the 16-character App Password
- ✅ **DO** keep the `gmail_credentials.env` file secure
- ✅ **DO** enable 2-Factor Authentication first
- ❌ **DON'T** use your regular Gmail password
- ❌ **DON'T** share or commit the credentials file to version control
- ❌ **DON'T** include spaces in the App Password

### Step 4: File Structure

```
Email_Scraper/
├── credentials/
│   ├── gmail_credentials_template.env  (Template - safe to share)
│   └── gmail_credentials.env          (Your actual credentials - keep secure)
├── visual_advanced_gui.py             (Loads credentials automatically)
├── gmail_ai_gui.py                    (Loads credentials automatically)
└── LAUNCH_DASHBOARD.bat               (Main launcher)
```

### Step 5: Testing

1. **Launch the application**:
   ```bash
   LAUNCH_DASHBOARD.bat
   ```

2. **Check the output box** - you should see:
   ```
   📁 Loading credentials from: credentials/gmail_credentials.env
   ✅ Loaded credentials for your.email@gmail.com
   🔑 App Password loaded: **** olth
   ```

3. **Test the connection**:
   - Click "🔍 Test Connection"
   - Should show: "✅ Gmail connection successful!"

### Troubleshooting

**Problem**: "❌ Gmail connection failed: authentication failed"
- **Solution**: Double-check your App Password is correct (16 characters, no spaces)

**Problem**: "⚠️ No credentials found"
- **Solution**: Make sure `gmail_credentials.env` exists in the credentials folder

**Problem**: "❌ Please enter Gmail credentials first!"
- **Solution**: The credentials file wasn't loaded properly - check the file path and format

### Advanced: Multiple Accounts

To use multiple Gmail accounts, create separate credential files:
```
credentials/
├── gmail_credentials_work.env
├── gmail_credentials_personal.env
└── gmail_credentials.env  (default)
```

The application will always load `gmail_credentials.env` by default.

---

## 🚀 Quick Start

1. Get your Gmail App Password from Google
2. Copy `gmail_credentials_template.env` to `gmail_credentials.env`
3. Put your email and App Password in the file
4. Run `LAUNCH_DASHBOARD.bat`
5. Click "🔍 Test Connection" to verify setup

**That's it! Your Gmail AI Manager is ready to use!** 🎉