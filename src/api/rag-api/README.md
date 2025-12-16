# RAG API - Scraper, Parser, Vectorizer, and API

Complete RAG (Retrieval-Augmented Generation) pipeline for Syntheverse, using Groq (fast cloud LLM) as the primary provider, with Hugging Face and Ollama as fallbacks.

## Status

✅ **Fully Operational** - Complete RAG pipeline with Groq integration, unified Syntheverse AI system, and web UI.

## Components

### 1. Scraper (`scraper/`)
Downloads PDFs from Zenodo repositories:
- **scrape_pdfs.py**: Scrapes scientific papers and research documents
- No duplicates - skips already downloaded files
- Saves metadata and download results

### 2. Parser (`parser/`)
Processes PDFs into searchable text chunks:
- **parse_all_pdfs.py**: Parses PDFs into searchable text chunks
- **langchain_pdf_processor.py**: LangChain-based PDF processing
- Intelligent text chunking with overlap
- Saves parsed chunks as JSON files

### 3. Vectorizer (`vectorizer/`)
Creates embeddings from parsed chunks:
- **vectorize_parsed_chunks_simple.py**: Creates embeddings from parsed chunks
- Uses local HuggingFace embeddings (no API calls)
- Saves vectorized embeddings as JSON files

### 4. API (`api/`)
FastAPI server for RAG queries:
- **rag_api.py**: Main FastAPI server with Groq integration
- **static/index.html**: Web UI for interactive queries
- **requirements_api.txt**: Python dependencies
- **start_rag_api.sh**: Startup script

## Quick Start

### 1. Install Dependencies

```bash
cd rag-api/api
pip install -r requirements_api.txt
```

### 2. Set Up Groq API Key

Get a free API key from https://console.groq.com/

```bash
# Set environment variable
export GROQ_API_KEY="your-groq-api-key-here"

# Or create .env file in project root
echo "GROQ_API_KEY=your-groq-api-key-here" > ../../.env
```

### 3. Start the API Server

```bash
cd rag-api/api
python rag_api.py

# Or use the startup script
./start_rag_api.sh
```

Access the API at: http://localhost:8000

### 4. Access Web UI

Open http://localhost:8000/static/index.html in your browser

## Complete Pipeline

### 1. Scrape PDFs

```bash
cd rag-api/scraper
python scrape_pdfs.py --urls https://zenodo.org/records/17244387
```

PDFs are saved to `data/pdfs/`

### 2. Parse PDFs

```bash
cd rag-api/parser
python parse_all_pdfs.py --pdf-dir ../../data/pdfs
```

Parsed chunks are saved to `data/parsed/`

### 3. Vectorize Chunks

```bash
cd rag-api/vectorizer
python vectorize_parsed_chunks_simple.py --parsed-dir ../../data/parsed
```

Embeddings are saved to `data/vectorized/embeddings/`

### 4. Start API Server

```bash
cd rag-api/api
python rag_api.py
```

The API automatically loads embeddings from `data/vectorized/embeddings/`

## LLM Providers

### Groq (Primary - Recommended)
- **Fast**: Sub-second response times
- **Free**: Free tier available
- **Model**: llama-3.1-8b-instant
- **Setup**: Just set `GROQ_API_KEY` environment variable

### Ollama (Fallback)
- **Local**: Runs on your machine
- **Free**: No API costs
- **Setup**: Install Ollama and run `ollama pull llama3.1`
- **See**: `api/OLLAMA_SETUP.md` for setup instructions

### Hugging Face (Fallback)
- **Cloud**: Uses Hugging Face Inference API
- **Setup**: Set `HUGGINGFACE_API_KEY` environment variable
- **See**: `api/CLOUD_API_SETUP.md` for setup instructions

## API Endpoints

### Health Check
```
GET /health
```
Returns API status and available LLM providers.

