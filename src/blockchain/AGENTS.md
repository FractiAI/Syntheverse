# Blockchain Agents

## Purpose

The `blockchain/` directory contains blockchain infrastructure including smart contracts and Layer 1 implementation.

## Key Modules

### Smart Contracts (`contracts/`)

Solidity contracts deployed on Base:
- **`SYNTH.sol`**: Internal accounting token (non-transferable)
- **`POCRegistry.sol`**: Contribution registry with tiered fees

**Development Stack:**
- Foundry + Anvil for local development
- Hardhat for deployment scripts
- OpenZeppelin contracts for security

### Layer 1 (`layer1/`)

Python implementation of blockchain logic:
- **`blockchain.py`**: Core blockchain structure
- **`node.py`**: Blockchain node implementation
- **`epoch_manager.py`**: Epoch progression management
- **`contracts/`**: Python contract interfaces

## Integration Points

- Smart contracts deployed on Base Layer 2
- Layer 1 Python code provides blockchain logic
- Layer 2 sends evaluation results to Layer 1
- Frontend connects via Web3 for registration
- PoC API bridges frontend to blockchain

## Development Guidelines

### Smart Contracts

- Follow Solidity best practices
- Use OpenZeppelin contracts
- Implement comprehensive tests
- Security audit before mainnet

### Layer 1 Python

- File-based state persistence
- Epoch-based token distribution
- Integration with Layer 2 evaluator
- Node interface for blockchain operations

## Common Patterns

- Epoch system: Founder, Pioneer, Community, Ecosystem
- Tier multipliers: Gold (1000x), Silver (100x), Copper (1x)
- Fee structure: First 3 free, then $50 per certificate
- Non-transferable tokens for internal accounting

## File Structure

```
blockchain/
├── contracts/                  # Solidity smart contracts
│   ├── src/
│   │   ├── SYNTH.sol          # Internal accounting token
│   │   └── POCRegistry.sol    # Contribution registry
│   ├── test/                  # Contract tests
│   ├── script/                # Deployment scripts
│   ├── lib/                   # Dependencies (OpenZeppelin)
│   └── foundry.toml           # Foundry configuration
├── layer1/                     # Python blockchain implementation
│   ├── blockchain.py          # Core blockchain logic
│   ├── node.py                # Node implementation
│   ├── epoch_manager.py       # Epoch management
│   ├── contracts/             # Python contract interfaces
│   └── requirements.txt       # Python dependencies
├── contract_interface.py      # Contract interaction utilities
├── wallet_integration.py      # Wallet management
└── web3_integration.py        # Web3 connection utilities
```

## Deployment & Testing

- **Local Development**: Foundry + Anvil
- **Test Network**: Base Sepolia
- **Main Network**: Base Mainnet
- **Testing**: Hardhat + Foundry tests

## Blueprint Alignment

### Layer 1 Blockchain Implementation ([Blueprint §3](docs/Blueprint for Syntheverse))
- **Syntheverse Blockmine L1**: `layer1/` implements the core blockchain logic for Base network integration
- **Smart Contracts**: `contracts/` contains SYNTH token and POCRegistry deployed on Base Layer 2
- **On-Chain Registration**: Permanent anchoring of approved PoCs with "I was here first" recognition

### PoC Registration Process ([Blueprint §1.4](docs/Blueprint for Syntheverse))
- **$200 Registration Fee**: Approved PoCs may be registered on-chain for permanent blockchain anchoring
- **Immutable Records**: Contributions become traceable, immutable building blocks of the Syntheverse AI
- **Early Contributor Recognition**: "I was here first" status ensures priority, visibility, and legacy
- **AI Training**: Registered PoCs train and evolve the Syntheverse AI ecosystem

### Financial Framework ([Blueprint §4](docs/Blueprint for Syntheverse))
- **Registration Fees**: $200 per approved PoC (submissions free for evaluation)
- **Free Evaluations**: Layer 2 evaluation engine processes all submissions at no cost
- **Alignment Contributions**: Foundation for Copper/Silver/Gold tier financial participation system

### Tokenomics Integration ([Blueprint §3.3](docs/Blueprint for Syntheverse))
- **SYNTH Token**: Internal ERC-20 accounting token for ecosystem rewards and allocations
- **Epoch-Based Distribution**: 90T total supply distributed across operator-controlled epochs
- **Non-Transferable**: Internal accounting token ensuring controlled ecosystem economics

### Governance & Operations ([Blueprint §6](docs/Blueprint for Syntheverse))
- **Human Oversight**: All PoCs require approval before on-chain registration
- **Operator Control**: Epoch progression and token allocation managed by ecosystem operators
- **Transparency**: All SYNTH allocations and PoC registrations auditable on-chain
- **Stewardship**: Founder-controlled with scalable FractiAI Team funding model

### Complete Workflow Implementation ([Blueprint §7](docs/Blueprint for Syntheverse))
1. **Zenodo Community**: Initial contribution submission and peer feedback
2. **Syntheverse Discovery**: Learning about blockchain anchoring possibilities
3. **PoC Evaluation**: Hydrogen holographic scoring through Layer 2 evaluation engine
4. **Human Approval**: Ecosystem alignment verification and qualification
5. **On-Chain Registration**: $200 payment for permanent blockchain anchoring
6. **"I Was Here First"**: Recognition, priority, and legacy establishment
7. **AI Integration**: Contribution becomes training data for evolving Syntheverse AI

### AI Training Integration ([Blueprint §5](docs/Blueprint for Syntheverse))
- **Archive Expansion**: Registered PoCs contribute to AI training dataset
- **Fractal Enhancement**: On-chain records expand hydrogen holographic awareness
- **Ecosystem Evolution**: Registered contributions reinforce and expand the regenerative system

### Implementation Status
- **✅ Operational**: Smart contracts deployed, Layer 1 logic implemented, registration process functional
- **🟡 Enhanced**: Fee structure validated, epoch management operational
- **📋 Complete**: Full Layer 1 blockchain registration system per Blueprint §1.4

## Cross-References

- **Blueprint Document**: [docs/Blueprint for Syntheverse](../../docs/Blueprint for Syntheverse) - Central system vision
- **Layer 1 Documentation**: [docs/L1_EXPLANATION.md](../../docs/L1_EXPLANATION.md) - Blockchain implementation details
- **Parent**: [src/AGENTS.md](../AGENTS.md) - Source code organization
- **Children**:
  - [contracts/AGENTS.md](contracts/AGENTS.md) - Smart contracts
  - [layer1/AGENTS.md](layer1/AGENTS.md) - Layer 1 implementation
- **Related**:
  - [api/poc-api/AGENTS.md](../api/poc-api/AGENTS.md) - API integration
  - [core/layer2/AGENTS.md](../core/layer2/AGENTS.md) - Layer 2 evaluation
  - [config/wallet/AGENTS.md](../../config/wallet/AGENTS.md) - Wallet configuration
  - [docs/POC_SUBMISSION_TO_ALLOCATION_FLOW.md](../../docs/POC_SUBMISSION_TO_ALLOCATION_FLOW.md) - Complete workflow

