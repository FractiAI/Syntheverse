# Token Allocator

Calculates SYNTH token rewards based on Proof-of-Contribution (PoC) and Proof-of-Discovery (PoD) evaluation scores. Implements comprehensive tokenomics rules including tier multipliers, epoch bonuses, and allocation validation.

## Features

- **Tier-Based Rewards**: Gold (1000x), Silver (100x), Copper (1x) multipliers
- **Epoch Validation**: Ensures tier availability in qualified epochs
- **Allocation Calculation**: Precise token amount computation
- **State Integration**: Works with persistent tokenomics state
- **Comprehensive Logging**: Detailed allocation tracking

## Core Functionality

### Token Calculation

The allocator implements the core tokenomics formula:

```
Reward = (PoD Score / 10000) × Epoch Balance × Tier Multiplier
```

Where:
- **PoD Score**: 0-10000 based on coherence, density, novelty
- **Epoch Balance**: Available tokens in qualified epoch
- **Tier Multiplier**: Gold (1000x), Silver (100x), Copper (1x)

### Tier Availability

Different tiers are available in different epochs:

| Tier | Multiplier | Available Epochs |
|------|------------|------------------|
| Gold | 1000x | All epochs |
| Silver | 100x | Community, Ecosystem |
| Copper | 1x | Pioneer, Community, Ecosystem |

## Usage

### Basic Allocation

```python
from allocator.token_allocator import TokenAllocator

allocator = TokenAllocator(base_reward=100.0)

# Calculate reward for evaluation
result = allocator.calculate_reward({
    "scores": {"coherence": 8500, "density": 9000, "novelty": 8000},
    "overall_score": 8500,
    "tier": "gold"
}, epoch=1)

print(f"Allocated tokens: {result['total_tokens']}")
```

### Integration with Tokenomics State

```python
from layer2.tokenomics_state import TokenomicsState

# Initialize with tokenomics state
tokenomics = TokenomicsState()
allocator = TokenAllocator()

# Check allocation availability
allocation = tokenomics.calculate_allocation(
    pod_score=7429.0,
    epoch="founder",
    tier="gold"
)

if allocation["success"]:
    print(f"Reward: {allocation['reward']} SYNTH")
    print(f"Epoch balance after: {allocation['epoch_balance_after']}")
```

## Components

### TokenAllocator Class

Core allocation logic:

- **`calculate_reward()`**: Main reward calculation method
- **`_calculate_bonuses()`**: Applies evaluation-based bonuses
- **`_validate_evaluation_input()`**: Input validation and error handling
- **`get_allocation_summary()`**: Detailed allocation reporting

### Allocation Results

Returns comprehensive allocation data:

```python
{
    "success": true,
    "total_tokens": 29910000000000.0,
    "breakdown": {
        "base_tokens": 29910000000.0,
        "bonuses": {...},
        "epoch_bonus": 2991000000.0
    },
    "tier": "gold",
    "epoch": 1,
    "metadata": {...}
}
```

## Tokenomics Rules

### Base Calculation

1. **PoD Score Validation**: Ensures score is within 0-10000 range
2. **Tier Validation**: Verifies tier availability for epoch
3. **Balance Checking**: Confirms sufficient epoch tokens available

### Bonus System

- **Novelty Bonus**: Additional rewards for high novelty scores
- **Significance Bonus**: Extra tokens for significant contributions
- **Epoch Bonus**: Decreasing bonus for early epoch participation

### Epoch Progression

- **Founder**: 45T tokens, Gold only
- **Pioneer**: 22.5T tokens, Gold + Copper
- **Community**: 11.25T tokens, Gold + Silver + Copper
- **Ecosystem**: 11.25T tokens, Gold + Silver + Copper

## Integration

### With Layer 2 Systems

- **PoC Server**: Receives allocation requests for multi-metal contributions
- **PoD Server**: Legacy allocation for single-tier contributions
- **Tokenomics State**: Persistent storage of epoch balances and history

### With Layer 1 Blockchain

- **Allocation Validation**: Ensures allocations don't exceed available balances
- **Transaction Preparation**: Formats allocations for blockchain submission
- **Balance Updates**: Triggers epoch balance reductions after confirmation

## File Structure

```
allocator/
├── token_allocator.py    # Main allocation logic
└── README.md            # This file
```

## Error Handling

### Validation Errors

- **Invalid Scores**: PoD scores outside 0-10000 range
- **Tier Unavailable**: Requested tier not available in epoch
- **Insufficient Balance**: Allocation exceeds epoch token supply

### Calculation Errors

- **Division by Zero**: Protected against invalid epoch values
- **Negative Results**: All allocations clamped to non-negative values
- **Type Errors**: Comprehensive input type validation

## Logging

### Allocation Tracking

- **Calculation Details**: Logs each allocation computation
- **Tier Validation**: Records tier availability checks
- **Balance Changes**: Tracks epoch balance modifications

### Error Reporting

- **Validation Failures**: Detailed error messages for failed allocations
- **Calculation Issues**: Logs computational problems with context
- **Integration Errors**: Reports issues with external system communication

## Testing

### Unit Tests

```bash
# Test allocation calculations
python -m pytest tests/test_token_allocator.py -v

# Test tier validation
python -m pytest tests/test_tier_availability.py -v
```

### Integration Tests

```bash
# Test with tokenomics state
python -m pytest tests/test_allocation_integration.py -v

# Test epoch transitions
python -m pytest tests/test_epoch_allocation.py -v
```

## Performance

- **Calculation Speed**: Sub-millisecond per allocation
- **Memory Usage**: Minimal memory footprint
- **Concurrent Access**: Thread-safe allocation calculations

## Best Practices

### Allocation Strategy

1. **Validate First**: Check tier availability before calculation
2. **Balance Verification**: Confirm sufficient epoch tokens
3. **Error Handling**: Implement comprehensive error recovery
4. **Logging**: Maintain detailed allocation audit trails

### Integration Guidelines

1. **State Synchronization**: Keep tokenomics state updated
2. **Transaction Batching**: Group multiple allocations efficiently
3. **Rollback Support**: Implement allocation reversal capabilities
4. **Monitoring**: Track allocation patterns and anomalies

## Configuration

### Base Reward Settings

```python
# Initialize with custom base reward
allocator = TokenAllocator(base_reward=1000.0)
```

### Tokenomics Parameters

```python
# Custom tokenomics rules
allocator.tokenomics = {
    "base_multiplier": 1.0,
    "novelty_bonus": 0.3,      # Reduced bonus
    "significance_bonus": 0.4, # Adjusted bonus
    "epoch_bonus": 0.2,        # Increased epoch bonus
}
```

## Future Enhancements

- **Dynamic Bonuses**: ML-based bonus calculation
- **Community Voting**: Allocation influence mechanisms
- **Staking Integration**: Allocation multipliers for stakers
- **Cross-Epoch Transfers**: Token movement between epochs</content>
</xai:function_call name="read_lints">
<parameter name="target_file">src/core/layer2/allocator/README.md





