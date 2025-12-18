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








