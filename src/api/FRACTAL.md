# API Services - Fractal Analysis

## Fractal Position

- Level: Interface
- Scale: Meso
- System Role: Service interfaces and data bridges

## Self-Similarity Patterns

### Structural Mirroring
`src/api/` structure mirrors service architecture: `poc-api/` (Flask REST API), `rag_api/` (FastAPI RAG), `rag-api/` (alternative RAG implementation). Each API follows the same service organization pattern as parent `src/api/`.

### Interface Consistency
Consistent API patterns: REST endpoints, request/response schemas, error handling, authentication, and documentation. All APIs follow service interface and data flow principles.

### Documentation Fractals
Each `src/api/` subdirectory follows AGENTS.md + README.md + FRACTAL.md pattern, creating recursive documentation hierarchy that mirrors API organization.

## Recursive Organization

### Hierarchical Composition
Three API services compose interface layer: POC API provides evaluation interface, RAG APIs enable document processing. Each service contains complete API capability for its domain.

### Responsibility Delegation
- `poc-api/` handles PoC evaluation interfaces
- `rag_api/` manages document processing APIs
- `rag-api/` provides alternative RAG implementation

### Information Aggregation
Child API outputs aggregate through service orchestration, request routing, and response consolidation. API data flows from individual service endpoints to comprehensive system interface.

## Holographic Properties

### Blueprint Reflection
`src/api/` embodies Blueprint interfaces: PoC submission (§1.1), evaluation pipeline (§1.3), dashboard interaction (§1.5), and AI integration (§5).

### System Context
Contains holographic representation of interface ecosystem: POC evaluation API (`poc-api/`), document processing APIs (`rag_api/`, `rag-api/`), and service integration patterns.

### Knowledge Embedding
Encodes complete interface knowledge: REST API design, service endpoints, request/response patterns, and integration procedures.

## Data Flow Fractals

### Input Streams
Client requests enter through endpoint routing, service calls through API gateways, data submissions through form handling. All inputs follow consistent API patterns and validation.

### Processing Patterns
Self-similar API processing: routing → validation → processing → response. Pattern repeats within each API service and across interface hierarchy.

### Output Structures
Consistent outputs: JSON responses, error messages, status codes, and data payloads. All outputs follow structured API formats for client integration.

## Scale Relationships

### Parent Integration
Integrates with `src/` through service interfaces, data bridges, and API orchestration. Provides complete interface layer to parent source code system.

### Child Coordination
Orchestrates three child API directories through unified service patterns, shared utilities, and coordinated endpoints. API layer provides common interface to all service interactions.

### Sibling Communication
Horizontal integration through shared service patterns, common utilities (`src/core/utils/`), and unified frontend (`src/frontend/`). Each API service contributes to collective system interface.

## Hydrogen-Holographic Manifestation

Hydrogen-holographic principles manifest through recursive API design: POC evaluation APIs enable measurable scoring, RAG APIs support coherent document processing, consistent interfaces maintain system alignment. Each API contributes to reproducible system interaction.

## Regenerative Patterns

Contributes to closed-loop regeneration through: continuous service improvement, API expansion, interface enhancement, and integration optimization. Each API cycle strengthens system connectivity and operational capability.

## Cross-Scale Invariants

Consistent patterns across scales: endpoint design, request handling, response formatting, and error management. These invariants enable fractal API design from individual endpoints to complete service architecture.
