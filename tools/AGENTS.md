# Development Tools Agents

## Purpose

Development tools, testing guides, and utilities for Syntheverse system development, testing, and maintenance.

## Key Modules

### Testing Guides (`TESTING_GUIDE.md`)

- **PoD UI Testing**: Comprehensive testing guide for PoD submission interface
- **Test Scenarios**: Different contribution types and evaluation outcomes
- **Troubleshooting**: Common testing issues and solutions
- **Output Analysis**: Understanding test results and reports

### Service Management (`SERVICE_MANAGEMENT.md`)

- **Service Control**: Managing system services during development
- **Process Management**: Starting, stopping, and monitoring services
- **Health Checks**: Service availability and status verification

### Testing Scripts

- **Browser Testing**: `START_BROWSER_TEST.txt` and `START_FOR_BROWSER_TEST.md`
- **Quick Testing**: `QUICK_TEST.md` for rapid test execution
- **Test Automation**: Scripts for automated testing workflows

### Hardhat Configuration (`hardhat/`)

- **Smart Contract Testing**: Hardhat configuration for Solidity development
- **Network Configuration**: Test network setup and management
- **Deployment Scripts**: Contract deployment automation

### Project Structure (`PROJECT_STRUCTURE.md`)

- **Repository Organization**: Complete project structure documentation
- **Directory Layout**: File organization and naming conventions
- **Navigation Guide**: Finding files and understanding structure

## Integration Points

- Testing tools connect to test suites in `tests/`
- Service management integrates with startup scripts in `scripts/startup/`
- Hardhat configuration used by contracts in `src/blockchain/contracts/`
- Testing guides reference documentation in `docs/`

## Development Guidelines

- Keep testing guides current with system changes
- Update service management procedures as architecture evolves
- Maintain comprehensive test scenarios for all features
- Document new tools and utilities as they are added
- Ensure testing procedures work across different environments

## Common Patterns

- Testing workflow documentation
- Service lifecycle management
- Test scenario development
- Troubleshooting guides
- Development environment setup
