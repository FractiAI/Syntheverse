# Data Management Agents

## Purpose

The `data/` directory manages all data files including PDFs, parsed content, embeddings, and metadata.

## Key Modules

### PDFs (`pdfs/`)

- Downloaded PDF documents from Zenodo
- Scraped research papers and documents
- Used as source material for RAG pipeline

### Parsed (`parsed/`)

- Text chunks extracted from PDFs
- Processed by RAG parser
- Stored as JSON files with metadata

### Vectorized (`vectorized/`)

- **`embeddings/`**: Vector embeddings for semantic search
- **`metadata/`**: Embedding metadata and indexing

### Metadata (`metadata/`)

- Scraping results and metadata
- Zenodo record information
- Download statistics

## Integration Points

- RAG scraper downloads PDFs
- RAG parser processes PDFs into chunks
- RAG vectorizer creates embeddings
- RAG API uses embeddings for search
- Data files excluded from git (see .gitignore)

## Development Guidelines

- Keep directory structure with .gitkeep files
- Exclude large data files from version control
- Document data processing pipeline
- Maintain data directory README files

## Common Patterns

- Pipeline: Scrape → Parse → Vectorize → Query
- JSON format for structured data
- Metadata tracking for all data
- Git-ignored content, tracked structure

## File Structure

```
data/
├── pdfs/                     # Raw PDF documents
│   └── .gitkeep             # Structure preservation
├── parsed/                  # Parsed text chunks
│   └── .gitkeep             # Structure preservation
├── vectorized/              # Vector embeddings
│   ├── embeddings/          # Vector data files
│   └── metadata/            # Embedding metadata
└── metadata/                # Scraping metadata
    ├── zenodo_scrape_results.json
    └── test_scrape_results.json
```

## Data Pipeline

1. **Scraping**: Zenodo API → PDF downloads (`pdfs/`)
2. **Parsing**: PDF processing → Text chunks (`parsed/`)
3. **Vectorization**: Embedding generation → Vectors (`vectorized/`)
4. **Search**: Semantic queries → Results via RAG API

## Cross-References

- **Parent**: [src/AGENTS.md](../AGENTS.md) - Source code organization
- **Children**:
  - [pdfs/AGENTS.md](pdfs/AGENTS.md) - PDF storage
  - [parsed/AGENTS.md](parsed/AGENTS.md) - Parsed content
  - [vectorized/AGENTS.md](vectorized/AGENTS.md) - Embeddings
  - [metadata/AGENTS.md](metadata/AGENTS.md) - Metadata storage
- **Related**:
  - [api/rag_api/AGENTS.md](../api/rag_api/AGENTS.md) - RAG pipeline
  - [core/layer2/AGENTS.md](../core/layer2/AGENTS.md) - PoC archive storage

