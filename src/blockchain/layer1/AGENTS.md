# Layer 1 Blockchain Agents

## Purpose

Python implementation of Syntheverse Blockmine L1 blockchain logic. Manages epochs, token distribution, and blockchain operations.

## Key Modules

- **`blockchain.py`**: Core blockchain structure with blocks and transactions
- **`node.py`**: Blockchain node implementation with mining
- **`epoch_manager.py`**: Epoch progression and management
- **`contracts/`**: Python contract interfaces
  - **`synth_token.py`**: SYNTH token contract interface
  - **`pod_contract.py`**: PoD contract interface
  - **`poc_contract.py`**: PoC contract interface

## Integration Points

- **Layer 2**: Receives evaluation results and allocation instructions
- **File System**: Persists blockchain state to JSON files
- **Smart Contracts**: Python interfaces to Solidity contracts
- **Frontend**: Provides blockchain status via APIs

## Development Guidelines

- File-based state persistence (suitable for test program)
- Epoch-based token distribution
- Integration with Layer 2 evaluator
- Node interface for blockchain operations
- State management with auto-save/load

## Common Patterns

- Epoch system: Founder, Pioneer, Community, Ecosystem
- Tier multipliers: Gold (1000x), Silver (100x), Copper (1x)
- PoD score calculation
- Token allocation based on scores and epochs
- State persistence to JSON files








