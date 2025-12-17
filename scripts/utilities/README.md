# Utility Scripts

## Purpose

Utility scripts for maintenance, administration, and system state management.

## Scripts

- **`clear_persistent_memory.py`**: Clear test data and reset system state

## Usage

### Clear Test Data

```bash
python scripts/utilities/clear_persistent_memory.py
```

This script:
- Clears test output files
- Resets tokenomics state
- Clears archive data
- Resets system to initial state

## Integration

- Maintains system state
- Provides cleanup operations
- Supports testing workflows
- Enables system reset

## Warnings

- Only use in development/test environments
- Will delete all test data
- Cannot be undone
- Backup important data before use



