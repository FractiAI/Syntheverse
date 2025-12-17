# Tests Agents

## Purpose

Comprehensive test suites for validating system functionality, API endpoints, submission flows, and integration testing. Features real-only testing framework with automatic dependency management, service startup, execution, reporting, caching, and analytics.

## Testing Policy

**REAL-ONLY TESTING**: All tests use real implementations with no mocking or skipping. Dependencies are automatically installed and services are automatically started. Tests either pass or fail with clear error messages - they never skip.

- ✅ **Zero Mock Usage**: All tests use real API calls, file operations, and service interactions
- ✅ **Zero Skip Conditions**: Tests never skip - dependencies are installed and services are started automatically
- ✅ **Automatic Dependency Management**: Python packages and system services are installed/started as needed
- ✅ **Clear Failure Messages**: When tests fail, they provide detailed error information for debugging

## Test Framework

### Core Components

- **`test_framework.py`** - Test framework with base classes (`SyntheverseTestCase`, `APITestCase`, `DataTestCase`), retry mechanisms, error reporting, and utilities
- **`test_runner.py`** - Python test orchestrator with discovery, filtering, caching, parallel execution, and HTML reporting
- **`run_tests.sh`** - Shell script for test execution with colored output and reporting
- **`test_config.json`** - Configuration file for test settings, scenarios, thresholds, and dependency requirements
- **`conftest.py`** - Pytest configuration for proper test discovery and marker definitions

### Test Categories

Tests are organized into categories for coverage:

#### **Unit Tests** - Individual Component Testing
- `test_core_modules.py` - Core business logic (archive, tokenomics, evaluator, allocator)
- `test_submission.py` - Basic submission functionality
- `test_rag_timeout.py` - RAG timeout handling
- `test_anvil_manager.py` - Blockchain node management
- `test_port_manager.py` - Port allocation and management
- `test_service_health.py` - Service health monitoring

#### **Integration Tests** - API and Service Integration
- `test_poc_api.py` - PoC API endpoints and error scenarios
- `test_rag_api.py` - RAG API connectivity and query variations
- `test_rag_pod_query.py` - RAG PoD query functionality
- `test_frontend_integration.py` - Frontend-backend integration
- `test_blockchain.py` - Blockchain layer integration

#### **End-to-End Tests** - Complete Workflow Testing
- `test_submission_flow.py` - Submission flow validation
- `test_full_submission_flow.py` - Full end-to-end process

#### **Data & Security Tests** - Data Management and Security
- `test_data_management.py` - File operations, JSON integrity, concurrent access
- `test_security.py` - Input validation, authentication, data exposure prevention

#### **Performance Tests** - Scalability and Performance
- `test_performance.py` - API response times, load testing, resource usage

#### **Infrastructure Tests** - Deployment and Startup
- `test_startup_scripts.py` - Service startup validation
- `test_deployment.py` - Contract deployment testing

### Test Execution

#### Interactive Menu (Recommended)
```bash
cd examples
./run.sh
# Navigate to: 3) 🧪 Tests
```

#### Direct Test Runner
```bash
cd tests
./run_tests.sh --all          # Run all tests
./run_tests.sh --quick        # Run quick validation
./run_tests.sh --frontend     # Run frontend tests
./run_tests.sh --submission   # Run specific test
```

#### Python Test Runner
```bash
cd tests
python test_runner.py --category unit     # Run unit tests only
python test_runner.py --category e2e      # Run end-to-end tests
python test_runner.py --report-only       # Generate report from results
```

#### Pytest with Service Control
```bash
cd tests
pytest -v -rs                          # Run all tests with skip reasons shown
pytest -m "not requires_service"       # Skip tests requiring external services
pytest -m "requires_rag_api"           # Run only RAG API tests
pytest --mock-services                 # Run tests with mocked services
pytest --skip-service-checks           # Skip all service availability checks
```

### Test Framework Features

#### Pytest Configuration

The test suite uses enhanced pytest configuration in `pytest.ini`:
- **Skip reporting**: `-rs` flag shows reasons for skipped tests
- **Service markers**: Automatic detection and skipping of service-dependent tests
- **Coverage integration**: Built-in coverage reporting for core modules
- **Custom markers**: Support for unit, integration, e2e, and service-specific markers

#### Standardized Test Base Classes
```python
from test_framework import SyntheverseTestCase, APITestCase, DataTestCase

class MyAPITest(APITestCase):
    def get_category(self):
        return "integration"

    def setUp(self):
        super().setUp()
        self.require_service("poc_api")  # Automatic service checking

    def test_api_endpoint(self):
        self.log_info("Testing API functionality")
        self.add_metric("response_time", 1.2)
        # Test logic here

class MyDataTest(DataTestCase):
    def test_file_operations(self):
        temp_file = self.create_temp_file("content", "test.txt")
        # Automatic cleanup handled by base class
```

#### Advanced Features
- **Retry Mechanism**: Automatic retry for flaky tests with configurable attempts
- **Result Caching**: Cache test results to speed up re-runs
- **Service Health Checking**: Automatic service availability validation
- **Parallel Execution**: Run tests concurrently for faster execution
- **HTML Reporting**: Generate interactive HTML test reports

#### Configuration Management
- API URLs, timeouts, test data, and performance thresholds
- Service health checks and dependency validation
- Test scenarios for error cases and edge conditions
- Comprehensive test categories and filtering options

#### Enhanced Framework Features

