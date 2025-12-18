# Alternative RAG API Agents

## Purpose

Alternative FastAPI implementation providing extended RAG (Retrieval-Augmented Generation) capabilities with enhanced analysis, visualization, and processing features for document search and semantic understanding.

## Key Modules

### API Server (`api/`)

Extended FastAPI server with advanced endpoints:
- Enhanced semantic search with multiple ranking algorithms
- Interactive query processing with conversation context
- Document upload and processing pipelines
- Analysis result visualization and export
- Alternative implementation with expanded feature set

**Key Files:**
- `api/rag_api.py`: Main FastAPI application server
- `requirements_api.txt`: Python dependencies for API server

### Analysis Suite (`analysis/`)

Comprehensive embedding analysis and visualization tools:
- **Embedding Analysis**: Statistical analysis of vector spaces
- **Word Analysis**: Semantic clustering and relationship mapping
- **Visualization**: Interactive charts and similarity heatmaps
- **Validation**: Embedding quality assessment and consistency checks
- **CLI Tools**: Command-line interfaces for batch processing

**Key Components:**
- `embedding_analyzer.py`: Statistical analysis of embeddings
- `similarity_analyzer.py`: Semantic relationship mapping
- `word_analyzer.py`: Linguistic pattern analysis
- `embedding_visualizer.py`: Interactive visualization tools
- `cli/`: Command-line analysis utilities

### Document Processing Pipeline

#### Scraper (`scraper/`)
- Web content extraction from Zenodo and academic sources
- Metadata preservation and source attribution
- Rate limiting and error handling for web requests

#### Parser (`parser/`)
- Advanced PDF parsing with layout preservation
- Text chunking with semantic boundary detection
- Multi-format document support (PDF, DOCX, HTML)

#### Vectorizer (`vectorizer/`)
- Enhanced embedding generation with multiple models
- Batch processing capabilities for large document collections
- Embedding optimization and dimensionality reduction

## Integration Points

### External Services
- **GROQ API**: Primary LLM for query processing and generation
- **Ollama API**: Local LLM fallback for offline processing
- **HuggingFace API**: Alternative embedding models and transformers

### Internal Systems
- **Document Storage**: Integration with `src/data/` for processed content
- **Vector Database**: FAISS or similar for semantic search indexing
- **Analysis Pipeline**: Connection to analysis tools for result processing

### Frontend Integration
- **CORS Configuration**: Cross-origin support for web applications
- **JSON API**: RESTful endpoints for frontend consumption
- **Real-time Updates**: WebSocket support for live analysis results

## Responsibilities

### Advanced RAG Processing
- Implement multiple retrieval strategies (semantic, keyword, hybrid)
- Provide conversation context and multi-turn query support
- Support document ranking and relevance scoring
- Enable query expansion and clarification

### Comprehensive Analysis
- Generate statistical insights from embedding spaces
- Identify semantic clusters and topic modeling
- Create interactive visualizations for exploration
- Validate embedding quality and consistency

### Enhanced User Experience
- Provide intuitive API interfaces for developers
- Support various output formats (JSON, CSV, visualizations)
- Implement caching and performance optimizations
- Offer comprehensive error handling and logging

## Interfaces

### API Endpoints

#### Search and Query
```
POST /search         # Semantic search with ranking
POST /query          # Interactive RAG queries
POST /converse       # Multi-turn conversation support
GET  /suggestions    # Query suggestions and auto-complete
```

#### Document Management
```
POST /upload         # Document upload and processing
GET  /documents      # List available documents
GET  /document/{id}  # Retrieve specific document
DELETE /document/{id} # Remove document from index
```

#### Analysis and Visualization
```
GET  /analysis/stats         # Statistical analysis results
GET  /analysis/clusters      # Semantic clustering data
GET  /analysis/visualize     # Interactive visualization data
POST /analysis/export        # Export analysis results
```

### Data Formats

#### Request Formats
```json
{
  "query": "hydrogen holographic fractal",
  "context": "previous conversation context",
  "filters": {
    "date_range": "2024-01-01:2024-12-31",
    "source": "zenodo",
    "similarity_threshold": 0.8
  },
  "options": {
    "ranking_algorithm": "hybrid",
    "max_results": 10,
    "include_metadata": true
  }
}
```

#### Response Formats
```json
{
  "results": [
    {
      "document_id": "abc123",
      "title": "Hydrogen Holographic Fractals in Blockchain",
      "similarity_score": 0.95,
      "ranking_score": 0.87,
      "snippets": ["relevant text excerpt"],
      "metadata": {
        "author": "Researcher Name",
        "publication_date": "2024-01-15",
        "source": "zenodo"
      }
    }
  ],
  "metadata": {
    "total_results": 1,
    "processing_time": 0.234,
    "query_expansion": ["expanded", "terms"]
  }
}
```

## Dependencies

### Core Dependencies
- **FastAPI**: Modern async web framework
- **Uvicorn**: ASGI server implementation
- **Pydantic**: Data validation and serialization
- **FAISS**: High-performance similarity search
- **NumPy/Pandas**: Data processing and analysis

