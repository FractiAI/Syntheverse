# PDF Parser Agents

## Purpose

Processes PDF documents into structured text chunks for semantic search and embedding generation. Uses LangChain's document processing to create searchable content from research papers and documents.

## Key Modules

### LangChainPDFProcessor (`langchain_pdf_processor.py`)

Core PDF processing agent using LangChain framework:

- **`__init__()`**: Initialize with chunking parameters and text splitter
- **`process_pdf()`**: Process single PDF into text chunks
- **`_load_pdf_with_langchain()`**: Load PDF using PyPDFLoader
- **`_split_text_into_chunks()`**: Split text using RecursiveCharacterTextSplitter
- **`_create_chunks_with_metadata()`**: Add metadata to chunks

### Batch Processor (`parse_all_pdfs.py`)

Directory-level PDF processing orchestration:

- **`parse_all_pdfs()`**: Main function processing entire PDF directories
- **PDF Discovery**: Find all PDF files in directory
- **Duplicate Prevention**: Skip already processed files
- **Progress Reporting**: Real-time status updates
- **Error Handling**: Continue processing despite individual failures

## Integration Points

### Input Sources

- **Scraper Agent**: Consumes PDFs from `../../data/pdfs/`
- **Zenodo Integration**: Processes research papers from academic repositories
- **File System**: Direct PDF file processing

### Output Consumers

- **Vectorizer Agent**: Receives parsed JSON for embedding generation
- **API Server**: Uses processed chunks for semantic search
- **Data Pipeline**: Feeds into complete RAG pipeline

### LangChain Ecosystem

- **PyPDFLoader**: Robust PDF text extraction
- **RecursiveCharacterTextSplitter**: Intelligent text segmentation
- **Document Schema**: Structured document representation

## Development Guidelines

### Text Processing

- **Chunk Strategy**: Recursive splitting preserves document structure
- **Overlap Design**: Configurable overlap maintains context continuity
- **Metadata Preservation**: Track source, page, and processing information

### Error Handling

- **File Errors**: Continue processing other PDFs on individual failures
- **Encoding Issues**: Handle various PDF encodings gracefully
- **Memory Management**: Process large PDFs efficiently

### Quality Assurance

- **Chunk Validation**: Ensure chunks contain meaningful content
- **Metadata Accuracy**: Verify source attribution and positioning
- **Duplicate Detection**: Prevent reprocessing of existing files

## Common Patterns

### PDF Processing Workflow

1. **File Discovery**: Scan directory for PDF files
2. **Duplicate Check**: Verify output file doesn't exist
3. **Text Extraction**: Load PDF with PyPDFLoader
4. **Text Splitting**: Apply RecursiveCharacterTextSplitter
5. **Metadata Addition**: Attach source and positioning data
6. **JSON Serialization**: Save structured chunks
7. **Progress Update**: Report completion status

### Chunking Strategy

- **Recursive Splitting**: Break on paragraphs, then sentences, then words
- **Overlap Preservation**: Maintain context across chunk boundaries
- **Size Optimization**: Balance information density with retrieval precision
- **Metadata Enrichment**: Include positioning for result attribution

## Key Functions

### LangChainPDFProcessor

- `process_pdf(pdf_path: str) -> Dict`: Process single PDF file
- `_load_pdf_with_langchain(pdf_path: str) -> List[Document]`: Extract text from PDF
- `_split_text_into_chunks(text: str) -> List[str]`: Split text into chunks
- `_create_chunks_with_metadata(chunks: List[str], filename: str) -> List[Dict]`: Add metadata

### parse_all_pdfs.py

- `parse_all_pdfs(pdf_dir: str, output_dir: str, chunk_size: int, chunk_overlap: int)`: Main batch processor
- PDF file discovery and filtering
- Progress tracking and reporting
- Error handling and recovery

## Performance Characteristics

- **Processing Speed**: 1-5 seconds per PDF (size dependent)
- **Memory Usage**: 100-500MB per large PDF
- **Chunk Quality**: Semantic coherence through recursive splitting
- **Scalability**: Linear scaling with PDF count

## Error Scenarios

### PDF Loading Failures

- **Corrupted Files**: Skip and continue with others
- **Encoding Issues**: Attempt multiple loading strategies
- **Large Files**: Memory management for oversized documents

### Text Extraction Problems

- **Image-based PDFs**: May require OCR preprocessing
- **Complex Layouts**: LangChain handles various document structures
- **Empty Documents**: Validation prevents empty chunk creation

## Quality Metrics

### Chunk Evaluation

- **Coherence**: Semantic completeness of individual chunks
- **Overlap Effectiveness**: Context preservation across boundaries
- **Metadata Accuracy**: Correct source attribution and positioning
- **Size Distribution**: Balanced chunk sizes for optimal retrieval

### Processing Success

- **Completion Rate**: Percentage of successfully processed PDFs
- **Error Recovery**: Ability to continue after individual failures
- **Output Validation**: Verification of JSON structure and content

## Testing and Validation

### Unit Tests

- **Individual PDF Processing**: Test various document types
- **Chunking Algorithms**: Verify splitting behavior
- **Metadata Generation**: Validate metadata accuracy
- **Error Handling**: Test failure scenarios

### Integration Tests

- **Pipeline Continuity**: Ensure output works with vectorizer
- **Data Consistency**: Verify chunk metadata integrity
- **Performance Benchmarks**: Measure processing efficiency

## Future Enhancements

- **OCR Integration**: Handle image-based PDFs
- **Multi-format Support**: Extend beyond PDF documents
- **Advanced Chunking**: Semantic chunking with embeddings
- **Parallel Processing**: Multi-threaded PDF processing
- **Quality Metrics**: Automated chunk quality assessment</content>
</xai:function_call name="read_lints">
<parameter name="target_file">src/api/rag-api/parser/AGENTS.md

