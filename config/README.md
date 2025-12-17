# Configuration

## Purpose

Configuration files and documentation for environment setup, wallet configuration, and system configuration.

## Components

### Environment (`environment/`)

Configuration guides for environment setup:
- **`SETUP_GROQ.md`**: Groq API key setup instructions
- **`GET_GROQ_KEY.md`**: How to obtain Groq API key
- **`EMAIL_TROUBLESHOOTING.md`**: Email configuration troubleshooting

### Wallet (`wallet/`)

Wallet configuration for blockchain operations:
- **`test-wallet-setup.md`**: Test wallet setup for blockchain testing

## Required Environment Variables

- **`GROQ_API_KEY`**: Groq API key for LLM operations (required)
- **`PRIVATE_KEY`**: Private key for blockchain deployment (optional)
- **`ETHERSCAN_API_KEY`**: Etherscan API key for contract verification (optional)

## Setup

### Groq API Key

1. Get API key from https://console.groq.com/
2. Set environment variable:
   ```bash
   export GROQ_API_KEY=your-key-here
   ```
3. Or create `.env` file in project root

### Wallet Setup

Follow `wallet/test-wallet-setup.md` for test wallet configuration.

## Documentation

- [Environment Setup](environment/)
- [Wallet Configuration](wallet/)



