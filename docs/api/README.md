# API Documentation

## RAG API

See `rag-api/README.md` and `rag-api/api/` for RAG API documentation.

### Endpoints

- `POST /query` - Query the RAG system
- `GET /health` - Health check
- `GET /stats` - System statistics

## PoC API

### Contribution Management

**Endpoint**: `POST /api/submit`
- Submit new contribution
- Returns submission hash

**Endpoint**: `POST /api/evaluate/{submission_hash}`
- Evaluate contribution
- Returns evaluation results and allocations

**Endpoint**: `GET /api/archive/contributions`
- Get all contributions with filtering
- Returns contribution list

**Endpoint**: `GET /api/archive/contributions/{hash}`
- Get specific contribution details
- Returns contribution data

**Endpoint**: `GET /api/archive/statistics`
- Get archive statistics
- Returns contribution counts and metrics

### Sandbox Map

**Endpoint**: `GET /api/sandbox-map`
- Get sandbox map visualization data
- Returns nodes and edges for graph display

### Tokenomics

**Endpoint**: `GET /api/tokenomics/epoch-info`
- Get epoch information
- Returns current epoch and availability

**Endpoint**: `GET /api/tokenomics/statistics`
- Get tokenomics statistics
- Returns allocation and balance data

### Blockchain Integration

**Endpoint**: `POST /api/register-poc`
- Register contribution certificate on blockchain
- Returns certificate details

**Endpoint**: `GET /health`
- API health check
- Returns system status

## Integration Examples

See component-specific README files for API usage examples.


