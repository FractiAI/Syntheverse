# PDF Scraper Agents

## Purpose

Collects research documents from Zenodo repositories to build the Syntheverse knowledge base. Downloads PDF papers and research materials while maintaining metadata and preventing duplicates.

## Key Modules

### ZenodoPDFScraper (`scrape_pdfs.py`)

Core scraping agent for Zenodo integration:

- **`__init__()`**: Initialize with download directory and rate limiting
- **`scrape_repository()`**: Process single Zenodo repository
- **`scrape_multiple_repositories()`**: Batch process multiple repositories
- **`download_file()`**: Stream download with progress tracking
- **`extract_pdf_files()`**: Parse Zenodo API for PDF metadata

### Command Line Interface

Script execution and configuration:

- **URL Processing**: Accept multiple Zenodo record URLs
- **Progress Reporting**: Real-time download status
- **Error Recovery**: Continue processing despite failures
- **Metadata Persistence**: Save download statistics

## Integration Points

### External Sources

- **Zenodo API**: REST API for repository metadata and file information
- **Academic Research**: Access to open research repositories
- **DOI System**: Integration with academic citation system

### Internal Pipeline

- **Parser Agent**: Receives downloaded PDFs for text extraction
- **Vectorizer Agent**: Consumes parsed content for embedding generation
- **API Server**: Serves knowledge from processed documents

### Data Flow

- **Input**: Zenodo repository URLs
- **Processing**: API queries and file downloads
- **Output**: PDF files and metadata for downstream processing

## Development Guidelines

### API Interaction

- **Rate Limiting**: Respect Zenodo API limits with configurable delays
- **Error Handling**: Graceful handling of API failures and network issues
- **Authentication**: No authentication required for public repositories

### File Management

- **Duplicate Prevention**: Track downloaded URLs and filenames
- **Naming Sanitization**: Ensure filesystem-compatible filenames
- **Integrity Verification**: Checksum validation for downloaded files

### Progress Tracking

- **Real-time Updates**: Console output for download progress
- **Statistics Collection**: Track download counts, sizes, and timing
- **Resume Capability**: Can restart without re-downloading

## Common Patterns

### Repository Processing Workflow

1. **URL Validation**: Extract and validate record IDs
2. **API Query**: Fetch repository metadata from Zenodo
3. **PDF Discovery**: Identify downloadable PDF files
4. **Duplicate Check**: Verify files not already downloaded
5. **Download Queue**: Add valid PDFs to download list
6. **Batch Download**: Stream files with progress tracking
7. **Metadata Update**: Record download statistics

### Error Recovery

- **Network Failures**: Retry with exponential backoff
- **API Limits**: Respect rate limits and implement delays
- **Partial Downloads**: Clean up incomplete files
- **Continue on Error**: Process remaining files despite individual failures

## Key Functions

### ZenodoPDFScraper

- `scrape_repository(url: str) -> Dict`: Process single repository
- `scrape_multiple_repositories(urls: List[str]) -> Dict`: Batch processing
- `download_file(url: str, filename: str, size: int) -> bool`: File download
- `extract_pdf_files(record_data: Dict) -> List[Dict]`: Parse PDF metadata
- `sanitize_filename(filename: str) -> str`: Filesystem-safe naming

### CLI Interface

- `main()`: Command-line argument processing
- URL validation and processing
- Configuration parameter handling
- Progress reporting and final statistics

## Performance Characteristics

- **Network Dependent**: Download speed varies by connection and file sizes
- **Rate Limited**: 1-second delays between requests by default
- **Memory Efficient**: Streams large files without loading entirely in memory
- **Resume Friendly**: Can be interrupted and restarted

## Error Scenarios

### Network Issues

- **Connection Failures**: Retry with backoff strategy
- **Timeout Errors**: Configurable timeout handling
- **Rate Limiting**: Automatic delay implementation

### API Issues

- **Invalid URLs**: Clear error messages for malformed URLs
- **Private Records**: Handle access restrictions
- **API Changes**: Adapt to Zenodo API modifications

### File System Issues

- **Permission Errors**: Clear error messages for write failures
- **Disk Space**: Pre-check available space
- **Filename Conflicts**: Automatic renaming for duplicates

## Quality Assurance

### Download Verification

- **Checksum Validation**: Verify file integrity when available
- **Size Validation**: Confirm downloaded file matches expected size
- **Content Validation**: Basic PDF format verification

### Metadata Accuracy

- **Source Tracking**: Maintain original Zenodo URLs
- **Timestamp Recording**: Track download timing
- **Statistics Accuracy**: Correct count and size reporting

## Testing and Validation

### Unit Tests

- **URL Processing**: Test various Zenodo URL formats
- **API Integration**: Mock API responses for testing
- **File Operations**: Test download and filesystem operations
- **Error Handling**: Verify failure scenario handling

### Integration Tests

- **Pipeline Continuity**: Ensure output works with parser
- **Data Consistency**: Verify metadata integrity
- **Performance Testing**: Measure download efficiency

## Ethical Considerations

### Academic Integrity

- **Public Access**: Only download publicly available materials
- **Citation Preservation**: Maintain source attribution
- **Usage Compliance**: Respect repository terms of use

### Resource Management

- **Rate Limiting**: Avoid overwhelming Zenodo infrastructure
- **Bandwidth Consideration**: Respect network resource usage
- **Storage Planning**: Consider long-term storage requirements

## Future Enhancements

- **Multi-Source Support**: Extend beyond Zenodo repositories
- **Content Filtering**: Intelligent selection of relevant documents
- **Incremental Updates**: Detect and download repository updates
- **Concurrent Downloads**: Multi-threaded downloading for performance
- **Content Classification**: Automatic categorization of downloaded materials</content>
</xai:function_call name="read_lints">
<parameter name="target_file">src/api/rag-api/scraper/AGENTS.md

