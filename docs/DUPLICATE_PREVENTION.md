# Duplicate and Redundancy Prevention

## Overview

Layer 2 (L2) now includes comprehensive duplicate and redundancy checking to ensure only the **first registered submission** receives token rewards.

## How It Works

### 1. Duplicate Detection

L2 maintains a **submissions registry** that tracks:
- **Submission hashes**: Unique identifiers for each submission
- **Content hashes**: SHA256 hash of normalized content (prevents exact duplicates)

**Duplicate Check Process:**
1. Calculate content hash from normalized text
2. Check if content hash already exists in registry
3. If exists, reject submission and identify first registered submission
4. If new, register content hash and allow submission

### 2. Redundancy Detection

L2 uses the RAG API to check for **highly similar content**:
- Queries knowledge base for similar documents
- Calculates similarity scores
- Rejects if similarity ≥ 85% (configurable threshold)

**Redundancy Check Process:**
1. Query RAG API with submission content
2. Get similarity scores from knowledge base
3. If similarity ≥ threshold, reject as redundant
4. Provide details about similar submissions

### 3. First Registered Priority

**Key Rule**: Only the **first registered submission** receives tokens.

- First submission with unique content → Gets tokens
- Duplicate submissions → Rejected, no tokens
- Redundant submissions → Rejected, no tokens

## Registry Storage

The submissions registry is stored in:
```
test_outputs/l2_submissions_registry.json
```

Contains:
- All registered submissions
- Content hashes mapped to first submission
- Timestamps and metadata

## Configuration

### Redundancy Threshold

Default: 85% similarity

To change, modify in `layer2/pod_server.py`:
```python
self.redundancy_threshold = 0.85  # 85% similarity = redundant
```

## User Experience

### Duplicate Submission

When a duplicate is detected:
```
✗ Evaluation failed: Exact duplicate of submission abc123...
  Reason: This submission is a duplicate. Only the first registered submission receives tokens.
  First registered: abc123...
```

### Redundant Submission

When redundancy is detected:
```
✗ Evaluation failed: Highly similar to existing content (similarity: 87.50%)
  Reason: This submission is redundant (similarity: 87.50%). Only the first registered submission receives tokens.
```

### First Registered Submission

When first registered:
```
✓ First registered submission - eligible for tokens
```

## Benefits

1. **Prevents Double Rewards**: Same content can't be rewarded twice
2. **Fair Distribution**: First contributor gets recognition
3. **Knowledge Base Integrity**: Prevents redundant entries
4. **Transparent Process**: Clear reasons for rejection

## Statistics

Get registry statistics:
```python
stats = pod_server.get_submissions_registry_stats()
# Returns:
# {
#   "total_registered": 150,
#   "unique_content_hashes": 145,
#   "duplicates_prevented": 5,
#   "last_updated": "2025-01-XX..."
# }
```

## Technical Details

### Content Hash Calculation

```python
def _calculate_content_hash(text: str) -> str:
    # Normalize: lowercase, remove extra whitespace
    normalized = " ".join(text.lower().split())
    return hashlib.sha256(normalized.encode()).hexdigest()
```

### Registry Structure

```json
{
  "submissions": {
    "hash1": {
      "title": "Paper Title",
      "content_hash": "abc123...",
      "timestamp": "2025-01-XX...",
      "category": "scientific",
      "status": "approved"
    }
  },
  "content_hashes": {
    "abc123...": "hash1"  // First submission with this content
  }
}
```

## Integration

The duplicate/redundancy checking is automatically integrated into:
- L2 PoD evaluation process
- Web UI submission flow
- CLI submission tool

No additional configuration needed - it works automatically!
