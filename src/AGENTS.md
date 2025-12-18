# Source Code Agents

## Purpose

The `src/` directory contains all source code for the Syntheverse system, organized by functional area.

## Key Modules

### API Services (`api/`)

- **`poc-api/`**: Flask API server connecting Next.js frontend to Layer 2 backend
- **`rag_api/`**: FastAPI server for document processing and RAG queries

### Blockchain (`blockchain/`)

- **`contracts/`**: Solidity smart contracts (SYNTH token, POCRegistry)
- **`layer1/`**: Python implementation of Layer 1 blockchain logic

### Core Logic (`core/`)

- **`layer2/`**: PoC and PoD evaluation engines, archive system, tokenomics, sandbox map

### Frontend (`frontend/`)

- **`poc-frontend/`**: Next.js 14 application (main PoC dashboard)
- **`web-legacy/`**: Legacy Flask web interface
- **`submission/`**: Basic submission interface
- **`admin/`**: Administrative interface

### Data (`data/`)

- **`pdfs/`**: Downloaded PDF documents
- **`parsed/`**: Parsed text chunks
- **`vectorized/`**: Embeddings and metadata
- **`metadata/`**: Scraping metadata

## Integration Points

- APIs serve as bridges between frontend and backend
- Layer 2 orchestrates evaluation and token allocation
- Layer 1 handles blockchain operations
- Data layer supports RAG pipeline

## Development Guidelines

- Maintain clear separation between components
- Use environment variables for configuration
- Follow component-specific coding standards
- Update documentation when making changes



