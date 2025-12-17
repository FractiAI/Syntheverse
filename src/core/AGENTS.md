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



