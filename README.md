# Syntheverse

**Hydrogen-Holographic Fractal Blockchain Game & PoC Ecosystem**

[![Status](https://img.shields.io/badge/status-fully_operational-brightgreen)](https://github.com/FractiAI/Syntheverse)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue)](requirements.txt)
[![Node.js](https://img.shields.io/badge/node.js-18+-green)](src/frontend/)

## Overview

Syntheverse is a hydrogen-holographic fractal blockchain game where independent researchers contribute through a unified Proof-of-Contribution (PoC) system. The platform evaluates submissions across multiple metals (Gold: Discovery, Silver: Technology, Copper: Alignment) using AI-powered validation and distributes SYNTH tokens based on structural impact.

## Current Status: ✅ Fully Operational

**The Syntheverse PoC system is NOW FULLY OPERATIONAL** with real blockchain integration and all critical bugs resolved. This includes:

- ✅ **Multi-Metal PoC Evaluation**: AI-powered evaluation with Grok API integration
- ✅ **Interactive Sandbox Map**: Real-time network visualization with 16 knowledge dimensions
- ✅ **Blockchain Integration**: Foundry + Anvil + Hardhat smart contracts on Base
- ✅ **Tiered Fee System**: First 3 submissions FREE, then $50 per submission + $200 blockchain registration
- ✅ **Modern UI**: Next.js dashboard with real-time updates and accurate tokenomics
- ✅ **Archive-First Redundancy**: Comprehensive duplicate detection system

## Quick Start

### Prerequisites
- **Python 3.8+** for backend services
- **Node.js 18+** for frontend development
- **GROQ API Key** for AI evaluation ([Get here](https://console.groq.com/))
- **Foundry** (optional, for blockchain development)

### One-Command System Startup
```bash
git clone https://github.com/FractiAI/Syntheverse.git
cd Syntheverse

# Set your Groq API key (required for AI evaluation)
export GROQ_API_KEY="your-groq-api-key-here"

# Clean up any existing processes (recommended)
./scripts/startup/cleanup_servers.sh

# Start the complete system automatically
python3 scripts/startup/start_servers.py
```

### Access Your Running System
| Service | URL | Description |
|---------|-----|-------------|
| **PoC Dashboard** | http://localhost:3001/dashboard | Modern Next.js UI with real-time stats |
| **Submit PoC** | http://localhost:3001/submission | Upload PDFs, get AI evaluation |
| **Sandbox Map** | http://localhost:3001/sandbox-map | Interactive knowledge network |
| **Registry** | http://localhost:3001/registry | Contribution timeline |
| **Blockchain Registration** | http://localhost:5000 | Register PoC certificates ($200 registration fee) |
| **PoC API** | http://localhost:5001 | Backend REST API |
| **Local Blockchain** | http://localhost:8545 | Anvil Ethereum node |

### Test the Complete Workflow
1. **Submit Contribution** → Upload PDF file
2. **AI Evaluation** → Grok analyzes coherence, density, redundancy
3. **Multi-Metal Scoring** → Receives Gold/Silver/Copper qualification
4. **Token Allocation** → SYNTH rewards based on structural impact
5. **Blockchain Registration** → Register certificate (FREE for first 3, $50 thereafter)
6. **Sandbox Visualization** → View contribution in interactive knowledge network

## Key Features

### Proof-of-Contribution System
- **Multi-Metal Evaluation**: Gold (Discovery), Silver (Technology), Copper (Alignment)
- **AI-Powered Validation**: Grok API integration with deterministic scoring (0-10000 scale)
- **Archive-First Redundancy**: Prevents duplicate contributions across entire history
- **Token Allocation**: SYNTH rewards based on structural impact and qualification

### Interactive Components
- **Sandbox Map**: Real-time vis-network visualization with 16 knowledge dimensions
- **Contribution Registry**: Append-only chronological timeline of all contributions
- **Live Dashboard**: Real-time statistics, tokenomics, and system metrics
- **Multi-Metal Display**: Visual representation of Gold, Silver, and Copper contributions

### Blockchain Integration
- **SYNTH Token**: ERC-20 compatible utility token with epoch-based rewards
- **Tiered Fee Structure**:
  - First 3 submissions: FREE
  - 4+ submissions: $50 per submission
  - Blockchain registration: $200 per qualified contribution
- **Smart Contracts**: Foundry + Anvil development environment
- **Networks**: Local Anvil → Base Sepolia (testnet) → Base Mainnet

## System Architecture

### Three-Layer Design
1. **Layer 1 (Blockchain)**: Syntheverse Blockmine L1 with smart contracts on Base
2. **Layer 2 (Evaluation)**: PoC evaluation engine with archive-first redundancy detection
3. **UI Layer**: Next.js frontend with Flask API bridge

### Core Components
- **`src/api/`**: REST API servers (PoC API, RAG API)
- **`src/blockchain/`**: Smart contracts and Layer 1 blockchain logic
- **`src/core/`**: PoC evaluation engine and tokenomics state
- **`src/frontend/`**: Next.js dashboard and legacy interfaces
- **`src/data/`**: Data management and persistent state
- **`scripts/`**: Startup, deployment, and utility scripts
- **`config/`**: Environment and wallet configuration
- **`docs/`**: Technical documentation and guides
- **`tests/`**: Comprehensive test suites

## Fee Structure

### PoC Submission Fees
- **First 3 Submissions**: FREE (no submission fee)
- **4+ Submissions**: $50 per submission (covers evaluation and processing)

### Syntheverse Blockmine Registration Fees
- **Blockchain Certificate Registration**: $200 per qualified contribution
- **Purpose**: Covers blockchain transaction costs and permanent certificate minting
- **Payment**: Required when registering qualified contributions on the blockchain

## Changelog

### v0.3 - Bug Fixes & Stability (2025-12-18)
- ✅ **FIXED**: Dashboard "Total Distributed" showing incorrect 58.21T → now shows accurate 37.125T
- ✅ **FIXED**: Tokenomics calculation using wrong formula (epoch allocations vs actual allocations)
- ✅ **FIXED**: `tier_multiplier` reference before assignment error in token allocation
- ✅ **FIXED**: Register PoC button "no server found" error → added legacy web UI server (port 5000)
- ✅ **ADDED**: Automatic startup of all required servers (Flask API, Next.js, Legacy UI, RAG API)
- ✅ **IMPROVED**: Token allocation accuracy and dashboard statistics reliability

### v0.2 - Core Functionality (2025-12-17)
- ✅ Complete AI-powered PoC evaluation system with Grok API integration
- ✅ Multi-metal evaluation (Gold/Silver/Copper) with tiered token allocation
- ✅ Interactive sandbox map with 16 knowledge dimensions
- ✅ Blockchain integration with Foundry + Anvil + Hardhat
- ✅ Modern Next.js frontend with real-time updates
- ✅ Archive-first redundancy detection system

## Development

### Local Development Setup

#### Prerequisites
- **Python 3.8+** for backend services
- **Node.js 18+** for frontend development
- **Git** for version control
- **GROQ API Key** for AI evaluation ([Get here](https://console.groq.com/))
- **Foundry** (optional, for blockchain development)

#### Quick Start - Local Demo
```bash
# Clone the repository
git clone https://github.com/FractiAI/Syntheverse.git
cd Syntheverse

# Set up environment
export GROQ_API_KEY="your-groq-api-key-here"

# Clean up any existing processes (recommended)
./scripts/startup/cleanup_servers.sh

# Start the local demonstration system
./scripts/development/start_poc_ui.sh

# Access the system
# Frontend: http://localhost:3000
# PoC API: http://localhost:5001
# Registration: http://localhost:5000
```

### Smart Contract Development
```bash
# Install Foundry (if not installed)
curl -L https://foundry.paradigm.xyz | bash
foundryup

# Set up smart contracts
cd src/blockchain
forge install OpenZeppelin/openzeppelin-contracts

# Run tests
forge test

# Start local node
anvil
```

### Base Blockchain Setup
For blockchain testing, set up a Base Sepolia test wallet:
- Follow: `config/wallet/test-wallet-setup.md`
- Get free test ETH: https://sepoliafaucet.com/ (for Base Sepolia)
- Add Base Sepolia network to MetaMask

## Contributing

### Ways to Contribute
- **🐛 Bug Reports**: Use GitHub Issues with detailed reproduction steps
- **💡 Feature Requests**: Submit enhancement ideas with use cases
- **📝 Documentation**: Improve guides, tutorials, and API docs
- **🔧 Code Contributions**: Submit pull requests with tests
- **🎨 UI/UX Improvements**: Enhance the contributor dashboard experience
- **📊 Analytics**: Help improve evaluation algorithms and metrics

### Development Guidelines
- **Code Style**: Follow PEP 8 for Python, ESLint for JavaScript/TypeScript
- **Testing**: Write unit tests for new features
- **Documentation**: Update docs for any API or UI changes
- **Security**: Report security issues privately to maintainers
- **Licensing**: All contributions under project license

## Repository Structure

### Core Components
- **`src/api/`**: REST API servers (PoC API, RAG API)
- **`src/blockchain/`**: Smart contracts and Layer 1 blockchain logic
- **`src/core/`**: PoC evaluation engine and tokenomics
- **`src/frontend/`**: Next.js dashboard and legacy interfaces
- **`src/data/`**: Data management and persistent state
- **`scripts/`**: Startup, deployment, and utility scripts
- **`config/`**: Environment and wallet configuration
- **`docs/`**: Technical documentation and guides
- **`tests/`**: Comprehensive test suites

### Key Features
- **Proof-of-Contribution System**: Multi-metal evaluation (Gold/Silver/Copper) with AI validation
- **Interactive Sandbox Map**: Real-time network visualization with 16 knowledge dimensions
- **Blockchain Integration**: SYNTH token contracts on Base Layer 2
- **Archive-First Redundancy**: Comprehensive duplicate detection system
- **Tiered Fee Structure**: First 3 submissions FREE, then $50 per submission + $200 blockchain registration

## Links & Resources

- **🏠 Website**: https://fractiai.com
- **📄 Documentation**: https://docs.syntheverse.io
- **🎥 YouTube**: https://www.youtube.com/@FractiAI
- **🐦 X/Twitter**: https://x.com/FractiAi
- **📧 Contact**: info@fractiai.com
- **🔬 Zenodo Papers**: https://zenodo.org/records/17873279

## Disclaimer

This is an active research and development project. While the test program is fully functional, it represents ongoing work toward the complete Syntheverse ecosystem. Early contributors should understand that:

- The system is in active development and may change
- Contributions are valuable for ecosystem evolution
- Tokenomics and rewards are subject to refinement
- Commercial deployment timeline is not guaranteed

---

**Ready to shape the future of AI, crypto, and scientific discovery?**

The Syntheverse test program is now live and ready for collaboration. Experience the power of multi-metal evaluation, explore the interactive sandbox map, and contribute to the evolution of the Hydrogen-Holographic Fractal ecosystem.

**🚀 Test the system today:**
- **Local Demo**: `./scripts/development/start_poc_ui.sh`
- **Contribute**: Submit PRs, report issues, join discussions

---
