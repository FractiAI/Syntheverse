# Development Scripts

## Purpose

Development workflow scripts for service management, testing, and validation during Syntheverse development and testing.

## Key Modules

### Service Manager (`manage_services.sh`)

- **Unified Service Control**: Single script for all service management operations
- **PoC Services**: Start/stop PoC API + Next.js frontend
- **All Services**: Start/stop RAG API
- **Service Status**: Check status of all services
- **Restart Functionality**: Restart services with single command

## Integration Points

- Development scripts connect to services in `src/api/`, `src/frontend/`, and `src/core/`
- Testing scripts interact with Layer 1 and Layer 2 components
- Service management integrates with startup scripts in `scripts/startup/`
- Path resolution works from script directory to project root

## Development Guidelines

- Ensure scripts work from their directory location
- Implement proper error handling and logging
- Support environment variable configuration
- Test scripts thoroughly in development environment
- Document script usage and parameters

## Common Patterns

- Service lifecycle management
- Development environment orchestration
- Testing workflow automation
- Path resolution and navigation
- Environment configuration handling


