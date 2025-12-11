# PDFs Directory

This directory stores PDF files downloaded from Zenodo repositories.

## Usage

PDFs are downloaded here when running:

```bash
cd rag-api/scraper
python scrape_pdfs.py --urls <zenodo_url> --download-dir ../../data/pdfs
```

## File Format

- Files are saved with sanitized filenames
- Original filenames from Zenodo are preserved when possible
- Duplicate downloads are automatically skipped

