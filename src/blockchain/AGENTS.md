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








