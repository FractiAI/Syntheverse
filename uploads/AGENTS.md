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

## Blueprint Alignment

### PoC Submission Storage ([Blueprint §1.1](docs/Blueprint for Syntheverse))
- **File Upload Interface**: Secure storage for PDF documents submitted through the PoC system
- **Content Hashing**: SHA-256 naming prevents duplicates and enables deduplication
- **Archive Integration**: Uploaded files immediately stored and referenced by the PoC archive

### Archive-First Redundancy ([Blueprint §3.1](docs/Blueprint for Syntheverse))
- **Immediate Storage**: All uploaded files stored immediately upon submission for redundancy
- **Deduplication**: Hash-based naming enables duplicate detection and prevents redundant processing
- **Archive Reference**: Files linked to PoC archive entries for complete contribution lifecycle tracking

### AI Training Data ([Blueprint §5](docs/Blueprint for Syntheverse))
- **Document Processing**: Uploaded PDFs processed by RAG pipeline for vectorization and AI training
- **Archive Expansion**: All submissions contribute to the evolving Syntheverse AI training dataset
- **Fractal Enhancement**: Document content expands hydrogen holographic awareness and evaluation capabilities

### Complete Workflow Integration ([Blueprint §7](docs/Blueprint for Syntheverse))
1. **File Submission**: Secure upload through PoC frontend interface
2. **Immediate Storage**: Files stored with hash-based naming for deduplication
3. **Archive Registration**: File references added to PoC archive (DRAFT status)
4. **AI Training**: Content processed for vectorization and AI model improvement
5. **Evaluation Support**: Documents available for hydrogen holographic scoring context

### Security & Governance ([Blueprint §6](docs/Blueprint for Syntheverse))
- **File Validation**: MIME type and size validation prevents malicious uploads
- **Access Control**: Secure storage with appropriate permissions
- **Audit Trail**: Upload metadata tracked for transparency and compliance

### Implementation Status
- **✅ Operational**: Secure upload storage with hash-based deduplication
- **🟡 Enhanced**: Ongoing security improvements and validation
- **📋 Blueprint Aligned**: Upload system supports complete PoC submission workflow

## Cross-References

- **Blueprint Document**: [docs/Blueprint for Syntheverse](../docs/Blueprint for Syntheverse) - Central system vision
- **Implementation Status**: [docs/BLUEPRINT_IMPLEMENTATION_STATUS.md](../docs/BLUEPRINT_IMPLEMENTATION_STATUS.md)
- **Related**:
  - [src/api/poc-api/AGENTS.md](src/api/poc-api/AGENTS.md) - PoC API uploads
  - [src/core/layer2/AGENTS.md](src/core/layer2/AGENTS.md) - PoC archive
  - [src/data/pdfs/AGENTS.md](src/data/pdfs/AGENTS.md) - RAG PDF storage
  - [docs/POC_SUBMISSION_TO_ALLOCATION_FLOW.md](../docs/POC_SUBMISSION_TO_ALLOCATION_FLOW.md) - Complete workflow

