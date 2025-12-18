# Layer 1 (L1) Explanation

## What Layer 1 Does

Layer 1 is the **Syntheverse Blockchain** - the foundational blockchain layer that:
1. **Stores immutable records** of all Proof-of-Contribution (PoC) submissions
2. **Manages SYNTH token distribution** across 4 epochs (Founder, Pioneer, Community, Ecosystem)
3. **Enforces tier-based rewards** (Gold: 1000x, Silver: 100x, Copper: 1x)
4. **Validates and mines blocks** containing PoC transactions
5. **Tracks epoch progression** and token balances
6. **Maintains contributor balances** and reward history

## L1 Inputs

### 1. PoC Submissions
```python
{
    "title": "Paper Title",
    "description": "Description",
    "category": "scientific|tech|alignment",
    "contributor": "contributor-address",
    "evidence": "PDF path or content"
}
```

### 2. PoC Evaluations (from Layer 2)
```python
{
    "coherence": 8500.0,  # 0-10000
    "density": 9000.0,     # 0-10000
    "novelty": 8000.0,     # 0-10000
    "status": "approved|rejected"
}
```

### 3. Token Allocation Requests
- Automatic after evaluation approval
- Based on PoD score, epoch qualification, and tier

## L1 Outputs

### 1. Submission Records
- Submission hash (unique identifier)
- Transaction hash
- Block number (when mined)
- Status (pending, approved, rejected)

### 2. Token Allocations
```python
{
    "success": true,
    "allocation": {
        "submission_hash": "...",
        "recipient": "contributor-address",
        "pod_score": 7429.0,
        "epoch": "founder",
        "tier": "gold",
        "reward": 1234567.89,  # SYNTH tokens
        "timestamp": "2025-01-XX..."
    }
}
```

### 3. Blockchain State
- Block chain with all transactions
- Epoch balances and status
- Contributor balances
- Reward history

### 4. Statistics
- Total submissions
- Approved/rejected counts
- Token distribution by epoch and tier
- Epoch progression status

## L1 Processing Flow

```
1. Submit PoC → L1 stores submission, creates transaction
2. Evaluate PoC → L2 evaluates, sends results to L1
3. L1 calculates PoC score → (coherence × density × novelty) / 10000² × 10000
4. L1 determines epoch → Based on density threshold
5. L1 checks tier availability → Gold/Silver/Copper in allowed epochs
6. L1 calculates reward → (PoC Score / 10000) × epoch balance × tier multiplier
7. L1 allocates tokens → Updates balances, records reward
8. L1 mines block → Includes all transactions
```

## Key L1 Functions

- **submit_poc()**: Accepts PoC submission, creates transaction
- **evaluate_poc()**: Records evaluation results, calculates PoC score
- **allocate_tokens()**: Allocates SYNTH tokens based on score/epoch/tier
- **mine_block()**: Mines pending transactions into a block
- **get_node_status()**: Returns comprehensive blockchain state

## Epoch System

| Epoch | Supply | Density Threshold | Tier Availability |
|-------|--------|------------------|------------------|
| Founder | 45T | ≥ 8,000 | Gold only |
| Pioneer | 9T | ≥ 6,000 | Gold, Copper |
| Community | 18T | ≥ 4,000 | Gold, Silver, Copper |
| Ecosystem | 18T | < 4,000 | Gold, Silver, Copper |

## Tier Multipliers

- **Gold** (Scientific): 1000x multiplier, all epochs
- **Silver** (Tech): 100x multiplier, Community/Ecosystem only
- **Copper** (Alignment): 1x multiplier, Pioneer/Community/Ecosystem

