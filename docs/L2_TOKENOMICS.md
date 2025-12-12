# Layer 2 Tokenomics State Management

## Overview

Layer 2 (L2) now maintains **persistent tokenomics memory** that tracks:
- Epoch balances and distributions
- Coherence density totals
- Allocation history
- Contributor balances
- Tier availability rules

This allows L2 to make informed allocation decisions based on:
- **Token availability** in each epoch
- **Coherence density** for halving calculations
- **Contribution type** (scientific/tech/alignment) for tier determination

## Tokenomics State Manager

### File: `layer2/tokenomics_state.py`

The `TokenomicsState` class maintains persistent state in:
- **State file**: `test_outputs/l2_tokenomics_state.json`

### State Structure

```json
{
  "epoch_balances": {
    "founder": 45000000000000,
    "pioneer": 9000000000000,
    "community": 18000000000000,
    "ecosystem": 18000000000000
  },
  "total_coherence_density": 125000.0,
  "founder_halving_count": 0,
  "current_epoch": "founder",
  "epoch_progression": {
    "founder": false,
    "pioneer": false,
    "community": false,
    "ecosystem": false
  },
  "allocation_history": [...],
  "contributor_balances": {
    "researcher-001": 1234567.89
  },
  "last_updated": "2025-01-XX..."
}
```

## Key Features

### 1. Persistent Memory
- State automatically saved after each update
- State loaded on initialization
- Survives server restarts

### 2. Allocation Calculation
L2 calculates allocations **before** sending to L1:
- Checks tier availability in epoch
- Verifies token availability
- Calculates reward with tier multipliers
- Returns allocation preview

### 3. Coherence Density Tracking
- Tracks total coherence density across all submissions
- Automatically triggers Founder epoch halving at 1M intervals
- Updates halving count and epoch balances

### 4. State Synchronization
- Can sync from L1 to keep state aligned
- Maintains independent view for allocation decisions
- Syncs epoch balances, coherence density, halving count

## Integration with PoD Server

### Evaluation Flow

1. **Evaluate Submission**
   - L2 evaluates PDF using RAG API
   - Gets scores (coherence, density, novelty)

2. **Calculate PoD Score**
   - Uses tokenomics state to calculate PoD score
   - Determines qualified epoch based on density

3. **Calculate Allocation**
   - Checks tier availability in epoch
   - Verifies token availability
   - Calculates reward with tier multiplier
   - Returns allocation preview

4. **Record Allocation**
   - After L1 confirms allocation
   - Updates epoch balances
   - Updates contributor balances
   - Updates coherence density
   - Records in allocation history

### Allocation Decision Logic

```python
# L2 checks availability before allocation
allocation = tokenomics.calculate_allocation(
    pod_score=pod_score,
    epoch=qualified_epoch,
    tier=contribution_tier
)

# Returns:
{
    "success": true/false,
    "available": true/false,
    "epoch": "founder",
    "tier": "gold",
    "reward": 1234567.89,
    "epoch_balance_before": 45000000000000,
    "epoch_balance_after": 43765432109832
}
```

## Allocation Based on Contribution Type

### Scientific Contributions (Gold Tier)
- **Multiplier**: 1000x
- **Available in**: All epochs
- **Decision**: Highest reward potential

### Tech Contributions (Silver Tier)
- **Multiplier**: 100x
- **Available in**: Community, Ecosystem only
- **Decision**: Moderate reward, limited epochs

### Alignment Contributions (Copper Tier)
- **Multiplier**: 1x
- **Available in**: Pioneer, Community, Ecosystem
- **Decision**: Base reward, not available in Founder

## Coherence Density Impact

L2 tracks coherence density to:
1. **Trigger halving**: Founder epoch halves every 1M coherence density
2. **Track progression**: Monitor total structural knowledge contribution
3. **Epoch transitions**: Inform epoch unlock decisions

## State Persistence

### Automatic Saving
- State saved after each allocation
- State saved after coherence density updates
- State saved after synchronization

### State File Location
- Default: `test_outputs/l2_tokenomics_state.json`
- Configurable via `TokenomicsState` constructor

## API Methods

### TokenomicsState

- `calculate_allocation(pod_score, epoch, tier)` - Calculate allocation
- `record_allocation(submission_hash, contributor, allocation, coherence)` - Record allocation
- `update_coherence_density(coherence)` - Update density tracking
- `get_statistics()` - Get tokenomics statistics
- `get_epoch_info()` - Get epoch information
- `sync_from_l1(l1_state)` - Sync from L1

### PODServer

- `evaluate_submission(...)` - Evaluate and calculate allocation
- `record_allocation(...)` - Record allocation in state
- `get_tokenomics_statistics()` - Get statistics
- `get_epoch_info()` - Get epoch info
- `sync_from_l1(l1_token_stats)` - Sync from L1

## Usage Example

```python
from layer2.pod_server import PODServer

# Initialize server (creates tokenomics state)
server = PODServer()

# Evaluate submission (calculates allocation)
result = server.evaluate_submission(
    submission_hash="abc123",
    title="Research Paper",
    pdf_path="/path/to/paper.pdf",
    category="scientific"
)

# Allocation preview included in report
allocation = result["report"]["allocation"]
if allocation["success"]:
    print(f"Reward: {allocation['reward']:,.2f} SYNTH")
    print(f"Epoch: {allocation['epoch']}")
    print(f"Tier: {allocation['tier']}")

# After L1 confirms, record allocation
server.record_allocation(
    submission_hash="abc123",
    contributor="researcher-001",
    coherence=8500.0
)

# Get statistics
stats = server.get_tokenomics_statistics()
print(f"Total Remaining: {stats['total_remaining']:,.2f} SYNTH")
print(f"Coherence Density: {stats['total_coherence_density']:,.2f}")
```

## Benefits

1. **Informed Decisions**: L2 knows token availability before allocation
2. **Persistent State**: Survives restarts, maintains history
3. **Coherence Tracking**: Monitors structural knowledge contribution
4. **Tier Awareness**: Understands tier availability in epochs
5. **Independent View**: Can make decisions without querying L1
6. **Synchronization**: Can sync with L1 when needed

## State File Structure

The state file contains:
- Epoch balances (current available tokens)
- Coherence density (total accumulated)
- Halving count (Founder epoch halvings)
- Allocation history (last 1000 allocations)
- Contributor balances (per-contributor totals)
- Epoch progression (which epochs are unlocked)

All data persists across server restarts and is automatically updated.

