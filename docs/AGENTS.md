# Documentation Agents

## Purpose

Documentation for the Syntheverse system including architecture, API documentation, user guides, and contributor resources.

## Key Modules

### API Documentation (`api/`)

- **`RAG_API.md`**: RAG API documentation
- **`README.md`**: API documentation overview

### Architecture (`architecture/`)

- **`README.md`**: System architecture overview

### Contributors (`contributors/`)

- **`SYNTH_Pitch.md`**: SYNTH token pitch document

### Deployment (`deployment/`)

- **`README.md`**: Deployment guides

### Main Documentation

- **`POC_SYSTEM_SUMMARY.md`**: System overview
- **`POC_SUBMISSION_SYSTEM.md`**: Complete PoC submission system overview
- **`POC_UPGRADE.md`**: System upgrade information
- **`POC_SUBMISSION_TO_ALLOCATION_FLOW.md`**: End-to-end flow documentation
- **`L1_EXPLANATION.md`**: Layer 1 blockchain explanation
- **`L2_SYSTEM_PROMPT.md`**: Layer 2 system prompt documentation
- **`L2_TOKENOMICS.md`**: Tokenomics and reward system
- **`DUPLICATE_PREVENTION.md`**: Archive-first redundancy system
- **`QUICK_START_POC_UI.md`**: Quick start guide
- **`START_WEB_UI.md`**: Web UI startup guide
- **`EMAIL_CONFIGURATION_GUIDE.md`**: Email setup guide
- **`EMAIL_TROUBLESHOOTING.md`**: Historical email functionality documentation

## Environment Configuration

### GROQ_API_KEY Setup
- **Required for**: All LLM-powered services (RAG API, PoC evaluation, Layer 2)
- **Location**: `.env` file in project root
- **Format**: `GROQ_API_KEY=gsk_your-key-here`
- **How to get**: Visit https://console.groq.com/ and create a free API key
- **Loading**: Use centralized `src.core.utils.load_groq_api_key()` utility
- **Security**: Never commit `.env` files to repository

### Configuration Files
- `config/environment/README.md` - Complete environment setup guide
- `config/environment/GET_GROQ_KEY.md` - Step-by-step API key acquisition
- `config/environment/SETUP_GROQ.md` - Groq integration setup

## Integration Points

- Documentation references code components
- Guides reference configuration files
- Architecture docs describe system design
- API docs describe endpoints

## Development Guidelines

- Keep documentation up-to-date with code
- Use clear, understated language
- Remove unnecessary adjectives
- Include code examples where helpful
- Document all public APIs
- Keep guides current with UI

## Common Patterns

- System overview documents
- Architecture diagrams
- API endpoint documentation
- Setup and configuration guides
- User guides and tutorials



