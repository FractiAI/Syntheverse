# Core Logic Agents

## Purpose

The `core/` directory contains core business logic for PoC evaluation, tokenomics, and system orchestration.

## Key Modules

### Layer 2 (`layer2/`)

PoC evaluation and tokenomics system:

- **`poc_server.py`**: Main PoC server orchestrating evaluation
- **`poc_archive.py`**: Archive-first storage system
- **`tokenomics_state.py`**: Token allocation state management
- **`sandbox_map.py`**: Network visualization generation
- **`evaluator/pod_evaluator.py`**: Evaluation logic
- **`allocator/token_allocator.py`**: Token allocation calculations

## Integration Points

- PoC Server receives submissions from PoC API
- Calls Grok API for LLM-based evaluation
- Archive stores all contributions for redundancy detection
- Tokenomics State manages epoch balances and allocations
- Sandbox Map generates visualization data for frontend

## Development Guidelines

### Archive-First Principle

- All contributions immediately added to archive as DRAFT
- Redundancy checks operate over entire archive
- Archive stores complete contribution history
- Status lifecycle: DRAFT → EVALUATING → QUALIFIED/UNQUALIFIED → ARCHIVED

### Evaluation Process

- Direct Grok API calls (no RAG retrieval)
- Comprehensive HHFE system prompt
- Parse markdown + JSON response
- Calculate scores and metal qualifications

### Token Allocation

- Calculate based on PoC score
- Apply epoch weights and metal multipliers
- Check epoch availability for metal type
- Update persistent tokenomics state

## Common Patterns

- Multi-metal system: Gold, Silver, Copper
- Archive-first redundancy detection
- Direct LLM integration for evaluation
- File-based state persistence
- Status-based contribution lifecycle

## File Structure

```
core/
├── layer2/                    # Layer 2 evaluation system
│   ├── poc_server.py         # Main PoC server
│   ├── poc_archive.py         # Archive storage system
│   ├── tokenomics_state.py    # Token allocation state
│   ├── sandbox_map.py         # Network visualization
│   ├── evaluator/             # Evaluation components
│   ├── allocator/             # Token allocation logic
│   └── contributor_tiers.py   # Contributor management
└── utils/                     # Core utilities
    └── env_loader.py          # Environment configuration
```

## Data Flow

1. **PoC API** → Receives submission
2. **PoC Server** → Orchestrates evaluation
3. **Archive** → Stores contribution (DRAFT)
4. **Evaluator** → Calls Groq API for assessment
5. **Tokenomics** → Calculates allocation
6. **Blockchain** → Registers certificate

## Blueprint Alignment

### Layer 2 Evaluation Engine ([Blueprint §3](docs/Blueprint for Syntheverse))
- **Core Architecture**: `layer2/` implements the complete PoC evaluation engine with archive-first redundancy
- **Hydrogen Holographic Evaluation**: `poc_server.py` + `evaluator/` execute the fractal scoring methodology
- **Tokenomics Engine**: `tokenomics_state.py` manages SYNTH allocation across epochs and metal types

### PoC Evaluation Pipeline ([Blueprint §1.3](docs/Blueprint for Syntheverse))
- **Archive-First Storage**: `poc_archive.py` immediately stores all contributions for redundancy detection
- **GROQ Integration**: Direct LLM calls using `src.core.utils.load_groq_api_key()` for evaluation
- **Multi-Dimensional Scoring**: 0-10,000 scores across novelty/density/coherence/alignment dimensions
- **Human Oversight**: Evaluation results require approval before qualification

### Token Allocation System ([Blueprint §3.3](docs/Blueprint for Syntheverse))
- **Epoch-Based Distribution**: `tokenomics_state.py` manages 90T SYNTH supply across operator-controlled epochs
- **Metallic Amplifications**: Gold/Silver/Copper multipliers (1.5×/1.25×/1.2×/1.15×) for cross-disciplinary value
- **Threshold Scaling**: Core (high-impact) to leaf (supporting) contribution scaling from high to low

### Metallic Qualification System ([Blueprint §3.4](docs/Blueprint for Syntheverse))
- **Gold + Silver**: Research + Technology → 1.25× amplification for integrated contributions
- **Gold + Copper**: Research + Alignment → 1.2× amplification for ecosystem-aligned work
- **Silver + Copper**: Development + Alignment → 1.15× amplification for balanced contributions
- **Full Integration**: Gold + Silver + Copper → 1.5× maximum amplification

### AI Integration ([Blueprint §5](docs/Blueprint for Syntheverse))
- **Archive Training**: All PoCs stored in `poc_archive.py` train and evolve the Syntheverse AI
- **Fractal Expansion**: Contributions expand hydrogen holographic awareness and ecosystem intelligence
- **Recursive Improvement**: AI evaluation quality improves through accumulated contribution data

### Governance & Operations ([Blueprint §6](docs/Blueprint for Syntheverse))
- **Human Approval Required**: All PoC evaluations need operator review for ecosystem alignment
- **Operator Control**: Epoch thresholds and metal availability managed through `tokenomics_state.py`
- **Transparency**: All SYNTH allocations auditable through blockchain Layer 1 integration

### Complete Workflow Implementation ([Blueprint §7](docs/Blueprint for Syntheverse))
1. **Archive Storage**: Immediate contribution storage in `poc_archive.py` (DRAFT status)
2. **Evaluation**: Hydrogen holographic scoring via `poc_server.py` and GROQ API
3. **Qualification**: Metal assignment based on score thresholds and dimensional analysis
4. **Approval**: Human review and ecosystem alignment verification
5. **Allocation**: SYNTH token calculation with metallic amplifications via `tokenomics_state.py`
6. **Registration**: Coordination with Layer 1 for $200 blockchain anchoring
7. **Integration**: Full contribution incorporation into evolving ecosystem

### Financial Framework ([Blueprint §4](docs/Blueprint for Syntheverse))
- **Free Evaluation**: All submissions processed at no cost through Layer 2 evaluation engine
- **Registration Fee**: $200 on-chain registration for approved, high-quality contributions
- **Alignment Tiers**: Foundation for Copper/Silver/Gold contributor participation system

### Implementation Status
- **✅ Fully Operational**: Complete Layer 2 evaluation pipeline with archive-first redundancy
- **🟡 Enhanced**: Metallic amplifications validated, epoch management operational
- **📋 Blueprint Complete**: All core evaluation and tokenomics mechanics implemented

## Cross-References

- **Blueprint Document**: [docs/Blueprint for Syntheverse](../../docs/Blueprint for Syntheverse) - Central system vision
- **Layer 2 Documentation**: [docs/L2_SYSTEM_PROMPT.md](../../docs/L2_SYSTEM_PROMPT.md) - Evaluation methodology
- **Tokenomics Guide**: [docs/L2_TOKENOMICS.md](../../docs/L2_TOKENOMICS.md) - Allocation system
- **Parent**: [src/AGENTS.md](../AGENTS.md) - Source code organization
- **Children**:
  - [layer2/AGENTS.md](layer2/AGENTS.md) - Layer 2 implementation
- **Related**:
  - [api/poc-api/AGENTS.md](../api/poc-api/AGENTS.md) - API integration
  - [blockchain/AGENTS.md](../blockchain/AGENTS.md) - Blockchain registration
  - [config/environment/AGENTS.md](../../config/environment/AGENTS.md) - Groq configuration
  - [docs/POC_SUBMISSION_TO_ALLOCATION_FLOW.md](../../docs/POC_SUBMISSION_TO_ALLOCATION_FLOW.md) - Complete workflow