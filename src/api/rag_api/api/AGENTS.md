# RAG API Agents

## Purpose

FastAPI-based REST API server providing access to the Syntheverse RAG (Retrieval-Augmented Generation) system. Enables semantic search over pre-computed embeddings with LLM-powered answer generation.

## Key Modules

### RAG Engine (`rag_api.py`)

Core RAG functionality with multi-provider LLM integration:

- **`RAGEngine` Class**: Manages embeddings loading, LLM provider setup, and query processing
- **`query()` Method**: Complete RAG pipeline (search + generate answer)
- **`search()` Method**: Semantic search without answer generation
- **LLM Integration**: Groq (primary), HuggingFace, Ollama fallback support

### FastAPI Server (`rag_api.py`)

REST API endpoints and server management:

- **`/query` Endpoint**: POST endpoint for complete RAG queries
- **`/search` Endpoint**: POST endpoint for semantic search only
- **`/health` Endpoint**: GET endpoint for system health check
- **`/llm-models` Endpoint**: GET endpoint for available LLM models
- **`/embedding-statistics` Endpoint**: GET endpoint for embedding statistics
- **`/embedding-validation` Endpoint**: GET endpoint for validation reports
- **CORS Middleware**: Cross-origin support for frontend integration

### Web UI (`static/index.html`)

Interactive query interface:

- **Query Form**: Input field for user queries
- **Results Display**: Shows answers with source citations
- **LLM Selection**: Dropdown for choosing LLM provider
- **Real-time Updates**: Dynamic result display

## Integration Points

### Frontend Applications

- **Next.js Frontend**: Receives CORS-enabled API responses
- **Legacy Flask UI**: Alternative web interface integration
- **External Applications**: Any HTTP client can use REST endpoints

### LLM Providers

- **Groq API**: Primary LLM provider via OpenAI-compatible interface
- **Ollama**: Local LLM fallback with automatic model detection
- **HuggingFace**: Cloud LLM fallback with API key authentication

### Data Pipeline

- **Vectorizer**: Consumes pre-computed embeddings from `../data/vectorized/embeddings/`
- **Parser**: Indirect integration through processed text chunks
- **Scraper**: Indirect integration through scraped PDF content

### Layer 2 (Limited)

- **General Queries**: Provides knowledge base search capabilities
- **Not for Evaluation**: PoC/PoD evaluation uses direct Grok API calls
- **Reference Material**: Supplies background knowledge for evaluations

## Development Guidelines

### API Design

- **FastAPI Framework**: Modern async API with automatic OpenAPI docs
- **Pydantic Models**: Type-validated request/response models
- **Error Handling**: Consistent error responses with appropriate HTTP status codes
- **Logging**: Request/response logging for debugging

### LLM Provider Management

- **Provider Priority**: Groq → HuggingFace → Ollama fallback chain
- **Environment Variables**: Secure API key management
- **Error Resilience**: Graceful fallback when providers unavailable
- **Rate Limiting**: Respect provider rate limits and quotas

### Performance Optimization

- **Embedding Loading**: One-time loading of pre-computed vectors
- **Async Processing**: Non-blocking I/O for API requests
- **Caching**: Consider response caching for frequent queries
- **Resource Management**: Memory-efficient embedding storage

## Common Patterns

### Query Processing

1. **Request Validation**: Pydantic model validation
2. **Semantic Search**: Cosine similarity against loaded embeddings
3. **Context Building**: Top-K relevant chunks for LLM context
4. **Answer Generation**: LLM call with system prompt + context
5. **Response Formatting**: Structured JSON response with metadata

### Provider Fallback

1. **Primary Check**: Attempt Groq API first
2. **Secondary Check**: Fall back to HuggingFace if available
3. **Tertiary Check**: Use local Ollama if running
4. **Error Handling**: Clear error messages when no providers available

### System Prompt Integration

- **Syntheverse Whole Brain AI**: Integrated Gina × Leo × Pru prompt
- **Custom Prompts**: Optional override via API parameter
- **Context Formatting**: Structured context from retrieved chunks
- **Response Consistency**: Maintains Syntheverse voice and framework

## Enhanced Search Capabilities

### Advanced Semantic Search

- **Embedding-Based Search**: Replaced text matching with proper cosine similarity search using optimized batch processing
- **Query Embedding Generation**: Uses sentence-transformers with input validation, normalization, and length limits
- **Analysis Integration**: Automatic use of analysis modules when available with comprehensive error handling
- **Fallback Support**: Graceful degradation to text-based search when needed with detailed logging

### Production-Ready Features

- **Performance Monitoring**: Request timing and success rate tracking
- **Input Sanitization**: Comprehensive validation of queries and parameters
- **Resource Management**: Memory-efficient processing for large embedding collections
- **Error Recovery**: Robust error handling with actionable error messages

### Statistics and Validation

- **Embedding Statistics**: Comprehensive metrics via `/embedding-statistics` endpoint
- **Quality Validation**: Automated validation reports via `/embedding-validation` endpoint
- **Real-time Analysis**: On-demand analysis without pipeline reprocessing

## Key Functions

### RAGEngine

- `__init__(embeddings_dir, ollama_url, ollama_model)`: Initialize with embedding directory and LLM settings
- `query(query, top_k, min_score, llm_model, system_prompt)`: Complete RAG query
- `search(query, top_k, min_score)`: Semantic search only
- `generate_answer(query, chunks, llm_model, system_prompt)`: LLM answer generation
- `_load_all_chunks()`: Load embeddings from JSON files
- `_check_cloud_apis()`: Verify LLM provider availability

### FastAPI Routes

- `query(request: QueryRequest)`: Handle `/query` POST requests
- `search(request: QueryRequest)`: Handle `/search` POST requests
- `health()`: Handle `/health` GET requests
- `get_llm_models()`: Handle `/llm-models` GET requests

## Error Handling

### HTTP Status Codes

- **200 OK**: Successful query processing
- **422 Unprocessable Entity**: Invalid request parameters
- **500 Internal Server Error**: LLM provider failures or processing errors
- **503 Service Unavailable**: RAG engine not initialized

### Error Messages

- **Clear Descriptions**: Human-readable error explanations
- **Troubleshooting Guidance**: Suggestions for resolving issues
- **Provider Status**: Information about LLM availability

## Performance Characteristics

- **Initialization**: Loads all embeddings on startup (~500MB-1GB memory)
- **Query Latency**: 1-3 seconds (search + LLM generation)
- **Concurrent Users**: Limited by LLM provider rate limits
- **Scalability**: Single instance with provider-based scaling limits

## Testing

### Health Checks

- **Provider Availability**: Verify all configured LLM providers
- **Embedding Loading**: Confirm embeddings loaded successfully
- **API Endpoints**: Test all REST endpoints
- **CORS Headers**: Verify cross-origin request support

### Integration Tests

- **Query Pipeline**: End-to-end query processing
- **Provider Fallback**: Test automatic fallback behavior
- **Error Scenarios**: Invalid requests and provider failures
- **Performance**: Response time and memory usage validation

## Future Enhancements

- **Streaming Responses**: Real-time answer generation
- **Advanced Retrieval**: Hybrid search with metadata filtering
- **Multi-modal Support**: Image and code understanding
- **Caching Layer**: Response caching for improved performance
- **Load Balancing**: Multiple instance support with provider distribution</content>
</xai:function_call name="read_lints">
<parameter name="target_file">src/api/rag-api/api/AGENTS.md
