# RAG API Development Standards

## RAG Pipeline Components

### Scraper
- Downloads PDFs from Zenodo repositories
- Skips duplicate downloads
- Saves metadata
- Handles download errors gracefully

### Parser
- Processes PDFs into text chunks
- Uses LangChain for PDF processing
- Implements intelligent chunking with overlap
- Saves parsed chunks as JSON

### Vectorizer
- Creates embeddings from parsed chunks
- Uses local HuggingFace models (no API calls)
- Saves embeddings and metadata
- Supports batch processing

### API Server
- FastAPI server for RAG queries
- Semantic search functionality
- LLM integration (Groq, Ollama, HuggingFace)
- Web UI for interactive queries

## API Key Configuration

GROQ_API_KEY must be set in `.env` file at project root.
See `config/environment/GET_GROQ_KEY.md` for setup instructions.
Use centralized `src.core.utils.load_groq_api_key()` for loading.

## LLM Provider Integration

### Groq (Primary)
- Fast cloud LLM provider
- Free tier available
- Model: llama-3.1-8b-instant
- OpenAI-compatible API
- API key required for all RAG operations

### Ollama (Fallback)
- Local LLM runner
- No API costs
- Requires local installation
- Good for offline development

### HuggingFace (Fallback)
- Cloud inference API
- Multiple model options
- Requires API key
- Good for experimentation

## Syntheverse AI Integration

### Whole Brain AI System
- Gina: Whole Brain Integrator
- Leo: Hydrogen-Holographic Fractal Engine
- Pru: Outcast Hero Life-Narrative Navigator
- Unified system prompt for all queries

### System Prompt Structure
- Base Syntheverse framework
- HHFE evaluation criteria
- Output format specifications
- Anti-hallucination rules

## Code Patterns

### Semantic Search
```python
def search(query: str, top_k: int = 5, min_score: float = 0.0):
    # Load embeddings
    # Calculate similarity
    # Filter by min_score
    # Return top_k results
```

### Query Processing
```python
def query(query: str, llm_model: str = "groq"):
    # Perform semantic search
    # Retrieve relevant chunks
    # Build context
    # Call LLM with context
    # Return response
```

### Embedding Generation
- Use sentence transformers
- Batch process chunks
- Store embeddings efficiently
- Index for fast retrieval

## Integration with Layer 2

### Evaluation Queries
- Specialized prompts for PoC evaluation
- Direct Grok API calls (no RAG retrieval)
- Comprehensive system prompt
- Structured output format

### Document Processing
- PDF parsing for submissions
- Text extraction and chunking
- Content hashing for redundancy
- Metadata extraction

## Performance Optimization

### Embedding Storage
- Pre-compute embeddings
- Store in JSON format
- Load on API startup
- Cache for fast retrieval

### Query Optimization
- Limit search results
- Use similarity thresholds
- Batch process when possible
- Optimize LLM calls







