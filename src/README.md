# Syntheverse Source Code

## Overview

The `src/` directory contains all source code for the Syntheverse system, organized by functional layers and components. This modular architecture implements the three-layer design: Layer 1 (Blockchain), Layer 2 (Evaluation), and UI Layer (Frontend + APIs).

## Architecture

### Three-Layer Design

1. **Layer 1 (Blockchain)**: `blockchain/` - Smart contracts and blockchain integration
2. **Layer 2 (Evaluation)**: `core/layer2/` - PoC evaluation engine and tokenomics
3. **UI Layer**: `frontend/` + `api/` - User interfaces and API bridges

### Component Organization

#### API Services (`api/`)
REST API servers providing bridges between frontend and backend:
- **`poc-api/`**: Flask server for PoC submissions and evaluation
- **`rag_api/`**: FastAPI server for document processing and RAG queries

#### Blockchain Infrastructure (`blockchain/`)
Blockchain implementation and smart contracts:
- **`contracts/`**: Solidity contracts (SYNTH token, POCRegistry)
- **`layer1/`**: Python blockchain integration and utilities

#### Core Business Logic (`core/`)
Evaluation and tokenomics engines:
- **`layer2/`**: PoC evaluation, archive system, token allocation, sandbox mapping

#### Frontend Applications (`frontend/`)
User interface implementations:
- **`poc-frontend/`**: Next.js 14 main dashboard (primary interface)
- **`web-legacy/`**: Legacy Flask web interface
- **`submission/`**: Basic submission form
- **`admin/`**: Administrative management interface

#### Data Processing (`data/`)
Document processing and storage pipeline:
- **`pdfs/`**: Raw PDF document storage
- **`parsed/`**: Text extraction and chunking
- **`vectorized/`**: Embeddings and semantic search
- **`metadata/`**: Scraping and processing metadata

## Installation

### Prerequisites
- **Python 3.8+**: Backend services and evaluation engine
- **Node.js 18+**: Frontend development
- **Foundry**: Smart contract development and testing
- **Git**: Version control

### Environment Setup
```bash
# Clone repository (if not already done)
git clone https://github.com/FractiAI/Syntheverse.git
cd Syntheverse/src

# Set required environment variables
export GROQ_API_KEY="your-groq-api-key-here"

# Optional: Base blockchain development
export PRIVATE_KEY="your-private-key"
export BASE_RPC_URL="https://sepolia.base.org"
```

### Component Installation

#### Backend Services
```bash
# Install Python dependencies
pip install -r requirements.txt

# For specific components
pip install -r api/poc-api/requirements.txt
pip install -r core/layer2/requirements.txt
```

#### Frontend Applications
```bash
# Install Next.js dependencies
cd frontend/poc-frontend
npm install

# Start development server
npm run dev
```

#### Blockchain Development
```bash
# Install Foundry (if not already installed)
curl -L https://foundry.paradigm.xyz | bash
foundryup

# Install contract dependencies
cd blockchain/contracts
forge install
```

## Usage

### Development Workflow
```bash
# Start complete development environment
cd ../scripts/startup
python3 start_servers.py

# Access development interfaces
# Frontend: http://localhost:3001/dashboard
# API: http://localhost:5001
# Blockchain: http://localhost:8545 (Anvil)
```

### Component Development
Each component has its own development setup. See individual AGENTS.md and README.md files for detailed instructions.

## Development

### Code Standards
- **Python**: PEP 8 with black formatting, comprehensive type hints
- **TypeScript**: ESLint with strict rules, full type coverage
- **Solidity**: OpenZeppelin standards, comprehensive testing
- **Documentation**: Clear, concise, blueprint-aligned

### Testing
```bash
# Run all tests
cd ../../tests
./run_tests.sh --all

# Run component-specific tests
pytest tests/test_poc_api.py
cd src/frontend/poc-frontend && npm test
```

### Contributing
- Create feature branches for all development work
- Submit pull requests with comprehensive tests
- Update documentation for any API or interface changes
- Ensure blueprint compliance for architectural changes

## Dependencies

### Core Dependencies
- **Python**: flask, fastapi, requests, numpy, pandas, web3
- **Node.js**: next.js, react, typescript, tailwindcss
- **Blockchain**: foundry, solidity, openzeppelin-contracts
- **AI/ML**: groq API client

### Development Dependencies
- **Testing**: pytest, jest, playwright
- **Code Quality**: black, flake8, eslint, prettier
- **Documentation**: sphinx, typedoc

## Guidelines

- **Separation of Concerns**: Maintain clear boundaries between layers
- **Environment Configuration**: Use environment variables, never hardcode secrets
- **Documentation**: Update AGENTS.md and README.md with all changes
- **Testing**: Comprehensive test coverage required for all features
- **Blueprint Alignment**: All development follows Syntheverse Blueprint specifications




