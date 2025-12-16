# PoC API Server

Flask API server that connects the Next.js frontend to the PoC backend.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export GROQ_API_KEY=your-groq-api-key-here
```

3. Run the server:
```bash
python app.py
```

The API will be available at `http://localhost:5001`

## Endpoints

- `GET /api/archive/statistics` - Get archive statistics
- `GET /api/archive/contributions` - Get all contributions (with optional filters)
- `GET /api/archive/contributions/<hash>` - Get specific contribution
- `POST /api/submit` - Submit new contribution
- `POST /api/evaluate/<hash>` - Evaluate contribution
- `GET /api/sandbox-map` - Get sandbox map data
- `GET /api/tokenomics/epoch-info` - Get epoch information
- `GET /api/tokenomics/statistics` - Get tokenomics statistics
- `GET /health` - Health check
