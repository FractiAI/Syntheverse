# RAG API Server Agents

## Purpose

FastAPI server for semantic document search and RAG queries. Alternative implementation with extended analysis capabilities.

## Key Modules

### Core Server
- **`rag_api.py`**: Main FastAPI application with document search endpoints
- **Server Functions**: Query processing, semantic search, LLM integration

## Integration Points

- **GROQ API**: Primary LLM provider for query processing
- **Ollama**: Local LLM fallback option
- **HuggingFace**: Alternative LLM provider
- **Vector Store**: FAISS-based semantic search over embeddings
- **Frontend**: Web UI for interactive RAG queries

## Responsibilities

### Query Processing
- Handle semantic search requests over vectorized documents
- Process natural language queries with LLM integration
- Retrieve relevant document chunks based on embedding similarity
- Format and return search results with metadata

### LLM Integration
- Coordinate between multiple LLM providers (GROQ, Ollama, HuggingFace)
- Handle API authentication and rate limiting
- Provide fallback mechanisms for service availability
- Optimize query processing for response time

### Vector Search
- Implement efficient semantic search over document embeddings
- Manage vector store indexing and retrieval
- Support filtering and ranking of search results
- Maintain search performance at scale

## Interfaces

### API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/search` | Semantic search over documents |
| POST | `/query` | Interactive RAG queries with LLM |
| GET | `/documents` | List available documents |
| POST | `/upload` | Upload new documents |
| GET | `/health` | API health check |

### External Services
- **GROQ API**: Primary LLM services
- **Ollama API**: Local LLM services
- **HuggingFace API**: Alternative LLM provider

## Dependencies

### Core Dependencies
- **FastAPI**: Async web framework
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation
- **GROQ Client**: LLM API integration

### Search Dependencies
- **FAISS**: Vector similarity search
- **Sentence Transformers**: Embedding models
- **NumPy**: Array operations

## Development

### Setup
```bash
cd src/api/rag-api/api
pip install -r requirements_api.txt
export GROQ_API_KEY="your-key"
python rag_api.py
```

### Configuration
- **GROQ_API_KEY**: Required for LLM operations
- **API Port**: Configurable via environment (default 8000)
- **Model Selection**: Configure LLM provider in code

## Testing

### Test Coverage
- **Unit Tests**: Endpoint validation
- **Integration Tests**: LLM provider fallback
- **Performance Tests**: Search response times

### Test Execution
```bash
pytest tests/test_rag_api.py
```

## Blueprint Alignment

### AI Integration ([Blueprint §5](docs/Blueprint for Syntheverse))
- **Archive Access**: RAG system provides semantic search over all stored contributions
- **Training Support**: Document processing pipeline supports AI training data preparation
- **Complementary System**: RAG search is separate from PoC evaluation (which uses direct LLM calls)

### Complete Workflow Support ([Blueprint §7](docs/Blueprint for Syntheverse))
- **Research Discovery**: Enable semantic search over Zenodo community contributions
- **Context Retrieval**: Support background research during contribution preparation
- **Knowledge Access**: Provide searchable archive of ecosystem contributions

## Cross-References

- **Parent**: [rag-api/AGENTS.md](../AGENTS.md) - Alternative RAG implementation
- **Sibling**: [rag_api/api/AGENTS.md](../../rag_api/api/AGENTS.md) - Primary RAG API
- **Related**:
  - [config/environment/AGENTS.md](../../../../config/environment/AGENTS.md) - API configuration
  - [docs/api/RAG_API.md](../../../../docs/api/RAG_API.md) - API documentation

