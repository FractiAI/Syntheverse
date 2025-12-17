# Legacy Web Interface Agents

## Purpose

Flask-based web interface for Syntheverse PoD submission, evaluation, and certificate registration.

## Key Modules

### Flask Application (`app.py`)

- **Web Server**: Flask application for PoD submission interface
- **Document Upload**: PDF file upload and processing
- **API Integration**: REST endpoints for submission and status
- **Template Rendering**: HTML templates for web interface
- **Certificate Registration**: Blockchain certificate registration workflow

### Templates (`templates/`)

- **Main Interface**: HTML template for submission and status display
- **Certificate Registration**: Template for blockchain certificate registration
- **Web3 Integration**: Frontend components for wallet connection
- **Status Display**: Dynamic status updates and progress tracking

### PDF Processing (`pdf_generator.py`)

- **PDF Generation**: Certificate and report PDF creation
- **Template Processing**: PDF template rendering and formatting
- **File Management**: PDF storage and retrieval

## Integration Points

- Flask application connects to Layer 2 evaluation system
- Integrates with Layer 1 blockchain for certificate registration
- Uses RAG API for document evaluation
- Links to frontend templates and static assets
- Connects to email system for notifications (legacy)

## Development Guidelines

- Maintain Flask routing and template structure
- Implement proper file upload security and validation
- Ensure Web3 integration works across different wallets
- Test PDF generation and certificate registration
- Update templates for responsive design

## Common Patterns

- Flask route definitions
- Template inheritance and rendering
- File upload handling
- Web3 wallet integration
- PDF generation workflows
