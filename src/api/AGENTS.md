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

### Alternative RAG API (`rag-api/`)

Extended FastAPI implementation with advanced analysis:
- Enhanced embedding analysis and visualization
- Word analysis and semantic clustering
- Interactive analysis tools and dashboards
- Alternative API implementation with expanded features

**Key Components:**
- `api/`: Main API server with extended endpoints
- `analysis/`: Comprehensive embedding analysis suite
- `scraper/`: PDF scraping with metadata extraction
- `parser/`: Advanced PDF parsing with layout preservation
- `vectorizer/`: Enhanced embedding generation pipeline

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

## File Structure

```
api/
├── poc-api/              # Flask API for PoC submissions
│   ├── app.py           # Main Flask application
│   ├── server.py        # Server setup and configuration
│   ├── requirements.txt # Python dependencies
│   ├── uploads/         # File upload storage
│   └── venv/            # Virtual environment
├── rag_api/              # FastAPI for RAG processing
│   ├── api/
│   │   └── rag_api.py   # Main FastAPI server
│   ├── scraper/         # PDF scraping utilities
│   ├── parser/          # PDF parsing pipeline
│   ├── vectorizer/      # Embedding generation
│   └── analysis/        # Embedding analysis tools
└── rag-api/              # Alternative RAG implementation
    ├── api/             # Extended API server
    ├── analysis/        # Advanced analysis suite
    ├── scraper/         # Enhanced PDF scraping
    ├── parser/          # Advanced PDF parsing
    └── vectorizer/      # Enhanced vectorization
```

## Ports & Endpoints

| Service | Port | Key Endpoints |
|---------|------|---------------|
| PoC API | 5001 | `/submit`, `/archive`, `/sandbox`, `/tokenomics` |
| RAG API | 8000 | `/search`, `/query`, `/documents` |

## Blueprint Alignment

### Three-Layer Architecture ([Blueprint §3](docs/Blueprint for Syntheverse))
- **UI Layer Bridge**: APIs serve as the connection between Next.js frontend and Layer 2 evaluation engine
- **Layer 2 Integration**: PoC API connects directly to `core/layer2/poc_server.py` for evaluation orchestration
- **Service Coordination**: APIs manage the flow between frontend submissions and backend processing

### Experience Walkthrough Implementation ([Blueprint §1](docs/Blueprint for Syntheverse))
- **PoC Submission** ([§1.1](docs/Blueprint for Syntheverse)): PoC API handles contribution uploads and initial processing
- **Evaluation Pipeline** ([§1.3](docs/Blueprint for Syntheverse)): APIs route submissions to hydrogen holographic scoring
- **Dashboard Interaction** ([§1.5](docs/Blueprint for Syntheverse)): APIs provide data for score exploration and metallic amplifications
- **Archive Access**: APIs serve stored contributions for redundancy detection and AI training

### PoC Pipeline Execution ([Blueprint §3.1](docs/Blueprint for Syntheverse))
- **Submission → Evaluation**: PoC API receives submissions and forwards to Layer 2 evaluation engine
- **Evaluation → Approval**: APIs handle human review workflow and approval status
- **Approval → Registration**: APIs coordinate with blockchain Layer 1 for $200 registration
- **Registration → Allocation**: APIs trigger SYNTH token distribution through tokenomics engine

### AI Integration ([Blueprint §5](docs/Blueprint for Syntheverse))
- **GROQ API Integration**: Both PoC and RAG APIs use centralized `src.core.utils.load_groq_api_key()` for LLM operations
- **Archive Training**: APIs ensure all contributions are immediately stored for AI training data
- **RAG Processing**: Separate RAG API handles document search while PoC API manages evaluation

### Financial Framework ([Blueprint §4](docs/Blueprint for Syntheverse))
- **Free Evaluation**: APIs handle free PoC submissions (only registration requires $200 payment)
- **Blockchain Integration**: APIs coordinate with Layer 1 for on-chain registration and certificate issuance
- **Token Allocation**: APIs provide interfaces for SYNTH distribution and metallic amplification queries

### Complete Workflow Support ([Blueprint §7](docs/Blueprint for Syntheverse))
1. **Submission**: APIs receive and validate contribution uploads
2. **Evaluation**: Route to Layer 2 for hydrogen holographic scoring
3. **Human Review**: APIs manage approval workflow and status updates
4. **Registration**: Coordinate $200 blockchain registration process
5. **Dashboard**: Provide real-time access to scores, amplifications, and ecosystem impact
6. **Integration**: Support full end-to-end workflow from submission to token allocation

### Implementation Status
- **✅ Fully Operational**: Complete API bridges between all three layers
- **🟡 Enhanced**: Ongoing improvements to error handling and performance
- **📋 Blueprint Compliant**: APIs implement the complete workflow from Blueprint §7

## Cross-References

- **Blueprint Document**: [docs/Blueprint for Syntheverse](../../docs/Blueprint for Syntheverse) - Central system vision
- **Parent**: [src/AGENTS.md](../AGENTS.md) - Source code organization
- **Children**:
  - [poc-api/AGENTS.md](poc-api/AGENTS.md) - PoC API implementation
  - [rag_api/AGENTS.md](rag_api/AGENTS.md) - RAG API implementation
  - [rag-api/AGENTS.md](rag-api/AGENTS.md) - Alternative RAG API implementation
- **Related**:
  - [core/layer2/AGENTS.md](../core/layer2/AGENTS.md) - Layer 2 backend integration
  - [config/environment/AGENTS.md](../../config/environment/AGENTS.md) - API configuration
  - [docs/POC_SUBMISSION_TO_ALLOCATION_FLOW.md](../../docs/POC_SUBMISSION_TO_ALLOCATION_FLOW.md) - Complete workflow