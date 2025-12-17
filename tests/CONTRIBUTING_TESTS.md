# Contributing Tests

## Overview

This guide provides comprehensive instructions for developing, running, and maintaining tests for the Syntheverse project. The test suite uses a **real-only testing framework** with automatic dependency management, service startup, and comprehensive error reporting.

## Testing Policy

**REAL-ONLY TESTING**: All tests must use real implementations with no mocking or skipping. The framework automatically manages dependencies and services.

### Key Principles
- **No Mocking**: Tests use real API calls, file operations, and service interactions
- **No Skipping**: Tests never skip - dependencies are installed and services are started automatically
- **Automatic Setup**: Python packages and services are installed/started as needed
- **Clear Failures**: Tests fail with detailed error messages when issues occur

## Test Framework Architecture

### Core Components

1. **`test_framework.py`** - Base testing infrastructure
   - `SyntheverseTestCase` - Base test class with logging and metrics
   - `TestUtils` - Utility functions for common operations
   - `TestResult` - Standardized test result container
   - `TestFixtures` - Common test setup/teardown utilities
   - `ErrorReporting` - Error handling and reporting

2. **`test_runner.py`** - Test execution orchestrator
   - Category-based test execution (unit, integration, e2e)
   - Result aggregation and reporting
   - Timeout handling and performance monitoring

3. **`test_config.json`** - Configuration management
   - API endpoints, timeouts, test data
   - Test scenarios and dependency requirements
   - Environment and reporting settings

4. **`test_fixtures.py`** - Test utilities and isolation
   - Data generators for test scenarios
   - Temporary file and directory management
   - Test isolation and cleanup utilities

## Test Categories

### Unit Tests (`test_category = "unit"`)
- Test individual functions and classes with real dependencies
- Use temporary files and isolated environments
- Focus on logic correctness and edge cases
- **Examples**: `test_core_modules.py`, `test_anvil_manager.py`

### Integration Tests (`test_category = "integration"`)
- Test component interactions and API communications
- Services automatically started by framework
- Validate real data flow between components
- **Examples**: `test_poc_api.py`, `test_rag_api.py`, `test_blockchain.py`

### End-to-End Tests (`test_category = "end_to_end"`)
- Test complete user workflows from start to finish
- Full system with real services and dependencies
- Validate actual user scenarios
- **Examples**: `test_submission_flow.py`, `test_full_submission_flow.py`, `test_blockchain.py`

## Writing Tests

### Basic Test Structure

```python
import sys
from pathlib import Path

# Add test framework to path
test_dir = Path(__file__).parent
sys.path.insert(0, str(test_dir))

from test_framework import SyntheverseTestCase, TestUtils, test_config

class TestMyFeature(SyntheverseTestCase):
    """Test suite for my feature"""

    def get_category(self) -> str:
        """Return test category for reporting"""
        return "integration"  # or "unit" or "end_to_end"

    def setUp(self):
        """Set up test with service availability check"""
        super().setUp()
        # Check if required services are running
        self.ensure_services(["poc_api", "rag_api"])

    def test_basic_functionality(self):
        """Test basic functionality"""
        self.log_info("Testing basic functionality")

        # Use test fixtures
        test_data = self.create_test_contribution(title="Test Title")

        # Your test logic here
        result = some_function(test_data)

        # Assertions with descriptive messages
        self.assertIsNotNone(result, "Function should return a result")
        self.assertEqual(result["status"], "success", "Operation should succeed")

        # Record metrics
        self.add_metric("processing_time", 1.5)
        self.add_metric("items_processed", len(result.get("items", [])))

    def test_error_handling(self):
        """Test error handling scenarios"""
        self.log_info("Testing error handling")

        # Test invalid inputs
        invalid_inputs = [None, "", {}, {"invalid": "data"}]

        for invalid_input in invalid_inputs:
            with self.subTest(input=invalid_input):
                try:
                    result = some_function(invalid_input)
                    # Should handle gracefully
                    self.assertIn("error", result, f"Should handle invalid input: {invalid_input}")
                except Exception as e:
                    # Or raise appropriate exceptions
                    self.assertIsInstance(e, (ValueError, TypeError))

    def test_performance(self):
        """Test performance characteristics"""
        self.log_info("Testing performance")

        import time
        start_time = time.time()

        # Perform operation
        result = some_operation()

        duration = time.time() - start_time

        # Check performance thresholds
        max_duration = test_config.get("timeouts.api_call", 30)
        self.assertLess(duration, max_duration, f"Operation too slow: {duration:.2f}s")

        self.add_metric("operation_duration", duration)

def run_my_tests():
    """Run tests with framework"""
    TestUtils.print_test_header(
        "My Feature Test Suite",
        "Testing my feature functionality and performance"
    )

    import unittest
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMyFeature)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()

if __name__ == "__main__":
    import unittest
    unittest.main()
```

