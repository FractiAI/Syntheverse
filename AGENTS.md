# Syntheverse System Agents

## Overview

Syntheverse is a hydrogen-holographic fractal blockchain game with a Proof-of-Contribution (PoC) system. This document describes the system architecture and component responsibilities.

## System Architecture

### Three-Layer Design

1. **Layer 1 (Blockchain)**: Syntheverse Blockmine L1 with smart contracts on Base
2. **Layer 2 (Evaluation)**: PoC evaluation engine with archive-first redundancy detection
3. **UI Layer**: Next.js frontend with Flask API bridge

## Directory Overview

| Directory | Purpose | AGENTS.md |
|-----------|---------|-----------|
| `src/` | Source code | [src/AGENTS.md](src/AGENTS.md) |
| `scripts/` | System scripts | [scripts/AGENTS.md](scripts/AGENTS.md) |
| `config/` | Configuration | [config/AGENTS.md](config/AGENTS.md) |
| `docs/` | Documentation | [docs/AGENTS.md](docs/AGENTS.md) |
| `tests/` | Test suites | [tests/AGENTS.md](tests/AGENTS.md) |
| `tools/` | Development tools | [tools/AGENTS.md](tools/AGENTS.md) |
| `examples/` | Demo code | [examples/AGENTS.md](examples/AGENTS.md) |
| `data/` | Runtime blockchain state | [data/AGENTS.md](data/AGENTS.md) |
| `test_outputs/` | Test state storage | [test_outputs/AGENTS.md](test_outputs/AGENTS.md) |
| `analysis_results/` | Embedding analysis | [analysis_results/AGENTS.md](analysis_results/AGENTS.md) |
| `uploads/` | File uploads | [uploads/AGENTS.md](uploads/AGENTS.md) |

## Key Components

### Source Code (`src/`)

- **`api/`**: API services (PoC API, RAG API in `rag_api/`)
  - [poc-api/AGENTS.md](src/api/poc-api/AGENTS.md) - Flask API server
  - [rag_api/AGENTS.md](src/api/rag_api/AGENTS.md) - FastAPI RAG server
- **`blockchain/`**: Blockchain infrastructure (contracts, Layer 1)
  - [contracts/AGENTS.md](src/blockchain/contracts/AGENTS.md) - Solidity contracts
  - [layer1/AGENTS.md](src/blockchain/layer1/AGENTS.md) - Python blockchain
- **`core/`**: Core business logic (Layer 2 evaluation, tokenomics)
  - [layer2/AGENTS.md](src/core/layer2/AGENTS.md) - PoC evaluation engine
  - [utils/AGENTS.md](src/core/utils/AGENTS.md) - Utilities
- **`frontend/`**: Frontend applications (Next.js, legacy Flask)
  - [poc-frontend/AGENTS.md](src/frontend/poc-frontend/AGENTS.md) - Next.js dashboard
- **`data/`**: Data management (PDFs, parsed content, embeddings)
  - [vectorized/AGENTS.md](src/data/vectorized/AGENTS.md) - Embeddings

### Scripts (`scripts/`)

- **`startup/`**: System startup scripts - [AGENTS.md](scripts/startup/AGENTS.md)
- **`development/`**: Development workflow - [AGENTS.md](scripts/development/AGENTS.md)
- **`deployment/`**: Contract deployment - [AGENTS.md](scripts/deployment/AGENTS.md)
- **`utilities/`**: Maintenance utilities - [AGENTS.md](scripts/utilities/AGENTS.md)

### Configuration (`config/`)

- **`environment/`**: Environment configuration - [AGENTS.md](config/environment/AGENTS.md)
- **`wallet/`**: Wallet setup - [AGENTS.md](config/wallet/AGENTS.md)

## Development Guidelines

### Code Standards

- Follow modular, well-documented, clearly reasoned code
- Use test-driven development (TDD)
- Remove unnecessary adjectives from names
- Ensure functional code

### Documentation

- Every folder level must have AGENTS.md and README.md
- Documentation shows rather than tells
- Documentation stays current with code changes

