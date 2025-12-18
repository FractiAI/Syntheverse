# Source Code Agents

## Purpose

The `src/` directory contains all source code for the Syntheverse system, organized by functional area.

## Key Modules

### API Services (`api/`)

- **`poc-api/`**: Flask API server connecting Next.js frontend to Layer 2 backend
- **`rag_api/`**: FastAPI server for document processing and RAG queries
- **`rag-api/`**: Alternative FastAPI RAG implementation with extended analysis

### Blockchain (`blockchain/`)

- **`contracts/`**: Solidity smart contracts (SYNTH token, POCRegistry)
- **`layer1/`**: Python implementation of Layer 1 blockchain logic

### Core Logic (`core/`)

- **`layer2/`**: PoC and PoD evaluation engines, archive system, tokenomics, sandbox map

### Frontend (`frontend/`)

- **`poc-frontend/`**: Next.js 14 application (main PoC dashboard)
- **`ui_web/`**: Legacy Flask web interface
- **`submission/`**: Basic submission interface
- **`admin/`**: Administrative interface

### Data (`data/`)

- **`pdfs/`**: Downloaded PDF documents
- **`parsed/`**: Parsed text chunks
- **`vectorized/`**: Embeddings and metadata
- **`metadata/`**: Scraping metadata
- **`blockchain/`**: Runtime blockchain state (see `data/blockchain/`)

## Integration Points

- APIs serve as bridges between frontend and backend
- Layer 2 orchestrates evaluation and token allocation
- Layer 1 handles blockchain operations
- Data layer supports RAG pipeline

## Responsibilities

### Component Coordination
- Maintain clear architectural boundaries between layers
- Ensure consistent interfaces between frontend, backend, and blockchain
- Coordinate data flow from submission to token allocation
- Support both legacy and modern frontend implementations

### Quality Assurance
- Enforce coding standards across all components
- Maintain comprehensive test coverage
- Ensure documentation accuracy and completeness
- Validate blueprint compliance for all implementations

### Performance Optimization
- Optimize evaluation pipeline performance
- Ensure scalable data processing for RAG operations
- Maintain responsive user interfaces
- Monitor and improve system resource usage

## Interfaces

### Internal APIs
- **PoC API** (`api/poc-api/`): REST endpoints for submission and evaluation
- **RAG API** (`api/rag_api/`): Document processing and query interfaces
- **Layer 2 Engine** (`core/layer2/`): Evaluation and tokenomics interfaces
- **Blockchain Layer** (`blockchain/layer1/`): Smart contract interaction

### Data Interfaces
- **File Storage**: PDF uploads and processing pipelines
- **Vector Database**: Embedding storage and retrieval
- **Archive System**: Contribution storage and redundancy detection
- **Tokenomics State**: Persistent allocation and epoch management

### External Integrations
- **GROQ API**: AI evaluation and analysis services
- **Base Blockchain**: Smart contract deployment and interaction
- **Frontend Applications**: Web interfaces for user interaction

## Dependencies

### Runtime Dependencies
- **Python Libraries**: Flask, FastAPI, requests, numpy, pandas
- **Node.js Packages**: Next.js, React, TypeScript, Tailwind CSS
- **Blockchain Tools**: Web3.py, eth-account, foundry
- **AI Services**: groq API client

### Development Dependencies
- **Testing**: pytest, jest, playwright
- **Code Quality**: black, flake8, eslint, prettier
- **Documentation**: sphinx, typedoc
- **Deployment**: docker, docker-compose

### System Requirements
- **Python 3.8+**: Backend services and evaluation
- **Node.js 18+**: Frontend development
- **Solidity 0.8.x**: Smart contract compilation
- **Git**: Version control

## Development

### Development Workflow
- **Feature Branches**: Create feature branches for all development
- **Pull Requests**: Required code review for all changes
- **Testing**: Comprehensive tests required before merge
- **Documentation**: Update AGENTS.md and README.md for API changes

### Environment Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
cd src/frontend/poc-frontend && npm install

# Set up blockchain development
cd src/blockchain && forge install

# Configure environment
export GROQ_API_KEY="your-api-key"
```

### Code Standards
- **Python**: PEP 8 with black formatting
- **TypeScript**: ESLint with Airbnb config
- **Solidity**: OpenZeppelin standards
- **Documentation**: Clear, concise, and comprehensive

## Testing

### Test Structure
- **Unit Tests**: Individual component testing
- **Integration Tests**: Cross-component functionality
- **API Tests**: Endpoint validation and error handling
- **E2E Tests**: Complete user workflow testing

### Test Execution
```bash
# Run all tests
cd tests && python -m pytest

# Run component-specific tests
pytest tests/test_poc_api.py
pytest tests/test_blockchain.py

