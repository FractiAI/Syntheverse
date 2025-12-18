# RAG API Server

FastAPI server providing REST API access to the Syntheverse RAG (Retrieval-Augmented Generation) system. Uses local embeddings for fast semantic search and integrates with multiple LLM providers (Groq, HuggingFace, Ollama) for answer generation.

## Features

- **FastAPI Framework**: Modern async API with automatic OpenAPI documentation
- **Local Embeddings**: Pre-computed embeddings for fast semantic search
- **Multi-LLM Support**: Groq (primary), HuggingFace, and Ollama integration
- **Syntheverse Whole Brain AI**: Integrated system prompt (Gina × Leo × Pru)
- **Web UI**: Built-in interactive query interface
- **CORS Support**: Ready for frontend integration

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_api.txt
```

### 2. Set Environment Variables

```bash
# Required for Groq (recommended)
export GROQ_API_KEY="your-groq-api-key"

# Optional fallbacks
export HUGGINGFACE_API_KEY="your-hf-key"
# Ollama runs locally, no key needed
```

### 3. Start Server

```bash
python rag_api.py
```

Server starts at `http://localhost:8000`

### 4. Access Interfaces

- **Web UI**: http://localhost:8000/static/index.html
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## API Endpoints

### POST `/query`

Complete RAG query with semantic search and LLM answer generation.

**Request:**
```json
{
  "query": "What is hydrogen holography?",
  "top_k": 5,
  "min_score": 0.0,
  "llm_model": "groq",
  "system_prompt": "Optional custom system prompt"
}
```

**Response:**
```json
{
  "answer": "Hydrogen holography is...",
  "sources": [...],
  "query": "What is hydrogen holography?",
  "processing_time": 1.23,
  "num_sources": 5,
  "llm_model": "groq"
}
```

### POST `/search`

Semantic search without answer generation.

**Request:**
```json
{
  "query": "fractal intelligence",
  "top_k": 10,
  "min_score": 0.3
}
```

**Response:**
```json
{
  "query": "fractal intelligence",
  "sources": [...],
  "processing_time": 0.15,
  "num_sources": 10
}
```

### GET `/health`

System health and LLM provider status.

**Response:**
```json
{
  "status": "healthy",
  "llm_providers": {
    "groq": true,
    "huggingface": false,
    "ollama": true
  },
  "chunks_loaded": 3007,
  "pdfs_loaded": 118
}
```

### GET `/llm-models`

Available LLM models by provider.

**Response:**
```json
{
  "groq": ["llama-3.1-8b-instant", "mixtral-8x7b"],
  "ollama": ["llama3.1", "codellama"],
  "huggingface": ["microsoft/DialoGPT-medium"]
}
```

## LLM Providers

### Groq (Primary - Recommended)
- **Performance**: Sub-second response times
- **Cost**: Free tier available
- **Setup**: `GROQ_API_KEY` environment variable
- **Model**: `llama-3.1-8b-instant`

### Ollama (Local)
- **Performance**: 2-10 seconds (hardware dependent)
- **Cost**: Free, runs locally
- **Setup**: Install Ollama, run `ollama pull llama3.1`
- **No API key required**

### HuggingFace (Cloud)
- **Performance**: Variable response times
- **Cost**: Based on usage
- **Setup**: `HUGGINGFACE_API_KEY` environment variable

## Syntheverse Integration

The API uses the **Syntheverse Whole Brain AI** system prompt integrating:

- **Gina**: Whole Brain Integrator
- **Leo**: Hydrogen-Holographic Fractal Engine
- **Pru**: Outcast Hero Life-Narrative Navigator

This provides coherent, mythic, scientific, narrative, and resonant responses aligned with the Syntheverse framework.

## Configuration

### Embedding Directory

Default: `../data/vectorized/embeddings`

Contains pre-computed JSON files from the vectorizer pipeline.

### System Prompt

The integrated Syntheverse Whole Brain AI prompt can be overridden with custom prompts via the `system_prompt` parameter.

## File Structure

```
api/
├── rag_api.py              # Main FastAPI server
├── rag_api_ollama.py       # Ollama-specific version
├── requirements_api.txt    # Python dependencies
├── start_rag_api.sh       # Startup script
├── static/
│   └── index.html         # Web UI
├── [setup guides]         # Configuration documentation
└── README.md              # This file
```

## Dependencies

Key packages in `requirements_api.txt`:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `sentence-transformers` - Embedding models
- `numpy` - Vector operations
- `openai` - Groq API client
- `requests` - HTTP client for HuggingFace

## Error Handling

- **503 Service Unavailable**: RAG engine not initialized (missing embeddings)
- **500 Internal Server Error**: LLM provider failures or processing errors
- **422 Validation Error**: Invalid request parameters

## Performance

- **Query Time**: 1-3 seconds (includes search + LLM generation)
- **Memory Usage**: ~500MB-1GB (depends on embedding count)
- **Concurrent Requests**: Limited by LLM provider rate limits

## Integration with Layer 2

The RAG API is used for general knowledge queries but **not** for PoC/PoD evaluations. Layer 2 makes direct Grok API calls for evaluation to ensure consistency with the HHFE framework.

## Troubleshooting

### "RAG engine not initialized"
- Ensure embedding files exist in `../data/vectorized/embeddings/`
- Run the complete RAG pipeline: scrape → parse → vectorize

### No LLM providers available
- Set `GROQ_API_KEY` for primary provider
- Install Ollama locally for fallback
- Set `HUGGINGFACE_API_KEY` for cloud fallback

### Slow responses
- Use Groq for fastest responses
- Reduce `top_k` parameter
- Check LLM provider status</content>
</xai:function_call name="read_lints">
<parameter name="target_file">src/api/rag-api/api/README.md

