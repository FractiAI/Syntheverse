# Blockchain State Data

Persistent blockchain state files and Layer 1 data storage for the Syntheverse system.

## Overview

This directory contains blockchain state information, contract deployment data, and Layer 1 persistent storage files used by the Syntheverse blockchain integration.

## File Types

### State Files
- **blockchain.json**: Complete blockchain state including blocks, transactions, and accounts
- **poc_contract.json**: POC Registry contract state and registered contributions
- **synth_token.json**: SYNTH token contract state and token allocations
- **epoch_data.json**: Current epoch information and allocation tracking

### Deployment Records
- **contract_addresses.json**: Deployed contract addresses by network
- **deployment_logs.json**: Contract deployment transaction records
- **verification_status.json**: Contract verification status on block explorers

## Data Structure

### Blockchain State
```json
{
  "network": "base",
  "latest_block": 12345678,
  "accounts": {
    "0x123...": {
      "balance": "1000000000000000000",
      "nonce": 42,
      "code": "0x..."
    }
  },
  "contracts": {
    "POCRegistry": "0x456...",
    "SynthToken": "0x789..."
  }
}
```

### Contract State
```json
{
  "address": "0x456...",
  "deployed_at": "2024-12-18T10:30:00Z",
  "network": "base",
  "verification_status": "verified",
  "abi": [...],
  "bytecode": "0x...",
  "events": [...],
  "functions": [...]
}
```

## Usage

### State Inspection
```bash
# View current blockchain state
cat blockchain.json | jq '.latest_block'

# Check contract deployments
cat contract_addresses.json | jq '.base'
```

### State Management
```python
import json

def load_blockchain_state():
    """Load blockchain state for analysis"""
    with open('data/blockchain/blockchain.json') as f:
        state = json.load(f)
    return state

def get_contract_address(contract_name, network='base'):
    """Get deployed contract address"""
    with open('data/blockchain/contract_addresses.json') as f:
        addresses = json.load(f)
    return addresses.get(network, {}).get(contract_name)

# Usage
state = load_blockchain_state()
poc_address = get_contract_address('POCRegistry')
```

## Integration

### Layer 1 Integration
- **Contract Deployment**: Scripts use state files for deployment tracking
- **Transaction Monitoring**: State updates from blockchain events
- **Verification Tracking**: Contract verification status updates

### Development Workflow
- **Local Testing**: Anvil blockchain state persistence
- **Test Validation**: Contract state verification in tests
- **Deployment Tracking**: Multi-network deployment management

## Security Considerations

- **State Encryption**: Sensitive state data should be encrypted at rest
- **Access Control**: Restricted access to blockchain state files
- **Backup Strategy**: Regular state backups for disaster recovery
- **Integrity Verification**: Cryptographic verification of state file integrity

## Maintenance

- **State Synchronization**: Regular updates from live blockchain networks
- **File Rotation**: Periodic archival of old state files
- **Compression**: Large state files should be compressed for storage efficiency
- **Validation**: Automated validation of state file integrity

## Documentation

- [AGENTS.md](AGENTS.md) - Detailed component documentation
- [FRACTAL.md](FRACTAL.md) - Fractal analysis and patterns
- [Layer 1 System](../../src/blockchain/layer1/AGENTS.md) - Blockchain integration documentation