# Run frontend tests
cd src/frontend/poc-frontend && npm test
```

### Test Coverage
- **Backend**: Minimum 80% coverage required
- **Frontend**: Component and integration tests
- **Blockchain**: Contract and interaction tests
- **API**: Endpoint and error scenario tests

## Blueprint Alignment

### Core Architecture Mapping ([Blueprint §3](docs/Blueprint for Syntheverse))
- **Layer 1 (Blockchain)**: `blockchain/` → Syntheverse Blockmine L1 with Base network smart contracts
- **Layer 2 (Evaluation)**: `core/layer2/` → PoC evaluation engine with archive-first redundancy detection
- **UI Layer**: `frontend/` + `api/` → Next.js dashboard with Flask API bridge

### Experience Walkthrough Implementation ([Blueprint §1](docs/Blueprint for Syntheverse))
- **PoC Submission** ([§1.1](docs/Blueprint for Syntheverse)): `frontend/poc-frontend/` submission interface
- **Evaluation Pipeline** ([§1.3](docs/Blueprint for Syntheverse)): `core/layer2/poc_server.py` + hydrogen holographic fractal scoring
- **Blockchain Registration** ([§1.4](docs/Blueprint for Syntheverse)): `blockchain/` Layer 1 with $200 registration fees
- **Dashboard Interaction** ([§1.5](docs/Blueprint for Syntheverse)): `frontend/poc-frontend/` exploration and amplification display
- **Financial Alignment** ([§1.6](docs/Blueprint for Syntheverse)): `docs/contributors/SYNTH_Pitch.md` tier system foundation

### System Components Alignment
- **PoC Pipeline** ([§3.1](docs/Blueprint for Syntheverse)): `api/poc-api/` → `core/layer2/` → `blockchain/` complete workflow
- **Contribution Scoring** ([§3.2](docs/Blueprint for Syntheverse)): `core/layer2/evaluator/` novelty/density/coherence/alignment dimensions
- **Token Allocation** ([§3.3](docs/Blueprint for Syntheverse)): `core/layer2/tokenomics_state.py` epoch-based SYNTH distribution
- **Metallic Amplifications** ([§3.4](docs/Blueprint for Syntheverse)): `core/layer2/poc_archive.py` Gold/Silver/Copper multipliers

### AI & Integration ([Blueprint §5](docs/Blueprint for Syntheverse))
- **Archive Training**: All PoCs stored in `core/layer2/poc_archive.py` to train evolving Syntheverse AI
- **GROQ Integration**: Required for evaluation via `config/environment/SETUP_GROQ.md`
- **Hydrogen Holographic Fractal**: Measurable, reproducible evaluation methodology

### Governance & Operations ([Blueprint §6](docs/Blueprint for Syntheverse))
- **Human Approval**: Required for all PoC evaluations through operator oversight
- **Operator Control**: Epochs and thresholds managed through `core/layer2/tokenomics_state.py`
- **Transparency**: All SYNTH allocations auditable on-chain via `blockchain/` Layer 1

### Financial Framework ([Blueprint §4](docs/Blueprint for Syntheverse))
- **Registration Fees**: $200 per approved PoC (submissions free for evaluation)
- **Alignment Tiers**: Copper/Silver/Gold contribution packages via `docs/contributors/SYNTH_Pitch.md`

### Complete Workflow ([Blueprint §7](docs/Blueprint for Syntheverse))
1. **Submit** → `frontend/poc-frontend/` interface
2. **Evaluate** → `core/layer2/poc_server.py` hydrogen holographic scoring
3. **Approve** → Human review and approval process
4. **Register** → `blockchain/` $200 on-chain registration
5. **Allocate** → `core/layer2/tokenomics_state.py` SYNTH token distribution
6. **Explore** → `frontend/poc-frontend/` dashboard with metallic amplifications

### Implementation Status ([docs/BLUEPRINT_IMPLEMENTATION_STATUS.md](docs/BLUEPRINT_IMPLEMENTATION_STATUS.md))
- **✅ Fully Operational**: Core evaluation pipeline, blockchain integration, tokenomics engine, UI dashboard
- **🟡 Ready for Phase 2**: Fee structure implemented, metallic amplifications validated
- **📋 Next Priorities**: See `docs/BLUEPRINT_IMPLEMENTATION_ROADMAP.md` Phase 2-3 roadmap

## File Structure

```
src/
├── api/                    # API services and bridges
│   ├── poc-api/           # Flask API for PoC submissions
│   ├── rag_api/           # FastAPI for RAG document processing
│   └── rag-api/           # Alternative RAG implementation
├── blockchain/            # Layer 1 blockchain implementation
│   ├── contracts/         # Solidity smart contracts
│   └── layer1/            # Python blockchain integration
├── core/                  # Layer 2 evaluation logic
│   └── layer2/            # PoC/PoD engines, tokenomics, archive
├── data/                  # Data management and storage
│   ├── pdfs/             # Raw PDF documents
│   ├── parsed/           # Parsed text chunks
│   ├── vectorized/       # Embeddings and vectors
│   ├── metadata/         # Scraping metadata
│   └── blockchain/       # Runtime blockchain state
├── frontend/              # User interface applications
│   ├── poc-frontend/     # Next.js main dashboard
│   ├── ui_web/           # Legacy Flask interface
│   ├── submission/       # Basic submission interface
│   └── admin/            # Administrative interface
└── test_outputs/          # Test result storage
```

## Cross-References

- **Parent**: [Root AGENTS.md](../AGENTS.md) - System overview and architecture
- **Children**:
  - [api/AGENTS.md](api/AGENTS.md) - API services documentation
  - [blockchain/AGENTS.md](blockchain/AGENTS.md) - Blockchain implementation
  - [core/AGENTS.md](core/AGENTS.md) - Core logic documentation
  - [data/AGENTS.md](data/AGENTS.md) - Data management
  - [frontend/AGENTS.md](frontend/AGENTS.md) - Frontend applications
- **Related**:
  - [config/AGENTS.md](../config/AGENTS.md) - Configuration management
  - [scripts/AGENTS.md](../scripts/AGENTS.md) - System scripts
  - [tests/AGENTS.md](../tests/AGENTS.md) - Test documentation


