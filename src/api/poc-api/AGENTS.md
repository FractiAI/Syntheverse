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



