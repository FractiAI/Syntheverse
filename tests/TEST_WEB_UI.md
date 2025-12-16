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
3. Select category (Scientific/Tech/Alignment)
4. Click "Submit for PoD Evaluation"

### Step 2: Wait for Processing

The system will:
- Submit to L1 blockchain
- Evaluate with L2 PoD server
- Calculate allocation
- Generate PDF report
- Generate PDF certificate (if approved)

### Step 3: View Results

- Check the "Submissions" tab to see your submission
- View evaluation scores and allocations
- Check epoch status for updated balances

## Viewing Results

All evaluation results are displayed directly in the web UI:
- Navigate to the **"📄 Results"** tab after submitting
- View detailed evaluation reports, scores, and certificates
- Download PDF reports directly from the UI

## What Gets Generated

### Files Created

1. **PDF Reports**: `test_outputs/pdf_reports/pod_report_{hash}.pdf`
2. **PDF Certificates**: `test_outputs/pdf_reports/pod_certificate_{hash}.pdf`
3. **JSON Reports**: `test_outputs/pod_reports/{hash}_report.json`
4. **Blockchain State**: `test_outputs/blockchain/`

### Viewing Reports

- PDF Reports: Available in the Results tab
- PDF Certificates: Available for approved submissions

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


### No PDFs Generated

- Check `test_outputs/pdf_reports/` directory
- Verify submission was approved
- Check console for error messages

## Next Steps

1. **Submit a test document** through the web UI
2. **View results** in the Results tab
3. **View submissions** in the Submissions tab
4. **Register certificate** at `/register` page

## Features Summary

✅ **Web-based submission** - No command line needed
✅ **PDF reports** - Professional evaluation reports
✅ **PDF certificates** - Official certificates for awarded submissions
✅ **In-UI results** - All results displayed directly in the web interface
✅ **Blockchain registration** - Register certificates on blockchain
✅ **Real-time status** - View epoch balances and submissions
✅ **Auto-refresh** - Status updates every 10 seconds

Enjoy testing the Syntheverse PoD Submission System! 🚀