- **Base Test Classes**: `SyntheverseTestCase` provides standardized logging, metrics collection, and service health checking
- **API Testing**: `APITestCase` includes built-in service availability checking and API request utilities
- **Data Testing**: `DataTestCase` provides temporary file management and data validation utilities
- **Error Reporting**: Enhanced error reporting with exception chaining, context capture, and diagnostic suggestions
- **Retry Mechanisms**: Configurable retry logic for flaky tests with exponential backoff
- **Performance Tracking**: Built-in metrics collection for response times, memory usage, and custom metrics
- **Mock Utilities**: Comprehensive test fixtures for creating mock data, services, and responses

#### Advanced Reporting
- JSON and HTML reports with detailed metrics
- Colored console output with progress indicators
- Test duration tracking and performance analytics
- Success/failure statistics with trend analysis
- Detailed error logging with stack traces
- Coverage integration with HTML visualization

## Test Files

### Core Test Files
- **`test_submission.py`**: Basic submission testing
- **`test_submission_flow.py`**: Complete submission flow testing
- **`test_full_submission_flow.py`**: End-to-end submission testing
- **`test_rag_api.py`**: RAG API testing with framework integration
- **`test_rag_pod_query.py`**: RAG PoD query testing
- **`test_rag_timeout.py`**: RAG timeout testing

### Legacy Test Scripts
- **`test_poc_frontend.sh`**: Frontend test script
- **`test_poc_quick.sh`**: Quick validation script

## Test Documentation

- **`TEST_POC_FRONTEND.md`**: PoC frontend testing guide
- **`TEST_POC_UI.md`**: PoC UI testing guide
- **`TEST_WEB_UI.md`**: Web UI testing guide

## Test Outputs

### Results Directory (`results/`)
- Detailed test logs with timestamps
- JSON reports with metrics and results
- Performance data and statistics
- Error traces and debugging information

### Legacy Outputs (`outputs/`)
- **`l2_tokenomics_state.json`**: Test tokenomics state
- Historical test output files

## Prerequisites

Before running tests:

1. **Python Dependencies**: `pip install requests pytest` (for API testing and pytest framework)
2. **System Services**: Use startup scripts to launch required services
3. **Configuration**: Check `test_config.json` for API URLs and settings
4. **Environment**: Set GROQ_API_KEY for AI-powered tests

## Service Requirements

Tests are marked with service requirements and will be automatically skipped if required services are not available:

### Service Markers

- **`@pytest.mark.requires_rag_api`**: Requires RAG API running on port 8000
- **`@pytest.mark.requires_poc_api`**: Requires PoC API running on port 5001
- **`@pytest.mark.requires_frontend`**: Requires frontend running on port 3001
- **`@pytest.mark.requires_blockchain`**: Requires blockchain modules and dependencies

### Running Tests with Services

#### Option 1: Start Services First (Recommended)
```bash
# Start required services using the interactive menu
cd examples
./run.sh
# Select: 4) 🚀 Startup Scripts → Start all services

# Then run tests
cd ../tests
pytest -v
```

#### Option 2: Run with Mocks
```bash
# Run tests even when services are unavailable (uses mocks)
pytest --mock-services -v
```

#### Option 3: Skip Service-Dependent Tests
```bash
# Run only unit tests that don't require external services
pytest -m "not requires_service"
```

### Service Status Checking

The test framework automatically checks service availability:
- **Health checks**: Tests service endpoints before running dependent tests
- **Graceful skipping**: Tests are skipped with clear messages when services are unavailable
- **Mock support**: Use `--mock-services` to run tests with mocked external dependencies

## Integration Points

- **API Validation**: Tests verify all API endpoints function correctly
- **Service Integration**: Tests validate component interactions
- **Workflow Testing**: Tests verify complete user journeys
- **Error Handling**: Tests validate error scenarios and recovery
- **Performance Monitoring**: Tests track response times and metrics

## Development Guidelines

### Writing New Tests
1. Inherit from `SyntheverseTestCase` for standardized behavior
2. Add service markers (`@pytest.mark.requires_service_name`) for tests needing external services
3. Use configuration values from `test_config.json`
4. Add appropriate logging with `self.log_info()`, `self.log_error()`
5. Record metrics with `self.add_metric()`
6. Implement proper category classification

### Test Organization
- Place tests in appropriate category directories
- Update `test_config.json` with new test categories
- Add descriptive docstrings and comments
- Follow naming convention: `test_*.py`

### Best Practices
- Test both success and failure scenarios
- Use realistic test data
- Implement proper cleanup in `tearDown()`
- Add timeout handling for network operations
- Validate response formats and error messages

## Common Patterns

- **Health Checks**: Verify services are running before testing
- **Data Validation**: Check response structure and content
- **Performance Tracking**: Record response times and throughput
- **Error Scenarios**: Test invalid inputs and failure conditions
- **Cleanup**: Ensure test isolation and resource cleanup

## Troubleshooting

### Common Issues
- **Service Not Running**: Use interactive menu to start services, or use `--mock-services`
- **Tests Being Skipped**: Check service availability with `pytest -rs` to see skip reasons
- **Mock Services Needed**: Use `--mock-services` flag to run tests without real services
- **Missing Dependencies**: Check Python/Node.js installations
- **API Timeouts**: Increase timeout values in config
- **Permission Errors**: Ensure proper file permissions

### Debugging Tests
- Check `results/` directory for detailed logs
- Use `--report-only` to analyze previous test runs
- Enable verbose logging in test configuration
- Run individual tests for isolation


