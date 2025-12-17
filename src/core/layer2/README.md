# Layer 2 - Proof-of-Contribution (PoC) and Proof-of-Discovery (PoD) Systems

Layer 2 contains two evaluation systems for Syntheverse contributions and discoveries:

1. **PoC System**: Archive-first evaluation with multi-metal contributions and sandbox map visualization
2. **PoD System**: Legacy evaluation system for discovery-based submissions

Both systems use direct Grok API calls and connect to Layer 1 blockchain for token distribution.

## Status

✅ **PoC System**: Complete archive-first evaluation with multi-metal support, sandbox map, and persistent state
✅ **PoD System**: Legacy evaluation system maintained for backward compatibility

## Components

### PoC System (Proof of Contribution)

#### 1. PoC Server (`poc_server.py`)
Archive-first contribution evaluation system:
- **Archive-First Evaluation**: Redundancy checks against entire contribution archive
- **Multi-Metal Support**: Gold/Silver/Copper contributions in single submission
- **Lifecycle Tracking**: DRAFT → SUBMITTED → EVALUATING → QUALIFIED/UNQUALIFIED
- **Sandbox Map Integration**: Generates visualization data for network graphs
- **Grok API Integration**: Direct LLM calls for evaluation

#### 2. PoC Archive (`poc_archive.py`)
Persistent storage for all contributions:
- **Archive-First Rule**: Stores ALL contributions regardless of status
- **Content Hashing**: Prevents exact duplicates
- **Multi-Metal Indexing**: Tracks Gold/Silver/Copper by contributor and metal
- **Lifecycle Management**: Manages contribution status transitions

#### 3. Sandbox Map (`sandbox_map.py`)
Visualization system for contribution relationships:
- **Overlap Detection**: Calculates similarity between contributions
- **Redundancy Analysis**: Identifies highly similar submissions
- **Network Generation**: Creates nodes and edges for frontend visualization
- **Statistics**: Provides metal distribution and contributor metrics

### PoD System (Proof of Discovery)

#### 4. PoD Server (`pod_server.py`)
Legacy discovery evaluation system:
- **Submission Handling**: Receives PoD submissions with PDFs or text content
- **Grok API Integration**: Direct Grok API calls for HHFE-based evaluation
- **Evaluation Parsing**: Extracts scores from Grok API responses (markdown + JSON)
- **Token Allocation**: Calculates SYNTH token rewards using tokenomics state
- **Report Generation**: Creates comprehensive PoD evaluation reports
- **Duplicate Prevention**: Tracks submissions to prevent duplicate rewards

#### 5. Evaluator (`evaluator/pod_evaluator.py`)
PoD evaluation logic:
- Evaluates submissions against Syntheverse criteria
- Uses direct Grok API calls for evaluation
- Generates evaluation reports

#### 6. Allocator (`allocator/token_allocator.py`)
Token allocation calculations:
- Implements tokenomics rules and epoch-based distribution
- Calculates rewards with tier multipliers
- Manages token allocation schedules

### Shared Components

#### 7. Tokenomics State (`tokenomics_state.py`)
Persistent state manager for token distribution:
- **Epoch Balances**: Tracks available tokens per epoch (Founder, Pioneer, Community, Ecosystem)
- **Coherence Density**: Tracks total coherence density for halving calculations
- **Allocation History**: Records all token allocations
- **Contributor Balances**: Maintains contributor token balances
- **State Persistence**: Automatically saves/loads state from JSON file

## Features

### PoC System Features

#### Archive-First Evaluation
- **Complete Archive**: All contributions stored regardless of status (drafts, unqualified, archived)
- **Redundancy Detection**: Compares against entire archive, not just approved submissions
- **Content Hashing**: Prevents exact duplicates across entire contribution history

#### Multi-Metal Contributions
- **Gold (Discovery)**: Novel findings and breakthroughs
- **Silver (Technology)**: Technical implementations and tools
- **Copper (Alignment)**: Alignment contributions and ecosystem support
- **Single Submission**: One contribution can qualify for multiple metals

#### Sandbox Map Visualization
- **Network Graphs**: Interactive visualization of contribution relationships
- **Overlap Detection**: Calculates similarity between contributions
- **Metal Distribution**: Statistics and charts by contribution type
- **Contributor Networks**: Collaboration and influence mapping

### PoD System Features

