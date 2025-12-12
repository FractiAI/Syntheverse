# Syntheverse PoD Submission System

## Overview

Complete test-mode system for submitting PDF research papers, evaluating them for Proof-of-Discovery (PoD), and allocating SYNTH tokens based on the Syntheverse PoD protocol.

## System Architecture

```
┌─────────────────┐
│  PoD UI Console │
│  (Submission)   │
└────────┬────────┘
         │
         ├─────────────────┐
         │                 │
         ▼                 ▼
┌─────────────────┐  ┌─────────────────┐
│   Layer 1 (L1)  │  │  Layer 2 (L2)  │
│   Blockchain    │  │   PoD Server    │
└────────┬────────┘  └────────┬────────┘
         │                    │
         │                    ▼
         │            ┌─────────────────┐
         │            │   RAG API       │
         │            │  (Evaluation)   │
         │            └─────────────────┘
         │
         ▼
┌─────────────────┐
│  Output Files   │
│  (test_outputs) │
└─────────────────┘
```

## Components

### 1. Layer 1 (L1) - Blockchain

**What it does:**
- Stores immutable POD submission records
- Manages SYNTH token distribution (90T total)
- Enforces epoch-based rewards (Founder, Pioneer, Community, Ecosystem)
- Applies tier multipliers (Gold: 1000x, Silver: 100x, Copper: 1x)
- Validates and mines blocks
- Tracks contributor balances

**Inputs:**
- POD submissions (title, description, category, contributor, evidence)
- POD evaluations (coherence, density, novelty scores from L2)
- Token allocation requests

**Outputs:**
- Submission records with hashes
- Token allocation results
- Blockchain state (blocks, transactions)
- Statistics (epoch balances, contributor balances, reward history)

**Files:**
- `layer1/node.py` - Blockchain node
- `layer1/contracts/synth_token.py` - Token contract
- `layer1/contracts/pod_contract.py` - POD contract
- `layer1/blockchain.py` - Core blockchain

### 2. Layer 2 (L2) - PoD Server

**What it does:**
- Evaluates PDF papers using Syntheverse RAG API
- Scores submissions based on PoD protocol:
  - **Coherence** (0-10000): Fractal grammar closure, structural consistency
  - **Density** (0-10000): Structural contribution per fractal unit
  - **Novelty** (0-10000): Non-redundancy relative to knowledge base
- Determines tier classification (scientific/tech/alignment)
- Generates evaluation reports

**Inputs:**
- PDF file path or text content
- Submission metadata (title, category)

**Outputs:**
- Evaluation reports with scores
- PoD reports saved to `test_outputs/pod_reports/`

**Files:**
- `layer2/pod_server.py` - PoD evaluation server

### 3. PoD Submission UI

**What it does:**
- Interactive console for submitting PDFs
- Displays epoch status and token balances
- Lists all POD submissions with scores and allocations
- Generates comprehensive PoD reports

**Features:**
1. Submit PDF paper
2. View epoch status (shows all epochs, balances, thresholds)
3. List all PoD submissions (with identifiers, titles, scores, allocations)
4. Exit

**Files:**
- `ui_pod_submission.py` - Main UI console

## Workflow

### Submission Process

1. **User submits PDF** via UI
   - Provides PDF path, contributor ID, category

2. **L1 stores submission**
   - Creates submission hash
   - Creates transaction
   - Returns submission hash

3. **L2 evaluates PDF**
   - Extracts text from PDF
   - Queries RAG API for knowledge base comparison
   - Evaluates using PoD protocol criteria
   - Returns scores (coherence, density, novelty)

4. **L1 records evaluation**
   - Calculates PoD score: `(coherence × density × novelty) / 10000² × 10000`
   - Determines qualified epoch based on density threshold
   - Updates coherence density for halving calculations

5. **L1 allocates tokens** (if approved)
   - Checks tier availability in epoch
   - Calculates reward: `(PoD Score / 10000) × epoch balance × tier multiplier`
   - Allocates SYNTH tokens to contributor
   - Records reward

6. **L1 mines block**
   - Includes all pending transactions
   - Creates new block with PoD score

7. **System generates report**
   - Comprehensive PoD report saved to `test_outputs/pod_reports/`
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

### `test_outputs/blockchain/`
- `blockchain.json` - Complete blockchain chain
- `synth_token.json` - Token contract state
- `pod_contract.json` - POD contract state

### `test_outputs/pod_reports/`
- `{hash}_report.json` - Individual PoD reports
- Contains: submission, evaluation, allocation, epoch status, token stats

### `test_outputs/submissions_history.json`
- Complete list of all submissions
- Includes all metadata, scores, allocations

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
# 1. Start RAG API
cd rag-api/api
python rag_api.py

# 2. In another terminal, start PoD UI
python ui_pod_submission.py

# 3. Use interactive menu:
#    - Option 1: Submit PDF
#    - Option 2: View epoch status
#    - Option 3: List all PoDs
```

### Example Submission

```
Select option (1-4): 1
Enter PDF file path: /path/to/paper.pdf
Enter contributor ID: researcher-001
Enter category (scientific/tech/alignment) [scientific]: scientific

[System processes submission, evaluates, allocates tokens, mines block]
[Generates comprehensive report]
```

## Integration Points

- **L1 ↔ L2**: L2 sends evaluations to L1, L1 allocates tokens
- **L2 ↔ RAG API**: L2 queries RAG API for knowledge base comparison and evaluation
- **UI ↔ L1**: UI submits to L1, displays L1 status
- **UI ↔ L2**: UI triggers L2 evaluation

## PoD Protocol Evaluation

The system evaluates based on the Syntheverse PoD protocol:

1. **Coherence**: Fractal grammar closure, structural consistency, recursive patterns
2. **Density**: Informational richness, structural depth, contribution magnitude
3. **Novelty**: Uniqueness compared to FractiEmbedding archive, novel insights

Evaluation uses the RAG API with a specialized prompt based on the PoD protocol document.

## Notes

- All data persists to `test_outputs/` directory
- Reports are generated for each submission
- Epoch status updates automatically
- Token allocation depends on PoD score, epoch, and tier
- System validates tier availability in epochs before allocation