### Query
```
POST /query
Content-Type: application/json

{
  "query": "Your question here",
  "top_k": 5,
  "min_score": 0.0,
  "llm_model": "groq",
  "system_prompt": "Optional custom system prompt"
}
```

### Search
```
POST /search
Content-Type: application/json

{
  "query": "Search query",
  "top_k": 5,
  "min_score": 0.0
}
```

## Syntheverse Whole Brain AI

The RAG API uses a unified **Syntheverse Whole Brain AI** system prompt that integrates:
- **Gina**: Whole Brain Integrator
- **Leo**: Hydrogen-Holographic Fractal Engine
- **Pru**: Outcast Hero Life-Narrative Navigator

This creates a coherent, mythic, scientific, narrative, and resonant AI voice that aligns with the Syntheverse framework.

## Features

### Semantic Search
- Pre-computed embeddings for fast retrieval
- Similarity scoring
- Top-K results with configurable thresholds

### Answer Generation
- Context-aware responses using retrieved chunks
- Multiple LLM provider support
- Custom system prompts for specialized tasks

### Web UI
- Interactive query interface
- Real-time results
- Source citations
- LLM provider selection

## File Structure

```
rag-api/
├── README.md                  # This file
├── scraper/
│   └── scrape_pdfs.py        # PDF scraper
├── parser/
│   ├── parse_all_pdfs.py     # PDF parser
│   └── langchain_pdf_processor.py
├── vectorizer/
│   └── vectorize_parsed_chunks_simple.py
└── api/
    ├── rag_api.py            # Main API server
    ├── rag_api_ollama.py     # Ollama-specific version
    ├── requirements_api.txt  # Dependencies
    ├── start_rag_api.sh      # Startup script
    ├── static/
    │   └── index.html        # Web UI
    └── [setup guides]
```

## Data Directory Structure

```
data/
├── pdfs/                     # Downloaded PDFs
├── parsed/                   # Parsed text chunks
└── vectorized/
    ├── embeddings/           # Vector embeddings
    └── metadata/            # Embedding metadata
```

## Configuration

### Environment Variables

```bash
# Required for Groq
GROQ_API_KEY=your-groq-api-key

# Optional for Hugging Face
HUGGINGFACE_API_KEY=your-hf-key

# Optional for Ollama (default: http://localhost:11434)
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1
```

### API Configuration

Edit `rag_api.py` to customize:
- Default LLM provider
- Embedding model
- Chunk size and overlap
- Top-K results

## Integration with Layer 2

The RAG API is used by Layer 2 for PoD evaluation:
- **Evaluation Queries**: Specialized PoD evaluation prompts
- **Response Format**: Markdown report + JSON data
- **System Prompts**: Custom prompts for HHFE evaluation

## Performance

### Groq
- **Response Time**: < 1 second for most queries
- **Throughput**: High (free tier limits apply)
- **Cost**: Free tier available

### Ollama
- **Response Time**: 2-10 seconds (depends on hardware)
- **Throughput**: Limited by local hardware
- **Cost**: Free (runs locally)

## Troubleshooting

### Groq Not Available
- Check `GROQ_API_KEY` is set
- Verify API key is valid
- Check Groq service status

### Ollama Not Available
- Install Ollama: https://ollama.ai
- Run `ollama pull llama3.1`
- Check Ollama is running: `ollama list`

### No Embeddings Found
- Run the complete pipeline (scrape → parse → vectorize)
- Check embeddings directory: `data/vectorized/embeddings/`
- Verify embedding files are JSON format

## Documentation

- [Quick Start Groq](api/QUICK_START_GROQ.md)
- [Ollama Setup](api/OLLAMA_SETUP.md)
- [Cloud API Setup](api/CLOUD_API_SETUP.md)
- [API Documentation](../docs/api/RAG_API.md)

## Next Steps

- [ ] Advanced embedding models
- [ ] Multi-modal support (images, code)
- [ ] Real-time embedding updates
- [ ] Distributed embedding storage
- [ ] Advanced retrieval strategies
