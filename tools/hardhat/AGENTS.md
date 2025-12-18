# Hardhat Configuration

## Purpose

Hardhat TypeScript configuration for smart contract development, testing, and deployment in the Syntheverse blockchain infrastructure.

## Key Modules

### Configuration (`hardhat.config.ts`)

Hardhat configuration for Solidity development:

- **Network Configuration**: Local Anvil, Base Sepolia, Base Mainnet
- **Compiler Settings**: Solidity version, optimization settings
- **Plugin Integration**: ethers, typechain, gas reporter
- **Deployment Scripts**: Contract deployment automation

## Integration Points

- Used by smart contracts in `src/blockchain/contracts/`
- Integrates with Foundry for testing (`foundry.toml`)
- Deployment scripts in `scripts/deployment/`
- Network configuration references wallet setup in `config/wallet/`

## Networks

| Network | Chain ID | RPC URL | Purpose |
|---------|----------|---------|---------|
| anvil | 31337 | http://127.0.0.1:8545 | Local development |
| base_sepolia | 84532 | https://sepolia.base.org | Testnet |
| base_mainnet | 8453 | https://mainnet.base.org | Production |

## Usage

```bash
# Compile contracts
npx hardhat compile

# Run tests
npx hardhat test

# Deploy to network
npx hardhat run scripts/deploy.js --network anvil

# Verify contract
npx hardhat verify --network base_sepolia CONTRACT_ADDRESS
```

## Development Guidelines

- Use TypeScript for type safety
- Configure optimizer for gas efficiency
- Test on local network before deployment
- Verify contracts on block explorers

## File Structure

```
hardhat/
├── hardhat.config.ts     # Main Hardhat configuration
└── AGENTS.md             # This documentation
```

## Cross-References

- **Parent**: [tools/AGENTS.md](../AGENTS.md) - Development tools
- **Contracts**: [src/blockchain/contracts/AGENTS.md](../../src/blockchain/contracts/AGENTS.md)
- **Deployment**: [scripts/deployment/AGENTS.md](../../scripts/deployment/AGENTS.md)
- **Related**:
  - [src/blockchain/AGENTS.md](../../src/blockchain/AGENTS.md) - Blockchain overview
  - [config/wallet/AGENTS.md](../../config/wallet/AGENTS.md) - Wallet configuration

