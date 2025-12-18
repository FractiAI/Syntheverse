# Tests Agents

## Purpose

Test suites for validating system functionality, API endpoints, submission flows, and integration testing. Tests use real implementations with dependency management and service startup.

## Key Modules

### Core Test Framework

- **`test_framework.py`**: Test framework with base classes (`SyntheverseTestCase`, `APITestCase`, `DataTestCase`), retry mechanisms, and utilities
- **`test_runner.py`**: Test orchestrator with filtering, caching, parallel execution, and HTML reporting
- **`run_tests.sh`**: Shell script for test execution with colored output
- **`test_config.json`**: Configuration with test scenarios, thresholds, and environment settings

### Unit Test Modules

- **`test_core_modules.py`**: Core business logic testing (PoCArchive, TokenomicsState, SandboxMap, PoCEvaluator, TokenAllocator, PoCServer)
- **`test_anvil_manager.py`**: Blockchain node management and lifecycle testing
- **`test_port_manager.py`**: Port allocation, process monitoring, and conflict resolution
- **`test_service_health.py`**: Service health checking and monitoring functionality

### Integration Test Modules

- **`test_poc_api.py`**: PoC API endpoints, error scenarios, rate limiting, and concurrent requests
- **`test_rag_api.py`**: RAG API connectivity, query variations, and error handling
- **`test_rag_pod_query.py`**: RAG PoD-specific query functionality
- **`test_frontend_integration.py`**: Frontend-backend integration and UI testing
- **`test_blockchain.py`**: Blockchain layer1 integration and contract testing

### End-to-End Test Modules

- **`test_submission_flow.py`**: Complete submission workflow validation
- **`test_full_submission_flow.py`**: Full end-to-end process testing
- **`test_submission.py`**: Submission testing with error scenarios

### Specialized Test Modules

- **`test_data_management.py`**: File operations, JSON integrity, backup/recovery, and concurrent access
- **`test_security.py`**: Input sanitization, authentication bypass prevention, data exposure protection
- **`test_performance.py`**: API response times, load testing, memory/CPU usage, and scalability analysis
- **`test_rag_timeout.py`**: RAG timeout handling and recovery mechanisms

### Infrastructure Test Modules

- **`test_startup_scripts.py`**: Service startup validation and environment configuration
- **`test_deployment.py`**: Smart contract deployment and validation
- **`test_fixtures.py`**: Test data generators and environment management utilities

### Test Documentation

- **`CONTRIBUTING_TESTS.md`**: Comprehensive guide for writing and maintaining tests
- **`TEST_POC_FRONTEND.md`**: PoC frontend testing guide
- **`TEST_POC_UI.md`**: PoC UI testing guide
- **`TEST_WEB_UI.md`**: Web UI testing guide

### Test Scripts

- **`test_poc_frontend.sh`**: Frontend test script
- **`test_poc_quick.sh`**: Quick validation script
- **`run_tests.sh`**: Main test execution script

### Test Outputs

- **`results/`**: Test execution logs, JSON/HTML reports, and performance metrics
- **`outputs/`**: Legacy test outputs and historical data
- **`test_outputs/`**: Test-generated data files and archives

## Integration Points

- Tests validate API endpoints
- Tests verify submission flows
- Tests check RAG functionality
- Tests validate blockchain integration

## Development Guidelines

- Write real tests for new functionality (no mocking)
- Follow test-driven development (TDD) with real dependencies
- Test both happy paths and error scenarios using real implementations
- Keep tests maintainable and readable
- Use automatic dependency management and service startup
- Document test dependencies and isolation requirements
- Never skip tests - ensure dependencies are available or installable

## Common Patterns

- Unit tests for individual functions
- Integration tests for component interactions
- End-to-end tests for complete flows
- API endpoint testing
- Error scenario testing



