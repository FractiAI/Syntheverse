# Blockchain Infrastructure

## Purpose

Blockchain infrastructure for Syntheverse including smart contracts and Layer 1 implementation.

## Components

### Smart Contracts (`contracts/`)

Solidity contracts deployed on Base Layer 2:
- **SYNTH.sol**: Internal accounting token (non-transferable)
- **POCRegistry.sol**: Contribution registry with tiered fees

**Technology:** Foundry + Anvil (development), Hardhat (deployment)

**Status:** ✅ Under Development

### Layer 1 (`layer1/`)

Python implementation of blockchain logic:
- Block structure and transaction system
- Epoch management and token distribution
- Node implementation with mining
- Contract interfaces

**Status:** ✅ Implemented

## Architecture

### Epoch System

- **Founder**: Highest quality (density ≥ 8000)
- **Pioneer**: Early high quality (density ≥ 6000)
- **Community**: Standard contributions (density ≥ 4000)
- **Ecosystem**: All other contributions

### Fee Structure

- First 3 submissions: FREE
- Subsequent submissions: $50 per certificate
- Gas fees: Minimal on Base (~$0.005)

## Integration

- Smart contracts deployed on Base network
- Layer 1 Python code provides blockchain logic
- Layer 2 sends evaluation results to Layer 1
- Frontend connects via Web3 for registration

## Development

### Local Development (Foundry + Anvil)

```bash
cd src/blockchain/contracts
forge test
anvil
forge script script/Deploy.s.sol --rpc-url http://localhost:8545 --broadcast
```

### Testnet Deployment

```bash
export PRIVATE_KEY=your_key
export ETHERSCAN_API_KEY=your_key
forge script script/Deploy.s.sol --rpc-url https://sepolia.base.org --broadcast --verify
```

## Documentation

- [Smart Contracts README](contracts/README.md)
- [Layer 1 README](layer1/README.md)



