# Email Configuration Guide

## Overview

To send PoD reports and certificates via email, you need to configure SMTP (Simple Mail Transfer Protocol) settings. This guide explains how to do this through the web UI.

## Step-by-Step Instructions

### 1. Open the Email Config Tab

1. Go to http://localhost:5000 in your browser
2. Look for the tabs at the top: **Status**, **Submissions**, **Email Config**
3. Click on the **"📧 Email Config"** tab

### 2. Fill in SMTP Settings

You'll see a form with the following fields:

#### **SMTP Server**
- **What it is**: The mail server address for your email provider
- **Common values**:
  - Gmail: `smtp.gmail.com`
  - Outlook/Hotmail: `smtp-mail.outlook.com`
  - Yahoo: `smtp.mail.yahoo.com`
  - Custom: Check with your email provider

#### **SMTP Port**
- **What it is**: The port number for SMTP connection
- **Common values**:
  - `587` (TLS/STARTTLS) - Most common, recommended
  - `465` (SSL) - Alternative
  - `25` (Unsecured) - Not recommended

#### **SMTP Username (Email)**
- **What it is**: Your email address used for authentication
- **Example**: `your.email@gmail.com`
- **Note**: This is the email account that will SEND the emails (not the recipient)

#### **SMTP Password**
- **What it is**: Password for SMTP authentication
- **Important for Gmail**: You MUST use an **App Password**, not your regular Gmail password
- **How to get Gmail App Password**:
  1. Go to https://myaccount.google.com/apppasswords
  2. Sign in to your Google account
  3. Select "Mail" and "Other (Custom name)"
  4. Enter "Syntheverse PoD" as the name
  5. Click "Generate"
  6. Copy the 16-character password (spaces don't matter)
  7. Paste it into the SMTP Password field

#### **From Email Address**
- **What it is**: The email address that appears as the sender
- **Example**: `noreply@syntheverse.ai` or your email address
- **Note**: Some providers require this to match your SMTP username

#### **Enable Email Sending**
- **What it is**: Checkbox to enable/disable email functionality
- **Recommendation**: Check this box after configuring all settings

### 3. Save Configuration

1. Click the **"💾 Save Configuration"** button
2. You should see a success message: "✅ Email configuration saved successfully"
3. Settings are automatically saved to `ui_web/.env` file

### 4. Test Your Configuration

#### Quick Test (Uses SMTP Username)
1. Click the **"✉️ Test Email"** button
2. This will automatically use your SMTP Username as the test recipient
3. Check your email inbox for the test message

#### Manual Test (Custom Email)
1. Enter any email address in the **"Test Email Address"** field
2. Click **"Send Test"**
3. Check that email inbox for the test message

### 5. Verify It Works

After testing:
- ✅ If you receive the test email: Configuration is correct!
- ❌ If you get an error: See troubleshooting below

## Example Configurations

### Gmail Configuration

```
SMTP Server: smtp.gmail.com
SMTP Port: 587
SMTP Username: your.email@gmail.com
SMTP Password: [16-character App Password from Google]
From Email: your.email@gmail.com
Enable Email Sending: ✓ (checked)
```

**Important**: Gmail requires App Passwords for third-party apps. Your regular password won't work.

### Outlook/Hotmail Configuration

```
SMTP Server: smtp-mail.outlook.com
SMTP Port: 587
SMTP Username: your.email@outlook.com
SMTP Password: [Your Outlook password]
From Email: your.email@outlook.com
Enable Email Sending: ✓ (checked)
```

### Custom Email Provider

1. Contact your email provider or check their documentation
2. Look for "SMTP settings" or "Outgoing mail server"
3. Use the provided server and port
4. Use your email credentials

## How It Works

### Two Different Email Addresses

1. **SMTP Username/Password**: 
   - Used to authenticate with the email server
   - This is the account that SENDS emails
   - Configured in "Email Config" tab

2. **Submission Email Address**:
   - Entered in the document submission form
   - This is the account that RECEIVES emails
   - Each user enters their own email when submitting

### Email Flow

```
User submits document → Enters their email in form
                    ↓
System uses SMTP settings → Authenticates with email server
                    ↓
Email sent to → User's email address (from form)
```

## Troubleshooting

### "SMTP authentication failed"

**Causes**:
- Wrong password (especially for Gmail - need App Password)
- Wrong username
- Two-factor authentication not set up (for Gmail)

**Solutions**:
- For Gmail: Generate App Password at https://myaccount.google.com/apppasswords
- Verify username matches your email exactly
- Check for typos in password

### "SMTP credentials not configured"

**Cause**: SMTP Username or Password fields are empty

**Solution**: Fill in both fields in the Email Config tab

### "Connection timeout" or "Connection refused"

**Causes**:
- Wrong SMTP server address
- Wrong port number
- Firewall blocking port 587

**Solutions**:
- Verify SMTP server address with your email provider
- Try port 465 instead of 587
- Check firewall settings

### "Email not sent" after submission

**Check**:
1. Is SMTP configured? (Check Email Config tab)
2. Did you enter an email in the submission form?
3. Check server logs for specific error messages

### Test Email Works, But Submission Emails Don't

**Possible causes**:
- Email address in submission form is invalid
- Email went to spam folder
- Server error during PDF generation

**Solutions**:
- Verify email address format in submission form
- Check spam/junk folder
- Check server terminal for error messages

## Security Notes

- **App Passwords**: For Gmail, always use App Passwords, never your main password
- **Password Storage**: Passwords are stored in `ui_web/.env` file - keep this file secure
- **Don't Share**: Never share your SMTP credentials
- **Environment Variables**: The `.env` file is automatically created and managed by the UI

## Quick Reference

| Provider | SMTP Server | Port | App Password Required |
|----------|-------------|------|----------------------|
| Gmail | smtp.gmail.com | 587 | ✅ Yes |
| Outlook | smtp-mail.outlook.com | 587 | ❌ No |
| Yahoo | smtp.mail.yahoo.com | 587 | ✅ Yes (usually) |
| Custom | Check provider docs | 587 or 465 | Varies |

## Need Help?

1. Check the server terminal for detailed error messages
2. Use the "Test Email" button to diagnose issues
3. Verify your email provider's SMTP requirements
4. Check that ports 587 or 465 are not blocked by firewall

## Summary

1. **Go to Email Config tab** in the web UI
2. **Enter SMTP settings** (server, port, username, password)
3. **Save configuration**
4. **Test email** to verify it works
5. **Submit documents** - emails will be sent to addresses entered in the form

That's it! Once configured, all future submissions will automatically send emails to the addresses users provide in the submission form.