### Integration Points

- APIs connect frontend to backend
- Layer 2 evaluates contributions using Grok API
- Layer 1 handles blockchain registration
- Archive stores all contributions for redundancy detection

## Common Patterns

- Archive-first evaluation: All contributions stored immediately
- Multi-metal system: Gold, Silver, Copper qualifications
- Direct LLM integration: Groq API for evaluations
- File-based storage: JSON files for persistent state

## Blueprint Alignment

This system architecture directly implements the Syntheverse Blueprint vision:

### Layer Architecture Mapping
- **Blueprint §3**: Three-layer design → Exact implementation with L1/L2/UI layers
- **Blueprint §1.4**: Blockchain registration → `src/blockchain/` Layer 1 implementation
- **Blueprint §1.3**: PoC evaluation → `src/core/` Layer 2 evaluation engine
- **Blueprint §1.5**: Dashboard interaction → `src/frontend/` UI layer

### Key Component Alignment
- **Blueprint §3.1**: PoC Pipeline → `scripts/startup/` system orchestration
- **Blueprint §3.3**: Token allocation → `src/core/layer2/tokenomics_state.py`
- **Blueprint §5**: AI integration → `config/environment/SETUP_GROQ.md`
- **Blueprint §7**: Complete workflow → End-to-end system implementation

### Development Standards Compliance
- **Blueprint Vision §0**: "Follow modular, well-documented, clearly reasoned code" → Implemented
- **Blueprint Vision §0**: "Remove unnecessary adjectives from names" → Active process
- **Documentation Standards**: Every folder has AGENTS.md and README.md → Verified

### Current Status
- **85% Blueprint Complete** - Core system fully operational
- **Gap Analysis**: See `docs/BLUEPRINT_IMPLEMENTATION_STATUS.md`
- **Implementation Roadmap**: See `docs/BLUEPRINT_IMPLEMENTATION_ROADMAP.md`
- **Enhanced Blueprint**: See `docs/Blueprint for Syntheverse` (with signposts and appendix)

### Blueprint-Centric Architecture Overview

The Syntheverse system is architected around the **Blueprint for Syntheverse** document, which defines the hydrogen-holographic fractal blockchain vision. All components align to this central blueprint:

#### Blueprint §3 - Three-Layer Architecture
- **Layer 1 (Blockchain)**: `src/blockchain/` - Syntheverse Blockmine L1 with Base network integration
- **Layer 2 (Evaluation)**: `src/core/layer2/` - PoC evaluation engine with archive-first redundancy
- **UI Layer**: `src/frontend/` + `src/api/` - Next.js dashboard with Flask API bridge

#### Blueprint §1 - Experience Walkthrough
- **PoC Submission**: `src/frontend/poc-frontend/` → `src/api/poc-api/` → `src/core/layer2/poc_server.py`
- **Evaluation Pipeline**: Archive-first storage → Hydrogen holographic fractal scoring → Human approval
- **Blockchain Registration**: $200 registration → "I was here first" recognition → SYNTH token allocation

#### Blueprint §5 - AI Integration
- **GROQ API**: Required for all LLM services (evaluation, RAG, Layer 2 processing)
- **Archive Training**: All PoCs stored immediately to train evolving Syntheverse AI
- **Hydrogen Holographic Fractal**: Measurable, reproducible evaluation methodology

#### Blueprint §7 - Complete Workflow
End-to-end implementation: Submission → Evaluation → Registration → Allocation → Integration

## Complete File Structure

