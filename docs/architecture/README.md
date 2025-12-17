# Syntheverse Architecture Documentation

## System Overview

Syntheverse is a hydrogen-holographic fractal blockchain game with a Proof-of-Contribution (PoC) system. The system consists of six main components:

1. **RAG API** - Scraper, Parser, Vectorizer with Groq API integration
2. **Layer 2** - PoC Evaluator and Token Allocator
3. **Layer 1** - Syntheverse Blockchain for PoC
4. **PoC Submission UI** - User interface for submitting contributions
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

1. **User submits PoC** → Submission UI → Layer 2 Evaluator
2. **Evaluator processes** → Queries RAG API → Verifies against knowledge base
3. **Evaluation complete** → Layer 2 Allocator → Calculates token rewards
4. **Allocation sent** → Layer 1 Blockchain → Records on-chain
5. **Admin manages** → Admin UI → Monitors all components

## Data Flow

1. **Scraping**: Zenodo → PDFs → Parser → Chunks
2. **Vectorization**: Chunks → Embeddings → Vector Store
3. **Query**: User Query → RAG API → Groq API → Response
4. **Evaluation**: PoC Submission → RAG Verification → Score
5. **Allocation**: Score → Token Calculation → Blockchain

## Technology Stack

- **RAG API**: Python, FastAPI, LangChain, HuggingFace, Groq API
- **Layer 2**: Python, Flask/FastAPI
- **Layer 1**: Solidity, Foundry, Anvil, Base network
- **UIs**: Next.js, React, HTML/CSS/JavaScript
- **Storage**: JSON files, Vector DB, Blockchain

## Security Considerations

- PoC submissions are immutable once recorded
- Token allocations are cryptographically verified
- Admin access requires authentication
- RAG API uses Groq API for LLM processing

## Scalability

- RAG API can scale horizontally
- Layer 2 evaluator can process submissions in parallel
- Layer 1 blockchain provides distributed consensus
- UIs can be deployed as static sites with API backends


