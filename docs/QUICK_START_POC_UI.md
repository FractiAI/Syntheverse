# Quick Start: PoC Submission UI

## Overview

The Syntheverse PoC Submission UI provides web-based and API interfaces for:
- Submitting PDF research papers for PoC evaluation
- Viewing epoch status and token balances
- Tracking all PoC submissions and allocations
- Generating comprehensive PoC reports

## Setup

### 1. Install Dependencies

```bash
# Python requirements
pip install flask flask-cors werkzeug requests PyPDF2

# Frontend dependencies (Next.js)
cd src/frontend/poc-frontend
npm install
cd ../../..
```

### 2. Start the System

Use the automated startup script:

```bash
# Start all services (PoC API + Frontend)
python scripts/startup/start_servers.py --mode poc

# Or use the menu system
python scripts/main.py
```

The system will start:
- PoC API at `http://localhost:5001`
- Next.js Frontend at `http://localhost:3001`

## Usage

### Web Interface

Open your browser to `http://localhost:3001` for the Next.js UI with:
- Dashboard view
- Submission interface
- Registry explorer
- Sandbox map visualization

### API Endpoints

The PoC API provides REST endpoints at `http://localhost:5001`:

- `POST /api/submit` - Submit a PDF for evaluation
- `GET /api/status` - Get epoch and system status
- `GET /api/submissions` - List all submissions
- `GET /health` - API health check

### Submit a PDF Paper

Using the web interface:
1. Navigate to the Submission page
2. Upload PDF file
3. Enter contributor ID (e.g., `researcher-001`)
4. Select category: `scientific`, `tech`, or `alignment`
5. Submit for evaluation

The system will:
1. Process the PDF
2. Evaluate with Layer 2 (using Groq API)
3. Calculate PoC score
4. Allocate SYNTH tokens if approved
5. Generate PoC report

### View Epoch Status

The Dashboard shows:
- Current active epoch
- Epoch statuses (Active/Unlocked/Locked)
- Remaining token balances per epoch
- Distribution percentages
- Density thresholds

### View Submissions

The Registry page displays:
- All submitted papers
- Submission hashes
- Evaluation scores (coherence, density, novelty)
- PoC scores
- Token allocations (epoch, tier, amount)

## Output Files

All outputs are saved to `test_outputs/`:

- **`test_outputs/poc_archive.json`**: Complete PoC submission archive
- **`test_outputs/poc_reports/`**: Individual PoC evaluation reports
- **`test_outputs/l2_tokenomics_state.json`**: Layer 2 tokenomics state
- **`test_outputs/l2_submissions_registry.json`**: Submission registry

## PoC Report Structure

Each PoC report contains:

```json
{
  "submission": {
    "hash": "...",
    "title": "Paper Title",
    "contributor": "researcher-001",
    "category": "scientific",
    "timestamp": "2025-01-XX..."
  },
  "evaluation": {
    "coherence": 8500,
    "density": 9000,
    "novelty": 8000,
    "tier": "gold",
    "status": "approved"
  },
  "poc_score": 7429.0,
  "allocation": {
    "epoch": "founder",
    "tier": "gold",
    "reward": 1234567.89
  }
}
```

## Example Workflow

```bash
# 1. Start the system
python scripts/startup/start_servers.py --mode poc

# 2. Open browser to http://localhost:3001

# 3. Submit a paper through the web interface

# 4. View results in Dashboard and Registry
```

## Integration

The UI integrates:
- **Layer 2 (PoC Evaluation)**: Evaluates papers using Groq API
- **PoC API**: REST API for submissions and status
- **Frontend**: Next.js UI for user interaction
- **Archive System**: Persistent storage and redundancy detection

## Notes

- PDFs are processed and evaluated automatically
- Token allocation depends on PoC score, epoch qualification, and tier
- All data persists to `test_outputs/` directory
- Reports are generated for each submission
- Archive-first design prevents duplicate submissions

