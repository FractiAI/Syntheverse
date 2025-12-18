# Layer 2 Development Standards

## PoC Server Architecture

### Core Components
- `PoCServer` - Main orchestration server
- `PoCArchive` - Archive-first storage system
- `TokenomicsState` - Token allocation state
- `SandboxMap` - Network visualization

### Archive-First Principle
- All contributions immediately added to archive as DRAFT
- Archive stores complete contribution history
- Redundancy detection against entire archive
- Status lifecycle: DRAFT → EVALUATING → QUALIFIED/UNQUALIFIED → ARCHIVED

### Multi-Metal System
- Gold (Discovery): Scientific contributions
- Silver (Technology): Technical implementations
- Copper (Alignment): Alignment contributions
- Contributions can qualify for multiple metals

### Evaluation Flow
1. Submission received → Added to archive as DRAFT
2. Redundancy check against archive
3. Grok API evaluation with HHFE system prompt
4. Parse evaluation results (markdown + JSON)
5. Calculate PoC scores and metal qualifications
6. Update archive status
7. Allocate tokens if qualified
8. Generate sandbox map data

## Grok API Integration

### System Prompt
- Combines Syntheverse Whole Brain AI framework
- Includes HHFE evaluation criteria
- Specifies output format (markdown + JSON)
- Contains all evaluation constants and formulas

### Response Parsing
- Extract JSON from markdown response
- Handle parsing errors gracefully
- Validate extracted data
- Fallback extraction methods

### Error Handling
- Clear error messages for API failures
- Retry logic for transient errors
- Validation of API responses
- Logging for debugging

## Tokenomics Integration

### Epoch System
- Founder: Highest quality (density ≥ 8000)
- Pioneer: Early high quality (density ≥ 6000)
- Community: Standard contributions (density ≥ 4000)
- Ecosystem: All other contributions

### Token Allocation
- Calculate based on PoC score
- Apply epoch weights
- Apply metal multipliers (Gold: 1000x, Silver: 100x, Copper: 1x)
- Check epoch availability for metal type
- Update tokenomics state

### State Management
- Persistent state in JSON files
- Auto-save after allocations
- Auto-load on initialization
- Track epoch balances and allocations

## Sandbox Map Generation

### Network Structure
- Nodes: Contributions with metadata
- Edges: Overlap and redundancy relationships
- Dimensions: 16 knowledge dimensions
- Hero's Journey: Narrative progression

### Data Generation
- Calculate overlap scores between contributions
- Generate network graph data
- Filter by metals, dimensions, epochs
- Export for frontend visualization

## Code Patterns

### Server Initialization
```python
server = PoCServer(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    output_dir="test_outputs/poc_reports",
    tokenomics_state_file="test_outputs/l2_tokenomics_state.json",
    archive_file="test_outputs/poc_archive.json"
)
```

### Submission Handling
- Validate inputs
- Generate content hash
- Check for duplicates
- Add to archive immediately
- Return submission status

### Evaluation Process
- Call Grok API with system prompt
- Parse response
- Calculate scores
- Determine metal qualifications
- Update archive status








