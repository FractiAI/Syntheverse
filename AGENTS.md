# Syntheverse System Agents

## Overview

Syntheverse is a hydrogen-holographic fractal blockchain game with a Proof-of-Contribution (PoC) system. This document describes the system architecture and component responsibilities.

## System Architecture

### Three-Layer Design

1. **Layer 1 (Blockchain)**: Syntheverse Blockmine L1 with smart contracts on Base
2. **Layer 2 (Evaluation)**: PoC evaluation engine with archive-first redundancy detection
3. **UI Layer**: Next.js frontend with Flask API bridge

## Key Components

### Source Code (`src/`)

- **`api/`**: API services (PoC API, RAG API in `rag_api/`)
- **`blockchain/`**: Blockchain infrastructure (contracts, Layer 1)
- **`core/`**: Core business logic (Layer 2 evaluation, tokenomics)
- **`frontend/`**: Frontend applications (Next.js, legacy Flask)
- **`data/`**: Data management (PDFs, parsed content, embeddings)

### Scripts (`scripts/`)

- **`startup/`**: System startup scripts
- **`development/`**: Development workflow scripts
- **`deployment/`**: Deployment and contract management
- **`utilities/`**: Maintenance utilities

### Configuration (`config/`)

- **`environment/`**: Environment configuration
- **`wallet/`**: Wallet setup and configuration

## Development Guidelines

### Code Standards

- Follow modular, well-documented, clearly reasoned code
- Use test-driven development (TDD)
- Remove unnecessary adjectives from names
- Ensure functional code

### Documentation

- Every folder level must have AGENTS.md and README.md
- Documentation shows rather than tells
- Documentation stays current with code changes

### Integration Points

- APIs connect frontend to backend
- Layer 2 evaluates contributions using Grok API
- Layer 1 handles blockchain registration
- Archive stores all contributions for redundancy detection

## Common Patterns

- Archive-first evaluation: All contributions stored immediately
- Multi-metal system: Gold, Silver, Copper qualifications
- Direct LLM integration: Groq API for evaluations
- File-based storage: JSON files for persistent state
