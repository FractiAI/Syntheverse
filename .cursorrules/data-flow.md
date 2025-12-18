# Data Flow and Integration Patterns

## Submission to Evaluation Flow

### 1. User Submission
```
Frontend (Next.js) → PoC API (Flask) → PoC Server (Layer 2)
```
- User uploads PDF via frontend
- Frontend sends to `/api/submit` endpoint
- PoC API receives file and metadata
- PoC Server processes submission

### 2. Archive-First Storage
```
PoC Server → PoC Archive → JSON File
```
- Contribution immediately added to archive as DRAFT
- Content hash generated for redundancy detection
- Metadata stored with contribution
- Status: DRAFT

### 3. Redundancy Check
```
PoC Server → PoC Archive → Content Hash Comparison
```
- Check against all archived contributions
- Calculate similarity scores
- Mark as redundant if threshold exceeded
- Update status accordingly

### 4. Evaluation
```
PoC Server → Grok API → System Prompt → Evaluation Response
```
- Send artifact to Grok API
- Use comprehensive HHFE system prompt
- Parse markdown + JSON response
- Extract scores and classifications

### 5. Token Allocation
```
PoC Server → Tokenomics State → Epoch Calculation → Allocation
```
- Calculate PoC score from metrics
- Determine qualified epoch
- Check metal availability
- Allocate tokens if qualified
- Update tokenomics state

### 6. Status Update
```
PoC Server → PoC Archive → Status Update
```
- Update contribution status
- Store evaluation results
- Store allocation information
- Generate sandbox map data

## Blockchain Registration Flow

### 1. Registration Initiation
```
Frontend → PoC API → Blockchain Service
```
- User clicks "Register on Blockchain"
- Frontend sends registration request
- PoC API validates contribution status

### 2. Smart Contract Interaction
```
Blockchain Service → Web3 → Base Network → Smart Contract
```
- Connect to Base network (Anvil local or Base Sepolia)
- Load contract ABIs
- Call `registerContribution()` function
- Pay fee if required (first 3 free)

### 3. Certificate Generation
```
Smart Contract → Transaction Receipt → Certificate Data
```
- Transaction confirmed on blockchain
- Extract certificate data from receipt
- Generate certificate object
- Return to frontend

## RAG Query Flow

### 1. Document Processing
```
Scraper → PDFs → Parser → Chunks → Vectorizer → Embeddings
```
- Scrape PDFs from Zenodo
- Parse into text chunks
- Generate embeddings
- Store embeddings and metadata

### 2. Query Processing
```
User Query → RAG API → Semantic Search → LLM → Response
```
- User submits query
- RAG API performs semantic search
- Retrieves relevant chunks
- Builds context for LLM
- Returns answer with citations

## Data Storage Patterns

### Archive Storage
- Single JSON file: `poc_archive.json`
- Stores all contributions (all statuses)
- Append-only for history
- In-memory index for fast lookup

### Tokenomics State
- Single JSON file: `l2_tokenomics_state.json`
- Epoch balances
- Allocation history
- Contributor balances
- Auto-save after changes

### Sandbox Map Data
- Generated on-demand from archive
- Network graph structure
- Nodes: contributions
- Edges: overlap relationships
- Exported as JSON for frontend

## Error Handling Flow

### API Errors
```
Error → Log → User-Friendly Message → Frontend Display
```
- Catch exceptions in API handlers
- Log full error details
- Return user-friendly message
- Frontend displays error state

### Evaluation Errors
```
Grok API Error → Retry Logic → Fallback → Error Report
```
- Handle API failures gracefully
- Implement retry for transient errors
- Fallback parsing methods
- Clear error messages

### Blockchain Errors
```
Transaction Error → Gas Estimation → User Notification
```
- Validate before transaction
- Estimate gas costs
- Handle network errors
- Inform user of failures









