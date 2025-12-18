# Vectorizer

Converts parsed text chunks into vector embeddings for semantic search using local HuggingFace models. Creates searchable representations of documents without requiring external API calls or database dependencies.

## Features

- **Local Embeddings**: Uses HuggingFace models with no API costs
- **Batch Processing**: Efficient processing of multiple documents
- **Duplicate Prevention**: Skips already vectorized content
- **Progress Tracking**: Real-time processing status and statistics
- **Flexible Output**: JSON format optimized for semantic search

## Quick Start

### Vectorize Parsed Chunks

```bash
cd vectorizer
python vectorize_parsed_chunks.py --parsed-dir ../../data/parsed
```

This processes all JSON files from `data/parsed/` and saves embeddings to `data/vectorized/embeddings/`

### Custom Configuration

```bash
# Use different embedding model
python vectorize_parsed_chunks.py \
    --parsed-dir ../../data/parsed \
    --embedding-model "all-mpnet-base-v2" \
    --batch-size 50
```

### Custom Output Directory

```bash
python vectorize_parsed_chunks.py \
    --parsed-dir ../../data/parsed \
    --output-dir "../../data/vectorized"
```

## Components

### vectorize_parsed_chunks.py

Main vectorization script:

- **File Processing**: Reads parsed JSON chunk files
- **Model Loading**: Initializes HuggingFace embedding models
- **Batch Embedding**: Processes chunks in configurable batches
- **Progress Reporting**: Real-time status updates
- **Duplicate Detection**: Skips already processed files

## Output Structure

Embeddings are saved in organized directory structure:

```
vectorized/
├── embeddings/          # Embedding JSON files
│   ├── doc1.json
│   ├── doc2.json
│   └── ...
└── metadata/           # Processing metadata
    ├── stats.json      # Overall statistics
    └── processed_files.json
```

Individual embedding file format:
```json
{
  "filename": "paper.pdf",
  "model": "all-MiniLM-L6-v2",
  "chunks": [
    {
      "text": "Extracted text content...",
      "embedding": [0.123, 0.456, ...],
      "chunk_index": 0,
      "metadata": {
        "source": "paper.pdf",
        "page": 1
      }
    }
  ],
  "metadata": {
    "total_chunks": 25,
    "embedding_dimension": 384,
    "processing_time": 3.2,
    "model": "all-MiniLM-L6-v2"
  }
}
```

## Configuration Options

### Embedding Models
- **Default**: `all-MiniLM-L6-v2` (384 dimensions, fast)
- **Alternative**: `all-mpnet-base-v2` (768 dimensions, higher quality)
- **Performance Trade-off**: Larger models = better quality, slower processing

### Batch Size
- **Default**: 100 chunks per batch
- **Range**: 10-500 recommended
- **Impact**: Larger batches = faster processing, higher memory usage

### Input Directory
- **Default**: `./parsed` (relative to vectorizer/)
- **Format**: JSON files from parser output
- **Validation**: Checks for required chunk structure

## Dependencies

```bash
pip install sentence-transformers torch langchain-community
```

## Processing Pipeline

1. **File Discovery**: Scan parsed directory for JSON files
2. **Duplicate Check**: Verify files not already processed
3. **Model Loading**: Initialize HuggingFace embedding model
4. **Chunk Processing**: Extract text from JSON chunks
5. **Batch Embedding**: Generate vectors in configurable batches
6. **Metadata Addition**: Attach processing information
7. **JSON Serialization**: Save embeddings with metadata
8. **Statistics Update**: Track processing metrics

## File Structure

```
vectorizer/
├── vectorize_parsed_chunks.py  # Main vectorization script
└── README.md                          # This file
```

## Integration

### Input
- **Directory**: `../../data/parsed/` (relative to vectorizer/)
- **Format**: JSON files from PDF parser
- **Content**: Text chunks with metadata

### Output
- **Directory**: `../../data/vectorized/embeddings/` (relative to vectorizer/)
- **Format**: JSON files with embeddings and metadata
- **API Ready**: Directly consumable by RAG API server

### Pipeline Integration
- **Parser**: Provides input JSON files
- **API Server**: Loads embeddings for semantic search
- **Query System**: Enables fast similarity search

## Performance

- **Processing Speed**: ~100-500 chunks per minute (model dependent)
- **Memory Usage**: 200-800MB (depends on model and batch size)
- **First Run**: Downloads model (~80-400MB) and caches locally
- **Subsequent Runs**: Fast loading from cache

## Model Options

### all-MiniLM-L6-v2 (Default)
- **Dimensions**: 384
- **Size**: ~80MB download
- **Speed**: Fast processing
- **Quality**: Good for general semantic search

### all-mpnet-base-v2 (High Quality)
- **Dimensions**: 768
- **Size**: ~400MB download
- **Speed**: Slower processing
- **Quality**: Better semantic understanding

## Error Handling

### Model Loading Issues
- **Download Failures**: Clear error messages with troubleshooting
- **Dependency Issues**: Check PyTorch/Torch installation
- **Disk Space**: Verify sufficient space for model download

### File Processing Issues
- **Invalid JSON**: Skip malformed files with warnings
- **Missing Chunks**: Validate chunk structure before processing
- **Encoding Issues**: Handle various text encodings

### Memory Issues
- **Large Batches**: Reduce batch_size parameter
- **Large Models**: Use smaller embedding model
- **System RAM**: Monitor available memory during processing

## Best Practices

- **Model Selection**: Start with default, upgrade for better quality
- **Batch Tuning**: Adjust based on available RAM
- **Progress Monitoring**: Use for long-running vectorization jobs
- **Incremental Processing**: Can resume after interruptions

## Troubleshooting

### Model Download Issues
- Check internet connection
- Verify sufficient disk space (~500MB free)
- Try different model if download fails

### Processing Failures
- Validate input JSON files from parser
- Check chunk structure and text content
- Reduce batch size if memory issues occur

### Performance Issues
- Use smaller embedding model for speed
- Reduce batch size to manage memory
- Process fewer files at once

## Usage Examples

### Complete Pipeline

```bash
# 1. Scrape PDFs
cd ../scraper
python scrape_pdfs.py --urls "https://zenodo.org/records/17927561"

# 2. Parse PDFs
cd ../parser
python parse_all_pdfs.py --pdf-dir ../../data/pdfs

# 3. Vectorize chunks
cd ../vectorizer
python vectorize_parsed_chunks.py --parsed-dir ../../data/parsed

# 4. Start API server
cd ../api
python rag_api.py
```

### High-Quality Embeddings

```bash
# Use larger model for better semantic search
python vectorize_parsed_chunks.py \
    --parsed-dir ../../data/parsed \
    --embedding-model "all-mpnet-base-v2" \
    --batch-size 50
```

### Memory-Constrained Environment

```bash
# Minimize memory usage
python vectorize_parsed_chunks.py \
    --parsed-dir ../../data/parsed \
    --embedding-model "all-MiniLM-L6-v2" \
    --batch-size 10
```</content>
</xai:function_call name="read_lints">
<parameter name="target_file">src/api/rag-api/vectorizer/README.md

