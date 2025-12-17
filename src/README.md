# Source Code

The `src/` directory contains source code for the Syntheverse system.

## Directory Structure

### API Services (`api/`)

REST API servers:
- **`poc-api/`**: Flask server connecting Next.js frontend to Layer 2 backend
- **`rag-api/`**: FastAPI server for document processing and RAG queries

### Blockchain (`blockchain/`)

Blockchain infrastructure:
- **`contracts/`**: Solidity smart contracts (SYNTH token, POCRegistry)
- **`layer1/`**: Python blockchain implementation

### Core Logic (`core/`)

Business logic:
- **`layer2/`**: PoC evaluation, archive system, tokenomics, sandbox map

### Frontend (`frontend/`)

User interfaces:
- **`poc-frontend/`**: Next.js 14 dashboard application
- **`web-legacy/`**: Legacy Flask web interface
- **`submission/`**: Basic submission interface
- **`admin/`**: Administrative interface

### Data (`data/`)

Data processing pipeline:
- **`pdfs/`**: Downloaded PDF documents
- **`parsed/`**: Parsed text chunks
- **`vectorized/`**: Embeddings and metadata
- **`metadata/`**: Scraping metadata

## Development Setup

### Environment Variables

Set required environment variables:
```bash
export GROQ_API_KEY=your-key-here
```

### Dependencies

Install Python packages:
```bash
pip install -r requirements.txt
```

### Component Setup

See individual component README files for setup instructions.

## Architecture

- APIs connect frontend to backend services
- Layer 2 manages evaluation and token allocation
- Layer 1 handles blockchain operations
- Data pipeline supports RAG functionality

## Guidelines

- Maintain component separation
- Use environment variables for configuration
- Follow coding standards
- Update documentation with changes
