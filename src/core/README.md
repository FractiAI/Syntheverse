# Core Business Logic

## Purpose

Core business logic for PoC evaluation, tokenomics, and system orchestration.

## Components

### Layer 2 (`layer2/`)

PoC evaluation engine with archive-first redundancy detection.

**Key Modules:**
- **PoC Server**: Main orchestration server
- **PoC Archive**: Archive-first storage system
- **Tokenomics State**: Token allocation state management
- **Sandbox Map**: Network visualization generation

**Features:**
- Multi-metal evaluation (Gold, Silver, Copper)
- Archive-first redundancy detection
- Direct Grok API integration
- Token allocation based on PoC scores
- Sandbox map generation

**Status:** ✅ Fully Operational

## Architecture

### Archive-First Principle

All contributions are immediately stored in archive as DRAFT, enabling comprehensive redundancy detection across the entire contribution history.

### Evaluation Flow

1. Submission received → Added to archive as DRAFT
2. Redundancy check against entire archive
3. Grok API evaluation with HHFE system prompt
4. Parse evaluation results (markdown + JSON)
5. Calculate PoC scores and metal qualifications
6. Update archive status
7. Allocate tokens if qualified
8. Generate sandbox map data

### Multi-Metal System

Contributions can qualify for multiple metals:
- **Gold (Discovery)**: Scientific contributions
- **Silver (Technology)**: Technical implementations
- **Copper (Alignment)**: Alignment contributions

## Integration

- Receives submissions from PoC API
- Calls Grok API for LLM-based evaluation
- Manages archive for redundancy detection
- Calculates token allocations
- Generates sandbox map data for frontend

## Usage

```python
from layer2.poc_server import PoCServer

server = PoCServer(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    output_dir="test_outputs/poc_reports",
    tokenomics_state_file="test_outputs/l2_tokenomics_state.json",
    archive_file="test_outputs/poc_archive.json"
)
```

## Documentation

- [Layer 2 README](layer2/README.md)