```
Syntheverse/
├── AGENTS.md                      # This file - System overview
├── README.md                      # Project introduction
├── requirements.txt               # Python dependencies
├── pytest.ini                     # Test configuration
│
├── src/                           # Source code [AGENTS.md]
│   ├── api/                       # API services [AGENTS.md]
│   │   ├── poc-api/              # Flask PoC API [AGENTS.md]
│   │   └── rag_api/              # FastAPI RAG [AGENTS.md]
│   │       └── analysis/         # Embedding analysis [AGENTS.md]
│   │           └── cli/          # CLI tools [AGENTS.md]
│   ├── blockchain/               # Layer 1 [AGENTS.md]
│   │   ├── contracts/            # Solidity [AGENTS.md]
│   │   │   └── lib/              # OpenZeppelin
│   │   └── layer1/               # Python L1 [AGENTS.md]
│   │       └── contracts/        # Contract interfaces [AGENTS.md]
│   ├── core/                     # Core logic [AGENTS.md]
│   │   ├── layer2/               # PoC engine [AGENTS.md]
│   │   │   ├── evaluator/        # Evaluation [AGENTS.md]
│   │   │   └── allocator/        # Token allocation [AGENTS.md]
│   │   └── utils/                # Utilities [AGENTS.md]
│   ├── frontend/                 # UI layer [AGENTS.md]
│   │   ├── poc-frontend/         # Next.js app [AGENTS.md]
│   │   ├── admin/                # Admin UI [AGENTS.md]
│   │   ├── submission/           # Submission UI [AGENTS.md]
│   │   └── ui_web/               # Legacy templates [AGENTS.md]
│   └── data/                     # Data management [AGENTS.md]
│       ├── pdfs/                 # PDF storage [AGENTS.md]
│       ├── parsed/               # Parsed content [AGENTS.md]
│       ├── vectorized/           # Embeddings [AGENTS.md]
│       │   └── embeddings/       # Vector data [AGENTS.md]
│       └── metadata/             # Scrape metadata [AGENTS.md]
│
├── scripts/                       # System scripts [AGENTS.md]
│   ├── main.py                   # Interactive menu
│   ├── startup/                  # Service orchestration [AGENTS.md]
│   ├── development/              # Dev workflows [AGENTS.md]
│   ├── deployment/               # Contract deployment [AGENTS.md]
│   └── utilities/                # Maintenance [AGENTS.md]
│
├── config/                        # Configuration [AGENTS.md]
│   ├── environment/              # Env setup [AGENTS.md]
│   └── wallet/                   # Wallet config [AGENTS.md]
│
├── docs/                          # Documentation [AGENTS.md]
│   ├── Blueprint for Syntheverse  # Central vision
│   ├── api/                       # API docs [AGENTS.md]
│   ├── architecture/              # Architecture [AGENTS.md]
│   ├── contributors/              # Contributor docs [AGENTS.md]
│   └── deployment/                # Deployment guides [AGENTS.md]
│
├── tests/                         # Test suites [AGENTS.md]
│   ├── results/                   # Test reports
│   └── outputs/                   # Test outputs
│
├── tools/                         # Dev tools [AGENTS.md]
│   └── hardhat/                   # Hardhat config [AGENTS.md]
│
├── examples/                      # Demo code [AGENTS.md]
│
├── data/                          # Runtime blockchain state [AGENTS.md]
│   └── blockchain/                # L1 state files
│
├── test_outputs/                  # Test state storage [AGENTS.md]
│   ├── blockchain/                # Test L1 state
│   ├── poc_reports/               # PoC reports
│   └── pod_reports/               # PoD reports
│
├── analysis_results/              # Embedding analysis [AGENTS.md]
│
└── uploads/                       # File uploads [AGENTS.md]
```

## Cross-References

### Core System Components
- [docs/Blueprint for Syntheverse](docs/Blueprint for Syntheverse) - Central vision document
- [docs/BLUEPRINT_IMPLEMENTATION_STATUS.md](docs/BLUEPRINT_IMPLEMENTATION_STATUS.md) - Implementation tracking
- [docs/BLUEPRINT_IMPLEMENTATION_ROADMAP.md](docs/BLUEPRINT_IMPLEMENTATION_ROADMAP.md) - Development phases

### Quick Start Guides
- [docs/QUICK_START_POC_UI.md](docs/QUICK_START_POC_UI.md) - Getting started
- [docs/START_WEB_UI.md](docs/START_WEB_UI.md) - Web UI startup
- [docs/POC_SUBMISSION_TO_ALLOCATION_FLOW.md](docs/POC_SUBMISSION_TO_ALLOCATION_FLOW.md) - Complete workflow