### ML/AI Dependencies
- **Sentence Transformers**: Embedding model integration
- **Scikit-learn**: Clustering and analysis algorithms
- **Matplotlib/Seaborn**: Data visualization
- **NLTK/SpaCy**: Natural language processing

### External API Clients
- **GROQ Python Client**: Primary LLM integration
- **Ollama Client**: Local LLM support
- **HuggingFace Transformers**: Alternative model support

## Development

### Local Development Setup
```bash
# Clone and setup
cd src/api/rag-api
python -m venv venv
source venv/bin/activate
pip install -r api/requirements_api.txt

# Start development server
cd api
python rag_api.py

# Access API documentation
open http://localhost:8000/docs
```

### Development Guidelines
- **Async First**: Leverage FastAPI's async capabilities
- **Type Hints**: Comprehensive type annotations for all functions
- **Error Handling**: Consistent error responses and logging
- **Testing**: Comprehensive test coverage for all endpoints
- **Documentation**: Auto-generated OpenAPI specs with examples

### Configuration
```bash
# Required environment variables
export GROQ_API_KEY="your-api-key"
export RAG_API_PORT="8000"
export VECTOR_DB_PATH="./vectors"
export DOCUMENT_STORE_PATH="./documents"
```

## Testing

### Test Categories
- **Unit Tests**: Individual function and class testing
- **Integration Tests**: End-to-end API workflow testing
- **Performance Tests**: Load testing and response time validation
- **Accuracy Tests**: Semantic search quality and ranking validation

### Test Execution
```bash
# Run all tests
cd src/api/rag-api
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=api --cov-report=html

# Performance testing
python -m pytest tests/test_performance.py
```

### Test Data Management
- **Fixtures**: Pre-loaded test documents and queries
- **Mock Services**: Simulated external API responses
- **Performance Benchmarks**: Established accuracy thresholds
- **Regression Tests**: Historical test case preservation

## Common Patterns

### Query Processing Pipeline
1. **Query Analysis**: Parse and expand search terms
2. **Vector Encoding**: Convert query to embedding space
3. **Similarity Search**: Find relevant documents via FAISS
4. **Re-ranking**: Apply additional ranking algorithms
5. **Response Formatting**: Structure results with metadata

### Document Processing Pipeline
1. **Ingestion**: Accept document uploads or URLs
2. **Parsing**: Extract text and preserve structure
3. **Chunking**: Split into semantically meaningful units
4. **Embedding**: Generate vector representations
5. **Indexing**: Add to searchable vector database

### Analysis Workflow
1. **Data Collection**: Gather embeddings and metadata
2. **Statistical Analysis**: Compute distributions and patterns
3. **Clustering**: Identify semantic groups and topics
4. **Visualization**: Generate interactive charts and maps
5. **Export**: Provide downloadable analysis results

## File Structure

```
rag-api/
├── api/                          # Main API server
│   ├── rag_api.py               # FastAPI application
│   ├── __init__.py
│   ├── requirements_api.txt     # Dependencies
│   └── AGENTS.md                # API server documentation
├── analysis/                     # Analysis and visualization
│   ├── embedding_analyzer.py    # Statistical analysis
│   ├── similarity_analyzer.py   # Relationship mapping
│   ├── word_analyzer.py         # Linguistic analysis
│   ├── embedding_visualizer.py  # Visualization tools
│   ├── cli/                     # Command-line tools
│   ├── utils.py                 # Analysis utilities
│   ├── logger.py                # Logging configuration
│   ├── AGENTS.md                # Analysis documentation
│   └── README.md
├── scraper/                      # Web scraping utilities
├── parser/                       # Document parsing pipeline
├── vectorizer/                   # Embedding generation
├── FRACTAL.md                   # Fractal analysis
└── AGENTS.md                    # This documentation
```

## Blueprint Alignment

### AI Integration ([Blueprint §5](docs/Blueprint for Syntheverse))
- **GROQ API Integration**: Primary LLM for query processing and generation
- **Archive Training**: Documents processed for AI training data expansion
- **RAG Processing**: Separate from PoC evaluation for document understanding

### Experience Enhancement ([Blueprint §1](docs/Blueprint for Syntheverse))
- **Dashboard Support**: Provides semantic search for contribution exploration
- **Knowledge Access**: Enables users to query and understand archived contributions
- **AI Assistance**: Supports interactive queries for system understanding

### Technical Implementation ([Blueprint §3](docs/Blueprint for Syntheverse))
- **Service Layer**: Provides advanced API capabilities beyond basic PoC evaluation
- **Data Processing**: Supports the document processing pipeline for knowledge management
- **Analysis Tools**: Enables deep semantic understanding of contributions

## Cross-References

- **Blueprint Document**: [docs/Blueprint for Syntheverse](../../../docs/Blueprint for Syntheverse) - Central system vision
- **Parent API**: [src/api/AGENTS.md](../AGENTS.md) - API services overview
- **Related Components**:
  - [src/data/vectorized/AGENTS.md](../../data/vectorized/AGENTS.md) - Vector storage integration
  - [src/data/pdfs/AGENTS.md](../../data/pdfs/AGENTS.md) - Document source integration
  - [config/environment/AGENTS.md](../../../config/environment/AGENTS.md) - API configuration
