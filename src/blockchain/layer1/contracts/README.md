# Contract Interfaces

Python implementations of Syntheverse smart contract logic for Layer 1 blockchain operations. Provides contract interfaces for SYNTH token management, contribution registration, and epoch-based distribution.

## Overview

These Python classes implement the business logic of the Solidity smart contracts, providing:

- **SYNTH Token Contract**: ERC20-like token with epoch-based distribution
- **PoC Contract**: Proof-of-Contribution registration and validation
- **PoD Contract**: Legacy Proof-of-Discovery contract interface

## Components

### SYNTH Token Contract (`synth_token.py`)

Core token contract implementation:

- **Total Supply**: 90 trillion SYNTH tokens
- **Epoch Distribution**: Founder (50%), Pioneer (10%), Community (20%), Ecosystem (20%)
- **Tier Multipliers**: Gold (1000x), Silver (100x), Copper (1x)
- **Epoch Thresholds**: Density-based epoch qualification

#### Key Features

```python
from contracts.synth_token import SYNTHToken

token = SYNTHToken()

# Check epoch balance
balance = token.get_epoch_balance(Epoch.FOUNDER)  # Returns 45T

# Calculate allocation
allocation = token.calculate_allocation(
    pod_score=7429,
    epoch=Epoch.FOUNDER,
    tier=ContributionTier.GOLD
)
```

### PoC Contract (`poc_contract.py`)

Proof-of-Contribution registration contract:

- **Multi-Metal Support**: Gold, Silver, Copper contributions
- **Archive-First Integration**: References contribution archive
- **Certificate Registration**: On-chain contribution certificates
- **Fee Structure**: Progressive fee system

### PoD Contract (`pod_contract.py`)

Legacy Proof-of-Discovery contract:

- **Single-Tier Support**: Traditional PoD submissions
- **Evaluation Integration**: Links to Layer 2 evaluation results
- **Token Allocation**: Direct allocation based on scores
- **Backward Compatibility**: Maintains existing PoD functionality

## Contract Architecture

### Tokenomics Structure

```
Total Supply: 90,000,000,000,000 SYNTH

Epoch Distribution:
├── Founder: 45T (50%) - Gold only, density ≥8000
├── Pioneer: 9T (10%) - Gold + Copper, density ≥6000
├── Community: 18T (20%) - All tiers, density ≥4000
└── Ecosystem: 18T (20%) - All tiers, density <4000

Tier Multipliers:
├── Gold: 1000x - Scientific contributions
├── Silver: 100x - Technology contributions
└── Copper: 1x - Alignment contributions
```

### Allocation Formula

```python
reward = (pod_score / 10000) × epoch_balance × tier_multiplier
```

Example: PoD score 7429, Founder epoch, Gold tier
```
reward = (7429/10000) × 45,000,000,000,000 × 1000 = ~33.5T SYNTH
```

## Usage

### Basic Token Operations

```python
from contracts.synth_token import SYNTHToken, Epoch, ContributionTier

token = SYNTHToken()

# Check epoch status
epoch_info = token.get_epoch_info(Epoch.FOUNDER)
print(f"Balance: {epoch_info['balance']}")
print(f"Available Tiers: {epoch_info['available_tiers']}")

# Calculate allocation
allocation = token.calculate_allocation(
    pod_score=8500,
    epoch=Epoch.FOUNDER,
    tier=ContributionTier.GOLD
)

print(f"Reward: {allocation['reward']}")
print(f"New Balance: {allocation['new_balance']}")
```

### Contribution Registration

```python
from contracts.poc_contract import POCContract

poc = POCContract()

# Register contribution
certificate = poc.register_contribution({
    "submission_hash": "abc123...",
    "contributor": "researcher-001",
    "metals": ["gold", "silver"],
    "allocations": [...],
    "timestamp": "2025-01-XX..."
})

print(f"Certificate ID: {certificate['id']}")
print(f"Transaction Hash: {certificate['tx_hash']}")
```

## Integration with Layer 1

### Blockchain Integration

These contract interfaces integrate with the Layer 1 blockchain:

- **Transaction Creation**: Generate blockchain transactions
- **State Updates**: Update contract state after allocations
- **Balance Tracking**: Maintain accurate token balances
- **Validation**: Verify allocation compliance with contract rules

### File-Based Persistence

