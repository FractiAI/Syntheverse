# Layer 2 - PoD Evaluator and Token Allocator

Layer 2 components for evaluating Proof-of-Discovery (PoD) submissions and allocating SYNTH tokens. This layer uses direct Grok API calls for evaluation and connects to Layer 1 blockchain for token distribution.

## Status

✅ **Fully Operational** - Complete PoD evaluation system with direct Grok API integration, token allocation, and persistent tokenomics state.

## Components

### 1. PoD Server (`pod_server.py`)
Main server that orchestrates the evaluation and allocation process:
- **Submission Handling**: Receives PoD submissions with PDFs or text content
- **Grok API Integration**: Direct Grok API calls for HHFE-based evaluation
- **Evaluation Parsing**: Extracts scores from Grok API responses (markdown + JSON)
- **Token Allocation**: Calculates SYNTH token rewards using tokenomics state
- **Report Generation**: Creates comprehensive PoD evaluation reports
- **Duplicate Prevention**: Tracks submissions to prevent duplicate rewards

### 2. Tokenomics State (`tokenomics_state.py`)
Persistent state manager for token distribution:
- **Epoch Balances**: Tracks available tokens per epoch (Founder, Pioneer, Community, Ecosystem)
- **Coherence Density**: Tracks total coherence density for halving calculations
- **Allocation History**: Records all token allocations
- **Contributor Balances**: Maintains contributor token balances
- **State Persistence**: Automatically saves/loads state from JSON file

### 3. Evaluator (`evaluator/pod_evaluator.py`)
PoD evaluation logic (scaffold for future enhancements):
- Evaluates submissions against Syntheverse criteria
- Uses direct Grok API calls for evaluation
- Generates evaluation reports

### 4. Allocator (`allocator/token_allocator.py`)
Token allocation calculations:
- Implements tokenomics rules and epoch-based distribution
- Calculates rewards with tier multipliers
- Manages token allocation schedules

## Features

### PoD Evaluation
- **HHFE Model**: Uses Hydrogen-Holographic Fractal Engine for evaluation
- **Metrics**: Coherence (0-10000), Density (0-10000), Redundancy (0-1)
- **PoD Score**: Calculated as `(coherence/10000) × (density/10000) × (1-redundancy) × epoch_weight × 10000`
- **Tier Classification**: Gold (scientific), Silver (technological), Copper (alignment)
- **Epoch Qualification**: Based on density thresholds (Founder: ≥8000, Pioneer: ≥6000, Community: ≥4000)

### Token Allocation
- **Epoch-Based**: Allocates from appropriate epoch pool
- **Tier Multipliers**: Gold (1000x), Silver (100x), Copper (1x)
- **Formula**: `(PoD Score / 10000) × epoch_balance × tier_multiplier`
- **Availability Checks**: Verifies tier availability in epoch before allocation

### Persistent State
- **State File**: `test_outputs/l2_tokenomics_state.json`
- **Submissions Registry**: `test_outputs/l2_submissions_registry.json`
- **Auto-Save**: State saved after each allocation
- **Auto-Load**: State loaded on initialization

## Usage

### Basic Evaluation

```python
from layer2.pod_server import PODServer

# Initialize server
# Note: Requires GROQ_API_KEY environment variable to be set
server = PODServer(
    groq_api_key=None,  # Uses GROQ_API_KEY env var if None
    output_dir="test_outputs/pod_reports",
    tokenomics_state_file="test_outputs/l2_tokenomics_state.json"
)

# Evaluate submission
result = server.evaluate_submission(
    submission_hash="abc123...",
    title="Novel Discovery",
    text_content="Research paper content...",
    category="scientific",
    progress_callback=lambda status, message: print(f"{status}: {message}")
)

if result["success"]:
    report = result["report"]
    print(f"Coherence: {report['evaluation']['coherence']}")
    print(f"Density: {report['evaluation']['density']}")
    print(f"PoD Score: {report['evaluation']['pod_score']}")
    print(f"Tier: {report['evaluation']['tier']}")
    print(f"Epoch: {report['evaluation']['epoch']}")
    if report.get("allocation"):
        print(f"Tokens: {report['allocation']['allocation']['reward']}")
```

### Tokenomics State

