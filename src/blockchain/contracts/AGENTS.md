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



