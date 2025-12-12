# Syntheverse PoD Submission Web UI

Browser-based interface for submitting documents for Proof-of-Discovery evaluation.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- Flask (web framework)
- Werkzeug (utilities)
- python-dotenv (for .env file support)

### 2. Configure Email (Optional)

To enable email reports:

```bash
cd ui_web
cp .env.example .env
# Edit .env with your email settings
```

See `EMAIL_SETUP.md` for detailed email configuration.

### 3. Start the Web Server

```bash
cd ui_web
python app.py
```

### 4. Open in Browser

Navigate to: **http://localhost:5000**

## Features

- 📄 **Document Upload**: Upload PDF files for PoD evaluation
- 📊 **Epoch Status**: View current epoch, token balances, and thresholds
- 📋 **Submission List**: See all PoD submissions with scores and allocations
- 🎨 **Modern UI**: Clean, responsive web interface
- 🔄 **Auto-refresh**: Status and submissions update automatically

## Usage

1. **Submit a Document**:
   - Click "Select PDF file" and choose your document
   - Enter your Contributor ID
   - Enter your Email Address (PoD report will be emailed to you)
   - Select category (Scientific/Tech/Alignment)
   - Click "Submit for PoD Evaluation"

2. **View Status**:
   - See current epoch and token balances
   - View all epoch details with thresholds
   - Monitor coherence density

3. **View Submissions**:
   - See all submitted documents
   - View evaluation scores (coherence, density, novelty)
   - See token allocations if approved

## API Endpoints

- `GET /` - Main web interface
- `GET /api/status` - Get epoch status and tokenomics
- `GET /api/submissions` - Get all PoD submissions
- `POST /api/submit` - Submit a document (multipart/form-data)
- `GET /api/submission/<hash>` - Get specific submission
- `GET /api/reports/<hash>` - Get PoD report

## File Structure

```
ui_web/
├── app.py              # Flask application
├── templates/
│   └── index.html      # Web UI template
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Email Reports

When you submit a document, if email is configured:
- PoD report is automatically sent to your email
- Report includes evaluation scores and token allocation
- JSON report file is attached to the email

See `EMAIL_SETUP.md` for email configuration.

## Notes

- Uploaded files are saved to `uploads/` directory
- All outputs go to `test_outputs/` (same as CLI)
- The web UI uses the same backend as the CLI tool
- Make sure RAG API is running for best evaluation results
- Email is optional - system works without it
