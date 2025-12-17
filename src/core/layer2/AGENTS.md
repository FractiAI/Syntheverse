# Layer 2 Evaluation Agents

## Purpose

PoC evaluation engine with archive-first redundancy detection, multi-metal qualification, and token allocation. Orchestrates the complete contribution lifecycle.

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

- Direct Grok API calls with comprehensive HHFE system prompt
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



