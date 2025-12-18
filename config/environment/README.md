# Environment Configuration

## Purpose

Configuration guides for environment setup, API keys, and external service integration.

## Guides

- **`SETUP_GROQ.md`**: Groq API key setup instructions
- **`GET_GROQ_KEY.md`**: How to obtain Groq API key

## Environment Variables Reference

### Required Variables

- **`GROQ_API_KEY`**: Groq API key for LLM operations
  - **Purpose**: Powers AI evaluation of PoC submissions
  - **Source**: https://console.groq.com/
  - **Usage**: Required for Layer 2 evaluation engine
  - **Validation**: Must start with `gsk_` and be valid API key

### Optional Variables

- **`PRIVATE_KEY`**: Private key for blockchain operations
  - **Purpose**: Smart contract deployment and certificate registration
  - **Security**: Never commit to version control
  - **Usage**: Required for deployment scripts and blockchain transactions

- **`ETHERSCAN_API_KEY`**: Etherscan API key for contract verification
  - **Purpose**: Verify deployed contracts on block explorers
  - **Source**: https://etherscan.io/apis
  - **Usage**: Optional for contract verification after deployment

- **`ANVIL_RPC_URL`**: Custom RPC URL for local blockchain node
  - **Default**: `http://localhost:8545`
  - **Usage**: Override default Anvil RPC endpoint

### Port Configuration

The Syntheverse system uses the following default ports (configurable in startup scripts):

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| PoC API (Flask) | `5001` | HTTP | REST API for PoC operations |
| Legacy Web UI (Flask) | `5000` | HTTP | Legacy web interface |
| Next.js Frontend | `3001` | HTTP | Modern React dashboard |
| RAG API (FastAPI) | `8000` | HTTP | Document processing and queries |
| Anvil (Blockchain) | `8545` | HTTP | Local Ethereum node |

### Service Startup Order

1. **RAG API** (`8000`) - Document processing backend
2. **PoC API** (`5001`) - Main PoC evaluation service
3. **Legacy Web UI** (`5000`) - Legacy Flask interface
4. **Next.js Frontend** (`3001`) - Modern React dashboard
5. **Anvil** (`8545`) - Local blockchain node (if needed)

### Health Check Endpoints

Verify services are running:

- **PoC API**: `http://localhost:5001/health`
- **RAG API**: `http://localhost:8000/health`
- **Legacy UI**: `http://localhost:5000/` (returns HTML)
- **Next.js**: `http://localhost:3001/` (returns HTML)
- **Anvil**: `http://localhost:8545/` (RPC endpoint)

## Configuration Methods

### Method 1: .env File (Recommended)

Create a `.env` file in the project root:

```bash
# Syntheverse Environment Configuration

# Required
GROQ_API_KEY=gsk_your-groq-api-key-here

# Optional
PRIVATE_KEY=your-blockchain-private-key-here
ETHERSCAN_API_KEY=your-etherscan-api-key-here
ANVIL_RPC_URL=http://localhost:8545
```

### Method 2: Shell Environment Variables

```bash
export GROQ_API_KEY=gsk_your-groq-api-key-here
export PRIVATE_KEY=your-blockchain-private-key-here
export ETHERSCAN_API_KEY=your-etherscan-api-key-here
```

### Method 3: Inline Export

```bash
GROQ_API_KEY=gsk_your-key python scripts/startup/start_servers.py
```

## Environment Variable Precedence

1. **Inline exports** (highest priority)
2. **Shell environment** variables
3. **.env file** values (lowest priority)

## Validation and Startup

The system validates required environment variables on startup:

```python
# Required variables check
required_vars = ['GROQ_API_KEY']
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    logger.error(f"Missing required environment variables: {missing_vars}")
    sys.exit(1)
```

## Troubleshooting

### Missing GROQ_API_KEY
```
Error: Missing required environment variables: GROQ_API_KEY
```
**Solution**: Set the `GROQ_API_KEY` environment variable (see configuration methods above)

### Invalid API Key
```
Error: Groq API authentication failed
```
**Solution**:
1. Verify API key format (starts with `gsk_`)
2. Check API key validity at https://console.groq.com/
3. Ensure no extra spaces or characters

### Port Conflicts
```
Error: Port 5001 already in use
```
**Solution**:
1. Find process using port: `lsof -i:5001`
2. Kill process: `kill -9 <PID>`
3. Or use different port in startup script

### Service Startup Failures
```
❌ Node.js not available - Next.js frontend cannot start
```
**Solution**: Install Node.js 18+ or run without Next.js frontend

## Documentation

- [`SETUP_GROQ.md`](SETUP_GROQ.md) - Groq API setup
- [`GET_GROQ_KEY.md`](GET_GROQ_KEY.md) - How to obtain Groq API key
- [`../README.md`](../README.md) - Configuration overview





