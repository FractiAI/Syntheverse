# Startup Scripts

## Purpose

System startup and service management scripts for orchestrating the Syntheverse platform, handling service lifecycle, port management, and dependency validation.

## Key Modules

### Main Startup (`start_servers.py`)

- Supports full, poc, and minimal startup modes
- Installs required packages before startup
- Checks required environment variables and dependencies
- Port conflict resolution and cleanup
- Validates all services are running and responsive
- Error reporting and recovery

### Port Manager (`port_manager.py`)

- Port conflict resolution
- Identifies processes using target ports
- Avoids killing critical system services
- Exponential backoff for persistent conflicts
- Cross-platform support (macOS, Linux, Windows)

### Anvil Manager (`anvil_manager.py`)

- Starts and manages Foundry Anvil Ethereum node
- Checks Anvil service status and connectivity
- Handles Anvil startup, shutdown, and restart
- Supports custom accounts, gas limits, and block time

### Service Health (`service_health.py`)

- Monitors all Syntheverse services
- HTTP and RPC endpoint checking
- Configurable timeout and retry for service availability
- Health status and diagnostics

## Integration Points

- Startup scripts orchestrate services across `src/api/`, `src/frontend/`, and `src/core/`
- Port manager used by all startup scripts for consistent port handling
- Environment validation references configuration in `config/`
- Service health checks connect to API endpoints
- Error handling integrates with testing framework in `tests/`

## Development Guidelines

- Use shared PortManager for all port-related operations
- Implement comprehensive environment validation
- Include proper logging for debugging and monitoring
- Test scripts thoroughly with mock services
- Document port usage and conflict resolution strategies

## Common Patterns

- Service orchestration and dependency management
- Intelligent port conflict resolution
- Environment variable validation
- Health check implementations
- Error handling and recovery


