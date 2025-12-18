# System Architecture Constraints

## Three-Layer Architecture

### Layer 1: Blockchain
- Syntheverse Blockmine L1 (Python implementation)
- Smart contracts (Solidity on Base)
- Epoch management and token distribution
- Certificate registration

### Layer 2: Evaluation
- PoC evaluation engine
- Archive-first redundancy detection
- Token allocation logic
- Sandbox map generation

### UI Layer: Frontend
- Next.js frontend (PoC dashboard)
- Flask API bridge (PoC API)
- Legacy Flask UI (web-legacy)
- Submission interfaces

## Component Boundaries

### API Services
- `poc-api/` - Flask API connecting frontend to Layer 2
- `rag-api/` - FastAPI for document processing and queries
- APIs are stateless and handle requests independently

### Core Logic
- `layer2/` - PoC evaluation and tokenomics
- `layer1/` - Blockchain logic (Python)
- Core components are independent modules

### Frontend
- `poc-frontend/` - Modern Next.js application
- `web-legacy/` - Legacy Flask application
- `submission/` - Basic submission interface
- Frontends communicate via APIs

## Data Flow

### Submission Flow
1. User submits via frontend
2. Frontend sends to PoC API
3. PoC API calls PoC Server
4. PoC Server evaluates with Grok API
5. Results stored in archive
6. Tokens allocated if qualified
7. Frontend polls for updates

### Blockchain Registration
1. Qualified contribution ready
2. User initiates registration
3. PoC API calls blockchain service
4. Smart contract registers on-chain
5. Certificate issued
6. Frontend displays certificate

## Integration Patterns

### API Integration
- RESTful APIs for all services
- JSON for data exchange
- CORS enabled for frontend
- Error handling with consistent format

### Database/Storage
- JSON files for persistent state
- Archive stores all contributions
- Tokenomics state in separate file
- No traditional database (file-based)

### External Services
- Groq API for LLM operations
- Base blockchain for on-chain registration
- Zenodo for document scraping
- No other external dependencies

## Security Boundaries

### API Security
- Environment variables for secrets
- Input validation on all endpoints
- File upload validation
- CORS configuration

### Blockchain Security
- Access control on contracts
- Input validation
- Reentrancy protection
- Emergency controls

### Data Security
- No sensitive data in code
- Environment variables for keys
- Secure file handling
- Content hashing for integrity

## Scalability Considerations

### Current Design
- File-based storage (suitable for test program)
- Single API instances
- Local blockchain node
- Suitable for development/testing

### Future Considerations
- Database migration for production
- Horizontal scaling for APIs
- Distributed blockchain nodes
- Caching strategies








