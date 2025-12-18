# File Upload Storage

## Purpose

Root-level storage for uploaded files, primarily PDF documents submitted through the PoC system.

## Contents

- PDF files uploaded via the PoC submission interface
- Files named with content hash for deduplication (e.g., `{sha256_hash}_test.pdf`)

## Integration Points

- Receives uploads from `src/api/poc-api/` Flask server
- Duplicates may exist in `src/api/poc-api/uploads/` (API-level storage)
- Referenced by PoC archive entries in `src/core/layer2/poc_archive.py`
- Processed by RAG pipeline for vectorization

## File Naming Convention

```
{content_hash}_{original_name_suffix}.pdf
```

- `content_hash`: SHA-256 hash of file content for deduplication
- `original_name_suffix`: Preserved portion of original filename

## Development Guidelines

- Treat as user-generated content
- Exclude from version control (sensitive data)
- Implement cleanup for orphaned files
- Validate file types before storage

## Security Considerations

- Validate file extensions and MIME types
- Scan for malware in production
- Limit file sizes to prevent abuse
- Hash-based naming prevents directory traversal

## Cross-References

- **Related**:
  - [src/api/poc-api/AGENTS.md](src/api/poc-api/AGENTS.md) - PoC API uploads
  - [src/core/layer2/AGENTS.md](src/core/layer2/AGENTS.md) - PoC archive
  - [src/data/pdfs/AGENTS.md](src/data/pdfs/AGENTS.md) - RAG PDF storage

