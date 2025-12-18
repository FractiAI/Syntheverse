# Wallet Configuration

## Purpose

Wallet setup and configuration for blockchain testing and deployment.

## Guides

- **`test-wallet-setup.md`**: Test wallet setup guide for Base Sepolia

## Network Configuration

### Base Sepolia Testnet (Primary)

| Parameter | Value |
|-----------|-------|
| Network Name | Base Sepolia |
| RPC URL | https://sepolia.base.org |
| Chain ID | 84532 |
| Currency Symbol | ETH |
| Block Explorer | https://sepolia.basescan.org/ |
| Faucet | https://faucet.base.org/ |

### Alternative Testnets

- **Base Goerli** (deprecated): Use Base Sepolia instead
- **Ethereum Sepolia**: For cross-chain testing
- **Local Anvil**: For development testing

## Wallet Setup Requirements

### Required for Certificate Registration

To register PoC certificates on-chain, you need:

1. **Wallet**: MetaMask, Coinbase Wallet, or compatible Web3 wallet
2. **Network**: Base Sepolia testnet configured
3. **Test ETH**: Sufficient funds for gas fees
4. **Private Key**: For deployment operations (optional)

### Optional for Basic Operations

For viewing and evaluating PoC submissions:

- **No wallet required** - Use the web UI without blockchain registration
- **Read-only access** to all PoC data and evaluations

## Quick Setup Guide

### 1. Install MetaMask
- Chrome/Firefox extension: https://metamask.io/
- Mobile app: App Store/Google Play

### 2. Add Base Sepolia Network
```
Network Name: Base Sepolia
RPC URL: https://sepolia.base.org
Chain ID: 84532
Currency Symbol: ETH
Block Explorer: https://sepolia.basescan.org/
```

### 3. Get Test ETH
- Visit: https://faucet.base.org/
- Connect wallet and request test ETH
- Wait 1-2 minutes for confirmation

### 4. Verify Setup
- Check MetaMask shows "Base Sepolia"
- Balance should display received test ETH
- Test small transaction to confirm functionality

## Security Best Practices

### Development Environment

- **Use test wallets only** - Never mainnet wallets for development
- **Burner accounts** - Create disposable wallets for testing
- **Separate environments** - Different wallets for different testnets

### Private Key Management

- **Never commit** private keys to version control
- **Environment variables** for development keys
- **Hardware wallets** for production operations
- **Key rotation** - Regularly rotate development keys

### Production Security

- **Hardware wallets** (Ledger, Trezor) for mainnet operations
- **Multi-signature** for high-value operations
- **Cold storage** for long-term holdings
- **Backup recovery phrases** securely offline

## Environment Configuration

### For Deployment Operations

Create `.env` file in project root:

```bash
# Wallet Configuration
PRIVATE_KEY=your-private-key-without-0x-prefix
ETHERSCAN_API_KEY=your-etherscan-api-key-for-verification
```

### For Web3 Integration

Environment variables used by the system:

- `PRIVATE_KEY`: For smart contract deployment
- `ETHERSCAN_API_KEY`: For contract verification
- `ANVIL_RPC_URL`: Local blockchain node (default: http://localhost:8545)

## Common Operations

### Check Wallet Balance
```bash
# Via MetaMask UI
1. Open MetaMask
2. Select Base Sepolia network
3. View account balance
```

### Switch Networks
```bash
# Via MetaMask
1. Click network dropdown
2. Select "Base Sepolia"
3. Confirm network switch
```

### View Transactions
```bash
# Via Block Explorer
1. Go to https://sepolia.basescan.org/
2. Search for wallet address
3. View transaction history
```

## Troubleshooting

### Network Connection Issues
- Verify RPC URL: `https://sepolia.base.org`
- Check Chain ID: `84532`
- Confirm network is added correctly in MetaMask

### Insufficient Funds
- Get more test ETH from faucet
- Wait for faucet transaction confirmation
- Check transaction status on block explorer

### Transaction Failures
- Verify sufficient gas fees
- Check Base Sepolia network status
- Confirm contract addresses are correct
- Ensure wallet has permission for transaction

## Integration Points

- **Deployment scripts**: Use `PRIVATE_KEY` for contract deployment
- **Web UI**: Connects to wallet for certificate registration
- **PoC API**: Bridges frontend to blockchain operations
- **Layer 1**: Handles on-chain certificate registration

## Documentation

- [`test-wallet-setup.md`](test-wallet-setup.md) - Setup guide
- [Base Sepolia Faucet](https://faucet.base.org/) - Get test ETH
- [Base Sepolia Explorer](https://sepolia.basescan.org/) - View transactions
- [MetaMask Support](https://support.metamask.io/) - Wallet help





