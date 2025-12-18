# Utility Scripts

## Purpose

Utility scripts for maintenance, administration, dependency management, and system state management.

## Scripts

- **`install_deps.py`**: Install system dependencies
- **`clear_state.py`**: Clear system state files

## Usage

### Install Dependencies

```bash
python scripts/utilities/install_deps.py
```

This script:
- Installs required Python packages
- Installs Node.js dependencies for frontend
- Checks system requirements
- Runs automatically in other scripts

### Clear System State

```bash
# Clear all state files
python scripts/utilities/clear_state.py --target all

# Clear only L2 tokenomics state
python scripts/utilities/clear_state.py --target l2

# Clear with backup
python scripts/utilities/clear_state.py --target all --backup

# Preview what would be cleared
python scripts/utilities/clear_state.py --target all --dry-run
```

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





