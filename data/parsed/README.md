# Parsed Directory

This directory stores parsed PDF chunks as JSON files.

## Usage

Parsed chunks are saved here when running:

```bash
cd rag-api/parser
python parse_all_pdfs.py --pdf-dir ../../data/pdfs --output-dir ../../data/parsed
```

## File Format

Each PDF generates one JSON file with:
- `text`: Chunk text content
- `metadata`: PDF metadata (filename, source, etc.)
- `chunk_index`: Index of chunk in document

## Notes

- Already parsed files are automatically skipped
- Files are named after the source PDF (e.g., `document.pdf` → `document.json`)

