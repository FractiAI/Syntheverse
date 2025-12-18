# Runtime Blockchain State Agents

## Purpose

Persistent storage for Layer 1 blockchain runtime state, including contract deployments, network configurations, and transaction data.

## Key Files

### blockchain.json

Core blockchain state configuration:

- **Network Configuration**: Base network settings and endpoints
- **Contract Addresses**: Deployed smart contract addresses
- **Genesis State**: Initial blockchain parameters
- **Node Information**: Connected blockchain nodes

### poc_contract.json

Proof-of-Contribution contract state:

- **Contract Deployment**: POC contract address and metadata
- **Contribution Registry**: Recorded contributions and evaluations
- **Certificate Records**: Issued contribution certificates
- **Transaction History**: Contract interaction records

### synth_token.json

SYNTH token contract state:

- **Token Deployment**: SYNTH contract address and parameters
- **Supply Information**: Total and circulating token supply
- **Allocation Records**: Token distribution and transfers
- **Holder Information**: Token holder addresses and balances

## Integration Points

### Input Sources

- **Layer 1 Blockchain**: Receives state updates from blockchain operations
- **Contract Deployment**: Gets initial state from deployment scripts
- **Transaction Processing**: Updates from contract interactions

### Output Consumers

- **Layer 2 Evaluation**: Reads contract state for validation
- **Frontend Dashboard**: Provides blockchain data for UI display
- **API Services**: Serves blockchain state via REST endpoints
- **Deployment Scripts**: Uses state for contract interactions

## Data Flow

1. **Deployment**: Initial state created during contract deployment
2. **Operation**: State updated through contract interactions
3. **Persistence**: JSON files maintain state across system restarts
4. **Synchronization**: State synced with on-chain data when needed

## Development Guidelines

- Maintain JSON schema consistency across updates
- Validate state integrity before operations
- Implement atomic state updates to prevent corruption
- Backup state files before modifications
- Document state schema changes

## File Structure

```
data/blockchain/
├── blockchain.json     # Core network state
├── poc_contract.json   # POC contract state
└── synth_token.json    # Token contract state
```

## Cross-References

- **Parent**: [data/AGENTS.md](../AGENTS.md) - Root data storage
- **Related**:
  - [src/blockchain/layer1/AGENTS.md](../../../src/blockchain/layer1/AGENTS.md) - Layer 1 implementation
  - [test_outputs/blockchain/AGENTS.md](../../../test_outputs/blockchain/AGENTS.md) - Test blockchain state
  - [docs/L1_EXPLANATION.md](../../../docs/L1_EXPLANATION.md) - Blockchain explanation
