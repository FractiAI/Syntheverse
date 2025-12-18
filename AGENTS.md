# Syntheverse System Agents

## 📋 Overview

Syntheverse is a hydrogen-holographic fractal blockchain game with a Proof-of-Contribution (PoC) system. This document describes the system architecture and component responsibilities.

## 🏗️ System Architecture

### Three-Layer Design

1. **Layer 1 (Blockchain)**: Syntheverse Blockmine L1 with smart contracts on Base
2. **Layer 2 (Evaluation)**: PoC evaluation engine with archive-first redundancy detection
3. **UI Layer**: Next.js frontend with Flask API bridge

**Quick Navigation:**
- [📁 Directory Overview](#-directory-overview)
- [🔧 Key Components](#-key-components)
- [⚙️ Development Guidelines](#️-development-guidelines)
- [🔗 Cross-References](#-cross-references)

## 📁 Directory Overview

| Directory | Purpose | AGENTS.md |
|-----------|---------|-----------|
| [`src/`](#-key-components) | Source code | [src/AGENTS.md](src/AGENTS.md) |
| [`scripts/`](#-key-components) | System scripts | [scripts/AGENTS.md](scripts/AGENTS.md) |
| [`config/`](#-key-components) | Configuration | [config/AGENTS.md](config/AGENTS.md) |
| [`docs/`](#-key-components) | Documentation | [docs/AGENTS.md](docs/AGENTS.md) |
| [`tests/`](#-key-components) | Test suites | [tests/AGENTS.md](tests/AGENTS.md) |
| [`tools/`](#-key-components) | Development tools | [tools/AGENTS.md](tools/AGENTS.md) |
| [`examples/`](#-key-components) | Demo code | [examples/AGENTS.md](examples/AGENTS.md) |
| [`data/`](#-key-components) | Runtime data and blockchain state | [data/AGENTS.md](data/AGENTS.md) |
| [`test_outputs/`](#-key-components) | Test state storage | [test_outputs/AGENTS.md](test_outputs/AGENTS.md) |
| [`analysis_results/`](#-key-components) | Embedding analysis | [analysis_results/AGENTS.md](analysis_results/AGENTS.md) |
| [`uploads/`](#-key-components) | File uploads | [uploads/AGENTS.md](uploads/AGENTS.md) |

## Key Components

### Source Code (`src/`)

- **`api/`**: API services (PoC API, RAG API)
  - [poc-api/AGENTS.md](src/api/poc-api/AGENTS.md) - Flask API server
  - [rag_api/AGENTS.md](src/api/rag_api/AGENTS.md) - FastAPI RAG server
  - [rag-api/AGENTS.md](src/api/rag-api/AGENTS.md) - Alternative RAG API implementation
- **`blockchain/`**: Blockchain infrastructure (contracts, Layer 1)
  - [contracts/AGENTS.md](src/blockchain/contracts/AGENTS.md) - Solidity contracts
  - [layer1/AGENTS.md](src/blockchain/layer1/AGENTS.md) - Python blockchain
- **`core/`**: Core business logic (Layer 2 evaluation, tokenomics)
  - [layer2/AGENTS.md](src/core/layer2/AGENTS.md) - PoC evaluation engine
  - [utils/AGENTS.md](src/core/utils/AGENTS.md) - Utilities
- **`frontend/`**: Frontend applications (Next.js, legacy Flask)
  - [poc-frontend/AGENTS.md](src/frontend/poc-frontend/AGENTS.md) - Next.js dashboard
- **`data/`**: Data management (PDFs, parsed content, embeddings, blockchain state)
  - [pdfs/AGENTS.md](src/data/pdfs/AGENTS.md) - PDF document storage
  - [parsed/AGENTS.md](src/data/parsed/AGENTS.md) - Parsed text content
  - [vectorized/AGENTS.md](src/data/vectorized/AGENTS.md) - Embeddings and vectors
  - [metadata/AGENTS.md](src/data/metadata/AGENTS.md) - Scraping metadata
  - [blockchain/AGENTS.md](data/blockchain/AGENTS.md) - Runtime blockchain state

### Scripts (`scripts/`)

- **`startup/`**: System startup scripts - [AGENTS.md](scripts/startup/AGENTS.md)
- **`development/`**: Development workflow - [AGENTS.md](scripts/development/AGENTS.md)
- **`deployment/`**: Contract deployment - [AGENTS.md](scripts/deployment/AGENTS.md)
- **`utilities/`**: Maintenance utilities - [AGENTS.md](scripts/utilities/AGENTS.md)

### Configuration (`config/`)

- **`environment/`**: Environment configuration - [AGENTS.md](config/environment/AGENTS.md)
- **`wallet/`**: Wallet setup - [AGENTS.md](config/wallet/AGENTS.md)

## ⚙️ Development Guidelines

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

## 🔄 Common Patterns

- Archive-first evaluation: All contributions stored immediately
- Multi-metal system: Gold, Silver, Copper qualifications
- Direct LLM integration: Groq API for evaluations
- File-based storage: JSON files for persistent state

**Navigate:** [Blueprint Alignment](#blueprint-alignment) | [Responsibilities](#responsibilities) | [Testing](#testing)

## Blueprint Alignment

The Syntheverse system is architected around the **Blueprint for Syntheverse** document, which defines the hydrogen-holographic fractal blockchain vision. All components align to this central blueprint:

### Three-Layer Architecture ([Blueprint §3](docs/Blueprint for Syntheverse))
- **✅ Layer 1 (Blockchain)**: `src/blockchain/` - Syntheverse Blockmine L1 with Base network smart contracts
- **✅ Layer 2 (Evaluation)**: `src/core/layer2/` - PoC evaluation engine with archive-first redundancy detection
- **✅ UI Layer**: `src/frontend/` + `src/api/` - Next.js dashboard with Flask API bridge

### Experience Walkthrough Implementation ([Blueprint §1](docs/Blueprint for Syntheverse))
- **✅ PoC Submission** ([§1.1](docs/Blueprint for Syntheverse)): `src/frontend/poc-frontend/` → `src/api/poc-api/` → `src/core/layer2/poc_server.py`
- **✅ Evaluation Pipeline** ([§1.3](docs/Blueprint for Syntheverse)): Archive-first storage → Hydrogen holographic fractal scoring → Human approval
- **✅ Blockchain Registration** ([§1.4](docs/Blueprint for Syntheverse)): $200 registration → "I was here first" recognition → SYNTH token allocation
- **✅ Dashboard Interaction** ([§1.5](docs/Blueprint for Syntheverse)): `src/frontend/poc-frontend/` exploration and amplification display
- **📋 Financial Alignment** ([§1.6](docs/Blueprint for Syntheverse)): Copper/Silver/Gold tier foundation via `docs/contributors/SYNTH_Pitch.md`

### System Architecture Components ([Blueprint §3](docs/Blueprint for Syntheverse))
- **✅ PoC Pipeline** ([§3.1](docs/Blueprint for Syntheverse)): `scripts/startup/` orchestration → `src/core/layer2/` evaluation → `src/blockchain/` registration
- **✅ Contribution Scoring** ([§3.2](docs/Blueprint for Syntheverse)): `src/core/layer2/evaluator/` novelty/density/coherence/alignment (0-10,000 scale)
- **✅ Token Allocation** ([§3.3](docs/Blueprint for Syntheverse)): `src/core/layer2/tokenomics_state.py` epoch-based SYNTH distribution
- **✅ Metallic Amplifications** ([§3.4](docs/Blueprint for Syntheverse)): `src/core/layer2/poc_archive.py` Gold/Silver/Copper multipliers (1.5×/1.2×/1.15×)

### Financial & Alignment Framework ([Blueprint §4](docs/Blueprint for Syntheverse))
- **✅ Registration Fees**: $200 per approved PoC ($0 for evaluation) - implemented in `src/blockchain/contracts/POCRegistry.sol`
- **📋 Alignment Tiers**: Copper ($10K-25K)/Silver ($50K-100K)/Gold ($250K-500K) - foundation in `docs/contributors/SYNTH_Pitch.md`

### AI & Ecosystem Integration ([Blueprint §5](docs/Blueprint for Syntheverse))
- **✅ GROQ API Integration**: Required for all LLM services via `config/environment/SETUP_GROQ.md` and `src/core/utils/env_loader.py`
- **✅ Archive Training**: All PoCs stored immediately in `src/core/layer2/poc_archive.py` to train evolving Syntheverse AI
- **✅ Hydrogen Holographic Fractal**: Measurable, reproducible evaluation methodology implemented

### Governance & Operations ([Blueprint §6](docs/Blueprint for Syntheverse))
- **✅ Human Approval**: Required for all PoC evaluations through operator oversight
- **✅ Operator Control**: Epochs and thresholds managed through `src/core/layer2/tokenomics_state.py`
- **✅ Transparency**: SYNTH allocations and PoC scores auditable on-chain via `src/blockchain/` Layer 1
- **📋 Stewardship**: Founder-controlled with scalable FractiAI Team funding model

### Complete Workflow ([Blueprint §7](docs/Blueprint for Syntheverse))
1. **✅ Zenodo Community Submission** → Initial peer feedback and novelty signals
2. **✅ Syntheverse Discovery** → Learning about blockchain anchoring and AI training
3. **✅ PoC Evaluation** → Hydrogen holographic fractal scoring (0-10,000 across dimensions)
4. **✅ Human Approval** → Ecosystem alignment verification
5. **✅ On-Chain Registration** → $200 payment for permanent anchoring and "I was here first" recognition
6. **✅ Dashboard Exploration** → Scores, metallic amplifications, ecosystem impact visualization
7. **📋 Alignment Participation** → Optional Copper/Silver/Gold tier engagement

### Development Standards Compliance ([Blueprint Vision §0](docs/Blueprint for Syntheverse))
- **✅ "Follow modular, well-documented, clearly reasoned code"** → Implemented across entire codebase
- **✅ "Remove unnecessary adjectives from names"** → Active process, naming conventions enforced
- **✅ "Documentation shows rather than tells"** → All AGENTS.md and README.md files demonstrate functionality
- **✅ "Every folder level must have AGENTS.md and README.md"** → Verified across entire repository

### Implementation Status
- **✅ 85% Blueprint Complete** - Core evaluation pipeline, blockchain integration, tokenomics engine, UI dashboard fully operational
- **🟡 Enhanced Features Ready** - Fee structure implemented, metallic amplifications validated, multi-interface support
- **📋 Next Phase Development** - See `docs/BLUEPRINT_IMPLEMENTATION_ROADMAP.md` for Phase 2-3 roadmap
- **📊 Live Tracking** - See `docs/BLUEPRINT_IMPLEMENTATION_STATUS.md` for current alignment metrics and gap analysis

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
│   │   ├── rag_api/              # FastAPI RAG [AGENTS.md]
│   │   │   ├── api/              # RAG API server [AGENTS.md]
│   │   │   ├── analysis/         # Embedding analysis [AGENTS.md]
│   │   │   │   └── cli/          # CLI tools [AGENTS.md]
│   │   │   ├── parser/           # PDF parsing [AGENTS.md]
│   │   │   ├── scraper/          # PDF scraping [AGENTS.md]
│   │   │   └── vectorizer/       # Embedding generation [AGENTS.md]
│   │   └── rag-api/              # Alternative RAG API [AGENTS.md]
│   │       └── analysis/         # Alternative analysis [AGENTS.md]
│   │           └── cli/          # Alternative CLI [AGENTS.md]
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
│   ├── data/                     # Data management [AGENTS.md]
│   │   ├── pdfs/                 # PDF storage [AGENTS.md]
│   │   ├── parsed/               # Parsed content [AGENTS.md]
│   │   ├── vectorized/           # Embeddings [AGENTS.md]
│   │   │   └── embeddings/       # Vector data [AGENTS.md]
│   │   └── metadata/             # Scrape metadata [AGENTS.md]
│   └── test_outputs/             # Test result storage [AGENTS.md]
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
│   ├── results/                   # Test reports [AGENTS.md]
│   └── outputs/                   # Test outputs [AGENTS.md]
│
├── tools/                         # Dev tools [AGENTS.md]
│   └── hardhat/                   # Hardhat config [AGENTS.md]
│
├── examples/                      # Demo code [AGENTS.md]
│
├── data/                          # Runtime data and blockchain state [AGENTS.md]
│   └── blockchain/                # L1 state files [AGENTS.md]
│
├── test_outputs/                  # Test state storage [AGENTS.md]
│   ├── blockchain/                # Test L1 state [AGENTS.md]
│   ├── poc_reports/               # PoC reports
│   └── pod_reports/               # PoD reports [AGENTS.md]
│
├── analysis_results/              # Embedding analysis [AGENTS.md]
│
└── uploads/                       # File uploads [AGENTS.md]
```

## 🔗 Cross-References

### 📋 Blueprint Documentation ([docs/Blueprint for Syntheverse](docs/Blueprint for Syntheverse))
- **Central Vision Document**: Hydrogen-holographic fractal blockchain blueprint with complete system specifications
- **Implementation Mapping**: Direct references to code locations for all Blueprint sections (§1-§7)
- **Three-Layer Architecture**: L1 (Blockchain) → L2 (Evaluation) → UI Layer implementation guide

**Navigate:** [Overview](#-overview) | [System Architecture](#️-system-architecture) | [Responsibilities](#responsibilities)

### Implementation Tracking
- **[BLUEPRINT_IMPLEMENTATION_STATUS.md](docs/BLUEPRINT_IMPLEMENTATION_STATUS.md)**: Real-time alignment metrics and gap analysis
- **[BLUEPRINT_IMPLEMENTATION_ROADMAP.md](docs/BLUEPRINT_IMPLEMENTATION_ROADMAP.md)**: Prioritized development phases and milestones

### Quick Start & User Guides
- **[QUICK_START_POC_UI.md](docs/QUICK_START_POC_UI.md)**: Getting started guide for contributors ([Blueprint §1.1](docs/Blueprint for Syntheverse))
- **[START_WEB_UI.md](docs/START_WEB_UI.md)**: Dashboard access and interaction guide ([Blueprint §1.5](docs/Blueprint for Syntheverse))
- **[POC_SUBMISSION_TO_ALLOCATION_FLOW.md](docs/POC_SUBMISSION_TO_ALLOCATION_FLOW.md)**: End-to-end workflow ([Blueprint §7](docs/Blueprint for Syntheverse))

### Technical Implementation Documentation
- **[L1_EXPLANATION.md](docs/L1_EXPLANATION.md)**: Blockchain registration process ([Blueprint §1.4](docs/Blueprint for Syntheverse))
- **[L2_SYSTEM_PROMPT.md](docs/L2_SYSTEM_PROMPT.md)**: Hydrogen holographic evaluation methodology ([Blueprint §3.2](docs/Blueprint for Syntheverse))
- **[L2_TOKENOMICS.md](docs/L2_TOKENOMICS.md)**: SYNTH allocation and epoch system ([Blueprint §3.3](docs/Blueprint for Syntheverse))
- **[DUPLICATE_PREVENTION.md](docs/DUPLICATE_PREVENTION.md)**: Archive-first redundancy system ([Blueprint §3.1](docs/Blueprint for Syntheverse))

### System Overview & Summary
- **[POC_SYSTEM_SUMMARY.md](docs/POC_SYSTEM_SUMMARY.md)**: Complete Syntheverse system description
- **[POC_UPGRADE.md](docs/POC_UPGRADE.md)**: System enhancement and migration guides
- **[SYNTH_Pitch.md](docs/contributors/SYNTH_Pitch.md)**: Token economics and alignment tiers ([Blueprint §4](docs/Blueprint for Syntheverse))

### Configuration & Setup
- **[SETUP_GROQ.md](config/environment/SETUP_GROQ.md)**: Complete API key configuration ([Blueprint §5](docs/Blueprint for Syntheverse))
- **[README.md](config/environment/README.md)**: Centralized environment management
- **[GET_GROQ_KEY.md](config/environment/GET_GROQ_KEY.md)**: Step-by-step key acquisition process

### Component-Specific References
- **Source Code**: [src/AGENTS.md](src/AGENTS.md) - Complete source code organization
- **API Services**: [src/api/AGENTS.md](src/api/AGENTS.md) - API service documentation
- **Layer 2 Engine**: [src/core/layer2/AGENTS.md](src/core/layer2/AGENTS.md) - Evaluation engine details
- **Blockchain Layer**: [src/blockchain/AGENTS.md](src/blockchain/AGENTS.md) - Layer 1 implementation
- **Frontend UI**: [src/frontend/AGENTS.md](src/frontend/AGENTS.md) - User interface components

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
