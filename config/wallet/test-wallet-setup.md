# Syntheverse Test Wallet Setup

## Overview
This guide helps you set up a test wallet for the Syntheverse PoC system on Base Goerli testnet.

## Prerequisites
- MetaMask browser extension or Coinbase Wallet mobile app
- Internet connection

## Base Goerli Testnet Setup

### 1. Add Base Goerli Network to MetaMask

**Manual Configuration:**
- Open MetaMask
- Click the network dropdown (top center)
- Click "Add Network"
- Click "Add a network manually"

**Network Details:**
```
Network Name: Base Goerli
RPC URL: https://goerli.base.org
Chain ID: 84531
Currency Symbol: ETH
Block Explorer: https://goerli.basescan.org/
```

### 2. Get Free Test ETH

Visit the [Base Goerli Faucet](https://faucet.base.org/) and:
- Connect your wallet
- Request test ETH (0.5 ETH max per day)
- Wait 1-2 minutes for confirmation

### 3. Verify Network Setup

- Check MetaMask shows "Base Goerli"
- Balance should show received test ETH
- Test transaction: Send 0.001 ETH to yourself

## Syntheverse Test Wallet

### Test Contributor Account
```
Address: 0x742d35Cc6634C0532925a3b844Bc454e4438f44e (Example)
Private Key: NEVER STORE PRIVATE KEYS IN CODE
```

**⚠️ SECURITY WARNING:**
- Never commit private keys to version control
- Use environment variables or secure key management
- This is for testing only - use burner wallets

### Environment Configuration

Create a `.env.local` file in the project root:

```bash
# Test Wallet Configuration
TEST_WALLET_ADDRESS=0x742d35Cc6634C0532925a3b844Bc454e4438f44e
TEST_WALLET_PRIVATE_KEY=your-private-key-here

# Base Goerli Configuration
BASE_GOERLI_RPC=https://goerli.base.org
BASE_GOERLI_CHAIN_ID=84531
BASE_GOERLI_EXPLORER=https://goerli.basescan.org/
```

## Wallet Integration Testing

### Frontend Testing
1. Start the local development server:
   ```bash
   cd src/frontend/poc-frontend
   npm run dev
   ```

2. Open http://localhost:3000

3. Test wallet connection:
   - Click "Connect Wallet" (when implemented)
   - Approve MetaMask connection
   - Verify wallet address displays

### Registration Testing
1. Start registration server:
   ```bash
   cd src/api/poc-api
   python app.py
   ```

2. Open http://localhost:5000/register

3. Test registration flow:
   - Enter submission hash and contributor ID
   - Click "Register Certificate"
   - Approve MetaMask transaction
   - Verify on Base Goerli explorer

## Fee Structure Testing

### Free Registrations (First 3)
- Contributor: `test-user-1`
- Expected fee: $0
- Process: Should require no payment

### Paid Registrations (4+ submissions)
- Contributor: `test-user-paid`
- Expected fee: $50 per submission
- Process: Should prompt for $50 payment

## Troubleshooting

### Common Issues

**"Network not found"**
- Verify Base Goerli network is added correctly
- Check RPC URL: `https://goerli.base.org`

**"Insufficient funds"**
- Get more test ETH from faucet
- Wait for faucet transaction confirmation

**"Transaction failed"**
- Check gas limit (Base is efficient, try 100,000 gas)
- Verify contract addresses are correct
- Check Base Goerli status: https://status.base.org/

**"Wallet not connecting"**
- Refresh browser page
- Reconnect wallet to dApp
- Check MetaMask permissions

### Debug Tools

**Base Goerli Explorer**: https://goerli.basescan.org/
- View transactions and contract interactions
- Check contract deployments
- Monitor network activity

**MetaMask Developer Tools**:
- View transaction history
- Check network configurations
- Debug connection issues

## Next Steps

Once local testing is complete:

1. **Deploy to Base Goerli**: Smart contracts and backend
2. **Frontend Integration**: Connect to testnet contracts
3. **User Testing**: Invite beta testers
4. **Mainnet Migration**: Deploy to Base mainnet
5. **Production Launch**: Full Syntheverse ecosystem

## Security Notes

- **Testnet Only**: All transactions on Base Goerli are for testing
- **No Real Value**: Test ETH and tokens have no monetary value
- **Private Keys**: Never expose private keys in code or logs
- **Rate Limits**: Respect faucet limits and API rate limits
- **Clean Up**: Delete test wallets after testing completes

---

**Ready to test?** Start with the [Base Goerli Faucet](https://faucet.base.org/) to get your test ETH! 🚀