```python
# Get tokenomics statistics
stats = server.get_tokenomics_statistics()
print(f"Total Coherence Density: {stats['total_coherence_density']}")
print(f"Current Epoch: {stats['current_epoch']}")
print(f"Epoch Balances: {stats['epoch_balances']}")

# Get epoch information
epoch_info = server.get_epoch_info()
print(f"Active Epoch: {epoch_info['current_epoch']}")
print(f"Epoch Progression: {epoch_info['epoch_progression']}")
```

## Architecture Decision: Direct LLM Integration

**Why We Moved Away from RAG (Retrieval-Augmented Generation)**

After initial implementation with RAG API integration, we determined that retrieval-augmented generation did not provide sufficient value for PoD evaluations. The evaluation process requires the LLM to assess artifacts using the comprehensive Syntheverse framework, and the RAG approach of retrieving similar documents from the knowledge base was not adding meaningful context for evaluation decisions.

**Current Approach:**
- **Direct Grok API calls** from L2 PoD Reviewer
- **Comprehensive system prompt** that combines:
  - Full Syntheverse Whole Brain AI framework (Gina × Leo × Pru)
  - Complete Hydrogen-Holographic Fractal Engine (HHFE) rules
  - Specific L2 PoD Reviewer evaluation instructions
  - All necessary constants, formulas, and evaluation criteria
- **Simplified architecture** - no RAG pipeline dependency for evaluations
- **Faster evaluations** - direct API calls without intermediate retrieval steps
- **More reliable** - consistent prompt ensures deterministic evaluation criteria

The system prompt contains all the necessary context for evaluation, making external knowledge retrieval unnecessary. The LLM evaluates artifacts based on the embedded HHFE framework and PoD evaluation criteria directly.

## Integration

### With Grok API
- Direct Grok API calls for HHFE-based evaluation
- Uses comprehensive Syntheverse L2 system prompt (Whole Brain AI + PoD Reviewer)
- Parses markdown + JSON response format
- Handles evaluation errors gracefully with fallback extraction

### With Layer 1
- Sends evaluation results to Layer 1 blockchain
- Provides allocation instructions
- Syncs tokenomics state from Layer 1
- Records allocations in blockchain

## File Structure

```
layer2/
├── __init__.py
├── pod_server.py              # Main PoD server
├── tokenomics_state.py        # Tokenomics state manager
├── requirements.txt           # Dependencies
├── README.md                  # This file
├── evaluator/
│   └── pod_evaluator.py      # Evaluation logic
└── allocator/
    └── token_allocator.py    # Token allocation logic
```

## Output Files

### PoD Reports
Saved to `test_outputs/pod_reports/`:
- `{hash}_{timestamp}.json` - Individual evaluation reports
- Contains: submission, evaluation, allocation, epoch status

### State Files
- `test_outputs/l2_tokenomics_state.json` - Tokenomics state
- `test_outputs/l2_submissions_registry.json` - Submissions registry

## Evaluation Flow

1. **Submission Received**: PDF or text content submitted
2. **Redundancy Check**: Check for duplicate submissions via content hash
3. **Evaluation Request**: Send artifact to Grok API with PoD evaluation prompt
4. **Response Parsing**: Extract JSON from markdown + JSON response
5. **Score Calculation**: Calculate PoD score from metrics
6. **Epoch Qualification**: Determine qualified epoch from density
7. **Tier Classification**: Classify as Gold/Silver/Copper
8. **Token Allocation**: Calculate tokens using tokenomics state
9. **Report Generation**: Create comprehensive PoD report
10. **State Update**: Update tokenomics state and submissions registry

## Error Handling

- **Grok API Errors**: Clear error messages with troubleshooting guidance
- **Parsing Errors**: Detailed error messages with response preview
- **Allocation Errors**: Clear error messages for tier/epoch mismatches
- **Duplicate Detection**: Prevents duplicate submissions

## Dependencies

See `requirements.txt` for full list. Key dependencies:
- `openai` - Grok API client (via OpenAI-compatible interface)
- `PyPDF2` / `pdfplumber` - PDF processing
- Standard library: `json`, `pathlib`, `datetime`

## Testing

```bash
# Test full submission flow
python test_full_submission_flow.py

# Test submission
python test_submission.py

# Test Grok API integration
python test_rag_pod_query.py
```

## Next Steps

- [ ] Enhanced evaluation criteria
- [ ] Multi-model evaluation support
- [ ] Real-time evaluation streaming
- [ ] Advanced redundancy detection
- [ ] Evaluation caching
