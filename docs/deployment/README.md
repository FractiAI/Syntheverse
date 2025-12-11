# Deployment Guide

## Prerequisites

- Python 3.8+
- Node.js 16+ (for UIs)
- Ollama installed locally
- Git

## Component Deployment

### 1. RAG API

```bash
cd rag-api/api
pip install -r requirements_api.txt
python rag_api.py
```

The RAG API will be available at `http://localhost:8000`

### 2. Layer 2 Services

```bash
cd layer2
pip install -r requirements.txt  # Create this file with dependencies
# Start evaluator service
python evaluator/pod_evaluator.py
# Start allocator service
python allocator/token_allocator.py
```

### 3. Layer 1 Blockchain

```bash
cd layer1
# Initialize blockchain node
python node/blockchain_node.py
```

### 4. POD Submission UI

```bash
cd ui-submission
# For static HTML version, serve with any web server
python -m http.server 3000
```

### 5. Admin UI

```bash
cd ui-admin
# For static HTML version, serve with any web server
python -m http.server 3001
```

## Docker Deployment (Coming Soon)

Docker configurations will be provided for containerized deployment.

## Production Considerations

- Use reverse proxy (nginx) for UIs
- Enable HTTPS with SSL certificates
- Set up authentication for Admin UI
- Configure CORS properly for API endpoints
- Use process managers (PM2, systemd) for services
- Set up monitoring and logging
- Configure database persistence for blockchain

## Environment Variables

Create `.env` files for each component with necessary configuration:

- RAG API: Embedding model, vector store path
- Layer 2: Evaluation criteria, tokenomics parameters
- Layer 1: Network configuration, consensus parameters

