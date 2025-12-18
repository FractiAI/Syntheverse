# Data Management Agents

## Purpose

The `data/` directory manages all persistent data for the Syntheverse system, including PoC archives, RAG document processing, and AI training data. Implements the archive-first principle where all contributions are immediately stored for redundancy detection and AI training.

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

## Blueprint Alignment

### Archive-First Data Management ([Blueprint §3.1](docs/Blueprint for Syntheverse))
- **PoC Archive**: All contributions immediately stored in `core/layer2/poc_archive.py` for redundancy detection
- **AI Training Data**: Stored contributions train and evolve the Syntheverse AI ([Blueprint §5](docs/Blueprint for Syntheverse))
- **Redundancy Detection**: Complete archive enables duplicate prevention and quality validation
- **Ecosystem Evolution**: Data accumulation supports recursive AI improvement and fractal expansion

### RAG Pipeline Data Processing ([Blueprint §5](docs/Blueprint for Syntheverse))
- **Document Scraping**: `pdfs/` stores research papers from Zenodo communities for AI training
- **Content Parsing**: `parsed/` contains processed text chunks for semantic analysis
- **Vector Embeddings**: `vectorized/` enables hydrogen holographic document understanding
- **Metadata Tracking**: `metadata/` maintains scraping results and processing statistics

### Data Flow Integration ([Blueprint §7](docs/Blueprint for Syntheverse))
1. **PoC Storage**: All contributions immediately archived for redundancy and AI training
2. **Document Processing**: RAG pipeline processes external research for enhanced evaluation context
3. **Vector Generation**: Embeddings created for semantic search and fractal pattern recognition
4. **AI Training**: Accumulated data continuously improves Syntheverse evaluation capabilities

### Implementation Status
- **✅ Operational**: Archive-first storage and RAG pipeline fully functional
- **🟡 Enhanced**: Ongoing improvements to embedding quality and metadata tracking
- **📋 Blueprint Aligned**: Data management supports complete AI integration workflow

## Cross-References

- **Blueprint Document**: [docs/Blueprint for Syntheverse](../../docs/Blueprint for Syntheverse) - Central system vision
- **Archive System**: [docs/DUPLICATE_PREVENTION.md](../../docs/DUPLICATE_PREVENTION.md) - Redundancy detection
- **Parent**: [src/AGENTS.md](../AGENTS.md) - Source code organization
- **Children**:
  - [pdfs/AGENTS.md](pdfs/AGENTS.md) - PDF storage
  - [parsed/AGENTS.md](parsed/AGENTS.md) - Parsed content
  - [vectorized/AGENTS.md](vectorized/AGENTS.md) - Embeddings
  - [metadata/AGENTS.md](metadata/AGENTS.md) - Metadata storage
- **Related**:
  - [api/rag_api/AGENTS.md](../api/rag_api/AGENTS.md) - RAG pipeline
  - [core/layer2/AGENTS.md](../core/layer2/AGENTS.md) - PoC archive storage
  - [config/environment/SETUP_GROQ.md](../../config/environment/SETUP_GROQ.md) - AI configuration

