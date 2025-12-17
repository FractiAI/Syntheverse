# Startup Scripts Agents

## Purpose

System startup and service management scripts for orchestrating the complete Syntheverse platform, handling service lifecycle, port management, and dependency validation.

## Key Modules

### Main Startup (`start_servers.py`)

- **Complete System Orchestration**: Starts all Syntheverse services simultaneously
- **Environment Validation**: Checks required environment variables and dependencies
- **Port Management**: Intelligent port conflict resolution and cleanup
- **Service Health Checks**: Validates all services are running and responsive
- **Error Handling**: Comprehensive error reporting and recovery

### Simplified Startup (`start_servers_simple.py`)

- **Streamlined Orchestration**: Simplified version of main startup script
- **Reduced Validation**: Minimal dependency checking for faster startup
- **Port Management**: Same intelligent port handling as main script
- **Service Monitoring**: Basic service availability checks

### Complete UI Startup (`start_complete_ui.py`)

- **UI-Focused Startup**: Specialized script for UI components
- **Frontend Priority**: Emphasizes Next.js and web interface startup
- **API Integration**: Ensures backend APIs are available for frontend
- **Cross-Service Coordination**: Manages UI-backend service dependencies

### Shell Script (`start_servers.sh`)

- **Shell-Based Startup**: Bash script alternative for system startup
- **Environment Setup**: Shell environment configuration
- **Service Sequencing**: Proper startup order for dependent services
- **Error Propagation**: Shell-compatible error handling

### Port Manager (`port_manager.py`)

- **Shared Port Management**: Intelligent port conflict resolution
- **Process Detection**: Identifies processes using target ports
- **System Service Protection**: Avoids killing critical system services
- **Retry Logic**: Exponential backoff for persistent conflicts
- **Cross-Platform Support**: Works on macOS, Linux, and Windows

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
