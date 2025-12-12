#!/usr/bin/env python3
"""
Check email configuration and test email sending.
"""

import os
from dotenv import load_dotenv

load_dotenv()

print("="*70)
print("Syntheverse PoD Email Configuration Check")
print("="*70)
print()

# Check configuration
email_enabled = os.getenv('EMAIL_ENABLED', 'false').lower() == 'true'
smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
smtp_port = os.getenv('SMTP_PORT', '587')
smtp_username = os.getenv('SMTP_USERNAME', '')
smtp_password = os.getenv('SMTP_PASSWORD', '')
from_email = os.getenv('FROM_EMAIL', 'noreply@syntheverse.ai')

print("Configuration:")
print(f"  EMAIL_ENABLED: {email_enabled}")
print(f"  SMTP_SERVER: {smtp_server}")
print(f"  SMTP_PORT: {smtp_port}")
print(f"  SMTP_USERNAME: {'*' * len(smtp_username) if smtp_username else 'NOT SET'}")
print(f"  SMTP_PASSWORD: {'*' * len(smtp_password) if smtp_password else 'NOT SET'}")
print(f"  FROM_EMAIL: {from_email}")
print()

if not email_enabled:
    print("⚠️  EMAIL_ENABLED is false. Emails will not be sent.")
    print("   Set EMAIL_ENABLED=true in .env file to enable.")
    print()

if not smtp_username or not smtp_password:
    print("⚠️  SMTP credentials not configured.")
    print("   Please set SMTP_USERNAME and SMTP_PASSWORD in .env file")
    print("   For Gmail, use an App Password: https://myaccount.google.com/apppasswords")
    print()

if email_enabled and smtp_username and smtp_password:
    print("✅ Configuration looks good!")
    print()
    print("Testing email connection...")
    
    try:
        import smtplib
        server = smtplib.SMTP(smtp_server, int(smtp_port))
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.quit()
        print("✅ SMTP connection successful!")
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        print("   Check your SMTP_USERNAME and SMTP_PASSWORD")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("   Check your SMTP_SERVER and SMTP_PORT settings")

print()
print("="*70)
