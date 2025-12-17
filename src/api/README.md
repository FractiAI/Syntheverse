# API Services

## Purpose

API services that connect different parts of the Syntheverse system, providing REST endpoints for frontend applications and backend integration.

## Components

### PoC API (`poc-api/`)

Flask REST API server connecting Next.js frontend to Layer 2 backend.

**Features:**
- Contribution submission and file uploads
- Archive statistics and contribution retrieval
- Sandbox map data generation
- Tokenomics statistics and epoch information
- Blockchain certificate registration

**Status:** ✅ Fully Operational

### RAG API (`rag-api/`)

FastAPI server for document processing and RAG queries.

**Features:**
- Semantic search over vectorized documents
- LLM integration (Groq, Ollama, HuggingFace)
- Document scraping, parsing, and vectorization
- Web UI for interactive queries

**Status:** ✅ Fully Operational

## Integration

- PoC API connects frontend to Layer 2 PoC Server
- RAG API provides document search capabilities
- Both APIs use Groq API for LLM operations
- APIs handle CORS for frontend access

## Usage

### PoC API

```bash
cd src/api/poc-api
pip install -r requirements.txt
export GROQ_API_KEY=your-key
python app.py
```

### RAG API

```bash
cd src/api/rag-api/api
pip install -r requirements_api.txt
export GROQ_API_KEY=your-key
python rag_api.py
```

## Documentation

- [PoC API README](poc-api/README.md)
- [RAG API README](rag-api/README.md)



