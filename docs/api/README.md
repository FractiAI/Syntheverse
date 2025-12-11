# API Documentation

## RAG API

See `rag-api/README.md` and `rag-api/api/` for detailed RAG API documentation.

### Endpoints

- `POST /query` - Query the RAG system
- `GET /health` - Health check
- `GET /stats` - System statistics

## Layer 2 API

### POD Evaluator API

**Endpoint**: `POST /evaluate`
- Submit POD for evaluation
- Returns evaluation report

**Endpoint**: `GET /evaluation/{submission_id}`
- Get evaluation status and results

### Token Allocator API

**Endpoint**: `POST /allocate`
- Calculate token allocation for evaluated POD
- Returns allocation details

**Endpoint**: `GET /allocation/{submission_id}`
- Get token allocation details

## Layer 1 Blockchain API

### POD Contract API

**Endpoint**: `POST /submit`
- Submit POD to blockchain
- Returns submission hash

**Endpoint**: `GET /submission/{hash}`
- Get POD submission details

**Endpoint**: `GET /balance/{contributor}`
- Get contributor SYNTH token balance

## Integration Examples

See component-specific README files for detailed API usage examples.