### Using Test Fixtures

```python
from test_fixtures import TestDataGenerators, ServiceMocks, TestContextManagers

class TestWithFixtures(SyntheverseTestCase):
    def test_with_mock_data(self):
        """Test using generated mock data"""
        # Generate test data
        contributions = TestDataGenerators.generate_sample_contributions(3)
        evaluations = TestDataGenerators.generate_evaluation_results(contributions)

        self.assertEqual(len(contributions), 3)
        self.assertEqual(len(evaluations), 3)

        # Verify data relationships
        for contrib, eval_result in zip(contributions, evaluations):
            self.assertEqual(contrib["title"], eval_result["title"])

    def test_with_mocked_services(self):
        """Test with mocked API responses"""
        with TestContextManagers.mock_api_calls():
            # Your test logic here - API calls will be mocked
            response = make_api_call()
            self.assertEqual(response["status"], "success")

    def test_with_temp_files(self):
        """Test file operations with temporary files"""
        with TestContextManagers.temp_environment() as env:
            # Create temporary test file
            test_file = env.create_temp_file("test content", ".txt")
            self.assertTrue(test_file.exists())

            # Perform file operations
            with open(test_file, 'r') as f:
                content = f.read()
                self.assertEqual(content, "test content")

            # File is automatically cleaned up
```

## Test Execution

### Interactive Menu (Recommended)
```bash
cd examples
./run.sh
# Navigate to: 3) 🧪 Tests
```

### Direct Commands
```bash
cd tests

# Run all tests
./run_tests.sh --all

# Run specific categories
./run_tests.sh --unit
./run_tests.sh --integration
./run_tests.sh --e2e

# Run individual tests
./run_tests.sh --submission
./run_tests.sh --rag-api

# Python test runner
python test_runner.py --category integration
python test_runner.py --report-only
```

### IDE Integration
```python
# Run specific test class
import unittest
from tests.test_poc_api import TestPoCAPI

suite = unittest.TestLoader().loadTestsFromTestCase(TestPoCAPI)
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)
```

## Best Practices

### Test Organization
1. **One Concept Per Test**: Each test method should validate one specific behavior
2. **Descriptive Names**: Use `test_descriptive_name` format
3. **Arrange-Act-Assert**: Structure tests clearly
4. **Independent Tests**: Tests should not depend on each other

### Assertions and Validation
```python
# Good: Descriptive assertions
self.assertEqual(actual, expected, f"Should return {expected}, got {actual}")

# Good: Check data types
self.assertIsInstance(result, dict, "Result should be a dictionary")

# Good: Validate ranges
self.assertGreater(score, 0, "Score should be positive")
self.assertLessEqual(score, 100, "Score should not exceed 100")

# Good: Check collections
self.assertIn("required_key", data, "Response missing required field")
self.assertEqual(len(items), expected_count, f"Expected {expected_count} items")
```

### Error Handling
```python
# Test expected exceptions
with self.assertRaises(ValueError):
    invalid_operation()

# Test error responses
try:
    risky_operation()
    self.fail("Should have raised an exception")
except ExpectedException as e:
    self.assertIn("expected message", str(e))
```

### Performance Testing
```python
import time

start_time = time.time()
result = operation_under_test()
duration = time.time() - start_time

# Check against performance thresholds
max_duration = test_config.get("performance_thresholds.api_call_max_time", 30)
self.assertLess(duration, max_duration, f"Operation too slow: {duration:.2f}s")

# Record metrics
self.add_metric("operation_duration", duration)
```

## Common Patterns

### API Testing Pattern
```python
class TestMyAPI(APITestCase):
    """Test API functionality using enhanced framework"""

    def get_category(self) -> str:
        return "integration"

    def setUp(self):
        super().setUp()
        # Automatically checks if poc_api service is available
        self.require_service("poc_api")

    def test_api_endpoint(self):
        """Test API endpoint with automatic service checking"""
        # Make API request with automatic error handling and metrics
        response = self.make_api_request("poc_api", "/api/health")

        # Validate response structure
        self.assert_api_response_structure(response, ["status", "timestamp"])

        # Check specific values
        self.assertEqual(response["status"], "healthy")

        # Response time is automatically tracked as metric
        # Additional custom metrics can be added
        self.add_metric("health_check_success", True)

    def test_api_with_retries(self):
        """Test API endpoint with retry logic"""
        # Test with automatic retries for potentially flaky endpoints
        response = self.make_api_request_with_retries(
            "poc_api", "/api/some-endpoint", max_retries=3
        )

        self.assertIsNotNone(response)
        self.assert_api_response_structure(response, ["data"])
```
    self.add_metric("response_size", len(str(data)))
