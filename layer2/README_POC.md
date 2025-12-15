# Proof of Contribution (PoC) System

## Quick Start

```python
from layer2.poc_server import PoCServer

# Initialize
server = PoCServer()

# Submit contribution
server.submit_contribution(
    submission_hash="hash123",
    title="My Contribution",
    contributor="contributor-001",
    text_content="Content here...",
    category="scientific"
)

# Evaluate
result = server.evaluate_contribution("hash123")

# Get sandbox map
map_data = server.get_sandbox_map()
```

## Key Features

### Archive-First Evaluation
- All contributions stored regardless of status
- Redundancy checks against ENTIRE archive
- Includes drafts, unqualified, archived contributions

### Multi-Metal Support
- Single contribution can contain Gold + Silver + Copper
- Separate allocation per metal
- Flexible categorization

### Lifecycle Tracking
- Draft → Submitted → Evaluating → Qualified/Unqualified → Archived
- Full status history

### Sandbox Map
- Visualization of all contributions
- Overlap/redundancy detection
- Contributor networks
- Metal distribution

## Components

- `poc_archive.py` - Archive storage and management
- `poc_server.py` - Main PoC server
- `sandbox_map.py` - Visualization system
- `tokenomics_state.py` - Tokenomics (updated epoch distribution)

## Archive Structure

```json
{
  "contributions": {
    "hash": {
      "submission_hash": "...",
      "title": "...",
      "contributor": "...",
      "content_hash": "...",
      "text_content": "...",
      "status": "qualified",
      "metals": ["gold", "silver"],
      "metadata": {...}
    }
  },
  "by_status": {...},
  "by_contributor": {...},
  "by_metal": {...}
}
```

## See Also

- [POC_UPGRADE.md](../docs/POC_UPGRADE.md) - Full upgrade documentation