### Technical Documentation
- [docs/L1_EXPLANATION.md](docs/L1_EXPLANATION.md) - Layer 1 blockchain
- [docs/L2_SYSTEM_PROMPT.md](docs/L2_SYSTEM_PROMPT.md) - Layer 2 evaluation
- [docs/L2_TOKENOMICS.md](docs/L2_TOKENOMICS.md) - Token allocation

## Responsibilities

### System Coordination
- Orchestrate three-layer architecture (Blockchain, Evaluation, UI)
- Manage Proof-of-Contribution evaluation pipeline
- Coordinate between frontend, backend, and blockchain components
- Ensure system reliability and performance

### Quality Assurance
- Maintain code standards and documentation consistency
- Validate blueprint alignment across all components
- Ensure functional, well-documented, clearly reasoned code
- Remove unnecessary adjectives from names and documentation

### Development Workflow
- Support test-driven development practices
- Maintain modular architecture with clear interfaces
- Ensure comprehensive testing coverage
- Facilitate collaboration across development teams

## Interfaces

### External Interfaces
- **GitHub Repository**: Public access to source code and documentation
- **Web Interfaces**: Dashboard, submission forms, sandbox map, registry
- **API Endpoints**: REST APIs for PoC evaluation and data access
- **Blockchain Networks**: Base testnet and mainnet integration

### Internal Interfaces
- **Layer Communication**: Frontend ↔ API ↔ Core ↔ Blockchain
- **Data Flow**: Submission → Evaluation → Registration → Token Allocation
- **Configuration**: Environment variables and configuration files
- **Testing**: Comprehensive test suites across all components

## Dependencies

### Core Dependencies
- **Python 3.8+**: Backend services and evaluation engine
- **Node.js 18+**: Frontend development and Next.js applications
- **Solidity**: Smart contract development
- **Foundry/Anvil**: Blockchain development and testing

### External Services
- **GROQ API**: AI-powered evaluation and analysis
- **Base Blockchain**: Layer 2 blockchain for token and certificate management
- **Git**: Version control and collaboration
- **Docker** (optional): Containerized deployment

### Development Tools
- **pytest**: Python testing framework
- **ESLint/Prettier**: JavaScript/TypeScript code quality
- **Hardhat**: Smart contract deployment and testing
- **GitHub Actions**: CI/CD pipeline

## Development

### Development Workflow
- **Test-Driven Development**: All features developed with comprehensive tests
- **Modular Architecture**: Clear separation of concerns across layers
- **Blueprint Alignment**: All development follows Syntheverse Blueprint
- **Code Review**: Pull requests required for all changes

### Environment Setup
- **Local Development**: Use provided startup scripts for full system
- **Blockchain Testing**: Foundry + Anvil for local blockchain development
- **API Integration**: GROQ API key required for evaluation features
- **Cross-Platform**: Works on macOS, Linux, and Windows (WSL)

### Quality Standards
- **Code Coverage**: Minimum 80% test coverage required
- **Documentation**: All code changes must update relevant documentation
- **Security**: Regular security audits and dependency updates
- **Performance**: Continuous monitoring of system performance metrics

## Testing

### Test Categories
- **Unit Tests**: Individual component testing
- **Integration Tests**: Cross-component interaction testing
- **End-to-End Tests**: Complete workflow validation
- **Performance Tests**: System load and response time testing

### Test Execution
```bash
# Run all tests
cd tests && ./run_tests.sh --all

# Run specific test categories
./run_tests.sh --unit
./run_tests.sh --integration
./run_tests.sh --e2e
```

### Test Environment
- **Local Testing**: Anvil blockchain for isolated testing
- **CI/CD**: GitHub Actions for automated testing
- **Staging**: Base Sepolia testnet for integration testing
- **Production**: Base mainnet monitoring and validation