```

### Service Integration Pattern
```python
def setUp(self):
    """Ensure required services are available"""
    super().setUp()
    self.ensure_services(["poc_api", "rag_api"])

def test_service_integration(self):
    """Test integration between services"""
    # Test data flow between components
    input_data = self.create_test_contribution()

    # Service A operation
    result_a = service_a.process(input_data)

    # Service B operation
    result_b = service_b.validate(result_a)

    # Verify end-to-end flow
    self.assertTrue(result_b["valid"])
    self.assertEqual(result_b["original_title"], input_data["title"])
```

### Mock Testing Pattern
```python
from unittest.mock import patch, MagicMock

def test_with_mocking(self):
    """Test with mocked dependencies"""
    with patch('module.Class.method') as mock_method:
        # Configure mock
        mock_method.return_value = {"status": "success", "data": []}

        # Test logic
        result = function_under_test()

        # Verify mock was called correctly
        mock_method.assert_called_once()
        self.assertEqual(result["status"], "success")
```

## Debugging Tests

### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Or in test
self.logger.setLevel(logging.DEBUG)
```

### Inspect Test Results
```python
# Check results directory
ls -la tests/results/

# View detailed logs
cat tests/results/test_name_timestamp.log

# Check JSON reports
cat tests/results/test_report_timestamp.json | jq .
```

### Run Tests in Isolation
```python
# Run single test method
python -m unittest tests.test_poc_api.TestPoCAPI.test_health_endpoint

# Run with verbose output
python -m unittest -v tests.test_poc_api
```

## Troubleshooting

### Common Issues

#### Services Not Available
```bash
# Check if services are running
curl http://localhost:5001/health
curl http://localhost:8000/health

# Start services
cd examples && ./run.sh
# Navigate to: 4) 🚀 Startup Scripts
```

#### Import Errors
```python
# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Verify test framework is available
python -c "from test_framework import SyntheverseTestCase; print('OK')"
```

#### Permission Errors
```bash
# Make test scripts executable
chmod +x tests/run_tests.sh
chmod +x examples/run.sh
```

#### Performance Issues
```python
# Check timeouts in config
cat tests/test_config.json | grep timeout

# Increase timeouts if needed
# Edit test_config.json
```

## Contributing New Tests

### Step 1: Plan Your Tests
1. Identify what you're testing (unit, integration, e2e)
2. Define test scenarios and edge cases
3. Determine required test data and mocks
4. Plan assertions and success criteria

### Step 2: Create Test File
```bash
# Create new test file
touch tests/test_my_feature.py

# Follow naming convention: test_*.py
# Use descriptive names for test methods
```

### Step 3: Implement Tests
1. Inherit from `SyntheverseTestCase`
2. Implement `get_category()` method
3. Add service checks in `setUp()` if needed
4. Write clear, focused test methods
5. Add appropriate logging and metrics

### Step 4: Update Configuration
1. Add test to appropriate category in `test_config.json`
2. Add any new test scenarios or data
3. Update API URLs or timeouts if needed

### Step 5: Run and Validate
```bash
# Run your new tests
cd tests
python test_runner.py --category unit  # or integration/e2e

# Check results
ls -la results/
cat results/test_report_*.json
```

### Step 6: Document and Review
1. Add comprehensive docstrings
2. Document any special setup requirements
3. Ensure tests follow established patterns
4. Run full test suite to ensure no regressions

## Test Maintenance

### Regular Tasks
- **Review test results**: Check for flaky tests or performance regressions
- **Update test data**: Keep test data current with system changes
- **Clean old results**: Remove old test result files periodically
- **Update dependencies**: Keep test framework and utilities current

### When Code Changes
1. **Run affected tests**: Identify and run tests related to changed code
2. **Update test expectations**: Modify tests if behavior changes are intentional
3. **Add new tests**: Cover new functionality with appropriate tests
4. **Verify integrations**: Ensure changes don't break existing integrations

### Performance Monitoring
- Track test execution times
- Identify slow or timing-sensitive tests
- Optimize test setup and teardown
- Monitor for test reliability issues

## Examples

### Complete Test Examples

See the existing test files for comprehensive examples:
- `test_poc_api.py` - API endpoint testing
- `test_rag_api.py` - Framework integration
- `test_submission.py` - End-to-end workflow testing
- `test_core_modules.py` - Unit testing with mocks

### Quick Reference

```python
# Basic test structure
class TestMyFeature(SyntheverseTestCase):
    def get_category(self): return "integration"

    def test_feature(self):
        self.log_info("Testing feature")
        result = my_function()
        self.assertTrue(result["success"])
        self.add_metric("duration", result["time"])
```

Remember: Tests should be **real**, **documented**, **comprehensive**, and **successful**. Each test validates actual system behavior and provides clear feedback on functionality and performance.


