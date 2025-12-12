# Test Outputs Directory

This directory contains all outputs from test mode operations.

## Directory Structure

```
test_outputs/
├── blockchain/              # L1 blockchain state files
│   ├── blockchain.json      # Blockchain chain data
│   ├── synth_token.json     # Token contract state
│   └── pod_contract.json     # POD contract state
│
├── pod_reports/             # L2 PoD evaluation reports
│   └── {hash}_report.json   # Individual PoD reports
│
└── submissions_history.json # All submission records
```

## Files

### Blockchain State (`blockchain/`)
- **blockchain.json**: Complete blockchain chain with all blocks and transactions
- **synth_token.json**: SYNTH token contract state including epoch balances and distributions
- **pod_contract.json**: POD contract state including submissions, rewards, and tier assignments

### PoD Reports (`pod_reports/`)
Each report contains:
- Submission details (hash, title, contributor, category)
- Evaluation scores (coherence, density, novelty)
- PoD score calculation
- Token allocation (epoch, tier, reward amount)
- Blockchain status at time of submission
- Epoch and token statistics

### Submission History (`submissions_history.json`)
Complete list of all submissions with:
- Submission identifiers
- Titles and metadata
- Evaluation results
- Allocation details
- Status (approved/rejected)
