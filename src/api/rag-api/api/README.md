# Alternative RAG API Server

FastAPI server implementation providing alternative RAG (Retrieval-Augmented Generation) capabilities with enhanced processing and analysis features.

## Overview

This directory contains the FastAPI server implementation for the alternative RAG system, offering advanced document processing, semantic search, and interactive analysis capabilities.

## API Architecture

### Server Structure
```
api/
├── __init__.py                   # Package initialization
├── rag_api.py                   # Main FastAPI application
├── requirements_api.txt         # Python dependencies
├── config.py                    # Server configuration
├── middleware.py                # Custom middleware
└── routers/                     # API route modules
    ├── search.py               # Search endpoints
    ├── analysis.py             # Analysis endpoints
    ├── documents.py            # Document management
    └── admin.py                # Administrative endpoints
```

### Core Features
- **Advanced Semantic Search**: Multi-strategy retrieval with ranking
- **Interactive Analysis**: Real-time document and embedding analysis
- **Document Processing**: Comprehensive document ingestion pipeline
- **Visualization Support**: Data visualization and export capabilities

## API Endpoints

### Search Endpoints
```
GET  /search/{query}              # Basic semantic search
POST /search/advanced             # Advanced search with filters
GET  /search/suggestions/{query}  # Search suggestions
POST /search/batch                # Batch search operations
```

### Document Management
```
POST /documents/upload            # Upload documents for processing
GET  /documents/{id}             # Retrieve document information
GET  /documents                   # List all documents
DELETE /documents/{id}           # Remove document
POST /documents/batch             # Batch document operations
```

### Analysis Endpoints
```
GET  /analysis/stats              # Statistical analysis of embeddings
GET  /analysis/clusters           # Semantic clustering results
POST /analysis/similarity         # Document similarity analysis
GET  /analysis/visualization      # Visualization data export
POST /analysis/export             # Export analysis results
```

### Administrative Endpoints
```
GET  /admin/health                # System health check
GET  /admin/metrics               # Performance metrics
POST /admin/reindex               # Rebuild search index
POST /admin/cleanup               # Database cleanup
```

## Request/Response Examples

### Semantic Search
```json
// Request
{
  "query": "hydrogen holographic fractal blockchain",
  "filters": {
    "date_range": ["2024-01-01", "2024-12-31"],
    "source": "academic",
    "similarity_threshold": 0.8
  },
  "options": {
    "ranking_strategy": "hybrid",
    "max_results": 20,
    "include_highlights": true
  }
}

// Response
{
  "results": [
    {
      "document_id": "doc_123",
      "title": "Holographic Fractals in Quantum Computing",
      "similarity_score": 0.92,
      "highlights": ["hydrogen holographic fractal"],
      "metadata": {
        "author": "Dr. Quantum",
        "publication_date": "2024-06-15",
        "source": "Nature Physics"
      }
    }
  ],
  "metadata": {
    "total_results": 1,
    "processing_time": 0.234,
    "query_expansion_terms": ["quantum", "computing"]
  }
}
```

### Document Upload
```json
// Request (multipart/form-data)
{
  "file": "research_paper.pdf",
  "metadata": {
    "title": "Advanced Fractal Analysis",
    "authors": ["Dr. Smith", "Dr. Jones"],
    "abstract": "Comprehensive study of fractal patterns...",
    "tags": ["fractals", "mathematics", "physics"],
    "publication_date": "2024-12-01"
  }
}

// Response
{
  "document_id": "doc_456",
  "status": "processing",
  "chunks_created": 45,
  "estimated_completion": "2024-12-18T15:30:00Z",
  "processing_steps": [
    "Text extraction",
    "Chunking",
    "Embedding generation",
    "Index update"
  ]
}
```

## Configuration

### Environment Variables
```bash
# Server Configuration
RAG_API_HOST=0.0.0.0
RAG_API_PORT=8000
RAG_API_WORKERS=4

# Database Configuration
VECTOR_DB_PATH=./data/vectors
DOCUMENT_STORE_PATH=./data/documents
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# External Services
GROQ_API_KEY=your-api-key
OLLAMA_BASE_URL=http://localhost:11434

# Security
API_SECRET_KEY=your-secret-key
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

### Application Settings
```python
# config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4

    # Database settings
    vector_db_path: str = "./data/vectors"
    document_store_path: str = "./data/documents"

    # Model settings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    similarity_threshold: float = 0.8

    # External services
    groq_api_key: str
    ollama_base_url: str = "http://localhost:11434"

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

## Development

### Local Development Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r api/requirements_api.txt

# Run development server
cd api
python rag_api.py

# Or with uvicorn
uvicorn rag_api:app --host 0.0.0.0 --port 8000 --reload
```

### API Documentation
```bash
# Access interactive API docs
open http://localhost:8000/docs

# Alternative documentation
open http://localhost:8000/redoc
```

### Testing
```bash
# Run API tests
cd api
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html

# Performance testing
python -m pytest tests/test_performance.py
```

## Performance Optimization

### Caching Strategy
- **Query Result Caching**: Redis-based caching for frequent queries
- **Embedding Caching**: Pre-computed embeddings for common documents
- **Response Compression**: GZIP compression for large response payloads

### Async Processing
- **Background Tasks**: Document processing and embedding generation
- **Streaming Responses**: Large result sets streamed to clients
- **Concurrent Requests**: Multiple worker processes for high throughput

### Database Optimization
- **Vector Indexing**: FAISS/HNSW indexing for fast similarity search
- **Query Optimization**: Efficient metadata filtering and sorting
- **Connection Pooling**: Optimized database connection management

## Monitoring and Logging

### Health Checks
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "services": {
            "vector_db": check_vector_db(),
            "document_store": check_document_store(),
            "external_apis": check_external_apis()
        }
    }
```

### Metrics Collection
```python
# Prometheus metrics
REQUEST_COUNT = Counter('rag_requests_total', 'Total RAG requests', ['endpoint'])
RESPONSE_TIME = Histogram('rag_response_time', 'Response time', ['endpoint'])

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    REQUEST_COUNT.labels(endpoint=request.url.path).inc()
    RESPONSE_TIME.labels(endpoint=request.url.path).observe(process_time)

    return response
```

## Security

### Authentication
- **API Key Authentication**: Required for all endpoints
- **Rate Limiting**: Per-client rate limiting with Redis
- **Request Validation**: Comprehensive input validation and sanitization

### Data Protection
- **Encryption**: Sensitive data encrypted at rest and in transit
- **Access Control**: Role-based access control for administrative endpoints
- **Audit Logging**: Comprehensive logging of all API operations

## Deployment

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements_api.txt .
RUN pip install -r requirements_api.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "rag_api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Configuration
```bash
# Production environment
export RAG_API_WORKERS=8
export VECTOR_DB_PATH=/data/vectors
export DOCUMENT_STORE_PATH=/data/documents
export LOG_LEVEL=INFO
```

## Documentation

- [AGENTS.md](AGENTS.md) - Detailed component documentation
- [FRACTAL.md](FRACTAL.md) - Fractal analysis and patterns
- [FastAPI Documentation](https://fastapi.tiangolo.com/) - Framework reference
- [API Specification](../../analysis/AGENTS.md) - Analysis capabilities
