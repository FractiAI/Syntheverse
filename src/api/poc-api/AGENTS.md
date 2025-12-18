# PoC API Agents

## Purpose

Flask REST API server that connects the Next.js frontend to the Layer 2 PoC backend. Handles contribution submissions, file uploads, and provides endpoints for archive, sandbox map, and tokenomics data.

## Key Modules

- **`app.py`**: Main Flask application with route handlers
- **`server.py`**: Server setup and configuration

## Integration Points

- **Frontend**: Next.js application sends requests to API endpoints
- **Layer 2**: Calls PoC Server for evaluation and archive operations
- **Blockchain**: Integrates with Web3 for certificate registration
- **File System**: Handles PDF uploads and storage

## API Endpoints

- `POST /api/submit` - Submit new contribution
- `POST /api/evaluate/<hash>` - Evaluate contribution
- `GET /api/archive/statistics` - Get archive statistics
- `GET /api/archive/contributions` - Get all contributions
- `GET /api/archive/contributions/<hash>` - Get specific contribution
- `GET /api/sandbox-map` - Get sandbox map data
- `GET /api/tokenomics/epoch-info` - Get epoch information
- `GET /api/tokenomics/statistics` - Get tokenomics statistics
- `POST /api/register-certificate` - Register certificate on blockchain
- `GET /health` - Health check

## Development Guidelines

- Use Flask for API server
- Enable CORS for frontend access
- Validate all inputs and file uploads
- Use secure filename handling
- Return consistent JSON response format
- Handle errors gracefully with informative messages
- Use environment variables for configuration

## Common Patterns

- RESTful API design
- JSON request/response format
- File upload validation
- Error handling with consistent structure
- Integration with PoC Server for business logic

## Responsibilities

### API Gateway
- Provide RESTful interface between frontend and backend systems
- Handle contribution submissions with file upload validation
- Route evaluation requests to Layer 2 PoC Server
- Serve archive, sandbox map, and tokenomics data to frontend

### Data Management
- Manage secure file uploads and storage
- Validate contribution metadata and file formats
- Provide archive access and statistics endpoints
- Support sandbox map data generation and retrieval

### Blockchain Integration
- Handle certificate registration requests
- Integrate with Web3 for blockchain transactions
- Process registration fees and transaction confirmations
- Provide registration status and history

## Interfaces

### External Interfaces
- **Frontend API**: REST endpoints for Next.js application
- **File Uploads**: HTTP multipart form data handling
- **Blockchain**: Web3 integration for certificate registration

### Internal Interfaces
- **PoC Server**: Direct calls to Layer 2 evaluation engine
- **Archive System**: Access to contribution storage and retrieval
- **Tokenomics**: Integration with allocation and epoch management
- **File System**: Local storage for uploads and logs

### Data Interfaces
- **JSON API**: Consistent request/response format
- **File Storage**: Secure handling of PDF uploads
- **Logging**: Application logs for monitoring and debugging

## Dependencies

### Core Dependencies
- **Flask**: Web framework for API server
- **Flask-CORS**: Cross-origin resource sharing
- **Werkzeug**: File upload security utilities
- **Python Standard Library**: JSON, OS, pathlib

### External Services
- **PoC Server**: Layer 2 evaluation engine
- **Blockchain Network**: Web3 provider for registration
- **File System**: Local storage for uploads

### Configuration Requirements
- **PORT**: Server port configuration (default: 5001)
- **UPLOAD_FOLDER**: File upload directory path
- **CORS_ORIGINS**: Allowed frontend origins
- **LOG_FILE**: Application logging destination

## File Structure

```
poc-api/
├── app.py              # Main Flask application with routes
├── server.py           # Server setup and configuration
├── requirements.txt    # Python dependencies
├── uploads/            # File upload storage directory
├── venv/               # Virtual environment
├── app.log             # Application logs
└── README.md           # API documentation
```

## Configuration

- **Port**: 5001 (default)
- **CORS**: Enabled for frontend access
- **Uploads**: Configurable upload directory
- **Logging**: File-based logging to `app.log`

## Cross-References

- **Parent**: [api/AGENTS.md](../AGENTS.md) - API services overview
- **Related**:
  - [core/layer2/AGENTS.md](../../core/layer2/AGENTS.md) - PoC Server integration
  - [blockchain/AGENTS.md](../../blockchain/AGENTS.md) - Blockchain registration
  - [frontend/poc-frontend/AGENTS.md](../../frontend/poc-frontend/AGENTS.md) - Frontend integration

