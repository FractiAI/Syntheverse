# File Uploads Directory

Temporary storage for user-submitted files and contributions in the Syntheverse PoC evaluation system.

## Overview

This directory serves as temporary storage for files uploaded through the Syntheverse contribution submission process. Files are processed by the evaluation pipeline and moved to permanent storage locations.

## File Types

- **PDF Documents**: Research papers, articles, and academic contributions
- **Text Files**: Supplementary documentation and metadata
- **Archives**: Compressed files containing multiple documents

## Processing Pipeline

1. **Upload**: Files submitted via frontend interfaces
2. **Validation**: File type, size, and content verification
3. **Processing**: Moved to `src/data/pdfs/` for permanent storage
4. **Evaluation**: Integrated into PoC evaluation pipeline
5. **Cleanup**: Temporary files removed after processing

## Security Considerations

- File type validation prevents malicious uploads
- Size limits prevent storage abuse
- Automatic cleanup prevents accumulation
- Access controls restrict file operations

## Directory Structure

```
uploads/
├── {timestamp}_{filename}.pdf    # Temporary PDF uploads
├── {timestamp}_{filename}.txt    # Temporary text files
└── {timestamp}_{filename}.zip    # Temporary archives
```

## Integration

- **Frontend**: File upload interfaces in Next.js dashboard
- **API**: PoC API handles multipart form data
- **Processing**: Layer 2 evaluation engine processes submissions
- **Storage**: Permanent storage in `src/data/` directories

## Maintenance

This directory should be monitored for:
- File accumulation (automatic cleanup recommended)
- Storage quota management
- Security scanning of uploaded content
- Performance impact of large files

## Documentation

- [AGENTS.md](AGENTS.md) - Detailed component documentation
- [FRACTAL.md](FRACTAL.md) - Fractal analysis and patterns
- [PoC Submission Guide](../../docs/QUICK_START_POC_UI.md) - User submission instructions
