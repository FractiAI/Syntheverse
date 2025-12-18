# Alternative RAG API

Extended RAG (Retrieval-Augmented Generation) implementation with advanced analysis and visualization.

## Features

- Enhanced semantic search with multiple ranking algorithms
- Comprehensive embedding analysis and visualization
- Document processing pipeline (scraping, parsing, vectorization)
- Interactive query processing with conversation context

## Directory Structure

```
rag-api/
├── api/                     # FastAPI server
├── analysis/                # Embedding analysis suite
│   └── cli/                 # Command-line tools
├── AGENTS.md               # Technical documentation
├── FRACTAL.md              # Fractal analysis
└── requirements_api.txt    # Python dependencies
```

## Quick Start

```bash
cd src/api/rag-api
python -m venv venv
source venv/bin/activate
pip install -r requirements_api.txt

# Start API server
cd api
python rag_api.py
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/search` | POST | Semantic search with ranking |
| `/query` | POST | Interactive RAG queries |
| `/documents` | GET | List available documents |
| `/analysis/stats` | GET | Statistical analysis |

## Integration

- **GROQ API**: Primary LLM provider
- **Ollama**: Local LLM fallback
- **HuggingFace**: Alternative embeddings

## Related Documentation

- [AGENTS.md](AGENTS.md) - Technical specifications
- [analysis/README.md](analysis/README.md) - Analysis tools
- [Parent: src/api/README.md](../README.md) - API services overview
