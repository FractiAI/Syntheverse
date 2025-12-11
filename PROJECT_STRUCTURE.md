# Syntheverse Project Structure

## Overview

This repository has been organized into six main components as specified:

1. **RAG API** - Scraper, Parser, Vectorizer with Ollama integration
2. **Layer 2** - POD Evaluator and Token Allocator
3. **Layer 1** - Syntheverse Blockchain for POD
4. **POD Submission UI** - Basic user interface
5. **Admin UI** - Basic administrative interface
6. **Documentation** - Supporting documentation

## Directory Structure

```
Syntheverse/
├── README.md                          # Main project README
├── .gitignore                         # Git ignore rules
├── PROJECT_STRUCTURE.md               # This file
│
├── rag-api/                           # Component 1: RAG API
│   ├── README.md
│   ├── scraper/
│   │   └── scrape_pdfs.py            # Zenodo PDF scraper
│   ├── parser/
│   │   ├── parse_all_pdfs.py         # PDF parser
│   │   └── langchain_pdf_processor.py # PDF processing helper
│   ├── vectorizer/
│   │   └── vectorize_parsed_chunks_simple.py # Vectorization
│   └── api/
│       ├── rag_api.py                # FastAPI server
│       ├── requirements_api.txt      # Python dependencies
│       ├── start_rag_api.sh          # Startup script
│       └── static/
│           └── index.html            # Web UI
│
├── layer2/                            # Component 2: POD Evaluator & Allocator
│   ├── README.md
│   ├── evaluator/
│   │   └── pod_evaluator.py          # POD evaluation logic
│   └── allocator/
│       └── token_allocator.py        # Token allocation logic
│
├── layer1/                            # Component 3: Blockchain
│   ├── README.md
│   ├── contracts/
│   │   └── pod_contract.py          # POD smart contract
│   ├── node/                          # Blockchain node (TBD)
│   └── consensus/                     # Consensus mechanism (TBD)
│
├── ui-submission/                     # Component 4: POD Submission UI
│   ├── README.md
│   ├── src/
│   │   └── index.html               # Submission form
│   └── public/                        # Static assets (TBD)
│
├── ui-admin/                          # Component 5: Admin UI
│   ├── README.md
│   ├── src/
│   │   └── index.html               # Admin dashboard
│   └── public/                        # Static assets (TBD)
│
└── docs/                              # Component 6: Documentation
    ├── api/
    │   ├── README.md                 # API overview
    │   └── RAG_API.md                # RAG API detailed docs
    ├── architecture/
    │   └── README.md                 # Architecture documentation
    └── deployment/
        └── README.md                 # Deployment guide
```

## Component Status

### ✅ Operational
- **RAG API**: Fully functional with all components (scraper, parser, vectorizer, API)

### 🚧 In Development
- **Layer 2**: Scaffolding created, needs implementation
- **Layer 1**: Contract scaffolding created, node and consensus pending
- **POD Submission UI**: Basic HTML created, backend integration pending
- **Admin UI**: Basic HTML created, backend integration pending

### ✅ Complete
- **Documentation**: Architecture, API, and deployment docs created

## Source Code

The RAG API components were copied from:
`/Users/macbook/Desktop/Syntheverse-Holographic-RAG/`

All other components are new scaffolding created for this repository structure.

## Next Steps

1. **Integrate Ollama**: Update RAG API to use Ollama for LLM inference
2. **Implement Layer 2**: Complete evaluator and allocator with API endpoints
3. **Implement Layer 1**: Complete blockchain node and consensus mechanism
4. **Connect UIs**: Integrate submission and admin UIs with backend APIs
5. **Testing**: Add unit tests and integration tests
6. **Deployment**: Set up Docker containers and deployment scripts

## Data Flow

1. User submits POD → `ui-submission` → `layer2/evaluator`
2. Evaluator queries → `rag-api` → Verifies against knowledge base
3. Evaluation result → `layer2/allocator` → Calculates token reward
4. Allocation → `layer1/contracts` → Records on blockchain
5. Admin monitors → `ui-admin` → Views all system activity

