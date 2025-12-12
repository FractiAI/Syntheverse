# Quick Start: PoD Submission UI

## Overview

The Syntheverse PoD Submission UI is a console-based interface for:
- Submitting PDF research papers for PoD evaluation
- Viewing epoch status and token balances
- Tracking all PoD submissions and allocations
- Generating comprehensive PoD reports

## Setup

### 1. Install Dependencies

```bash
# Layer 2 requirements
pip install requests PyPDF2

# Ensure RAG API is running (see rag-api/README.md)
```

### 2. Start RAG API (if not already running)

```bash
cd rag-api/api
python rag_api.py
# Or: ./start_rag_api.sh
```

The RAG API should be running at `http://localhost:8000`

### 3. Run PoD Submission UI

```bash
python ui_pod_submission.py
```

## Usage

### Interactive Mode

The UI provides an interactive console:

```
Options:
  1. Submit PDF paper
  2. View epoch status
  3. List all PoD submissions
  4. Exit
```

### Submit a PDF Paper

1. Select option `1`
2. Enter PDF file path
3. Enter contributor ID (e.g., `researcher-001`)
4. Enter category: `scientific`, `tech`, or `alignment`

The system will:
1. Submit to L1 blockchain
2. Evaluate with L2 PoD server (using RAG API)
3. Record evaluation in L1
4. Allocate SYNTH tokens if approved
5. Mine block with transaction
6. Generate PoD report

### View Epoch Status

Select option `2` to see:
- Current active epoch
- All epoch statuses (Active/Unlocked/Locked)
- Remaining token balances per epoch
- Distribution percentages
- Density thresholds

### List PoD Submissions

Select option `3` to see:
- All submitted papers
- Submission hashes
- Evaluation scores (coherence, density, novelty)
- PoD scores
- Token allocations (epoch, tier, amount)

## Output Files

All outputs are saved to `test_outputs/`:

- **`test_outputs/blockchain/`**: L1 blockchain state
- **`test_outputs/pod_reports/`**: Individual PoD evaluation reports
- **`test_outputs/submissions_history.json`**: All submission records

## PoD Report Structure

Each PoD report (`{hash}_report.json`) contains:

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
  "pod_score": 7429.0,
  "allocation": {
    "epoch": "founder",
    "tier": "gold",
    "reward": 1234567.89
  },
  "epoch_status": {...},
  "token_stats": {...}
}
```

## Example Workflow

```bash
# 1. Start RAG API
cd rag-api/api && python rag_api.py

# 2. In another terminal, start PoD UI
python ui_pod_submission.py

# 3. Submit a paper
# Select option 1
# Enter: /path/to/paper.pdf
# Enter: researcher-001
# Enter: scientific

# 4. View results
# Select option 2 (epoch status)
# Select option 3 (list submissions)
```

## Integration

The UI integrates:
- **L1 (Blockchain)**: Stores submissions, evaluates, allocates tokens
- **L2 (PoD Server)**: Evaluates papers using RAG API
- **RAG API**: Provides knowledge base comparison and evaluation

## Notes

- PDFs are processed and evaluated automatically
- Token allocation depends on PoD score, epoch qualification, and tier
- All data persists to `test_outputs/` directory
- Reports are generated for each submission
