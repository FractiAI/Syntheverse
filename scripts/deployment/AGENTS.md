# Deployment Scripts

## Purpose

Smart contract deployment and blockchain management scripts for Syntheverse Layer 1 infrastructure.

## Key Modules

### Contract Deployment (`deploy_contracts.py`)

- Automated deployment to blockchain networks
- Local Anvil, Base Sepolia, Base Mainnet support
- Verification on block explorers
- Storage and tracking of deployed contract addresses
- Environment variable handling for keys and networks

### Deployment Workflow

- SYNTH token contract deployment
- POCRegistry contract deployment
- Contract verification on Etherscan/BaseScan
- Deployment address storage

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


