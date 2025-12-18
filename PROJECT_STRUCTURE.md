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
├── 📁 data/                     # Data files and resources
├── 📁 tools/                    # Development tools
└── 📁 config/                   # Configuration files
```

## 📁 Source Code (`src/`)

```
src/
├── 📁 api/                      # Backend API services
│   ├── 📁 poc-api/             # Main PoC API (Flask)
│   │   ├── 📄 app.py           # Flask application
│   │   ├── 📄 server.py        # Server implementation
│   │   └── 📁 uploads/         # File uploads directory
│   └── 📁 rag_api/             # RAG API for document processing
│       ├── 📁 analysis/        # Analysis modules
│       │   ├── 📁 cli/         # Command line tools
│       │   └── 📄 *.py         # Analysis utilities
│       ├── 📁 api/             # API endpoints
│       ├── 📁 parser/          # Document parsing
│       ├── 📁 scraper/         # Web scraping tools
│       └── 📁 vectorizer/      # Vectorization tools
├── 📁 blockchain/              # Blockchain/smart contract code
│   ├── 📁 contracts/           # Solidity contracts and deployment
│   │   ├── 📁 src/             # Contract source code
│   │   ├── 📁 test/            # Contract tests
│   │   ├── 📁 script/          # Deployment scripts
│   │   ├── 📁 lib/             # External libraries
│   │   ├── 📁 deploy/          # Deployment scripts
│   │   └── 📄 foundry.toml     # Foundry configuration
│   ├── 📁 layer1/              # Python Layer 1 blockchain logic
│   ├── 📁 test/                # Additional tests
│   └── 📄 *.py                 # Blockchain integration scripts
├── 📁 core/                    # Core business logic
│   └── 📁 layer2/              # PoC evaluation and tokenomics
│       ├── 📁 allocator/       # Token allocation logic
│       ├── 📁 evaluator/       # PoC evaluation engine
│       └── 📄 *.py             # Core services
├── 📁 data/                    # Data files and resources
│   ├── 📁 metadata/            # Metadata storage
│   ├── 📁 parsed/              # Parsed document data
│   ├── 📁 pdfs/                # PDF document storage
│   └── 📁 vectorized/          # Vectorized data and embeddings
├── 📁 frontend/                # Frontend applications
│   ├── 📁 poc-frontend/        # Main Next.js PoC UI
│   ├── 📁 web-legacy/          # Legacy Flask web UI
│   ├── 📁 submission/          # Submission form UI
│   ├── 📁 admin/               # Administrative interface
│   └── 📁 ui_web/              # Web UI components
└── 📁 test_outputs/            # Test output data
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
    ├── 📄 clear_persistent_memory.py
    ├── 📄 test_setup_functions.sh    # Test setup functions
    ├── 📄 test_startup_readiness.sh  # Test startup readiness
    └── 📄 test_verify.sh             # Test verification script
```

## 📁 Documentation (`docs/`)

```
docs/
├── 📄 README.md                # Documentation index
├── 📁 api/                     # API documentation
├── 📁 architecture/            # System architecture docs
├── 📁 contributors/            # Contributor resources
├── 📁 deployment/              # Deployment guides
└── 📄 *.md                     # Technical documentation files
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
├── 📁 results/                 # Test result logs and reports
├── 📄 conftest.py              # Pytest configuration
├── 📄 test_*.py                # Python test modules (20+ test files)
├── 📄 test_*.sh                # Shell script tests
├── 📄 run_tests.sh             # Test runner script
├── 📄 test_config.json         # Test configuration
└── 📄 *.md                     # Test documentation
```

## 📁 Data (`data/`)

```
data/
├── 📄 blockchain.json          # Blockchain state data
├── 📄 poc_contract.json        # PoC contract state
└── 📄 synth_token.json         # SYNTH token contract state
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