For the test implementation, contracts use JSON file persistence:

```
test_outputs/
├── blockchain/
│   ├── blockchain.json     # Chain state
│   ├── synth_token.json    # Token balances
│   └── poc_registry.json   # Contribution registry
```

## Contract Methods

### SYNTH Token

- **`get_epoch_balance(epoch)`**: Get current epoch token balance
- **`calculate_allocation(pod_score, epoch, tier)`**: Calculate token reward
- **`allocate_tokens(allocation)`**: Execute token allocation
- **`get_epoch_info(epoch)`**: Get comprehensive epoch information
- **`validate_tier_availability(tier, epoch)`**: Check tier availability

### PoC Contract

- **`register_contribution(contribution_data)`**: Register new contribution
- **`get_contribution(contribution_id)`**: Retrieve contribution details
- **`verify_contribution(contribution_id)`**: Verify contribution validity
- **`get_contribution_history(contributor)`**: Get contributor history

### PoD Contract

- **`submit_discovery(discovery_data)`**: Submit PoD discovery
- **`evaluate_discovery(discovery_id, evaluation)`**: Record evaluation
- **`allocate_pod_tokens(allocation)`**: Allocate PoD tokens
- **`get_discovery_status(discovery_id)`**: Get discovery status

## Error Handling

### Validation Errors

- **Invalid Epoch**: Epoch not recognized or not active
- **Tier Unavailable**: Requested tier not available in epoch
- **Insufficient Balance**: Allocation exceeds epoch token supply
- **Invalid Score**: PoD score outside valid range

### Contract Errors

- **State Corruption**: Contract state inconsistency
- **Transaction Failure**: Blockchain transaction rejection
- **Concurrency Issues**: Multiple allocations conflict
- **Data Validation**: Input data format errors

## Testing

### Unit Tests

```bash
# Test token calculations
python -m pytest tests/test_synth_token.py -v

# Test contract interactions
python -m pytest tests/test_contracts.py -v
```

### Integration Tests

```bash
# Test with Layer 1 blockchain
python -m pytest tests/test_layer1_integration.py -v

# Test allocation workflows
python -m pytest tests/test_allocation_flow.py -v
```

## Configuration

### Token Distribution

The epoch distribution can be modified in `synth_token.py`:

```python
EPOCH_DISTRIBUTION = {
    Epoch.FOUNDER: 0.50,    # 50%
    Epoch.PIONEER: 0.10,    # 10%
    Epoch.COMMUNITY: 0.20,  # 20%
    Epoch.ECOSYSTEM: 0.20,  # 20%
}
```

### Tier Multipliers

Tier reward multipliers can be adjusted:

```python
TIER_MULTIPLIERS = {
    ContributionTier.GOLD: 1000.0,
    ContributionTier.SILVER: 100.0,
    ContributionTier.COPPER: 1.0,
}
```

## File Structure

```
contracts/
├── __init__.py
├── synth_token.py     # SYNTH token contract
├── poc_contract.py    # PoC registration contract
├── pod_contract.py    # PoD legacy contract
└── README.md         # This file
```

## Performance

- **Calculation Speed**: Sub-millisecond for allocation calculations
- **Memory Usage**: Minimal memory footprint
- **File I/O**: JSON-based persistence for test environment
- **Scalability**: Linear scaling with transaction volume

## Best Practices

### Allocation Logic

1. **Validate First**: Check tier availability and balance before calculation
2. **Atomic Operations**: Ensure allocation and balance update consistency
3. **Error Recovery**: Implement rollback mechanisms for failed allocations
4. **Audit Logging**: Maintain comprehensive allocation audit trails

### Contract Management

1. **State Consistency**: Keep contract state synchronized with blockchain
2. **Input Validation**: Validate all inputs before contract operations
3. **Security**: Implement access controls and validation checks
4. **Testing**: Comprehensive testing of all contract methods

## Future Enhancements

- **Smart Contract Migration**: Deploy to actual blockchain networks
- **Multi-Token Support**: Support for additional reward tokens
- **Dynamic Tokenomics**: ML-based token distribution adjustment
- **Governance Integration**: Community voting on tokenomics parameters
- **Cross-Chain Support**: Multi-blockchain deployment capability</content>
</xai:function_call name="read_lints">
<parameter name="target_file">src/blockchain/layer1/contracts/README.md





