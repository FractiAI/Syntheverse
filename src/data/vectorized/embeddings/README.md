# Embeddings Directory

This directory stores vectorized embeddings for semantic search and RAG operations.

## Structure

```
embeddings/
├── syntheverse_seed.json    # Minimal test corpus (committed)
└── <pdf_name>.json          # Generated embeddings (gitignored)
```

## Seed Corpus

The `syntheverse_seed.json` file contains a minimal set of chunks for testing:
- 5 chunks covering Syntheverse system overview
- Enables RAG API to start in fresh clones
- Used for integration tests

## Generated Files

Embedding files are generated when running the vectorization pipeline:

```bash
cd src/api/rag-api/vectorizer
python vectorize_parsed_chunks_simple.py
```

## File Format

Each JSON file contains an array of chunk objects:

```json
[
  {
    "text": "Chunk text content...",
    "metadata": {
      "source": "document_name",
      "chunk_type": "content_type",
      "word_count": 42
    },
    "chunk_index": 0
  }
]
```

## Usage

- RAG API automatically loads all `*.json` files at startup
- Test framework uses seed corpus for integration tests
- Generated embeddings are excluded from version control
