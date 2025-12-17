# Deployment Scripts Agents

## Purpose

Smart contract deployment and blockchain management scripts for Syntheverse Layer 1 infrastructure.

## Key Modules

### Contract Deployment (`deploy_contracts.py`)

- **Smart Contract Deployment**: Automated deployment to blockchain networks
- **Multi-Network Support**: Local Anvil, Base Sepolia, Base Mainnet
- **Contract Verification**: Automatic verification on block explorers
- **Address Management**: Storage and tracking of deployed contract addresses
- **Configuration Management**: Environment variable handling for keys and networks

### Deployment Workflow

- **SYNTH Token Deployment**: ERC-20 token contract deployment
- **POCRegistry Deployment**: Proof-of-Contribution registry contract deployment
- **Verification Process**: Contract source code verification on Etherscan/BaseScan
- **Address Storage**: Persistent storage of deployment addresses

### Network Configuration

- **Local Development**: Anvil local blockchain support
- **Test Networks**: Base Sepolia testnet deployment
- **Main Networks**: Base mainnet production deployment
- **RPC Management**: Custom RPC endpoint configuration

## Integration Points

- Deployment scripts connect to contract artifacts in `src/blockchain/contracts/`
- Environment configuration references `config/wallet/` and `config/environment/`
- Network management integrates with Layer 1 in `src/blockchain/layer1/`
- Contract verification uses Etherscan/BaseScan APIs

## Development Guidelines

- Secure private key handling and never commit to repository
- Test deployments on local network before mainnet
- Implement proper error handling for deployment failures
- Document network-specific requirements and gas costs
- Maintain deployment history and rollback capabilities

## Common Patterns

- Smart contract deployment workflows
- Multi-network deployment support
- Contract verification processes
- Environment variable configuration
- Address management and storage
