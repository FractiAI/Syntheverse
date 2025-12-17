# Utility Scripts Agents

## Purpose

Maintenance, administration, and system state management utilities for the Syntheverse platform.

## Key Modules

### System State Management (`clear_persistent_memory.py`)

- **Test Data Cleanup**: Removal of test output files and temporary data
- **Tokenomics Reset**: Clearing and resetting tokenomics state to initial values
- **Archive Management**: Clearing contribution archives and historical data
- **System State Reset**: Returning system to clean initial state

### Maintenance Operations

- **Data Cleanup**: Safe removal of temporary and test files
- **State Management**: Resetting persistent state across components
- **Environment Preparation**: Preparing system for fresh testing cycles
- **Backup Protection**: Warnings and safeguards for data loss prevention

### Administrative Tools

- **Development Support**: Utilities for development workflow
- **Testing Support**: Scripts for test environment management
- **System Health**: Tools for system state inspection and maintenance

## Integration Points

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
