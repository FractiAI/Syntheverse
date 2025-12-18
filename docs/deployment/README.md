# Deployment Guide

## Prerequisites

- Python 3.8+
- Node.js 18+ (for Next.js frontend)
- Groq API key
- Git

## Quick Start

The easiest way to deploy the Syntheverse system is using the startup scripts:

```bash
# From project root
python scripts/startup/start_servers.py
```

This starts all services:
- PoC API (Flask) on http://localhost:5001
- PoC Frontend (Next.js) on http://localhost:3001
- RAG API (FastAPI) on http://localhost:8000

## Component Deployment

### Environment Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/FractiAI/Syntheverse.git
   cd Syntheverse
   ```

2. **Set environment variables:**
   ```bash
   export GROQ_API_KEY=your-groq-api-key-here
   # Or create a .env file in the project root
   ```

3. **Install dependencies:**
   ```bash
   # Python dependencies
   pip install flask flask-cors werkzeug requests

   # Next.js frontend dependencies
   cd src/frontend/poc-frontend
   npm install
   cd ../../..
   ```

### Individual Component Startup

#### 1. PoC API (Layer 2)

```bash
cd src/api/poc-api
python app.py
```

Available at: http://localhost:5001

#### 2. Next.js Frontend

```bash
cd src/frontend/poc-frontend
npm run dev
```

Available at: http://localhost:3001

#### 3. RAG API

```bash
cd src/api/rag-api/api
python rag_api.py
```

Available at: http://localhost:8000

## Production Deployment

### Using Process Managers

For production, use process managers to keep services running:

```bash
# Using PM2 for Node.js services
npm install -g pm2
cd src/frontend/poc-frontend
pm2 start npm --name "poc-frontend" -- run start

# Using systemd for Python services (example)
sudo cp scripts/startup/syntheverse.service /etc/systemd/system/
sudo systemctl enable syntheverse
sudo systemctl start syntheverse
```

### Reverse Proxy Setup (nginx)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api/ {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        proxy_pass http://localhost:3001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Environment Variables

Required environment variables:

```bash
# Required
GROQ_API_KEY=your-groq-api-key-here

# Optional
PRIVATE_KEY=your-blockchain-private-key
ETHERSCAN_API_KEY=your-etherscan-api-key
ANVIL_RPC_URL=http://localhost:8545
```

## Blockchain Deployment

### Local Development (Anvil)

```bash
# Install Foundry
curl -L https://foundry.paradigm.xyz | bash
foundryup

# Start local blockchain
anvil
```

### Deploy Contracts

```bash
cd scripts/deployment
python deploy_contracts.py
```

### Base Network Deployment

Set `PRIVATE_KEY` and update deployment scripts for Base network configuration.


