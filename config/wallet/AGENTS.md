# Wallet Configuration Agents

## Purpose

Wallet setup and configuration documentation for blockchain operations, testing, and deployment in the Syntheverse system.

## Key Modules

### Test Wallet Setup (`test-wallet-setup.md`)

- **Wallet Creation**: Instructions for creating test wallets for development
- **Testnet Configuration**: Setup for Base Sepolia and other test networks
- **MetaMask Integration**: Browser wallet configuration and setup
- **Test ETH Acquisition**: Methods for obtaining test network tokens

### Security Guidelines

- **Key Management**: Secure storage and handling of private keys
- **Development Practices**: Using test wallets for development environments
- **Production Security**: Hardware wallet recommendations for mainnet operations
- **Best Practices**: Security guidelines for blockchain operations

### Network Configuration

- **Test Networks**: Base Sepolia and other testnet setup
- **Main Networks**: Base mainnet configuration for production
- **RPC Endpoints**: Network connection and endpoint management
- **Gas Management**: Transaction cost optimization

## Integration Points

- Wallet configuration used by deployment scripts in `scripts/deployment/`
- Test wallet setup referenced by development guides in `docs/`
- Network configuration connects to Layer 1 in `src/blockchain/layer1/`
- Security guidelines referenced by environment setup in `config/environment/`

## Development Guidelines

- Document secure wallet creation and management
- Provide testnet-specific setup instructions
- Include wallet integration guides for popular wallets
- Update documentation for new networks and features
- Emphasize security best practices throughout

## Common Patterns

- Test wallet creation and funding
- Wallet integration with development tools
- Network configuration for different environments
- Security practices for key management
- Testnet and mainnet deployment procedures

## File Structure

```
wallet/
├── test-wallet-setup.md      # Test wallet configuration
├── README.md                 # Wallet overview
└── AGENTS.md                 # This documentation
```

## Supported Networks

| Network | Purpose | Chain ID |
|---------|---------|----------|
| Base Sepolia | Testing | 84532 |
| Base Mainnet | Production | 8453 |
| Ethereum Sepolia | Cross-chain testing | 11155111 |

## Cross-References

- **Parent**: [config/AGENTS.md](../AGENTS.md) - Configuration overview
- **Related**:
  - [scripts/deployment/AGENTS.md](../../scripts/deployment/AGENTS.md) - Deployment scripts
  - [src/blockchain/AGENTS.md](../../src/blockchain/AGENTS.md) - Blockchain integration
  - [docs/deployment/AGENTS.md](../../docs/deployment/AGENTS.md) - Deployment guides

