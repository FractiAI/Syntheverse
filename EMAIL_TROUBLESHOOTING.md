# Email Troubleshooting Guide

## Why You Didn't Receive Emails

### Common Issues

1. **Email Not Enabled**
   - Check if `EMAIL_ENABLED=true` in `ui_web/.env`
   - Default is `false` (disabled)

2. **SMTP Credentials Not Set**
   - Need `SMTP_USERNAME` and `SMTP_PASSWORD` in `.env`
   - For Gmail, use an **App Password** (not your regular password)

3. **Email Configuration Missing**
   - Create `ui_web/.env` file
   - Copy from `ui_web/.env.example`
   - Fill in your email settings

## Quick Fix

### Step 1: Check Email Configuration

```bash
cd ui_web
python check_email_config.py
```

This will show:
- Current email settings
- Whether email is enabled
- SMTP connection test results

### Step 2: Set Up .env File

```bash
cd ui_web
cp .env.example .env
# Edit .env with your settings
```

### Step 3: For Gmail Users

1. Go to https://myaccount.google.com/apppasswords
2. Generate App Password for "Mail"
3. Use the 16-character password in `.env`

### Step 4: Test Email

After configuring, restart the web server and try submitting again.

## Check Server Logs

When you submit, check the terminal where the web server is running. You'll see:

- ✅ `Email sent successfully to your@email.com` - Email worked!
- ⚠️ `Email disabled` - Need to enable in .env
- ❌ `SMTP authentication failed` - Check credentials
- ❌ `SMTP credentials not configured` - Need to set username/password

## Email Status in Web UI

The web UI will show:
- `📧 X email(s) sent!` - Success
- `⚠️ Email failed` - Check server logs
- `ℹ️ Email not sent` - Check configuration

## Multiple PDF Submissions

When submitting multiple PDFs:
- Each submission gets its own email
- Email count shows how many were sent
- Errors are logged per file

## Still Not Working?

1. **Check .env file exists**: `ui_web/.env`
2. **Verify values**: All required fields filled
3. **Test SMTP connection**: Run `check_email_config.py`
4. **Check firewall**: SMTP port 587 might be blocked
5. **Try different email provider**: Gmail, Outlook, etc.

## Alternative: Manual Download

If email isn't working, you can still:
- View reports in `test_outputs/pod_reports/`
- Download PDFs from `test_outputs/pdf_reports/`
- Check submissions in the web UI

Email is optional - the system works without it!
