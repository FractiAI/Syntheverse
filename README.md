# Syntheverse PoC System

Syntheverse is a hydrogen-holographic fractal blockchain game with a Proof-of-Contribution (PoC) system. This repository contains the PoC test program with multi-metal evaluation, interactive sandbox mapping, and blockchain integration.

## Quick Start

```bash
git clone https://github.com/FractiAI/Syntheverse.git
cd Syntheverse
export GROQ_API_KEY="your-groq-api-key-here"
python3 scripts/startup/start_servers.py
```

Access the system:
- **Dashboard**: http://localhost:3001/dashboard
- **Submit PoC**: http://localhost:3001/submission
- **Sandbox Map**: http://localhost:3001/sandbox-map
- **Registry**: http://localhost:3001/registry
- **Blockchain Registration**: http://localhost:5000
- **PoC API**: http://localhost:5001
- **Local Blockchain**: http://localhost:8545

## Repository Structure

### Core Components
- **`src/api/`**: REST API servers (PoC API, RAG API)
- **`src/blockchain/`**: Smart contracts and Layer 1 blockchain logic
- **`src/core/`**: PoC evaluation engine and tokenomics
- **`src/frontend/`**: Next.js dashboard and legacy interfaces
- **`src/data/`**: PDF processing and vectorization pipeline

### Supporting Systems
- **`scripts/`**: Startup, deployment, and utility scripts
- **`config/`**: Environment and wallet configuration
- **`docs/`**: Technical documentation and guides
- **`tests/`**: Test suites and validation
- **`examples/`**: Demo scripts and interface examples
- **`tools/`**: Development tools and guides

## Key Features

### Proof-of-Contribution System
- Multi-metal evaluation (Gold: Discovery, Silver: Technology, Copper: Alignment)
- AI-powered evaluation using Grok API
- Archive-first redundancy detection
- Token allocation based on structural impact

### Interactive Components
- Sandbox map with 16 knowledge dimensions updates in real-time
- Contribution registry shows chronological timeline
- Dashboard shows system statistics
- Visualization shows metals: Gold, Silver, Copper

### Blockchain Integration
- SYNTH token contracts on Base Layer 2
- Tiered fee structure (first 3 submissions free)
- Certificate registration system
- Foundry + Anvil development environment

## Requirements

- Python 3.8+ for backend services
- Node.js 18+ for Next.js frontend
- Groq API key for AI evaluation
- Foundry (optional, for blockchain development)

## Development

Each component has its own README with setup instructions. See `docs/` for documentation.

## Testing

Run the full test suite:
```bash
cd tests
./run_tests.sh --all
```

## License
