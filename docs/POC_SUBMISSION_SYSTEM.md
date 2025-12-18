# Syntheverse PoC Submission System

## Overview

System for submitting PDF research papers, evaluating them for Proof-of-Contribution (PoC), and allocating SYNTH tokens based on the Syntheverse PoC protocol.

## System Architecture

```
┌─────────────────┐
│  Web UI / API   │
│  (Submission)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Layer 2 (L2)   │
│   PoC Server    │
│  (Evaluation)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Archive       │
│  (Storage)      │
└─────────────────┘
```

## Components

### 1. PoC API (Layer 2)

**What it does:**
- Receives PDF submissions via REST API
- Evaluates papers using Groq API
- Scores submissions based on PoC protocol:
  - **Coherence** (0-10000): Structural consistency, fractal grammar
  - **Density** (0-10000): Informational richness per unit
  - **Novelty** (0-10000): Non-redundancy relative to archive
- Manages token allocation and epoch system
- Prevents duplicate submissions via archive-first design
- Generates evaluation reports

**Endpoints:**
- `POST /api/submit` - Submit PDF for evaluation
- `GET /api/status` - Get system and epoch status
- `GET /api/submissions` - List all submissions
- `GET /health` - API health check

**Files:**
- `src/api/poc-api/app.py` - Main API server
- `src/core/layer2/tokenomics.py` - Token allocation logic
- `src/core/layer2/poc_archive.py` - Archive management

### 2. Frontend (Next.js)

**What it does:**
- Provides web interface for submissions
- Displays epoch status and token balances
- Shows submission history and reports
- Visualizes sandbox map

**Features:**
- Dashboard view
- PDF submission interface
- Registry explorer
- Sandbox map network visualization

**Files:**
- `src/frontend/poc-frontend/` - Next.js application

### 3. Archive System

**What it does:**
- Stores all PoC submissions permanently
- Enables redundancy detection
- Maintains submission history
- Tracks token allocations

**Files:**
- `test_outputs/poc_archive.json` - Complete archive
- `test_outputs/poc_reports/` - Individual reports
- `test_outputs/l2_tokenomics_state.json` - Token state
- `test_outputs/l2_submissions_registry.json` - Registry

## Workflow

### Submission Process

1. **User submits PDF** via web UI or API
   - Provides PDF, contributor ID, category

2. **System validates submission**
   - Checks for duplicates in archive
   - Validates PDF format

3. **Layer 2 evaluates PDF**
   - Extracts text from PDF
   - Uses Groq API for evaluation
   - Applies PoC protocol criteria
   - Returns scores (coherence, density, novelty)

4. **System calculates allocation**
   - Calculates PoC score: `(coherence × density × novelty) / 10000² × 10000`
   - Determines qualified epoch based on density threshold
   - Calculates reward based on tier and epoch

5. **Archive stores submission**
   - Adds to permanent archive
   - Creates evaluation report
   - Updates registry

6. **System generates report**
   - Comprehensive PoC report saved to `test_outputs/poc_reports/`
   - Includes submission, evaluation, allocation, epoch status

## Epoch System

| Epoch | Supply | Density Threshold | Available Tiers |
|-------|--------|------------------|-----------------|
| **Founder** | 45T (50%) | ≥ 8,000 | Gold only |
| **Pioneer** | 9T (10%) | ≥ 6,000 | Gold, Copper |
| **Community** | 18T (20%) | ≥ 4,000 | Gold, Silver, Copper |
| **Ecosystem** | 18T (20%) | < 4,000 | Gold, Silver, Copper |

## Tier System

| Tier | Multiplier | Available Epochs | Categories |
|------|-----------|------------------|------------|
| **Gold** | 1000x | All epochs | scientific, science, research |
| **Silver** | 100x | Community, Ecosystem | tech, technology, technical, engineering |
| **Copper** | 1x | Pioneer, Community, Ecosystem | alignment, ai-alignment, safety |

## Output Files

All outputs saved to `test_outputs/`:

### Archive Files
- `poc_archive.json` - Complete submission archive
- `l2_tokenomics_state.json` - Token allocation state
- `l2_submissions_registry.json` - Submission registry

### Reports
- `poc_reports/{hash}_report.json` - Individual PoC reports
- Contains: submission, evaluation, allocation, epoch status

## PoD Report Structure

```json
{
  "submission": {
    "hash": "abc123...",
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
    "status": "approved",
    "reasoning": "Evaluation explanation..."
  },
  "pod_score": 7429.0,
  "allocation": {
    "epoch": "founder",
    "tier": "gold",
    "reward": 1234567.89,
    "pod_score": 7429.0
  },
  "epoch_status": {
    "current_epoch": "founder",
    "epochs": {...}
  },
  "token_stats": {
    "total_supply": 90000000000000,
    "epoch_balances": {...}
  }
}
```

## Usage

### Quick Start

```bash
# Start the system
python scripts/startup/start_servers.py --mode poc

# Open browser to http://localhost:3001

# Submit papers through web interface
```

### API Usage

```bash
# Submit a PDF via API
curl -X POST http://localhost:5001/api/submit \
  -F "pdf=@/path/to/paper.pdf" \
  -F "contributor=researcher-001" \
  -F "category=scientific"

# Check status
curl http://localhost:5001/api/status

# List submissions
curl http://localhost:5001/api/submissions
```

## Integration Points

- **Frontend ↔ API**: Web UI calls PoC API endpoints
- **API ↔ Layer 2**: API uses Layer 2 evaluation engine
- **Layer 2 ↔ Groq**: Layer 2 calls Groq API for LLM evaluation
- **Archive**: All components write to persistent archive

## PoD Protocol Evaluation

The system evaluates based on the Syntheverse PoD protocol:

1. **Coherence**: Structural consistency, fractal grammar, recursive patterns
2. **Density**: Informational richness, structural depth, contribution magnitude
3. **Novelty**: Uniqueness compared to archive, novel insights

Evaluation uses Groq API with specialized prompts based on the PoC protocol.

## Notes

- All data persists to `test_outputs/` directory
- Reports are generated for each submission
- Archive-first design prevents duplicates
- Token allocation depends on PoC score, epoch, and tier
- System validates tier availability before allocation

