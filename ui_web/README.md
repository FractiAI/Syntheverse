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

### 2. Start the Web Server

No additional configuration needed. All results are displayed in the web UI.

### 3. Start the Web Server

```bash
cd ui_web
python app.py
```

### 3. Open in Browser

Navigate to: **http://localhost:5000**

## Features

- 📄 **Document Upload**: Upload PDF files for PoD evaluation
- 📊 **Epoch Status**: View current epoch, token balances, and thresholds
- 📋 **Interactive Submissions**: Expandable submission list with detailed PoD metrics
  - Click any submission to expand and view:
    - Full evaluation results (Coherence, Density, Novelty, Redundancy, PoD Score, Tier)
    - Token allocation details (Epoch, Tier, SYNTH tokens)
    - Tier justification and evaluation reasoning
    - PDF viewing and certificate registration buttons
- 📄 **PDF Viewing**: Direct access to view/download submitted PDF documents
- 🔗 **Certificate Registration**: Register PoD certificates on blockchain
  - Wallet integration with address display
  - SYNTH token balance tracking
  - Multi-chain gas balance display (ETH, MATIC, BNB, AVAX)
  - Credit card payment information management
- 🎨 **Modern UI**: Clean, responsive web interface
- 🔄 **Auto-refresh**: Status and submissions update automatically

## Usage

1. **Submit a Document**:
   - Click "Select PDF file" and choose your document
   - Enter your Contributor ID
   - Select category (Scientific/Tech/Alignment)
   - Click "Submit for PoD Evaluation"

2. **View Status**:
   - See current epoch and token balances
   - View all epoch details with thresholds
   - Monitor coherence density

3. **View Submissions**:
   - See all submitted documents in an expandable list
   - Click any submission to expand and view:
     - Complete evaluation metrics (Coherence Φ, Density ρ, Novelty, Redundancy R, PoD Score)
     - Token allocation details (Epoch, Tier, SYNTH tokens)
     - Tier justification and evaluation reasoning
   - Click "View PDF" to open the submitted document
   - Click "Register Certificate" to register approved submissions on blockchain

4. **Register Certificate**:
   - Navigate to Register Certificate page (from submissions or header link)
   - Click "Connect Wallet" to add payment information
   - View wallet address and SYNTH token balance
   - Monitor gas balances across multiple chains (ETH, MATIC, BNB, AVAX)
   - Enter credit card information for payment processing
   - Register certificate on blockchain with submission hash and contributor ID

## API Endpoints

- `GET /` - Main web interface
- `GET /register` - Certificate registration page
- `GET /api/status` - Get epoch status and tokenomics
- `GET /api/submissions` - Get all PoD submissions
- `POST /api/submit` - Submit a document (multipart/form-data)
- `GET /api/submission/<hash>` - Get specific submission
- `GET /api/submission/<hash>/progress` - Get submission progress
- `GET /api/reports/<hash>` - Get PoD report
- `GET /api/pdf/<hash>` - Get PDF file for a submission

## File Structure

```
ui_web/
├── app.py                      # Flask application
├── templates/
│   ├── index.html             # Main web UI template
│   └── register_certificate.html  # Certificate registration page
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Viewing Results

All PoD evaluation results, reports, and certificates are displayed directly in the web UI:
- Navigate to the **"📄 Results"** tab after submitting
- View detailed evaluation reports, scores, and certificates
- Download PDF reports directly from the UI

## Notes

- Uploaded files are saved to `uploads/` directory
- All outputs go to `test_outputs/` (same as CLI)
- The web UI uses the same backend as the CLI tool
- Make sure RAG API is running for best evaluation results
- All results are displayed in the web UI - no email configuration needed
