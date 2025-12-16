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

### Development
```bash
# Individual component startup
python scripts/startup/start_servers_simple.py
```

### Deployment
```bash
# Deploy smart contracts
python scripts/deployment/deploy_contracts.py
```

### Maintenance
```bash
# Clear persistent memory/test data
python scripts/utilities/clear_persistent_memory.py
```
