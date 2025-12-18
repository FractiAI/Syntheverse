# Configuration

## Purpose

Configuration files and documentation for environment setup, wallet configuration, and system configuration.

## Components

### Environment (`environment/`)

Configuration guides for environment setup:
- **`SETUP_GROQ.md`**: Groq API key setup instructions
- **`GET_GROQ_KEY.md`**: How to obtain Groq API key

### Wallet (`wallet/`)

Wallet configuration for blockchain operations:
- **`test-wallet-setup.md`**: Test wallet setup for blockchain testing

## Environment Variables

### Required Variables

- **`GROQ_API_KEY`**: Groq API key for LLM operations (required for PoC evaluation)
  - Get from: https://console.groq.com/
  - Used by: Layer 2 evaluation engine

### Optional Variables

- **`PRIVATE_KEY`**: Private key for blockchain deployment and transactions (optional)
  - Used by: Smart contract deployment, certificate registration
  - Security: Never commit to version control

- **`ETHERSCAN_API_KEY`**: Etherscan API key for contract verification (optional)
  - Get from: https://etherscan.io/apis
  - Used by: Contract verification on block explorers

### Port Configuration

The system uses the following default ports (configurable in startup scripts):

- **PoC API (Flask)**: `5001` - REST API for PoC operations
- **Legacy Web UI (Flask)**: `5000` - Legacy web interface
- **Next.js Frontend**: `3001` - Modern React dashboard
- **RAG API (FastAPI)**: `8000` - Document processing and queries
- **Anvil (Blockchain)**: `8545` - Local Ethereum node

### Service Dependencies

- **Python 3.8+** with packages: flask, flask-cors, requests, PyPDF2
- **Node.js 18+** with npm (required for Next.js frontend)
- **Foundry** (optional, for smart contract development)
- **Groq API** access for AI evaluation

## Quick Setup Checklist

### 1. Environment Setup
- [ ] Install Python 3.8+ and Node.js 18+
- [ ] Clone Syntheverse repository
- [ ] Navigate to project directory

### 2. API Configuration
- [ ] Get Groq API key from https://console.groq.com/
- [ ] Set `GROQ_API_KEY` environment variable
- [ ] (Optional) Set `PRIVATE_KEY` for blockchain operations
- [ ] (Optional) Set `ETHERSCAN_API_KEY` for contract verification

### 3. Install Dependencies
- [ ] Install Python packages: `pip install flask flask-cors werkzeug requests PyPDF2`
- [ ] Install Node.js dependencies: `cd src/frontend/poc-frontend && npm install`

### 4. Wallet Setup (Optional)
- [ ] Install MetaMask browser extension
- [ ] Add Base Sepolia testnet
- [ ] Get test ETH from faucet
- [ ] Configure wallet for Syntheverse operations

### 5. Start System
- [ ] Run: `python scripts/startup/start_servers.py`
- [ ] Access dashboard: http://localhost:3001
- [ ] Access legacy UI: http://localhost:5000

## Detailed Setup Instructions

### Environment Variables

Create a `.env` file in the project root:

```bash
# Syntheverse Environment Configuration

# Required: Groq API for AI evaluation
GROQ_API_KEY=gsk_your-api-key-here

# Optional: Blockchain operations
PRIVATE_KEY=your-private-key-here
ETHERSCAN_API_KEY=your-etherscan-api-key-here

# Optional: Custom port configuration
POC_API_PORT=5001
NEXTJS_FRONTEND_PORT=3001
RAG_API_PORT=8000
```

Or set environment variables directly:

```bash
export GROQ_API_KEY=your-key-here
export PRIVATE_KEY=your-private-key  # Optional
export ETHERSCAN_API_KEY=your-api-key  # Optional
```

### Groq API Setup

1. Visit https://console.groq.com/
2. Sign up for a free account
3. Generate an API key
4. Set the environment variable as shown above

### Wallet Configuration

For blockchain operations and certificate registration:

1. Follow detailed instructions in `wallet/test-wallet-setup.md`
2. Set up MetaMask with Base Sepolia testnet
3. Get test ETH from the Base faucet
4. Configure private key for deployment operations

## Documentation

### Configuration Guides
- [Environment Setup](environment/) - API keys, environment variables, dependencies
- [Wallet Configuration](wallet/) - Test wallet setup, blockchain operations

### Related Documentation
- [System Architecture](../docs/architecture/) - System design
- [Deployment Guide](../docs/deployment/) - Deployment instructions
- [API Documentation](../docs/api/) - Service endpoints and integration
- [Development Setup](../src/README.md) - Component setup instructions

## Troubleshooting

### Common Issues

**Missing GROQ_API_KEY**
```
Error: Missing required environment variables: GROQ_API_KEY
```
Solution: Set `GROQ_API_KEY` environment variable (see setup instructions above)

**Port conflicts**
```
Error: Port XXXX already in use
```
Solution: Use different ports or free the occupied ports

**Node.js not found (Next.js frontend)**
```
❌ Node.js not available - Next.js frontend cannot start
```
Solution: Install Node.js 18+ or use legacy UI only

### Health Checks

Verify services are running:
- PoC API: `curl http://localhost:5001/health`
- Legacy UI: `curl http://localhost:5000/`
- Next.js: `curl http://localhost:3001/`
- RAG API: `curl http://localhost:8000/health`





