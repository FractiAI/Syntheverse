# PDF Storage Agents

## Purpose

Storage and management of PDF documents downloaded from Zenodo repositories for the Syntheverse RAG pipeline.

## Key Modules

### PDF File Storage (`*.pdf`)

- **Research Documents**: PDF files downloaded from Zenodo repositories
- **File Naming**: Sanitized filenames preserving original names when possible
- **Duplicate Prevention**: Automatic skipping of duplicate downloads
- **Metadata Tracking**: Connection to scraping metadata in `metadata/`

### Download Process

- **Zenodo Integration**: PDF download from Zenodo repository URLs
- **Batch Processing**: Multiple PDF download support
- **Error Handling**: Robust error handling for failed downloads
- **Progress Tracking**: Download progress and completion status

## Integration Points

- PDF files downloaded by RAG scraper in `src/api/rag-api/scraper/`
- Input for RAG parser in `src/api/rag-api/parser/`
- Referenced by metadata files in `src/data/metadata/`
- Used by RAG API for document retrieval and display

## Development Guidelines

- Maintain file naming conventions for traceability
- Ensure PDF files are properly excluded from version control
- Implement efficient duplicate detection
- Handle large file downloads gracefully
- Document download sources and permissions

## Common Patterns

- PDF file storage and organization
- Filename sanitization and normalization
- Duplicate download prevention
- Batch processing workflows
- Repository integration patterns





