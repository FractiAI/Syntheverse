# PDF Parser

Processes PDF documents into searchable text chunks using LangChain's advanced document processing capabilities. Converts PDFs into structured JSON format for vectorization and semantic search.

## Features

- **LangChain Integration**: Uses LangChain's PyPDFLoader and RecursiveCharacterTextSplitter
- **Intelligent Chunking**: Recursive text splitting with configurable overlap
- **Duplicate Prevention**: Skips already processed PDFs
- **Progress Tracking**: Real-time processing status and statistics
- **Flexible Output**: JSON format optimized for embedding generation

## Quick Start

### Process All PDFs

```bash
cd parser
python parse_all_pdfs.py --pdf-dir ../../data/pdfs
```

This processes all PDFs from `data/pdfs/` and saves chunks to `data/parsed/`

### Custom Configuration

```bash
# Custom chunk size and overlap
python parse_all_pdfs.py \
    --pdf-dir ../../data/pdfs \
    --chunk-size 1500 \
    --chunk-overlap 300
```

## Components

### parse_all_pdfs.py

Batch processor for entire PDF directories:

- **PDF Discovery**: Finds all PDF files in specified directory
- **Duplicate Checking**: Skips files already processed
- **Progress Reporting**: Shows processing status and completion
- **Error Handling**: Continues processing despite individual file errors

### langchain_pdf_processor.py

LangChain-based PDF processing core:

- **PyPDFLoader**: Robust PDF text extraction
- **RecursiveCharacterTextSplitter**: Intelligent text chunking
- **Fallback Processing**: Multiple extraction strategies
- **Metadata Preservation**: Maintains document structure

## Output Format

Each processed PDF creates a JSON file:

```json
{
  "filename": "paper.pdf",
  "chunks": [
    {
      "text": "Extracted text content...",
      "chunk_index": 0,
      "metadata": {
        "source": "paper.pdf",
        "page": 1,
        "chunk_size": 1000,
        "chunk_overlap": 200
      }
    }
  ],
  "metadata": {
    "total_chunks": 25,
    "total_characters": 25000,
    "processing_time": 2.3
  }
}
```

## Configuration Options

### Chunk Size
- **Default**: 1000 characters
- **Range**: 500-2000 recommended
- **Impact**: Larger chunks = more context, smaller chunks = more precision

### Chunk Overlap
- **Default**: 200 characters
- **Range**: 0-500 recommended
- **Impact**: Higher overlap = better continuity, lower overlap = less redundancy

## Dependencies

```bash
pip install langchain langchain-community pypdf unstructured
```

## Processing Pipeline

1. **PDF Loading**: PyPDFLoader extracts text from PDFs
2. **Text Splitting**: RecursiveCharacterTextSplitter creates overlapping chunks
3. **Metadata Addition**: Adds source, page, and processing information
4. **JSON Serialization**: Saves structured data for vectorization
5. **Progress Tracking**: Reports completion status

## File Structure

```
parser/
├── parse_all_pdfs.py          # Batch PDF processor
├── langchain_pdf_processor.py # LangChain processing core
└── README.md                  # This file
```

## Integration

### Input
- **PDF Directory**: `../../data/pdfs/` (relative to parser/)
- **File Format**: PDF documents
- **File Size**: No specific limits, but processing time scales with size

### Output
- **Directory**: `../../data/parsed/` (relative to parser/)
- **Format**: JSON files, one per PDF
- **Naming**: `{original_filename}.json`

### Next Step
- **Vectorizer**: Processes parsed JSON into embeddings
- **API Server**: Uses embeddings for semantic search

## Performance

- **Processing Speed**: ~1-5 seconds per PDF (depends on size/complexity)
- **Memory Usage**: ~100-500MB depending on PDF size
- **Chunk Quality**: LangChain's recursive splitting provides better semantic coherence

## Troubleshooting

### PDF Loading Errors
- Check PDF file integrity
- Try different PDF sources
- Some PDFs may require OCR preprocessing

### Empty Chunks
- Increase chunk_size parameter
- Check PDF text extraction quality
- Some PDFs may be image-based (require OCR)

### Memory Issues
- Process fewer PDFs at once
- Reduce chunk_size and chunk_overlap
- Restart processing with smaller batches

## Best Practices

- **Chunk Size**: Start with 1000, adjust based on document type
- **Overlap**: 20-30% of chunk size works well
- **Batch Processing**: Process in reasonable batches to monitor progress
- **Quality Check**: Review sample output chunks for coherence</content>
</xai:function_call name="read_lints">
<parameter name="target_file">src/api/rag-api/parser/README.md

