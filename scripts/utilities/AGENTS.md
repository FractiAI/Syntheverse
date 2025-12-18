# Utility Scripts

## Purpose

Maintenance, administration, and system state management utilities for the Syntheverse platform.

## Key Modules

### Dependency Installer (`install_deps.py`)

- **Python Package Management**: Auto-detect and install required Python packages
- **Node.js Dependency Management**: Install npm packages for frontend components
- **System Dependency Checks**: Validate Node.js, Python version, and system tools
- **Silent Auto-installation**: Install dependencies without user interaction

### System State Management (`clear_state.py`)

- **Selective Clearing**: Clear specific state components (L1, L2, reports, all)
- **Backup Functionality**: Create backups before clearing state
- **Safe Operations**: Preserve system structure while clearing data
- **Dry Run Support**: Preview what would be cleared without actually doing it

## Integration Points

- Dependency installer runs automatically in startup scripts
- State management connects to persistent data in `test_outputs/`
- Backup system creates timestamped archives in `backups/` directory
- Scripts work from project root and handle relative paths correctly
- Utility scripts connect to persistent data in `test_outputs/`
- State management interacts with tokenomics in `src/core/layer2/`
- Archive operations work with `layer2/poc_archive.py`
- Development workflow integration with scripts in `scripts/development/`

## Development Guidelines

- Implement safety checks and confirmation prompts
- Provide clear warnings about data loss
- Support selective cleanup options
- Log all operations for audit trail
- Test utilities thoroughly before use in production

## Common Patterns

- System state management and reset
- Data cleanup and maintenance
- Safety checks and user confirmation
- Selective operation modes
- Audit logging and tracking


