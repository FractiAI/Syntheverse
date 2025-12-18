# Scripts

This directory contains scripts for development, deployment, and maintenance of the Syntheverse system.

## Directory Structure

- `development/` - Development workflow and service management
- `startup/` - System startup and orchestration
- `deployment/` - Smart contract deployment
- `utilities/` - System maintenance and dependency management

## Key Scripts

### Startup Scripts

Located in `scripts/startup/`:

- `start_servers.py` - Main startup script with multiple modes
  - `full`: All services (default)
  - `poc`: PoC API + Frontend
  - `minimal`: PoC API only

### Development Scripts

Located in `scripts/development/`:

- `manage_services.sh` - Unified service manager for development

### Deployment Scripts

Located in `scripts/deployment/`:

- `deploy_contracts.py` - Deploy smart contracts to blockchain

### Utility Scripts

Located in `scripts/utilities/`:

- `install_deps.py` - Install system dependencies
- `clear_state.py` - Clear system state files

## Usage

### Central Script Menu

For easy access to all scripts, use the main menu:

```bash
# From repository root
python scripts/main.py
```

This provides an interactive text menu to:
- Browse scripts by category (startup, development, deployment, utilities)
- View descriptions for each script
- Execute any script with confirmation
- Navigate between categories

### Quick Start
```bash
# From repository root - start all services
python scripts/startup/start_servers.py

# Or start specific mode
python scripts/startup/start_servers.py --mode poc
```

Services started:
- PoC API on http://localhost:5001
- Next.js Frontend on http://localhost:3001 (poc/full modes)
- RAG API on http://localhost:8000 (full mode only)

### Development Services
```bash
# Start PoC UI development environment
./scripts/development/manage_services.sh start poc

# Start all services
./scripts/development/manage_services.sh start all

# Check service status
./scripts/development/manage_services.sh status
```

### Deployment
```bash
# Deploy smart contracts to Anvil (local)
python scripts/deployment/deploy_contracts.py
```

### System Maintenance
```bash
# Install dependencies (runs automatically in other scripts)
python scripts/utilities/install_deps.py

# Clear system state
python scripts/utilities/clear_state.py --target all --backup
```
