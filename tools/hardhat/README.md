# Hardhat Tools

Smart contract development and testing infrastructure for the Syntheverse blockchain Layer 1.

## Overview

This directory contains Hardhat configuration and scripts for developing, testing, and deploying Solidity smart contracts used in the Syntheverse ecosystem, including SYNTH token contracts and POC registry functionality.

## Quick Start

```bash
# Install dependencies
npm install

# Compile contracts
npx hardhat compile

# Run tests
npx hardhat test

# Start local network
npx hardhat node
```

## Configuration

The `hardhat.config.js` file contains:
- Network configurations (local, testnet, mainnet)
- Compiler settings for Solidity contracts
- Plugin configurations for testing and deployment
- Gas optimization settings

## Available Scripts

| Script | Description |
|--------|-------------|
| `compile` | Compile all Solidity contracts |
| `test` | Run contract test suites |
| `node` | Start local Hardhat network |
| `deploy` | Deploy contracts to specified network |
| `verify` | Verify contracts on block explorers |

## Contract Development

### SYNTH Token Contract
- ERC-20 compatible token implementation
- Non-transferable accounting token for internal use
- Epoch-based allocation mechanisms

### POC Registry Contract
- Contribution registration and certification
- $200 registration fee handling
- On-chain certificate minting

## Testing

```bash
# Run all tests
npx hardhat test

# Run specific test file
npx hardhat test test/SynthToken.test.js

# Run with gas reporting
npx hardhat test --gas
```

## Deployment

### Local Development
```bash
npx hardhat run scripts/deploy.js --network localhost
```

### Testnet Deployment
```bash
npx hardhat run scripts/deploy.js --network sepolia
```

### Mainnet Deployment
```bash
npx hardhat run scripts/deploy.js --network mainnet
```

## Integration

This Hardhat setup integrates with:
- **Base Blockchain**: Primary deployment target
- **Layer 1 Python**: Contract interaction interfaces
- **Testing Framework**: Comprehensive contract validation
- **CI/CD Pipeline**: Automated deployment and verification

## Requirements

- Node.js 18+
- npm or yarn
- Local blockchain network (Hardhat node or Anvil)

## Documentation

- [AGENTS.md](AGENTS.md) - Detailed component documentation
- [FRACTAL.md](FRACTAL.md) - Fractal analysis and patterns
- [Syntheverse Blueprint](../../docs/Blueprint for Syntheverse) - System architecture overview
