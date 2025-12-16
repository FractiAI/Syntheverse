# Vectorized Directory

This directory stores vectorized embeddings for semantic search.

## Structure

```
vectorized/
├── embeddings/        # Embedding JSON files (one per PDF)
└── metadata/          # Vectorization metadata and statistics
```

## Usage

Embeddings are generated here when running:

```bash
cd rag-api/vectorizer
python vectorize_parsed_chunks_simple.py --parsed-dir ../../data/parsed --output-dir ../../data/vectorized
```

## File Format

### Embeddings (`embeddings/`)
Each JSON file contains an array of vectorized chunks with:
- `text`: Original chunk text
- `embedding`: Vector embedding (array of floats)
- `metadata`: Chunk metadata
- `chunk_index`: Chunk index

### Metadata (`metadata/`)
- `vectorization_metadata.json`: Processing statistics and model information

## Notes

- The RAG API loads embeddings from `embeddings/` directory
- Already vectorized files are automatically skipped
- Embeddings use local HuggingFace models (no API calls)


