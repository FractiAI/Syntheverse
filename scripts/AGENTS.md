# Scripts Agents

## Purpose

Scripts for development, deployment, startup, and maintenance of the Syntheverse system.

## Key Modules

### Startup (`startup/`)

- **`start_servers.py`**: Main startup script for system
- **`start_servers_simple.py`**: Simplified startup script
- **`start_complete_ui.py`**: UI startup script
- **`start_servers.sh`**: Shell script for starting servers

### Development (`development/`)

- **`start_poc_ui.sh`**: Start PoC UI development environment (Next.js frontend + PoC API)
- **`stop_poc_ui.sh`**: Stop PoC UI services
- **`start_all_services.sh`**: Start all system services (RAG API + Legacy Web UI)
- **`stop_all_services.sh`**: Stop all system services
- **`submit_pod.py`**: Submit PoD for testing (legacy PoD system)
- **`ui_pod_submission.py`**: UI for PoD submission (legacy PoD system)
- **`Syntheverse.sh`**: Main Syntheverse startup script (Legacy Web UI)

### Deployment (`deployment/`)

- **`deploy_contracts.py`**: Deploy smart contracts to blockchain

### Utilities (`utilities/`)

- **`clear_persistent_memory.py`**: Clear test data and reset system state

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
- Port management: Frontend (3001), PoC API (5001), Legacy Web UI (5000), RAG API (8000)

