# Root Data Storage

## Purpose

Persistent blockchain state and contract data for the Syntheverse Layer 1 implementation.

## Key Modules

### Blockchain (`blockchain/`)

Runtime state files for the blockchain layer:

- **`blockchain.json`**: Core blockchain state (chain data, blocks, transactions)
- **`poc_contract.json`**: POCRegistry contract state and registered contributions
- **`synth_token.json`**: SYNTH token balances and allocations

## Integration Points

- Layer 1 (`src/blockchain/layer1/`) reads and writes blockchain state
- Contract interfaces (`src/blockchain/layer1/contracts/`) manage individual contract data
- Startup scripts load blockchain state on initialization
- Test outputs (`test_outputs/`) mirror this structure for testing

## Data Lifecycle

1. **Initialization**: Created on first Layer 1 startup
2. **Runtime**: Updated during blockchain operations
3. **Persistence**: JSON files ensure state survives restarts
4. **Reset**: Can be cleared using `scripts/utilities/clear_state.py`

## Responsibilities

### Data Management
- Maintain data integrity across system operations
- Ensure consistent JSON schema for all state files
- Provide reliable persistence for blockchain operations
- Support system recovery and state restoration

### State Synchronization
- Coordinate state updates between Layer 1 and external systems
- Ensure atomic operations to prevent data corruption
- Maintain audit trails for all state changes
- Support backup and recovery procedures

## Dependencies

### Runtime Dependencies
- **Python JSON**: Standard library for data serialization
- **File System**: Local storage for state persistence
- **Layer 1 Components**: Blockchain state management modules

### Development Dependencies
- **Git**: Version control (state files excluded via .gitignore)
- **Backup Tools**: State preservation and restoration utilities

## Development Guidelines

- Treat as runtime-generated data (excluded from version control)
- Use `test_outputs/` for test-specific state
- Back up before clearing or resetting
- Validate JSON integrity after updates

## File Structure

```
data/
└── blockchain/
    ├── blockchain.json      # Core blockchain state
    ├── poc_contract.json    # POCRegistry contract data
    └── synth_token.json     # SYNTH token allocations
```

## Blueprint Alignment

### Blockchain State Management ([Blueprint §1.4](docs/Blueprint for Syntheverse))
- **Layer 1 Implementation**: Persistent storage for Syntheverse Blockmine L1 blockchain operations
- **Registration Records**: On-chain PoC registration with $200 fees and "I was here first" recognition
- **Token Allocations**: SYNTH token distribution tracking and epoch-based management

### Archive-First Redundancy ([Blueprint §3.2](docs/Blueprint for Syntheverse))
- **State Persistence**: Blockchain state survives system restarts for continuity
- **Audit Trail**: Complete transaction history for transparency and governance
- **Recovery Support**: State files enable system restoration and integrity validation

### Tokenomics Engine ([Blueprint §3.3](docs/Blueprint for Syntheverse))
- **SYNTH Balances**: Real-time tracking of token allocations and metallic amplifications
- **Epoch Management**: Distribution tracking across contribution evaluation cycles
- **Threshold Scaling**: Core/leaf contribution scaling from high-impact to supporting work

### Complete Workflow Support ([Blueprint §7](docs/Blueprint for Syntheverse))
- **Registration → Allocation**: Blockchain state tracks the complete PoC to SYNTH workflow
- **On-Chain Transparency**: All allocations auditable and verifiable through state files
- **System Continuity**: Persistent state ensures workflow completion across system restarts

## Cross-References

- **Blueprint Document**: [docs/Blueprint for Syntheverse](../docs/Blueprint for Syntheverse) - Central system vision
- **Related**:
  - [src/blockchain/layer1/AGENTS.md](src/blockchain/layer1/AGENTS.md) - Layer 1 implementation
  - [test_outputs/AGENTS.md](test_outputs/AGENTS.md) - Test state storage
  - [scripts/utilities/AGENTS.md](scripts/utilities/AGENTS.md) - State management
  - [docs/L1_EXPLANATION.md](../docs/L1_EXPLANATION.md) - Blockchain explanation

