# Architecture Documentation Agents

## Purpose

System architecture documentation for the Syntheverse platform, describing the three-layer architecture, component interactions, technology stack, and design principles.

## Key Modules

### System Architecture Overview (`README.md`)

- **Three-Layer Design**: L1 Blockchain, L2 Evaluation, UI Layer
- **Six Main Components**: RAG API, Layer 2, Layer 1, PoC UI, Admin UI, Documentation
- **Architecture Diagram**: Visual representation of component relationships
- **Component Interactions**: Data flow between system components
- **Data Flow**: End-to-end processing from scraping to allocation
- **Technology Stack**: Python, FastAPI, blockchain frameworks, frontend technologies
- **Security Considerations**: Immutable submissions, cryptographic verification, authentication
- **Scalability**: Horizontal scaling, parallel processing, distributed consensus

## Integration Points

- Architecture documentation describes actual system components in `src/`
- References configuration in `config/` and deployment in `scripts/`
- Links to API documentation in `docs/api/`
- Describes integration with external services (Groq API, Ollama)
- References frontend applications in `src/frontend/`

## Development Guidelines

- Update architecture diagrams when system changes
- Document new components and their interactions
- Maintain accurate technology stack information
- Include security considerations for new features
- Document scalability considerations for new components

## Common Patterns

- Three-layer architectural pattern
- Component interaction documentation
- Data flow diagrams
- Technology stack descriptions
- Security and scalability considerations
