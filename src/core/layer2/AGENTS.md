# Layer 2 Evaluation Agents

## Purpose

PoC evaluation engine with archive-first redundancy detection, multi-metal qualification, and token allocation. Orchestrates the contribution lifecycle.

## Key Modules

### Core Components

- **`poc_server.py`**: Main PoC server orchestrating evaluation and allocation
- **`poc_archive.py`**: Archive-first storage system for all contributions
- **`tokenomics_state.py`**: Token allocation state management
- **`sandbox_map.py`**: Network visualization generation

### Submodules

- **`evaluator/pod_evaluator.py`**: Evaluation logic (scaffold)
- **`allocator/token_allocator.py`**: Token allocation calculations

## Integration Points

- **PoC API**: Receives submissions from Flask API
- **Grok API**: Direct LLM calls for evaluation (no RAG retrieval)
- **Archive**: Stores all contributions for redundancy detection
- **Tokenomics**: Manages epoch balances and allocations
- **Sandbox Map**: Generates visualization data for frontend

## Development Guidelines

### Archive-First Principle

- All contributions immediately added to archive as DRAFT
- Redundancy checks operate over entire archive
- Archive stores complete contribution history
- Status lifecycle: DRAFT → EVALUATING → QUALIFIED/UNQUALIFIED → ARCHIVED

### Evaluation Process

- Direct Grok API calls with HHFE system prompt
- Parse markdown + JSON response format
- Calculate scores: coherence, density, redundancy
- Determine metal qualifications: Gold, Silver, Copper
- Check epoch qualification based on density thresholds

### Token Allocation

- Calculate based on PoC score and epoch weights
- Apply metal multipliers (Gold: 1000x, Silver: 100x, Copper: 1x)
- Check epoch availability for metal type
- Update persistent tokenomics state

## Common Patterns

- Multi-metal system: Contributions can qualify for multiple metals
- Archive-first redundancy detection
- Direct LLM integration (no RAG for evaluation)
- File-based state persistence
- Status-based contribution lifecycle
- Sandbox map generation from archive data

## Blueprint Alignment

### Core Implementation Mapping
- **Blueprint §1.3**: PoC Evaluation → `poc_server.py` + `poc_archive.py` evaluation system
- **Blueprint §3.2**: Contribution Classes & Scoring → HHFE metrics (coherence, density, novelty)
- **Blueprint §3.3**: Token Allocation & Epochs → `tokenomics_state.py` epoch-based distribution
- **Blueprint §3.4**: Metallic Combination Amplifications → Multi-metal qualification system

### Process Flow Implementation
- **Blueprint §3.1**: PoC Pipeline → Archive-first → Evaluation → Allocation → Ecosystem Integration
- **Implementation**: `poc_archive.py` (storage) → `poc_server.py` (evaluation) → `tokenomics_state.py` (allocation)

### Key Algorithm Alignment
- **Blueprint §3.2**: 0-10,000 scoring via hydrogen holographic fractal lens → HHFE evaluation prompt
- **Blueprint §3.3**: Epoch qualification by density → Thresholds: Founder ≥8000, Pioneer ≥6000, Community ≥4000
- **Blueprint §3.4**: Multipliers (1.25× Gold+Silver, 1.2× Gold+Copper, etc.) → Applied in allocation calculations

### Status & Verification Needed
- **✅ Confirmed**: Multi-metal evaluation, archive-first redundancy, HHFE scoring system
- **🟡 Verify**: Metallic amplification multipliers match Blueprint table exactly
- **🟡 Verify**: Epoch qualification thresholds align with Blueprint specifications
- **📋 Testing**: Create validation tests for Blueprint §3.2-3.4 mathematical accuracy

### Dependencies & Integration
- **Grok API**: Direct integration for HHFE evaluation (Blueprint §5)
- **Archive System**: Complete redundancy detection (Blueprint §3.1)
- **Tokenomics State**: Persistent allocation tracking (Blueprint §3.3)
- **Sandbox Map**: Visualization generation (Blueprint §1.5)

## File Structure

