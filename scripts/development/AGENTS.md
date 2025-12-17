# Development Scripts Agents

## Purpose

Development workflow scripts for service management, testing, and validation during Syntheverse development and testing.

## Key Modules

### Service Management Scripts

- **PoC UI Development**: `start_poc_ui.sh` and `stop_poc_ui.sh` for Next.js + PoC API development
- **All Services Control**: `start_all_services.sh` and `stop_all_services.sh` for complete service management
- **Syntheverse Control**: `Syntheverse.sh` and `stop_Syntheverse.sh` for legacy system management

### Testing and Submission Scripts

- **PoD Submission**: `submit_pod.py` for testing PoD submission workflow
- **UI Submission**: `ui_pod_submission.py` for interactive PoD submission testing
- **Test Data Generation**: Scripts for creating test contributions and scenarios

### Development Workflow

- **Environment Setup**: Scripts for setting up development environments
- **Service Orchestration**: Coordinated startup of multiple services
- **Testing Automation**: Automated testing and validation workflows
- **Data Management**: Test data creation and cleanup

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
