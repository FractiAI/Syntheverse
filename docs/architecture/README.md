# Syntheverse Architecture Documentation

## System Overview

Syntheverse is a hydrogen-holographic fractal blockchain game with a Proof-of-Discovery (POD) protocol. The system consists of six main components:

1. **RAG API** - Scraper, Parser, Vectorizer with Ollama integration
2. **Layer 2** - POD Evaluator and Token Allocator
3. **Layer 1** - Syntheverse Blockchain for POD
4. **POD Submission UI** - User interface for submitting discoveries
5. **Admin UI** - Administrative interface for managing the system
6. **Documentation** - Supporting documentation and guides

## Architecture Diagram

```
┌─────────────────┐
│  POD Submission │
│       UI        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Layer 2       │
│  ┌───────────┐  │
│  │ Evaluator │  │
│  └─────┬─────┘  │
│  ┌─────▼─────┐  │
│  │ Allocator │  │
│  └─────┬─────┘  │
└────────┼────────┘
         │
         ▼
┌─────────────────┐
│   Layer 1       │
│   Blockchain    │
│  ┌───────────┐  │
│  │ Contracts │  │
│  │   Node    │  │
│  │ Consensus │  │
│  └───────────┘  │
└─────────────────┘

┌─────────────────┐
│    RAG API      │
│  ┌───────────┐  │
│  │  Scraper  │  │
│  │  Parser   │  │
│  │ Vectorizer│  │
│  │    API    │  │
│  └─────┬─────┘  │
└────────┼────────┘
         │
         ▼
┌─────────────────┐
│     Ollama      │
│  (Local LLM)    │
└─────────────────┘
```

## Component Interactions

1. **User submits POD** → Submission UI → Layer 2 Evaluator
2. **Evaluator processes** → Queries RAG API → Verifies against knowledge base
3. **Evaluation complete** → Layer 2 Allocator → Calculates token rewards
4. **Allocation sent** → Layer 1 Blockchain → Records on-chain
5. **Admin manages** → Admin UI → Monitors all components

## Data Flow

1. **Scraping**: Zenodo → PDFs → Parser → Chunks
2. **Vectorization**: Chunks → Embeddings → Vector Store
3. **Query**: User Query → RAG API → Ollama → Response
4. **Evaluation**: POD Submission → RAG Verification → Score
5. **Allocation**: Score → Token Calculation → Blockchain

## Technology Stack

- **RAG API**: Python, FastAPI, LangChain, HuggingFace, Ollama
- **Layer 2**: Python, FastAPI
- **Layer 1**: Blockchain framework (TBD)
- **UIs**: HTML/CSS/JavaScript (React/Vue.js TBD)
- **Storage**: JSON files, Vector DB, Blockchain

## Security Considerations

- POD submissions are immutable once recorded
- Token allocations are cryptographically verified
- Admin access requires authentication
- RAG API uses local processing (no external API calls)

## Scalability

- RAG API can scale horizontally
- Layer 2 evaluator can process submissions in parallel
- Layer 1 blockchain provides distributed consensus
- UIs can be deployed as static sites with API backends


