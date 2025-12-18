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

## Cross-References

- **Related**:
  - [src/blockchain/layer1/AGENTS.md](src/blockchain/layer1/AGENTS.md) - Layer 1 implementation
  - [test_outputs/AGENTS.md](test_outputs/AGENTS.md) - Test state storage
  - [scripts/utilities/AGENTS.md](scripts/utilities/AGENTS.md) - State management

