# RAG API - Scraper, Parser, Vectorizer

This component provides the complete RAG (Retrieval-Augmented Generation) pipeline for Syntheverse, using local Ollama integration.

## Components

### 1. Scraper (`scraper/`)
- **scrape_pdfs.py**: Downloads PDFs from Zenodo repositories
- Scrapes scientific papers and research documents
- No duplicates - skips already downloaded files

### 2. Parser (`parser/`)
- **parse_all_pdfs.py**: Parses PDFs into searchable text chunks
- **langchain_pdf_processor.py**: LangChain-based PDF processing
- Intelligent text chunking with overlap
- Saves parsed chunks as JSON files

### 3. Vectorizer (`vectorizer/`)
- **vectorize_parsed_chunks_simple.py**: Creates embeddings from parsed chunks
- Uses local HuggingFace embeddings (no API calls)
- Saves vectorized embeddings as JSON files

### 4. API (`api/`)
- **rag_api.py**: FastAPI server for RAG queries
- **static/**: Web UI for interactive queries
- **requirements_api.txt**: Python dependencies
- **start_rag_api.sh**: Startup script

## Quick Start

### 1. Scrape PDFs
```bash
cd rag-api/scraper
python scrape_pdfs.py --urls https://zenodo.org/records/17244387
```

### 2. Parse PDFs
```bash
cd rag-api/parser
python parse_all_pdfs.py --pdf-dir ../../data/pdfs
```

### 3. Vectorize Chunks
```bash
cd rag-api/vectorizer
python vectorize_parsed_chunks_simple.py --parsed-dir ../../data/parsed
```

### 4. Start API Server
```bash
cd rag-api/api
pip install -r requirements_api.txt
python rag_api.py
```

Access the API at: http://localhost:8000

## Integration with Ollama

The RAG API is designed to integrate with Ollama for local LLM inference. Update `rag_api.py` to use Ollama models for answer generation.

See `docs/api/` for detailed API documentation.

