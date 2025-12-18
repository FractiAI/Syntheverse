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

- **`vectorize_parsed_chunks_simple.py`**: Creates embeddings from parsed chunks with validation and statistics

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



