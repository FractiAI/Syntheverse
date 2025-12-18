# Syntheverse Repository Structure

This document outlines the organized directory structure following GitHub best practices for the Syntheverse PoC system.

## 📁 Root Level Structure

```
syntheverse/
├── 📄 README.md                 # Main project documentation
├── 📄 LICENSE                   # MIT License
├── 📄 CONTRIBUTING.md           # Contribution guidelines
├── 📄 CODE_OF_CONDUCT.md        # Code of conduct
├── 📄 SECURITY.md               # Security policy
├── 📄 .gitignore                # Git ignore patterns
├── 📄 PROJECT_STRUCTURE.md      # This file
├── 📁 src/                      # Source code
├── 📁 scripts/                  # Build/deployment scripts
├── 📁 docs/                     # Documentation
├── 📁 examples/                 # Example code and demos
├── 📁 tests/                    # Test suites
├── 📁 tools/                    # Development tools
└── 📁 config/                   # Configuration files
```

## 📁 Source Code (`src/`)

```
src/
├── 📁 api/                      # Backend API services
│   ├── 📁 poc-api/             # Main PoC API (Flask)
│   ├── 📁 rag-api/             # RAG API for document processing
│   └── 📁 test_outputs/         # API test data and outputs
├── 📁 blockchain/              # Blockchain/smart contract code
│   ├── 📁 contracts/           # Solidity contracts (Foundry)
│   ├── 📁 foundry/             # Foundry configuration
│   ├── 📁 hardhat/             # Hardhat configuration
│   ├── 📁 layer1/              # Layer 1 blockchain logic
│   ├── 📁 scripts/             # Deployment scripts
│   └── 📁 test/                # Contract tests
├── 📁 core/                    # Core business logic
│   └── 📁 layer2/              # PoC evaluation and tokenomics
├── 📁 data/                    # Data files and resources
├── 📁 frontend/                # Frontend applications
│   ├── 📁 poc-frontend/        # Main Next.js PoC UI
│   ├── 📁 web-legacy/          # Legacy Flask web UI
│   └── 📁 submission/          # Submission form UI
└── 📁 ui/                      # Additional UI components
```

## 📁 Scripts (`scripts/`)

```
scripts/
├── 📁 development/             # Development workflow scripts
├── 📁 startup/                 # System startup scripts
│   ├── 📄 start_servers.py     # Main startup script
│   ├── 📄 start_servers_simple.py
│   └── 📄 start_servers.sh
├── 📁 deployment/              # Deployment scripts
│   └── 📄 deploy_contracts.py
└── 📁 utilities/               # Maintenance utilities
    └── 📄 clear_persistent_memory.py
```

## 📁 Documentation (`docs/`)

```
docs/
├── 📄 README.md                # Documentation index
├── 📁 api/                     # API documentation
├── 📁 architecture/            # System architecture docs
├── 📁 contributors/            # Contributor resources
├── 📁 deployment/              # Deployment guides
└── 📁 user-guides/             # User manuals
```

## 📁 Examples (`examples/`)

```
examples/
├── 📄 README.md                # Examples overview
├── 📄 demo_poc_system.py       # Complete PoC workflow demo
├── 📄 demo_interface.html      # Static UI demonstration
└── 📄 test_ui.html             # Test interface
```

## 📁 Tests (`tests/`)

```
tests/
├── 📁 outputs/                 # Test output files
├── 📄 test_full_submission_flow.py
├── 📄 test_poc_frontend.sh
├── 📄 test_rag_api.py
└── 📄 test_submission_flow.py
```

## 📁 Tools (`tools/`)

```
tools/
├── 📄 PROJECT_STRUCTURE.md     # This file (duplicate)
├── 📄 QUICK_TEST.md            # Quick testing guide
├── 📄 SERVICE_MANAGEMENT.md    # Service management docs
├── 📄 TESTING_GUIDE.md         # Comprehensive testing guide
├── 📁 foundry/                 # Foundry tools
└── 📁 hardhat/                 # Hardhat tools
```

## 📁 Configuration (`config/`)

```
config/
├── 📄 .env                     # Environment variables
├── 📁 environment/             # Environment-specific configs
│   ├── 📄 EMAIL_TROUBLESHOOTING.md
│   ├── 📄 GET_GROQ_KEY.md
│   └── 📄 SETUP_GROQ.md
└── 📁 wallet/                  # Wallet configuration
    └── 📄 test-wallet-setup.md
```

## 🏗️ Key Design Principles

### 1. **Separation of Concerns**
- Source code in `src/`
- Scripts in `scripts/`
- Documentation in `docs/`
- Examples in `examples/`

### 2. **Logical Grouping**
- Related functionality grouped together
- Clear naming conventions
- Hierarchical organization

### 3. **GitHub Best Practices**
- Standard directory names
- Clear documentation structure
- Proper ignore patterns
- Organized by function, not technology

### 4. **Scalability**
- Room for growth in each directory
- Easy to add new components
- Clear extension points

## 🚀 Quick Access

**Start the system:**
```bash
python scripts/startup/start_servers.py
```

**Run tests:**
```bash
cd tests && python test_poc_frontend.sh
```

**View documentation:**
```bash
open docs/README.md
```

**Deploy contracts:**
```bash
python scripts/deployment/deploy_contracts.py
```




