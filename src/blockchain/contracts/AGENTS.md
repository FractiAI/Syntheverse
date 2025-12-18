# Smart Contracts Agents

## Purpose

Solidity smart contracts for Syntheverse PoC system, designed to deploy on Base Layer 2. Manages SYNTH token and PoC contribution registry.

## Key Modules

### Contracts (`src/`)

- **`SYNTH.sol`**: Internal accounting token (non-transferable, ERC-20 compatible)
- **`POCRegistry.sol`**: Contribution management and certificate registration

### Deployment (`deploy/`)

- **`01_deploy_SYNTH.cjs`**: SYNTH token deployment script
- **`02_deploy_POCRegistry.cjs`**: POCRegistry deployment script

### Testing (`test/`)

- **`SYNTH.t.sol`**: Foundry tests for SYNTH token
- **`hardhat/`**: Hardhat test files

## Integration Points

- **Foundry**: Development and testing framework
- **Hardhat**: Deployment scripts and network management
- **Anvil**: Local Ethereum node for testing
- **Base Network**: Target deployment network
- **Frontend**: Web3 integration for user interactions

## Development Guidelines

### Contract Development

- Use Solidity ^0.8.19
- Follow OpenZeppelin patterns
- Implement comprehensive tests
- Use Foundry for fast development
- Security audit before mainnet

### Deployment

- Test on Anvil (local) first
- Deploy to Base Sepolia (testnet)
- Verify contracts on block explorer
- Document deployment addresses

### Security

- Use OpenZeppelin contracts
- Implement access control
- Validate all inputs
- Protect against reentrancy
- Use SafeMath or Solidity 0.8+

## Common Patterns

- Non-transferable token pattern
- Registry pattern for contributions
- Tiered fee structure
- Epoch-based token distribution
- Certificate registration with blockchain verification

## Blueprint Alignment

### Core Contract Implementation
- **Blueprint §1.4**: "On-Chain Registration: 'I Was Here First'" → `POCRegistry.sol` certificate registration
- **Blueprint §4.1**: "$200 per approved PoC" registration fee → Fee structure in smart contracts
- **Blueprint §3.3**: "90T total, distributed in Gold, Silver, Copper" → `SYNTH.sol` token mechanics
- **Blueprint §6**: "ERC-20 SYNTH allocations and PoC scores auditable on-chain" → Transparent token distribution

### Fee Structure Implementation
- **Blueprint §4.1**: $200 per approved PoC registration → Implemented in `POCRegistry.sol`
- **Blueprint §4.1**: Submissions free for evaluation → Evaluation costs not on-chain
- **Verification Needed**: Confirm $200 fee is correctly implemented and matches Blueprint

### Token System Alignment
- **Blueprint §3.3**: 90T SYNTH total supply → `SYNTH.sol` total supply implementation
- **Blueprint §3.3**: Epoch-based distribution (Founder 50%, Pioneer 25%, etc.) → Epoch logic in contracts
- **Blueprint §6**: Non-transferable internal accounting → `SYNTH.sol` non-transferable design
- **Blueprint §6**: On-chain auditability → Transparent contract state

### Security & Governance
- **Blueprint §6**: "Human Approval for all PoCs" → Contract requires approved submissions only
- **Blueprint §6**: "Operator-Controlled Epochs & Thresholds" → Owner controls for epoch management
- **Blueprint §6**: "Transparency: ERC-20 SYNTH allocations... auditable on-chain" → Public view functions

### Status & Critical Verification
- **✅ Confirmed**: Smart contract architecture, Base deployment, Foundry development stack
- **🟡 Critical Verification**: Fee structure implementation ($200 registration fee)
- **🟡 Critical Verification**: Token supply and epoch distribution percentages
- **📋 Testing Required**: Blueprint validation tests for fee collection and token allocation

### Integration Points
- **Layer 2**: Receives evaluation results and triggers token allocations
- **Frontend**: Web3 integration for user registration and fee payment
- **Base Network**: Primary deployment target with low-cost transactions
- **Anvil**: Local testing environment for development workflow

## File Structure

```
contracts/
├── src/
│   ├── SYNTH.sol              # Internal accounting token
│   └── POCRegistry.sol        # Contribution registry
├── test/
│   ├── SYNTH.t.sol            # Foundry tests
│   └── hardhat/               # Hardhat test files
├── script/
│   └── Deploy.s.sol           # Deployment scripts
├── deploy/
│   ├── 01_deploy_SYNTH.cjs    # SYNTH deployment
│   └── 02_deploy_POCRegistry.cjs # Registry deployment
├── lib/
│   └── openzeppelin-contracts/ # Security libraries
└── foundry.toml               # Foundry configuration
```

## Cross-References

- **Parent**: [blockchain/AGENTS.md](../AGENTS.md) - Blockchain infrastructure
- **Related**:
  - [layer1/AGENTS.md](../layer1/AGENTS.md) - Python blockchain implementation
  - [config/wallet/AGENTS.md](../../config/wallet/AGENTS.md) - Wallet configuration
  - [scripts/deployment/AGENTS.md](../../scripts/deployment/AGENTS.md) - Deployment scripts