```
layer2/
├── poc_server.py             # Main PoC server
├── poc_archive.py             # Archive storage system
├── tokenomics_state.py        # Token allocation state
├── sandbox_map.py             # Network visualization
├── contributor_tiers.py       # Contributor management
├── pod_server.py             # PoD server (legacy)
├── evaluator/                 # Evaluation components
│   └── pod_evaluator.py       # Evaluation logic
├── allocator/                 # Token allocation logic
│   └── token_allocator.py     # Allocation calculations
└── zenodo_integration.py      # Zenodo integration
```

## Data Flow

1. **API Submission** → PoC Server receives contribution
2. **Archive Storage** → Immediate DRAFT status storage
3. **Evaluation** → Grok API assessment
4. **Qualification** → Metal assignment (Gold/Silver/Copper)
5. **Allocation** → Token calculation and distribution
6. **Registration** → Blockchain certificate creation

## Responsibilities

### Evaluation Orchestration
- Coordinate complete PoC evaluation pipeline from submission to allocation
- Manage archive-first storage and redundancy detection
- Execute hydrogen holographic fractal evaluation (HHFE) scoring
- Determine multi-metal qualifications (Gold, Silver, Copper)

### Tokenomics Management
- Calculate and apply epoch-based token allocations
- Apply metal multipliers and qualification thresholds
- Maintain persistent tokenomics state across system restarts
- Track epoch progression and availability

### Archive Management
- Ensure all contributions are immediately archived as DRAFT status
- Provide redundancy detection across entire contribution history
- Support status lifecycle management (DRAFT → EVALUATING → QUALIFIED/UNQUALIFIED → ARCHIVED)
- Generate sandbox map visualizations from archive data

## Interfaces

### Input Interfaces
- **PoC API**: Receives contribution submissions with metadata and file uploads
- **Grok API**: Direct LLM integration for evaluation scoring
- **File System**: Persistent storage for archive and tokenomics state

### Output Interfaces
- **Blockchain Layer**: Sends qualified contributions for on-chain registration
- **Frontend**: Provides sandbox map data and contribution status
- **Archive**: Complete contribution history for redundancy detection

### Internal Interfaces
- **Archive System**: Complete contribution storage and retrieval
- **Tokenomics Engine**: Epoch management and allocation calculations
- **Evaluation Engine**: HHFE scoring and metal qualification logic

## Dependencies

### Core Dependencies
- **Python Libraries**: requests, json, pathlib, datetime
- **Grok API**: Required for all evaluation operations
- **File System**: JSON-based persistent state storage

### External Services
- **Grok API**: LLM evaluation service (primary provider)
- **File Storage**: Local filesystem for archive and state persistence

### Configuration Requirements
- **GROQ_API_KEY**: Environment variable for API authentication
- **Archive Path**: Configurable archive storage location
- **Tokenomics State**: Persistent state file path

## Cross-References

- **Parent**:
  - [core/AGENTS.md](../AGENTS.md) | [core/FRACTAL.md](../FRACTAL.md) - Core logic
  - [src/AGENTS.md](../../AGENTS.md) | [src/FRACTAL.md](../../FRACTAL.md) - Source code
- **Related**:
  - [api/poc-api/AGENTS.md](../../api/poc-api/AGENTS.md) | [api/poc-api/FRACTAL.md](../../api/poc-api/FRACTAL.md) - API integration
  - [blockchain/AGENTS.md](../../blockchain/AGENTS.md) | [blockchain/FRACTAL.md](../../blockchain/FRACTAL.md) - Blockchain registration
  - [data/AGENTS.md](../../data/AGENTS.md) | [data/FRACTAL.md](../../data/FRACTAL.md) - Archive and state storage
  - [config/environment/AGENTS.md](../../../config/environment/AGENTS.md) | [config/environment/FRACTAL.md](../../../config/environment/FRACTAL.md) - Groq configuration
- **This Level**:
  - [FRACTAL.md](FRACTAL.md) - Hydrogen-holographic evaluation analysis
  - [evaluator/FRACTAL.md](evaluator/FRACTAL.md) - Scoring algorithms
  - [allocator/FRACTAL.md](allocator/FRACTAL.md) - Token allocation



