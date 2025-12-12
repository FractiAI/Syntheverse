# Testing the Syntheverse PoD Web UI

## Quick Start

### 1. Web Server is Running

The web UI should now be running at:
```
http://localhost:5000
```

### 2. Open in Browser

Open your web browser and navigate to:
```
http://localhost:5000
```

## What You'll See

### Main Page Features

1. **Submit Document Section**
   - File upload (PDF)
   - Contributor ID field
   - **Email Address field** (NEW - required)
   - Category selection (Scientific/Tech/Alignment)
   - Submit button

2. **Status Tab**
   - Current epoch
   - Token balances for all epochs
   - Coherence density
   - Available tiers per epoch

3. **Submissions Tab**
   - All submitted documents
   - Evaluation scores
   - Token allocations
   - Status (approved/rejected)

4. **Register Certificate Link**
   - Link to certificate registration page

## Testing Steps

### Step 1: Submit a Document

1. Click "Select PDF file" and choose a PDF document
2. Enter your Contributor ID (e.g., `researcher-001`)
3. **Enter your Email Address** (e.g., `your.email@example.com`)
4. Select category (Scientific/Tech/Alignment)
5. Click "Submit for PoD Evaluation"

### Step 2: Wait for Processing

The system will:
- Submit to L1 blockchain
- Evaluate with L2 PoD server
- Calculate allocation
- Generate PDF report
- Generate PDF certificate (if approved)
- Send email with PDFs

### Step 3: Check Email

If email is configured, you'll receive:
- **PDF Report**: Complete evaluation report
- **PDF Certificate**: Official certificate (if tokens awarded)
- **Instructions**: How to register certificate on blockchain

### Step 4: View Results

- Check the "Submissions" tab to see your submission
- View evaluation scores and allocations
- Check epoch status for updated balances

## Email Setup (Optional)

To receive email reports:

1. Create `.env` file in `ui_web/`:
```bash
cd ui_web
cp .env.example .env
```

2. Edit `.env` with your email settings:
```env
EMAIL_ENABLED=true
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com
```

3. For Gmail, use an App Password:
   - Go to https://myaccount.google.com/apppasswords
   - Generate app password
   - Use it in `.env`

## What Gets Generated

### Files Created

1. **PDF Reports**: `test_outputs/pdf_reports/pod_report_{hash}.pdf`
2. **PDF Certificates**: `test_outputs/pdf_reports/pod_certificate_{hash}.pdf`
3. **JSON Reports**: `test_outputs/pod_reports/{hash}_report.json`
4. **Blockchain State**: `test_outputs/blockchain/`

### Email Attachments

- PDF Report (always sent)
- PDF Certificate (only if tokens awarded)

## Troubleshooting

### Web Server Not Running

Check if it's running:
```bash
curl http://localhost:5000
```

If not, start it:
```bash
cd ui_web
python app.py
```

### PDF Generation Errors

Make sure reportlab is installed:
```bash
pip install reportlab
```

### Email Not Sending

1. Check `.env` file exists and is configured
2. Verify `EMAIL_ENABLED=true`
3. Check SMTP credentials are correct
4. For Gmail, use App Password not regular password

### No PDFs Generated

- Check `test_outputs/pdf_reports/` directory
- Verify submission was approved
- Check console for error messages

## Next Steps

1. **Submit a test document** through the web UI
2. **Check your email** for PDF report and certificate
3. **View submissions** in the web UI
4. **Register certificate** at `/register` page

## Features Summary

✅ **Web-based submission** - No command line needed
✅ **PDF reports** - Professional evaluation reports
✅ **PDF certificates** - Official certificates for awarded submissions
✅ **Email delivery** - Automatic email with PDFs
✅ **Blockchain registration** - Instructions for certificate registration
✅ **Real-time status** - View epoch balances and submissions
✅ **Auto-refresh** - Status updates every 10 seconds

Enjoy testing the Syntheverse PoD Submission System! 🚀
