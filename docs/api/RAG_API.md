# RAG API Documentation

REST API for querying the Syntheverse RAG system using local embeddings for retrieval and LLM APIs for answer generation.

## Features

- ✅ **Local Retrieval**: Uses local embeddings for fast semantic search
- ✅ **LLM Integration**: Groq (primary), HuggingFace, and Ollama for answer generation
- ✅ **Fast Search**: Cosine similarity search on pre-computed embeddings
- ✅ **REST API**: Standard REST endpoints for easy integration
- ✅ **Web UI**: Built-in web interface for interactive queries
- ✅ **CORS Enabled**: Ready for frontend integration
- ✅ **Auto-generated Docs**: Swagger/OpenAPI documentation

## Installation

```bash
pip install -r requirements_api.txt
```

## Quick Start

### Start the API Server

```bash
python rag_api.py
```

Or use the startup script:

```bash
./start_rag_api.sh
```

The server will start on `http://localhost:8000`

### Access Points

- **Web UI**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Stats**: http://localhost:8000/stats

## API Endpoints

### POST `/query`

Query the RAG system and get an answer with sources.

**Request Body:**
```json
{
  "query": "What is hydrogen holography?",
  "top_k": 5,
  "min_score": 0.0
}
```

**Response:**
```json
{
  "answer": "Based on the available documents...",
  "sources": [
    {
      "text": "Chunk text...",
      "score": 0.85,
      "pdf_filename": "example.pdf",
      "metadata": {...},
      "chunk_index": 0
    }
  ],
  "query": "What is hydrogen holography?",
  "processing_time": 0.15,
  "num_sources": 5
}
```

### POST `/search`

Search for relevant chunks without answer generation.

**Request Body:**
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
  "results": [...],
  "count": 10
}
```

### GET `/health`

Check API health and status.

**Response:**
```json
{
  "status": "healthy",
  "chunks_loaded": 3007,
  "pdfs_loaded": 118
}
```

### GET `/stats`

Get system statistics.

**Response:**
```json
{
  "total_chunks": 3007,
  "total_pdfs": 118,
  "embedding_model": "all-MiniLM-L6-v2",
  "pdfs": ["file1.pdf", "file2.pdf", ...]
}
```

## Usage Examples

### Python

```python
import requests

# Query the RAG system
response = requests.post(
    "http://localhost:8000/query",
    json={
        "query": "What is the Hydrogen Holographic Framework?",
        "top_k": 5,
        "min_score": 0.0
    }
)

data = response.json()
print(data["answer"])
for source in data["sources"]:
    print(f"Source: {source['pdf_filename']} (Score: {source['score']:.2f})")
```

### cURL

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is fractal intelligence?",
    "top_k": 5,
    "min_score": 0.0
  }'
```

### JavaScript/Fetch

```javascript
const response = await fetch('http://localhost:8000/query', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    query: 'What is hydrogen holography?',
    top_k: 5,
    min_score: 0.0
  })
});

const data = await response.json();
console.log(data.answer);
```

## Configuration

### Environment Setup

Before running the RAG API, set up your environment:

1. **Create .env file** in project root:
```bash
# In project root directory
echo "GROQ_API_KEY=gsk_your-groq-api-key-here" > .env
```

2. **Get Groq API Key**:
   - Visit https://console.groq.com/
   - Sign up (free)
   - Create API key
   - Copy the key (starts with `gsk_`)

3. **Verify setup**:
```bash
python -c "from src.core.utils import load_groq_api_key; print('✓' if load_groq_api_key() else '✗')"
```

### Embedding Model

The API uses `all-MiniLM-L6-v2` by default. To change:

```python
rag_engine = RAGEngine(
    embeddings_dir="./vectorized/embeddings",
    embedding_model="all-mpnet-base-v2"  # Better quality, slower
)
```

### Embeddings Directory

Default: `./vectorized/embeddings`

Ensure this directory contains the vectorized JSON files from `vectorize_parsed_chunks_simple.py`.

## LLM Providers

The RAG API supports multiple LLM providers for answer generation:

### Groq (Primary - Recommended)
- **Fast**: Sub-second response times
- **Free**: Free tier available
- **Model**: llama-3.1-8b-instant
- **Setup**: Set `GROQ_API_KEY` environment variable

### Ollama (Local)
- **Free**: No API costs
- **Local**: Runs on your machine
- **Setup**: Install Ollama and run `ollama pull llama3.1`
- **Performance**: 2-10 seconds per query

### Hugging Face (Cloud)
- **Cloud**: Uses Hugging Face Inference API
- **Setup**: Set `HUGGINGFACE_API_KEY` environment variable
- **Cost**: Varies by usage

## Syntheverse Whole Brain AI

The API uses a unified **Syntheverse Whole Brain AI** system prompt that integrates:
- **Gina**: Whole Brain Integrator
- **Leo**: Hydrogen-Holographic Fractal Engine
- **Pru**: Outcast Hero Life-Narrative Navigator

This creates a coherent, mythic, scientific, narrative, and resonant AI voice that aligns with the Syntheverse framework.

Custom system prompts can be provided in the query request for specialized tasks.

## How It Works

1. **Load Embeddings**: On startup, loads all vectorized chunks from JSON files
2. **Query Embedding**: Converts user query to embedding using local model
3. **Similarity Search**: Computes cosine similarity with all chunks
4. **Rank Results**: Returns top-k most similar chunks
5. **Generate Answer**: Uses LLM (Groq/HuggingFace/Ollama) to generate answer from top chunks

## Performance

- **Query Processing**: ~1-3 seconds per query (depends on LLM provider and number of chunks)
- **Memory Usage**: ~500MB-1GB (depends on number of chunks and embedding model)
- **API Costs**: Varies by LLM provider (Groq free tier available, others may have costs)

## Production Deployment

For production:

1. **Update CORS**: Set specific origins in `rag_api.py`
2. **Use Gunicorn**: `gunicorn rag_api:app -w 4 -k uvicorn.workers.UvicornWorker`
3. **Add Authentication**: Implement API keys or OAuth
4. **Enable HTTPS**: Use reverse proxy (nginx) with SSL
5. **Monitor**: Add logging and monitoring

## Troubleshooting

### "RAG engine not initialized"

Ensure the `vectorized/embeddings/` directory exists and contains JSON files.

### Slow queries

- Reduce `top_k` parameter
- Use a smaller embedding model
- Consider using a vector database (ChromaDB) for faster search

### Memory issues

- Process fewer PDFs
- Use a smaller embedding model
- Increase system RAM

## License

See repository for license information.

