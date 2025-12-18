# RAG API Agents

## Purpose

Complete RAG (Retrieval-Augmented Generation) pipeline with Groq integration. Provides document scraping, parsing, vectorization, and semantic search capabilities.

## Key Modules

### API Server (`api/`)

- **`rag_api.py`**: Main FastAPI server with Groq integration
- **`rag_api_ollama.py`**: Ollama-specific version
- **`static/index.html`**: Web UI for interactive queries

### Scraper (`scraper/`)

- **`scrape_pdfs.py`**: Downloads PDFs from Zenodo repositories

### Parser (`parser/`)

- **`parse_all_pdfs.py`**: Parses PDFs into searchable text chunks
- **`langchain_pdf_processor.py`**: LangChain-based PDF processing

### Vectorizer (`vectorizer/`)

- **`vectorize_parsed_chunks.py`**: Creates embeddings from parsed chunks with validation and statistics

### Analysis (`analysis/`)

Embedding analysis and visualization suite:

- **`embedding_analyzer.py`**: Statistics, quality scoring, and clustering analysis
- **`embedding_visualizer.py`**: Static plots with customizable styling
- **`pca_reducer.py`**: Dimensionality reduction with explained variance analysis
- **`embedding_validator.py`**: Validation with severity-based reporting
- **`similarity_analyzer.py`**: Similarity analysis with duplicate detection
- **`embedding_search.py`**: Semantic search with query validation
- **`cli/`**: Command-line tools for analysis workflows

## Integration Points

- **Zenodo**: Scrapes PDFs from repositories
- **Groq API**: Primary LLM provider (fast, free tier)
- **Ollama**: Fallback local LLM
- **HuggingFace**: Fallback cloud LLM
- **Layer 2**: Not used for PoC evaluation (direct Grok API calls)

## Development Guidelines

- Use FastAPI for modern async support
- Implement semantic search with pre-computed embeddings
- Support multiple LLM providers with fallback
- Use Syntheverse Whole Brain AI system prompt
- Handle file operations securely
- Document all API endpoints

## Common Patterns

- Pipeline: Scrape → Parse → Vectorize → Query
- Semantic search with similarity scoring
- LLM integration with context building
- Web UI for interactive queries
- Multiple provider support with fallback

## File Structure

```
rag_api/
├── api/
│   ├── rag_api.py              # Main FastAPI server (Groq)
│   ├── rag_api_ollama.py       # Ollama version
│   ├── static/index.html       # Web UI
│   └── requirements_api.txt    # API dependencies
├── scraper/
│   └── scrape_pdfs.py          # Zenodo PDF scraping
├── parser/
│   ├── parse_all_pdfs.py       # PDF parsing pipeline
│   └── langchain_pdf_processor.py # LangChain processing
├── vectorizer/
│   └── vectorize_parsed_chunks.py # Embedding generation
├── analysis/                   # Analysis and visualization
│   ├── cli/                   # Command-line tools
│   ├── embedding_analyzer.py
│   ├── embedding_visualizer.py
│   ├── pca_reducer.py
│   ├── embedding_validator.py
│   ├── similarity_analyzer.py
│   └── embedding_search.py
└── README.md
```

## Ports & Configuration

- **Port**: 8000 (default)
- **LLM Providers**: Groq (primary), Ollama (fallback), HuggingFace (fallback)
- **Data Pipeline**: Scrape → Parse → Vectorize → Analyze

## Cross-References

- **Parent**: [api/AGENTS.md](../AGENTS.md) - API services overview
- **Related**:
  - [data/AGENTS.md](../../data/AGENTS.md) - Data pipeline integration
  - [config/environment/AGENTS.md](../../../config/environment/AGENTS.md) - Groq API configuration

