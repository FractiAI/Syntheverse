# PDF Scraper

Downloads PDF documents from Zenodo research repositories for processing into the Syntheverse RAG knowledge base. Provides academic paper collection capabilities with duplicate prevention and metadata tracking.

## Features

- **Zenodo Integration**: Downloads PDFs from Zenodo research repositories
- **Duplicate Prevention**: Skips already downloaded files
- **Metadata Collection**: Preserves file metadata and checksums
- **Progress Tracking**: Real-time download status and statistics
- **Error Resilience**: Continues downloading despite individual failures

## Quick Start

### Scrape Single Repository

```bash
cd scraper
python scrape_pdfs.py --urls "https://zenodo.org/records/123456"
```

### Scrape Multiple Repositories

```bash
python scrape_pdfs.py \
    --urls "https://zenodo.org/records/123456" \
    --urls "https://zenodo.org/records/789012"
```

### Custom Output Directory

```bash
python scrape_pdfs.py \
    --urls "https://zenodo.org/records/123456" \
    --output-dir "../../data/pdfs"
```

## Components

### scrape_pdfs.py

Main scraper script with Zenodo integration:

- **URL Processing**: Accepts multiple Zenodo record URLs
- **API Integration**: Uses Zenodo REST API for metadata
- **File Download**: Downloads PDFs with progress tracking
- **Duplicate Detection**: Prevents re-downloading existing files

### ZenodoPDFScraper Class

Core scraping functionality:

- **Record Processing**: Extracts PDF information from Zenodo records
- **Batch Downloads**: Handles multiple files per repository
- **Error Handling**: Graceful failure handling
- **Metadata Preservation**: Maintains file information

## Output Structure

PDFs are saved to the specified directory with metadata:

```
pdfs/
├── paper1.pdf
├── paper2.pdf
├── metadata.json  # Download metadata and statistics
└── ...
```

Metadata file contains:
```json
{
  "total_downloaded": 25,
  "total_size_mb": 45.2,
  "repositories_processed": 3,
  "download_timestamp": "2025-01-XX...",
  "files": [
    {
      "filename": "paper1.pdf",
      "original_url": "https://zenodo.org/...",
      "size_bytes": 2048576,
      "checksum": "md5:abc123...",
      "downloaded_at": "2025-01-XX..."
    }
  ]
}
```

## Configuration Options

### Input URLs
- **Format**: Zenodo record URLs (e.g., `https://zenodo.org/records/123456`)
- **Multiple**: Use `--urls` flag multiple times for batch processing
- **Validation**: Automatic URL format validation

### Output Directory
- **Default**: `./pdfs` (relative to scraper/)
- **Custom**: Specify with `--output-dir` flag
- **Auto-creation**: Creates directory if it doesn't exist

### Request Settings
- **Delay**: Configurable delay between requests (default: 1 second)
- **Timeout**: 30-second timeout for API calls
- **Retries**: Automatic retry on transient failures

## Dependencies

```bash
pip install requests
```

## Processing Pipeline

1. **URL Parsing**: Extract record IDs from Zenodo URLs
2. **API Query**: Fetch record metadata from Zenodo API
3. **PDF Discovery**: Identify PDF files in the record
4. **Duplicate Check**: Verify file not already downloaded
5. **Download**: Stream PDF content with progress tracking
6. **Verification**: Validate downloaded file integrity
7. **Metadata Update**: Record download information

## File Structure

```
scraper/
├── scrape_pdfs.py    # Main scraper script
└── README.md         # This file
```

## Integration

### Output Directory
- **Default**: `../../data/pdfs/` (relative to scraper/)
- **Parser Input**: Feeds directly into PDF parser
- **Naming**: Original Zenodo filenames preserved

### Metadata Tracking
- **Download History**: Prevents duplicate downloads
- **Size Tracking**: Monitors total downloaded content
- **Source Attribution**: Maintains Zenodo record links

### Pipeline Integration
- **Parser**: Consumes downloaded PDFs
- **Vectorizer**: Receives parsed content
- **API**: Serves knowledge from processed documents

## Performance

- **Download Speed**: Depends on file sizes and network
- **Rate Limiting**: 1-second delay between requests (configurable)
- **Resume Capability**: Can be restarted without re-downloading
- **Memory Usage**: Low memory footprint

## Error Handling

### Network Issues
- **Timeout Handling**: 30-second timeouts with retry
- **Connection Errors**: Automatic retry with backoff
- **Rate Limiting**: Respects Zenodo API limits

### File Issues
- **Corrupted Downloads**: Checksum verification
- **Permission Errors**: Clear error messages
- **Disk Space**: Size validation before download

### API Issues
- **Invalid URLs**: Clear validation errors
- **Record Not Found**: Informative error messages
- **API Changes**: Handles API response variations

## Best Practices

- **Batch Processing**: Download from multiple repositories
- **Progress Monitoring**: Use for long-running downloads
- **Space Planning**: Check available disk space
- **Rate Respect**: Maintain reasonable delays between requests

## Troubleshooting

### No PDFs Found
- Verify Zenodo record contains PDF files
- Check URL format is correct
- Confirm record is publicly accessible

### Download Failures
- Check network connectivity
- Verify sufficient disk space
- Try individual repository downloads

### Duplicate Prevention Issues
- Clear download directory if needed
- Check existing files manually
- Use different output directory

## Usage Examples

### Academic Repository Scraping

```bash
# Download from Syntheverse research collection
python scrape_pdfs.py --urls "https://zenodo.org/records/17927561"

# Download multiple collections
python scrape_pdfs.py \
    --urls "https://zenodo.org/records/123456" \
    --urls "https://zenodo.org/records/789012" \
    --output-dir "../../data/pdfs"
```

### Integration with Pipeline

```bash
# 1. Scrape PDFs
cd scraper
python scrape_pdfs.py --urls "https://zenodo.org/records/17927561"

# 2. Parse PDFs
cd ../parser
python parse_all_pdfs.py --pdf-dir ../../data/pdfs

# 3. Vectorize chunks
cd ../vectorizer
python vectorize_parsed_chunks_simple.py --parsed-dir ../../data/parsed

# 4. Start API server
cd ../api
python rag_api.py
```</content>
</xai:function_call name="read_lints">
<parameter name="target_file">src/api/rag-api/scraper/README.md
