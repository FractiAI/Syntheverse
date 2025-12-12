# Email Setup for PoD Reports

## Overview

The Syntheverse PoD Submission system can send email reports to submitters. This guide explains how to configure email functionality.

## Quick Setup

### 1. Create .env File

Copy the example file:
```bash
cd ui_web
cp .env.example .env
```

### 2. Edit .env File

Open `.env` and configure your email settings:

```env
EMAIL_ENABLED=true
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@syntheverse.ai
```

### 3. Gmail Setup (Recommended)

For Gmail, you need to use an **App Password** instead of your regular password:

1. Go to https://myaccount.google.com/apppasswords
2. Sign in with your Google account
3. Select "Mail" and "Other (Custom name)"
4. Enter "Syntheverse PoD" as the name
5. Click "Generate"
6. Copy the 16-character password
7. Use this password in your `.env` file

### 4. Other Email Providers

#### Outlook/Hotmail
```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
```

#### Yahoo
```env
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
```

#### Custom SMTP
```env
SMTP_SERVER=your-smtp-server.com
SMTP_PORT=587
```

## Email Content

The email includes:
- Submission details (title, hash, category)
- Evaluation results (coherence, density, novelty, PoD score)
- Token allocation (if approved)
- Status (approved/rejected)
- **Attached PDF Report**: Complete PoD evaluation report
- **Attached PDF Certificate**: Official certificate (if tokens were awarded)
- **Blockchain Registration Instructions**: How to register certificate on blockchain

## Testing

### Test Email Without Server

You can test email functionality by setting environment variables:

```bash
export EMAIL_ENABLED=true
export SMTP_SERVER=smtp.gmail.com
export SMTP_PORT=587
export SMTP_USERNAME=your-email@gmail.com
export SMTP_PASSWORD=your-app-password
export FROM_EMAIL=your-email@gmail.com

cd ui_web
python app.py
```

### Disable Email

To disable email sending (for testing):
```env
EMAIL_ENABLED=false
```

Or remove the email field requirement from the form.

## Troubleshooting

### "Email not sent" Error

1. Check that `EMAIL_ENABLED=true` in `.env`
2. Verify SMTP credentials are correct
3. Check firewall/network settings
4. For Gmail, ensure 2-factor authentication is enabled and you're using an App Password

### "Authentication failed"

- Gmail: Make sure you're using an App Password, not your regular password
- Other providers: Check username/password are correct
- Some providers require enabling "Less secure app access" (not recommended)

### Email Goes to Spam

- Use a proper FROM_EMAIL address
- Consider using a dedicated email service (SendGrid, Mailgun, etc.)
- Add SPF/DKIM records to your domain

## Security Notes

- Never commit `.env` file to git (it's in .gitignore)
- Use App Passwords for Gmail, not your main password
- Consider using environment variables in production
- Use a dedicated email account for sending reports

## Production Recommendations

For production, consider:
- Using a dedicated email service (SendGrid, Mailgun, AWS SES)
- Setting up proper SPF/DKIM records
- Using environment variables instead of .env file
- Implementing email queue for reliability