#### HHFE-Based Evaluation
- **Hydrogen-Holographic Fractal Engine**: Comprehensive evaluation framework
- **Metrics**: Coherence (0-10000), Density (0-10000), Novelty (0-10000)
- **PoD Score**: `(coherence/10000) × (density/10000) × (novelty/10000) × 10000`
- **Tier Classification**: Gold (scientific), Silver (technological), Copper (alignment)
- **Epoch Qualification**: Density-based thresholds (Founder: ≥8000, Pioneer: ≥6000, etc.)

### Shared Features

#### Token Allocation
- **Epoch-Based Distribution**: Founder, Pioneer, Community, Ecosystem epochs
- **Tier Multipliers**: Gold (1000x), Silver (100x), Copper (1x)
- **Availability Rules**: Different tiers available in different epochs
- **Persistent State**: Automatic saving/loading of allocation state

#### Integration
- **Direct Grok API**: No RAG dependency for evaluations
- **Layer 1 Connection**: Sends results to blockchain for token distribution
- **Comprehensive Reports**: Detailed evaluation and allocation reports

## Usage

### PoC System Usage

```python
from layer2.poc_server import PoCServer

# Initialize PoC server
server = PoCServer(
    groq_api_key=None,  # Uses GROQ_API_KEY env var
    archive_file="test_outputs/poc_archive.json"
)

# Submit contribution (archive-first)
result = server.submit_contribution(
    submission_hash="abc123...",
    title="Multi-Metal Contribution",
    contributor="researcher-001",
    text_content="Content covering discovery, technology, and alignment...",
    category="scientific"
)

# Evaluate contribution
evaluation = server.evaluate_contribution(
    submission_hash="abc123...",
    progress_callback=lambda status, msg: print(f"{status}: {msg}")
)

if evaluation["success"]:
    print(f"Metals: {evaluation['metals']}")  # ['gold', 'silver']
    print(f"Qualified: {evaluation['qualified']}")
    for allocation in evaluation["allocations"]:
        print(f"{allocation['metal']}: {allocation['allocation']['reward']} SYNTH")

# Get sandbox map for visualization
map_data = server.get_sandbox_map()
# Returns nodes, edges, and statistics for frontend
```

### PoD System Usage

```python
from layer2.pod_server import PODServer

# Initialize PoD server
server = PODServer(
    groq_api_key=None,  # Uses GROQ_API_KEY env var
    output_dir="test_outputs/pod_reports"
)

# Evaluate submission
result = server.evaluate_submission(
    submission_hash="def456...",
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

### Tokenomics State (Shared)

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
├── README.md                  # This file
├── requirements.txt           # Dependencies
├── README_POC.md             # PoC system quick start
│
├── poc_server.py             # PoC server (archive-first, multi-metal)
├── poc_archive.py             # PoC archive system
├── sandbox_map.py             # Sandbox map visualization
│
├── pod_server.py             # PoD server (legacy)
├── tokenomics_state.py        # Tokenomics state manager (shared)
│
├── evaluator/
│   └── pod_evaluator.py      # PoD evaluation logic
└── allocator/
    └── token_allocator.py    # Token allocation logic
```

## Output Files

### PoC System Outputs
- `test_outputs/poc_archive.json` - Complete contribution archive
- `test_outputs/poc_reports/` - Evaluation reports with multi-metal allocations

### PoD System Outputs
- `test_outputs/pod_reports/` - Individual PoD evaluation reports
- `test_outputs/l2_submissions_registry.json` - PoD submissions registry

### Shared Outputs
- `test_outputs/l2_tokenomics_state.json` - Tokenomics state (epochs, balances, history)

## Evaluation Flows

### PoC Evaluation Flow (Archive-First)

1. **Archive Submission**: Contribution added to archive as DRAFT
2. **Status Update**: Changed to SUBMITTED
3. **Archive-First Check**: Compare against ENTIRE archive (not just approved)
4. **Redundancy Analysis**: Calculate similarity with existing contributions
5. **LLM Evaluation**: Grok API evaluates with archive context
6. **Metal Detection**: Identify Gold/Silver/Copper components
7. **Qualification**: Determine if contribution qualifies
8. **Multi-Metal Allocation**: Calculate allocations for each metal
9. **Archive Update**: Update contribution with evaluation results
10. **Sandbox Map Update**: Generate visualization data

### PoD Evaluation Flow (Legacy)

1. **Submission Received**: PDF or text content submitted
2. **Redundancy Check**: Check for duplicate submissions via content hash
3. **Evaluation Request**: Send artifact to Grok API with PoD evaluation prompt
4. **Response Parsing**: Extract JSON from markdown + JSON response
5. **Score Calculation**: Calculate PoD score from coherence/density/novelty
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
