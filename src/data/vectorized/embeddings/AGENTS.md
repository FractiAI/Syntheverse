# Embeddings Agents

## Purpose

The `embeddings/` directory stores vectorized embeddings for semantic search and RAG (Retrieval-Augmented Generation) operations.

## Key Modules

### Embedding Files

- **`syntheverse_seed.json`**: Minimal test corpus with Syntheverse documentation chunks
- **`<pdf_name>.json`**: Generated embedding files (one per PDF document)

### File Structure

Each embedding JSON file contains an array of chunk objects with:
- `text`: Original chunk text content
- `metadata`: Chunk metadata (source, type, word count, etc.)
- `chunk_index`: Sequential index of chunk in document

## Integration Points

- RAG API loads embeddings at startup for semantic search
- Vectorizer generates embedding files from parsed chunks
- Test framework uses seed corpus to enable RAG API startup
- Embeddings enable keyword-based search (currently implemented)

## Development Guidelines

- Keep embedding files in JSON format for portability
- Include metadata with each chunk for debugging and analysis
- Use descriptive chunk indices for traceability
- Document embedding generation parameters

## Common Patterns

- Chunk-based text processing (400-1000 character chunks)
- Metadata enrichment for search relevance
- Sequential chunk indexing within documents
- JSON serialization for persistence





