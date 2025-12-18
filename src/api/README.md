# Syntheverse API Services

## Overview

The API services provide RESTful interfaces that connect the Syntheverse frontend applications to backend systems, enabling the complete Proof-of-Contribution workflow from submission to token allocation.

## Architecture

### Service Components

#### PoC API (`poc-api/`)
Flask-based REST API server that bridges the Next.js frontend with Layer 2 evaluation systems.

**Core Functionality:**
- **Submission Handling**: File upload validation and contribution processing
- **Archive Management**: Contribution storage and retrieval operations
- **Sandbox Integration**: Real-time network visualization data
- **Tokenomics Access**: Epoch balances and allocation statistics
- **Blockchain Coordination**: Certificate registration workflow

#### RAG API (`rag_api/`)
FastAPI-based server for document processing and retrieval-augmented generation.

**Core Functionality:**
- **Semantic Search**: Vector-based document querying
- **LLM Integration**: Multi-provider support (GROQ, Ollama, HuggingFace)
- **Document Pipeline**: Complete scraping → parsing → vectorization workflow
- **Interactive UI**: Web interface for document exploration

## Installation

### Prerequisites
- **Python 3.8+**: Backend runtime environment
- **GROQ API Key**: Required for LLM operations ([Get here](https://console.groq.com/))
- **Git**: Version control for dependency management

### PoC API Setup
```bash
cd poc-api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### RAG API Setup
```bash
cd rag_api/api
pip install -r requirements_api.txt
# Optional: Set up Ollama for local LLM
# See rag_api/api/OLLAMA_SETUP.md for details
```

## Usage

### Starting Services

#### Development Mode
```bash
# PoC API (Port 5001)
cd poc-api
export GROQ_API_KEY="your-api-key"
python app.py

# RAG API (Port 8000)
cd rag_api/api
export GROQ_API_KEY="your-api-key"
python rag_api.py
```

#### Production Mode
```bash
# Using the startup scripts
cd ../../../../scripts/startup
python start_servers.py  # Starts all services including APIs
```

### API Endpoints

#### PoC API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/submit` | Submit contribution with PDF upload |
| `GET` | `/archive` | Retrieve archived contributions |
| `GET` | `/sandbox` | Generate sandbox map visualization |
| `GET` | `/tokenomics` | Get current tokenomics state |
| `POST` | `/register` | Register approved contribution |

#### RAG API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/search` | Semantic search over documents |
| `POST` | `/query` | Interactive RAG query with context |
| `GET` | `/documents` | List available documents |
| `POST` | `/upload` | Upload new documents for processing |

## Development

### Code Standards
- **Flask API**: RESTful design with consistent error responses
- **FastAPI**: Async operations with automatic OpenAPI documentation
- **Validation**: Comprehensive input validation and sanitization
- **Logging**: Structured logging for debugging and monitoring

### Testing
```bash
# PoC API tests
cd poc-api
python -m pytest tests/

# RAG API tests
cd rag_api
python -m pytest tests/

# Integration tests
cd ../../../tests
python -m pytest test_poc_api.py test_rag_api.py
```

### Configuration
```bash
# Required environment variables
export GROQ_API_KEY="your-groq-api-key"
export FLASK_ENV="development"  # or "production"
export POC_API_PORT="5001"
export RAG_API_PORT="8000"

# Optional configurations
export CORS_ORIGINS="http://localhost:3000,http://localhost:3001"
export UPLOAD_FOLDER="./uploads"
export MAX_CONTENT_LENGTH="16777216"  # 16MB
```

## Integration

### Frontend Integration
Both APIs are configured with CORS to support Next.js frontend applications running on standard ports (3000, 3001).

### Backend Integration
- **PoC API** connects directly to `src/core/layer2/poc_server.py`
- **RAG API** operates independently for document processing
- Both APIs use centralized GROQ API integration via `src/core/utils/env_loader.py`

### Blockchain Integration
PoC API coordinates with Layer 1 blockchain services for contribution registration and certificate minting.

## Troubleshooting

### Common Issues
- **CORS Errors**: Ensure frontend URLs are in CORS_ORIGINS
- **File Upload Issues**: Check MAX_CONTENT_LENGTH and UPLOAD_FOLDER permissions
- **API Key Errors**: Verify GROQ_API_KEY is set and valid
- **Port Conflicts**: Check if ports 5001/8000 are available

### Logs and Debugging
- Check `poc-api/app.log` for Flask API errors
- Check `rag_api/api/rag_api.log` for FastAPI errors
- Enable debug mode with `export FLASK_ENV=development`

## Documentation

- [PoC API Implementation](poc-api/README.md) - Detailed Flask API documentation
- [RAG API Implementation](rag_api/README.md) - FastAPI documentation and setup
- [API Testing Guide](../../tests/README.md) - Comprehensive testing procedures



