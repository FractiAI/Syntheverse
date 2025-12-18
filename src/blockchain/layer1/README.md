# Layer 1 - Syntheverse Blockchain

Blockchain implementation for Proof-of-Discovery (POD) protocol and SYNTH token management with epoch-based distribution and tier rewards.

## Status

✅ **Implemented** - Full Layer 1 blockchain with epochs, tiers, and token distribution.

## Architecture

### Core Components

1. **Blockchain** (`blockchain.py`)
   - Block structure with Proof-of-Discovery scoring
   - Transaction system with multiple transaction types
   - Chain validation and consensus

2. **SYNTH Token Contract** (`contracts/synth_token.py`)
   - Total Supply: 90 Trillion SYNTH tokens
   - Epoch-based distribution (Founder, Pioneer, Community, Ecosystem)
   - Tier multipliers (Gold: 1000x, Silver: 100x, Copper: 1.0x)
   - Founder epoch halving mechanism

3. **POD Contract** (`contracts/pod_contract.py`)
   - Proof-of-Discovery submission management
   - Automatic tier assignment based on category
   - Epoch qualification based on density scores
   - Token allocation integration

4. **Epoch Manager** (`epoch_manager.py`)
   - Epoch progression management
   - Automatic epoch transitions based on coherence density
   - Epoch unlock thresholds

5. **Blockchain Node** (`node.py`)
   - Full node implementation
   - Transaction processing
   - Block mining
   - State persistence

## Epochs

The Syntheverse blockchain uses 4 epochs for token distribution:

| Epoch | Distribution | Threshold | Description |
|-------|-------------|-----------|-------------|
| **Founder** | 45T (50%) | Density ≥ 8,000 | Highest quality contributions |
| **Pioneer** | 9T (10%) | Density ≥ 6,000 | Early high-quality contributions |
| **Community** | 18T (20%) | Density ≥ 4,000 | Community contributions |
| **Ecosystem** | 18T (20%) | Density < 4,000 | All other contributions |

### Epoch Progression

- Founder epoch starts immediately
- Pioneer epoch unlocks at 1M coherence density units
- Community epoch unlocks at 2M coherence density units
- Ecosystem epoch unlocks at 3M coherence density units

### Founder Epoch Halving

The Founder epoch pool halves every 1M coherence density units:
- Initial: 45T
- After 1M: 22.5T
- After 2M: 11.25T
- And so on...

## Contribution Tiers

Three tiers determine reward multipliers and epoch availability:

| Tier | Multiplier | Available Epochs | Category | Description |
|------|-----------|------------------|----------|-------------|
| **Gold** | 1000x | All epochs | Scientific | Scientific research contributions |
| **Silver** | 100x | Community, Ecosystem | Tech | Technology and engineering contributions |
| **Copper** | 1x | Pioneer, Community, Ecosystem | Alignment | AI alignment and safety contributions |

### Tier Availability by Epoch

- **Gold**: Available in all epochs (Founder, Pioneer, Community, Ecosystem)
- **Silver**: Available only in Community and Ecosystem epochs
- **Copper**: Available in Pioneer, Community, and Ecosystem epochs (not Founder)

Tier is automatically assigned based on submission category:
- `"scientific"`, `"science"`, `"research"` → Gold
- `"tech"`, `"technology"`, `"technical"`, `"engineering"` → Silver
- `"alignment"`, `"ai-alignment"`, `"safety"` → Copper

**Note**: If a submission qualifies for an epoch where its tier is not available, token allocation will fail with an appropriate error message.

## Proof-of-Discovery (PoD) Score

PoD Score calculation:
```
PoD Score = (coherence/10000) × (density/10000) × (novelty/10000) × 10000
```

### Reward Calculation

```
Reward = (PoD Score / 10000) × available epoch balance × tier multiplier
```

## Usage

### Basic Example

```python
from layer1.node import SyntheverseNode

# Initialize node
node = SyntheverseNode(node_id="node-001")

# Submit a POD
submission = {
    "title": "Novel Discovery",
    "description": "A significant finding",
    "category": "scientific",  # Will be assigned Gold tier
    "contributor": "researcher-001",
    "evidence": "Research paper",
}

result = node.submit_pod(submission)
submission_hash = result["submission_hash"]

# Evaluate submission
evaluation = {
    "coherence": 8500.0,
    "density": 9000.0,  # Qualifies for Founder epoch
    "novelty": 8000.0,
    "status": "approved",
}

node.evaluate_pod(submission_hash, evaluation)

# Allocate tokens
allocation = node.allocate_tokens(submission_hash)
print(f"Allocated: {allocation['allocation']['reward']} SYNTH")
print(f"Epoch: {allocation['allocation']['epoch']}")
print(f"Tier: {allocation['allocation']['tier']}")

# Mine block
block = node.mine_block(pod_score=7500.0)
```

### Running Example

```bash
cd layer1
python example_usage.py
```

## File Structure

```
layer1/
├── __init__.py              # Package initialization
├── blockchain.py            # Core blockchain implementation
├── node.py                  # Blockchain node
├── epoch_manager.py         # Epoch management
├── example_usage.py         # Usage examples
├── requirements.txt         # Dependencies
├── README.md               # This file
└── contracts/
    ├── __init__.py
    ├── synth_token.py      # SYNTH token contract
    └── pod_contract.py     # POD contract
```

## Data Persistence

The node automatically saves state to `data/blockchain/`:
- `blockchain.json` - Blockchain state
- `synth_token.json` - Token contract state
- `pod_contract.json` - POD contract state

State is automatically loaded on node initialization.

## Integration with Layer 2

The Layer 1 blockchain receives:
- POD submissions from Layer 2 evaluator
- Evaluation results with scores
- Token allocation instructions

The blockchain handles:
- Transaction recording
- Block creation
- Token distribution
- Epoch management

## API Reference

### SyntheverseNode

#### Methods

- `submit_pod(submission: Dict) -> Dict` - Submit POD submission
- `evaluate_pod(submission_hash: str, evaluation: Dict) -> Dict` - Record evaluation
- `allocate_tokens(submission_hash: str) -> Dict` - Allocate tokens
- `mine_block(pod_score: float) -> Block` - Mine pending transactions
- `get_node_status() -> Dict` - Get comprehensive node status
- `get_blockchain_info() -> Dict` - Get blockchain information
- `get_token_statistics() -> Dict` - Get token statistics
- `get_epoch_info() -> Dict` - Get epoch information
- `get_pod_statistics() -> Dict` - Get POD statistics

## Testing

Run the example script to test the implementation:

```bash
python example_usage.py
```

This will:
1. Initialize a node
2. Submit PODs in all three tiers
3. Evaluate and allocate tokens
4. Mine blocks
5. Display comprehensive statistics

## Next Steps

- [ ] Network consensus (multi-node)
- [ ] P2P networking
- [ ] Block synchronization
- [ ] Consensus mechanisms
- [ ] Governance voting
- [ ] Staking mechanisms
