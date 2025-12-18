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

## Responsibilities

### Service Coordination
- Provide reliable bridges between frontend and backend systems
- Ensure consistent data flow from submission to evaluation to registration
- Maintain API stability and backwards compatibility
- Handle file uploads, validation, and processing

### Data Management
- Validate all incoming requests and file uploads
- Ensure secure storage and retrieval of contribution data
- Maintain data integrity across the evaluation pipeline
- Support both PoC evaluation and RAG document processing

### Integration Management
- Coordinate between Next.js frontend and Python backend
- Integrate with Layer 2 evaluation engine
- Connect to blockchain services for registration
- Manage external LLM API integrations (GROQ, Ollama, HuggingFace)

## Interfaces

### PoC API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/submit` | Submit contribution with file upload |
| GET | `/archive` | Retrieve contribution archive |
| GET | `/sandbox` | Get sandbox map data |
| GET | `/tokenomics` | Get tokenomics state |
| POST | `/register` | Register contribution on blockchain |

### RAG API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/search` | Semantic search over documents |
| POST | `/query` | Interactive RAG queries |
| GET | `/documents` | List available documents |
| POST | `/upload` | Upload documents for processing |

### External Interfaces
- **GROQ API**: LLM services for evaluation and RAG
- **Ollama API**: Local LLM fallback option
- **HuggingFace API**: Alternative LLM provider
- **Blockchain Layer 1**: Registration and certificate services

## Dependencies

### PoC API Dependencies
- **Flask**: Web framework for REST API
- **Werkzeug**: File upload handling
- **Requests**: HTTP client for backend communication
- **Python-multipart**: File upload processing

### RAG API Dependencies
- **FastAPI**: Modern async web framework
- **Uvicorn**: ASGI server for FastAPI
- **Pydantic**: Data validation and serialization
- **FAISS**: Vector similarity search
- **Sentence Transformers**: Embedding generation

### Shared Dependencies
- **GROQ Python Client**: Primary LLM integration
- **Ollama Python Client**: Local LLM integration
- **Transformers**: HuggingFace model support
- **NumPy/Pandas**: Data processing

## Development

### Development Setup
```bash
# PoC API setup
cd poc-api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py

# RAG API setup
cd rag_api
pip install -r api/requirements_api.txt
python api/rag_api.py
```

### API Development Guidelines
- **Versioning**: Use semantic versioning for API changes
- **Documentation**: Auto-generate OpenAPI specs with FastAPI
- **Testing**: Comprehensive endpoint testing with pytest
- **Security**: Input validation and rate limiting
- **Monitoring**: Request logging and error tracking

### Configuration
```bash
# Required environment variables
export GROQ_API_KEY="your-api-key"
export FLASK_ENV="development"
export RAG_API_PORT="8000"
export POC_API_PORT="5001"
```

## Testing

### API Testing Strategy
- **Unit Tests**: Individual endpoint testing
- **Integration Tests**: End-to-end workflow testing
- **Load Tests**: Performance and concurrency testing
- **Security Tests**: Input validation and injection testing

### Test Execution
```bash
# Test PoC API
cd poc-api
python -m pytest tests/

# Test RAG API
cd rag_api
python -m pytest tests/

# Integration tests
cd ../../../tests
python -m pytest test_poc_api.py
```

### Test Coverage Goals
- **PoC API**: 90%+ endpoint coverage
- **RAG API**: 85%+ functionality coverage
- **Integration**: Full workflow coverage
- **Error Scenarios**: Comprehensive error handling tests

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