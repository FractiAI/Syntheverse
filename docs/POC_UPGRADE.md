# Proof of Contribution (PoC) Upgrade

## Overview

Major upgrade from Proof-of-Discovery (PoD) to Proof-of-Contribution (PoC) model with archive-first evaluation, multi-metal contributions, and Syntheverse Sandbox Map visualization.

## Key Changes

### 1. Archive-First Evaluation Rule (Critical)

**All redundancy and overlap detection operates over the ENTIRE PoC archive**, including:
- Drafts
- Unqualified submissions
- Archived or superseded versions
- Historical contributions across epochs

**Registration status does NOT affect redundancy evaluation.** The archive is the system's cognitive memory.

### 2. Multi-Metal Contributions

A single contribution can contain **multiple metals**:
- **Gold** - Discovery/Scientific contributions
- **Silver** - Technology contributions
- **Copper** - Alignment contributions

Example: A contribution can be Gold + Silver if it contains both scientific discovery and technological implementation.

### 3. Submission Lifecycle Tracking

Full lifecycle states:
- `DRAFT` - Initial submission
- `SUBMITTED` - Submitted for evaluation
- `EVALUATING` - Currently being evaluated
- `QUALIFIED` - Passed evaluation, eligible for allocation
- `UNQUALIFIED` - Failed evaluation thresholds
- `ARCHIVED` - Archived/superseded
- `SUPERSEDED` - Superseded by newer version

### 4. New Epoch Distribution

Total SYNTH supply: 90T (internal accounting units)

| Epoch | Distribution | Percentage |
|-------|-------------|------------|
| **Founders** | 45T | 50% |
| **Pioneer** | 22.5T | 25% |
| **Community** | 11.25T | 12.5% |
| **Ecosystem** | 11.25T | 12.5% |

These are accounting units only, not on-chain assets.

### 5. Syntheverse Sandbox Map

Visualization system for:
- Contribution nodes and relationships
- Overlap/redundancy detection
- Metal distribution
- Contributor network
- Archive browsing

## Architecture

```
┌─────────────────┐
│   PoC Server    │
│  (poc_server)   │
└────────┬────────┘
         │
    ┌────┴─────┐
    │          │
    ▼          ▼
┌─────────┐  ┌──────────────┐
│  Archive │  │ Tokenomics   │
│ (Archive)│  │    State     │
└────┬─────┘  └──────────────┘
     │
     ▼
┌──────────────┐
│ Sandbox Map  │
│(Visualization)│
└──────────────┘
```

## Components

### PoC Archive (`poc_archive.py`)

- **Archive-first storage**: Stores ALL contributions regardless of status
- **Lifecycle tracking**: Full status management
- **Multi-metal support**: Tracks multiple metals per contribution
- **Content hash tracking**: For duplicate detection
- **Indexed access**: By status, contributor, metal type

### PoC Server (`poc_server.py`)

- **Archive-first evaluation**: Redundancy checks against entire archive
- **Multi-metal evaluation**: Supports Gold + Silver + Copper combinations
- **Lifecycle management**: Manages submission states
- **Allocation calculation**: Per-metal allocation support

### Sandbox Map (`sandbox_map.py`)

- **Visualization data**: Nodes and edges for graph visualization
- **Overlap detection**: Calculates similarity between contributions
- **Redundancy reporting**: Detailed overlap analysis
- **Metal distribution**: Statistics and distribution analysis
- **Contributor network**: Collaboration network visualization

### Tokenomics State (`tokenomics_state.py`)

- **Updated epoch distribution**: New 45T/22.5T/11.25T/11.25T split
- **Multi-metal allocation**: Supports multiple allocations per contribution

## Usage

### Initialize PoC Server

```python
from layer2.poc_server import PoCServer

server = PoCServer(
    groq_api_key=None,  # Uses GROQ_API_KEY env var
    archive_file="test_outputs/poc_archive.json"
)
```

### Submit Contribution

```python
result = server.submit_contribution(
    submission_hash="abc123...",
    title="Novel Discovery",
    contributor="researcher-001",
    text_content="Research paper content...",
    category="scientific"
)
```

### Evaluate Contribution

```python
evaluation = server.evaluate_contribution(
    submission_hash="abc123...",
    progress_callback=lambda status, msg: print(f"{status}: {msg}")
)

if evaluation["success"]:
    print(f"Metals: {evaluation['metals']}")
    print(f"Qualified: {evaluation['qualified']}")
    for allocation in evaluation["allocations"]:
        print(f"{allocation['metal']}: {allocation['allocation']['reward']} SYNTH")
```

### Get Sandbox Map

```python
map_data = server.get_sandbox_map()
# Returns nodes, edges, and statistics for visualization
```

### Get Archive Statistics

```python
stats = server.get_archive_statistics()
print(f"Total contributions: {stats['total_contributions']}")
print(f"Status breakdown: {stats['status_counts']}")
print(f"Metal distribution: {stats['metal_counts']}")
```

## Archive-First Evaluation Flow

1. **Submit**: Contribution added to archive as DRAFT
2. **Status Update**: Changed to SUBMITTED
3. **Archive Check**: System retrieves ALL contributions from archive
4. **Redundancy Check**: Compares against entire archive (not just approved)
5. **LLM Evaluation**: Grok API evaluates with archive context
6. **Metal Detection**: Identifies Gold/Silver/Copper components
7. **Qualification**: Determines if contribution qualifies
8. **Allocation**: Calculates allocations for each metal
9. **Archive Update**: Updates contribution with evaluation results

## Multi-Metal Allocation

When a contribution contains multiple metals:

```python
{
    "metals": ["gold", "silver"],
    "allocations": [
        {
            "metal": "gold",
            "epoch": "founder",
            "tier": "gold",
            "allocation": {
                "reward": 1234567.89,
                "tier_multiplier": 1000.0
            }
        },
        {
            "metal": "silver",
            "epoch": "community",
            "tier": "silver",
            "allocation": {
                "reward": 12345.67,
                "tier_multiplier": 100.0
            }
        }
    ]
}
```

## Migration Notes

- **Backward Compatibility**: Original `PODServer` maintained for legacy systems
- **New System**: Use `PoCServer` for new implementations
- **Archive Migration**: Can migrate existing submissions to new archive format
- **Tokenomics**: Epoch distribution updated (existing balances preserved)

## Files

- `layer2/poc_archive.py` - Archive system
- `layer2/poc_server.py` - PoC server
- `layer2/sandbox_map.py` - Sandbox map visualization
- `layer2/tokenomics_state.py` - Updated tokenomics (epoch distribution)

## Status

✅ Archive system implemented
✅ Multi-metal support implemented
✅ Archive-first redundancy detection implemented
✅ Lifecycle tracking implemented
✅ Sandbox map visualization implemented
✅ PoC server integrated
🚧 Web UI integration (pending)
🚧 Documentation updates (in progress)
