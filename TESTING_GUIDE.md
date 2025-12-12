# Testing Guide for PoD Submission UI

## Quick Test Results

The test script ran successfully! Here's what happened:

### Test Results
- ✅ UI initialized successfully
- ✅ Epoch status displayed correctly
- ✅ Submission created and stored in L1
- ✅ Evaluation completed by L2
- ✅ Report generated and saved
- ⚠️ Submission rejected (density too low: 410 < 4000)

### Why It Was Rejected

The test submission had:
- Coherence: 5000
- Density: 410 (too low - needs ≥ 4000 for Community epoch)
- Novelty: 5500
- Status: **rejected**

## Interactive Testing

### Start the UI

```bash
python ui_pod_submission.py
```

### Menu Options

1. **Submit PDF paper** - Submit a research paper for evaluation
2. **View epoch status** - See all epochs, balances, and thresholds
3. **List all PoD submissions** - View all submissions with scores
4. **Exit** - Quit the application

### Testing with a PDF

1. Select option `1`
2. Enter PDF path (e.g., `/path/to/your/paper.pdf`)
3. Enter contributor ID (e.g., `researcher-001`)
4. Enter category: `scientific`, `tech`, or `alignment`

### What Happens

1. **L1 Submission**: Creates submission hash, stores in blockchain
2. **L2 Evaluation**: Evaluates PDF using RAG API
3. **Allocation Preview**: Shows potential reward before allocation
4. **L1 Allocation**: Allocates tokens if approved
5. **L2 Recording**: Records allocation in tokenomics state
6. **Block Mining**: Mines block with all transactions
7. **Report Generation**: Creates comprehensive PoD report

### Expected Outputs

All outputs saved to `test_outputs/`:

- **`blockchain/`**: L1 blockchain state files
  - `blockchain.json` - Complete chain
  - `synth_token.json` - Token state
  - `pod_contract.json` - POD contract state

- **`pod_reports/`**: Individual PoD reports
  - `{hash}_report.json` - Full evaluation and allocation report

- **`l2_tokenomics_state.json`**: L2 persistent tokenomics state
  - Epoch balances
  - Coherence density
  - Allocation history

- **`submissions_history.json`**: All submission records

## Testing Different Scenarios

### 1. Scientific Contribution (Gold Tier)

- Category: `scientific`
- Needs density ≥ 8000 for Founder epoch
- Gets 1000x multiplier
- Available in all epochs

### 2. Tech Contribution (Silver Tier)

- Category: `tech`
- Needs density ≥ 4000 for Community epoch
- Gets 100x multiplier
- Only available in Community/Ecosystem epochs

### 3. Alignment Contribution (Copper Tier)

- Category: `alignment`
- Needs density ≥ 6000 for Pioneer epoch
- Gets 1x multiplier
- Available in Pioneer/Community/Ecosystem epochs

## Tips for Testing

1. **RAG API**: Make sure RAG API is running at `http://localhost:8000`
   - Check: `curl http://localhost:8000/health`

2. **PDF Files**: Use actual research papers for better evaluation
   - The system extracts text and evaluates content

3. **Density Scores**: Higher density = better epoch qualification
   - ≥ 8000: Founder epoch (Gold tier only)
   - ≥ 6000: Pioneer epoch (Gold, Copper)
   - ≥ 4000: Community epoch (All tiers)
   - < 4000: Ecosystem epoch (All tiers)

4. **View Status**: Use option 2 to see current epoch balances
   - Shows remaining tokens per epoch
   - Shows coherence density
   - Shows halving count

5. **View Submissions**: Use option 3 to see all PoD submissions
   - Shows all submissions with scores
   - Shows allocations if approved
   - Shows epoch and tier assignments

## Troubleshooting

### RAG API Not Running
- Start it: `cd rag-api/api && python rag_api.py`
- Or use fallback evaluation (less accurate)

### Import Errors
- Make sure you're in the Syntheverse directory
- Check that all dependencies are installed

### Low Scores
- Use actual research papers for better evaluation
- The RAG API provides better context for scoring

## Next Steps

1. Try submitting a real PDF paper
2. Check the generated reports in `test_outputs/pod_reports/`
3. View the tokenomics state in `test_outputs/l2_tokenomics_state.json`
4. Check blockchain state in `test_outputs/blockchain/`

