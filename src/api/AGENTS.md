# API Services Agents

## Purpose

The `api/` directory contains API services that connect different parts of the Syntheverse system.

## Key Modules

### PoC API (`poc-api/`)

Flask REST API server that:
- Connects Next.js frontend to Layer 2 backend
- Handles contribution submissions and file uploads
- Provides endpoints for archive, sandbox map, and tokenomics
- Integrates with blockchain for certificate registration

**Key Files:**
- `app.py`: Main Flask application
- `server.py`: Server setup and configuration

### RAG API (`rag_api/`)

FastAPI server for document processing:
- Semantic search over vectorized documents
- LLM integration (Groq, Ollama, HuggingFace)
- Document scraping, parsing, and vectorization pipeline
- Web UI for interactive queries

**Key Components:**
- `api/rag_api.py`: Main FastAPI server
- `scraper/`: PDF scraping from Zenodo
- `parser/`: PDF parsing into text chunks
- `vectorizer/`: Embedding generation

## Integration Points

- PoC API connects to Layer 2 PoC Server
- RAG API used for document search (not for PoC evaluation)
- Both APIs use Groq API for LLM operations
- APIs handle CORS for frontend access

## Development Guidelines

- Use Flask for PoC API (legacy compatibility)
- Use FastAPI for RAG API (modern async support)
- Implement consistent error handling
- Validate all inputs
- Use environment variables for API keys
- Document all endpoints

## Common Patterns

- RESTful API design
- JSON request/response format
- Error handling with consistent structure
- File upload validation
- CORS configuration for frontend