# Scripts

## Purpose

Scripts for development, deployment, startup, and maintenance of the Syntheverse system.

## Key Modules

### Main Menu (`main.py`)

- **`main.py`**: Central menu-based runner for all scripts
  - Organized by category (startup, development, deployment, utilities)
  - Interactive menu system with descriptions
  - Supports both Python and shell script execution
  - Error handling and script validation

### Startup (`startup/`)

- **`start_servers.py`**: System startup script with multiple modes
  - Full mode: All services (default)
  - PoC mode: API + Frontend only
  - Minimal mode: API only

### Development (`development/`)

- **`manage_services.sh`**: Unified service manager
  - Start/stop PoC services (API + Frontend)
  - Start/stop all services (RAG API)
  - Service status and restart functionality

### Deployment (`deployment/`)

- **`deploy_contracts.py`**: Deploy smart contracts to blockchain

### Utilities (`utilities/`)

- **`install_deps.py`**: Install system dependencies
- **`clear_state.py`**: Clear system state files

## Integration Points

- Scripts orchestrate multiple services
- Startup scripts manage service lifecycle
- Deployment scripts interact with blockchain
- Utility scripts maintain system state
- All paths are relative to project root
- Scripts navigate correctly from their directory location

## Development Guidelines

- Use Python for complex orchestration
- Use shell scripts for simple service management
- Handle errors gracefully
- Provide clear output and logging
- Support environment variable configuration
- Document script usage in README files

## Common Patterns

- Service orchestration and lifecycle management
- Environment variable configuration
- Error handling and logging
- Service health checks
- Cleanup and maintenance operations
- Path resolution: Scripts use `PROJECT_ROOT` variable to navigate to project root
- Port management: Frontend (3001), PoC API (5001), RAG API (8000)

