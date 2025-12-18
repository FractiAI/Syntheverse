# Syntheverse Smart Contracts

Solidity smart contracts for the Syntheverse PoC system, designed to deploy on Base Layer 2.

## 🏗️ Architecture

### Core Contracts

#### SYNTH.sol
- **Purpose**: Internal accounting token for PoC rewards
- **Features**:
  - Non-transferable (internal accounting only)
  - Epoch-based allocation system
  - PoC contribution rewards
  - Emergency controls

#### POCRegistry.sol
- **Purpose**: Manages PoC contributions and certificate registration
- **Features**:
  - Contribution submission and evaluation recording
  - Tiered fee system (first 3 free, then $50)
  - Certificate registration with blockchain verification
  - SYNTH token allocation for qualified contributions

## 🛠️ Development Stack

### Phase 1: Foundry + Anvil (Local Development)
```bash
# Install Foundry
curl -L https://foundry.paradigm.xyz | bash
foundryup

# Install dependencies
forge install OpenZeppelin/openzeppelin-contracts

# Run tests
forge test

# Start local node
anvil

# Deploy locally
forge script script/Deploy.s.sol --rpc-url http://localhost:8545 --broadcast
```

### Phase 2: Hardhat (Base Compatibility)
```bash
# Coming in Phase 2
npm install --save-dev hardhat @nomiclabs/hardhat-ethers ethers
npx hardhat init
```

### Phase 3: Base Sepolia (Public Testing)
```bash
# Deploy to Base Sepolia
forge script script/Deploy.s.sol --rpc-url https://sepolia.base.org --broadcast --verify
```

## 📋 Prerequisites

- **Foundry**: Latest version (`foundryup`)
- **Solidity**: ^0.8.19
- **OpenZeppelin**: ^4.9.0
- **Base Sepolia ETH**: For testnet deployment

## 🚀 Quick Start

### 1. Local Development
```bash
# Install dependencies
forge install

# Run tests
forge test

# Start Anvil (local Ethereum node)
anvil

# Deploy contracts locally
forge script script/Deploy.s.sol --rpc-url http://localhost:8545 --broadcast
```

### 2. Testnet Deployment
```bash
# Set environment variables
export PRIVATE_KEY=your_private_key
export ETHERSCAN_API_KEY=your_etherscan_key

# Deploy to Base Sepolia
forge script script/Deploy.s.sol --rpc-url https://sepolia.base.org --broadcast --verify
```

## 📊 Contract Architecture

```
┌─────────────────────────────────┐
│         SYNTH Token             │
│  • Internal accounting only     │
│  • Epoch-based rewards          │
│  • Non-transferable             │
│  • Emergency controls           │
└─────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│      POC Registry               │
│  • Contribution management      │
│  • Fee collection ($50)         │
│  • Certificate registration     │
│  • Token allocation             │
└─────────────────────────────────┘
```

## 🎯 Fee Structure

- **PoC Submissions**: First 3 FREE, then $50 per submission
- **Blockchain Registration**: $200 per qualified contribution
- **Gas fees**: Minimal on Base (~$0.005)
- **Token rewards**: SYNTH allocations for qualified contributions

## 🔐 Security Features

- **Non-transferable tokens**: SYNTH tokens cannot be traded externally
- **Access controls**: Only authorized PoC evaluator can allocate tokens
- **Emergency controls**: Owner can pause and withdraw in emergencies
- **Input validation**: All contract inputs are validated
- **Reentrancy protection**: OpenZeppelin ReentrancyGuard

## 🧪 Testing

### Run All Tests
```bash
forge test
```

### Run Specific Test
```bash
forge test --match-path test/SYNTH.t.sol
```

### Test Coverage
```bash
forge coverage
```

### Gas Usage
```bash
forge test --gas-report
```

## 📈 Deployment Addresses

### Base Sepolia (Testnet)
- **SYNTH Token**: [Contract Address]
- **POC Registry**: [Contract Address]
- **Block Explorer**: https://sepolia.basescan.org/

### Base Mainnet (Production)
- **SYNTH Token**: [Contract Address]
- **POC Registry**: [Contract Address]
- **Block Explorer**: https://basescan.org/

## 🔧 Configuration

### Environment Variables
```bash
# Deployment
PRIVATE_KEY=your_private_key_without_0x
ETHERSCAN_API_KEY=your_etherscan_api_key

# Contract parameters
POC_EVALUATOR=0x...
TREASURY=0x...
```

### Network Configuration
See `foundry.toml` for network-specific settings and RPC endpoints.

## 📚 Documentation

- [Foundry Book](https://book.getfoundry.sh/)
- [Solidity Documentation](https://docs.soliditylang.org/)
- [OpenZeppelin Contracts](https://docs.openzeppelin.com/contracts/4.x/)
- [Base Documentation](https://docs.base.org/)

## 🤝 Contributing

1. Follow Solidity style guide
2. Write comprehensive tests
3. Update documentation
4. Test on Anvil before committing
5. Ensure all tests pass

## 📞 Support

- **Technical Issues**: Create GitHub issues
- **Security**: Report privately to maintainers
- **Documentation**: Update via pull requests

---

**Ready to deploy?** Start with `forge test` then `anvil` for local development! 🚀
