# Scripts

This directory contains scripts for development, deployment, and maintenance of the Syntheverse system.

## Directory Structure

- `development/` - Development and testing scripts
- `startup/` - Scripts to start the various system components
- `deployment/` - Deployment and contract management scripts
- `utilities/` - Utility scripts for maintenance and administration

## Startup Scripts

Located in `scripts/startup/`:

- `start_servers.py` - Main startup script for the complete system
- `start_servers_simple.py` - Simplified startup script
- `start_complete_ui.py` - Complete UI startup script
- `start_servers.sh` - Shell script for starting servers

## Utility Scripts

Located in `scripts/utilities/`:

- `clear_persistent_memory.py` - Clear test data and reset system state

## Usage

### Quick Start
```bash
# From repository root
python scripts/startup/start_servers.py
```

This starts:
- PoC API on http://localhost:5001
- Next.js Frontend on http://localhost:3001
- Legacy Web UI on http://localhost:5000 (optional)

### Development
```bash
# Start PoC UI (Next.js + API)
cd scripts/development
./start_poc_ui.sh

# Or use simple startup
python scripts/startup/start_servers_simple.py
```

### Deployment
```bash
# Deploy smart contracts to Anvil (local)
cd scripts/deployment
python deploy_contracts.py
```

### Maintenance
```bash
# Clear persistent memory/test data
cd scripts/utilities
python clear_persistent_memory.py
```
