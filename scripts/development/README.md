# Development Scripts

## Purpose

Scripts for development workflow, service management, and testing during development.

## Scripts

### Service Management

- **`manage_services.sh`**: Unified service manager for all development services

## Usage

### Service Management

The `manage_services.sh` script provides unified control over all development services:

```bash
# Start PoC UI development environment
./manage_services.sh start poc

# Stop PoC UI services
./manage_services.sh stop poc

# Start all services (RAG API)
./manage_services.sh start all

# Stop all services
./manage_services.sh stop all

# Restart services
./manage_services.sh restart poc

# Check service status
./manage_services.sh status
```

## Integration

- Scripts orchestrate multiple services
- Manage service lifecycle
- Support development workflow
- Enable testing and validation
- Paths are relative to project root (scripts navigate correctly)

