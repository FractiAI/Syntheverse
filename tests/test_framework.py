#!/usr/bin/env python3
"""
Syntheverse Test Framework
Standardized testing utilities and base classes for consistent test execution
"""

import sys
import os
import time
import json
import logging
import traceback
import functools
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import unittest

def retry_test(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0,
               exceptions: tuple = (Exception,)):
    """
    Decorator to retry test methods on failure

    Args:
        max_attempts: Maximum number of attempts
        delay: Initial delay between retries
        backoff: Backoff multiplier for delay
        exceptions: Tuple of exceptions to catch and retry
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            last_exception = None
            current_delay = delay

            for attempt in range(max_attempts):
                try:
                    # Record retry attempt in test result
                    if hasattr(self, 'test_result'):
                        self.test_result.retry_count = attempt
                        self.test_result.max_retries = max_attempts - 1

                    return func(self, *args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        self.log_warning(f"Test attempt {attempt + 1} failed: {e}. Retrying in {current_delay}s...")
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        self.log_error(f"Test failed after {max_attempts} attempts: {e}")
                        raise

            # This should never be reached, but just in case
            raise last_exception

        return wrapper
    return decorator

# Dependency Management Functions

def ensure_dependency(package_name: str, max_attempts: int = 3) -> bool:
    """
    Ensure a Python dependency is available, installing it if necessary.

    Args:
        package_name: Name of the Python package to check/install
        max_attempts: Maximum number of installation attempts

    Returns:
        bool: True if dependency is available after installation attempts

    Raises:
        RuntimeError: If dependency cannot be installed after all attempts
    """
    import subprocess
    import sys

    # First, try to import the package
    try:
        __import__(package_name.replace('-', '_'))
        return True
    except ImportError:
        pass

    print(f"📦 Installing missing dependency: {package_name}")

    for attempt in range(max_attempts):
        try:
            # Try to install the package (use --user to avoid externally managed environment issues)
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '--user', package_name],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                # Try to import again
                try:
                    __import__(package_name.replace('-', '_'))
                    print(f"✅ Successfully installed and imported {package_name}")
                    return True
                except ImportError as e:
                    if attempt == max_attempts - 1:
                        raise RuntimeError(f"Failed to import {package_name} after installation: {e}")
                    continue
            else:
                error_msg = result.stderr.strip()
                if attempt == max_attempts - 1:
                    raise RuntimeError(f"Failed to install {package_name}: {error_msg}")

        except subprocess.TimeoutExpired:
            if attempt == max_attempts - 1:
                raise RuntimeError(f"Installation of {package_name} timed out")
        except Exception as e:
            if attempt == max_attempts - 1:
                raise RuntimeError(f"Error installing {package_name}: {e}")

        print(f"⚠️ Installation attempt {attempt + 1} failed, retrying...")

    return False

def ensure_service_running(service_name: str, startup_command: list = None, health_url: str = None,
                          startup_timeout: int = 60, health_check_interval: float = 2.0, startup_cwd: str = None) -> bool:
    """
    Ensure a service is running, starting it if necessary.

    Args:
        service_name: Name of the service to check/start
        startup_command: Command to start the service (if None, assumes service is already running)
        health_url: URL to check for service health
        startup_timeout: Maximum time to wait for service to start
        health_check_interval: Time between health checks

    Returns:
        bool: True if service is running and healthy

    Raises:
        RuntimeError: If service cannot be started or fails health checks
    """
    import subprocess
    import time
    import requests
    from pathlib import Path

    # First, check if service is already healthy
    if health_url:
        try:
            response = requests.get(health_url, timeout=5)
            if response.status_code == 200:
                print(f"✅ Service {service_name} is already running and healthy")
                return True
        except:
            pass

    # If no startup command provided, assume service should be running
    if not startup_command:
        raise RuntimeError(f"Service {service_name} is not running and no startup command provided")

    print(f"🚀 Starting service: {service_name}")

    try:
        # Start the service
        project_root = Path(__file__).parent.parent
        working_dir = startup_cwd if startup_cwd else project_root
        process = subprocess.Popen(
            startup_command,
            cwd=working_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True
        )

        # Wait for service to become healthy
        start_time = time.time()
        while time.time() - start_time < startup_timeout:
            if health_url:
                try:
                    response = requests.get(health_url, timeout=2)
                    if response.status_code == 200:
                        print(f"✅ Service {service_name} started successfully")
                        return True
                except:
                    pass

            time.sleep(health_check_interval)

        # If we get here, service failed to start
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()

        raise RuntimeError(f"Service {service_name} failed to start within {startup_timeout} seconds")

    except Exception as e:
        raise RuntimeError(f"Failed to start service {service_name}: {e}")

def ensure_module_available(module_name: str, package_name: str = None, max_attempts: int = 3) -> bool:
    """
    Ensure a Python module is available, installing the package if necessary.

    Args:
        module_name: Name of the Python module to check
        package_name: Name of the package to install (defaults to module_name)
        max_attempts: Maximum number of installation attempts

    Returns:
        bool: True if module is available after installation attempts

    Raises:
        RuntimeError: If module cannot be made available after all attempts
    """
    if package_name is None:
        package_name = module_name

    # Try to import the module
    try:
        __import__(module_name)
        return True
    except ImportError:
        pass

    # Module not available, try to install the package
    return ensure_dependency(package_name, max_attempts)

class TestResult:
    """Standardized test result container with enhanced reporting"""

    def __init__(self, test_name: str, category: str = "general"):
        self.test_name = test_name
        self.category = category
        self.start_time = None
        self.end_time = None
        self.success = False
        self.error_message = None
        self.output = []
        self.metrics = {}
        self.retry_count = 0
        self.max_retries = 0
        self.exception_details = None

    def start(self):
        """Mark test start time"""
        self.start_time = time.time()

    def end(self, success: bool = True, error_message: str = None, exception: Exception = None):
        """Mark test end time and result with enhanced error details"""
        self.end_time = time.time()
        self.success = success
        self.error_message = error_message
        if exception:
            self.exception_details = {
                "type": type(exception).__name__,
                "message": str(exception),
                "traceback": traceback.format_exception(type(exception), exception, exception.__traceback__)
            }

    @property
    def duration(self) -> float:
        """Get test duration in seconds"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0

    def add_output(self, message: str, level: str = "INFO"):
        """Add output message"""
        timestamp = datetime.now().isoformat()
        self.output.append({
            "timestamp": timestamp,
            "level": level,
            "message": message
        })

    def add_metric(self, key: str, value: Any):
        """Add performance metric"""
        self.metrics[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization with enhanced details"""
        result = {
            "test_name": self.test_name,
            "category": self.category,
            "success": self.success,
            "duration": self.duration,
            "error_message": self.error_message,
            "output": self.output,
            "metrics": self.metrics,
            "timestamp": datetime.now().isoformat(),
            "retry_count": self.retry_count,
            "max_retries": self.max_retries
        }
        if self.exception_details:
            result["exception"] = self.exception_details
        return result

class SyntheverseTestCase(unittest.TestCase):
    """Base test case class with standardized logging and reporting"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_result = None
        self.logger = None

    def setUp(self):
        """Set up test with standardized logging"""
        super().setUp()

        # Create test result
        self.test_result = TestResult(
            test_name=self._testMethodName,
            category=self.get_category()
        )
        self.test_result.start()

        # Set up logger
        self.logger = logging.getLogger(f"{self.__class__.__name__}.{self._testMethodName}")
        self.logger.setLevel(logging.DEBUG)

        # Remove existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        # Add console handler with colored output
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def tearDown(self):
        """Clean up and record test results with enhanced error reporting"""
        success = self._outcome.success
        error_message = None
        exception = None

        if not success:
            # Get error details with enhanced reporting
            if hasattr(self._outcome, 'errors') and self._outcome.errors:
                error_message = str(self._outcome.errors[0][1])
                # Try to extract the actual exception
                try:
                    exception = self._outcome.errors[0][1]
                except:
                    pass

        self.test_result.end(success=success, error_message=error_message, exception=exception)

        # Log final result with enhanced formatting
        status = "PASSED" if success else "FAILED"
        duration = self.test_result.duration
        retry_info = ""
        if self.test_result.retry_count > 0:
            retry_info = f" (retry {self.test_result.retry_count}/{self.test_result.max_retries})"

        print(f"\n{'='*70}")
        print(f"TEST RESULT: {self._testMethodName} - {status}{retry_info}")
        print(f"Duration: {duration:.2f}s")
        print(f"Category: {self.get_category()}")

        if error_message:
            print(f"Error: {error_message}")
            # Use enhanced error reporting
            if exception:
                ErrorReporting.log_test_error(self._testMethodName, exception, self.logger)

        # Show metrics if available
        if self.test_result.metrics:
            print("Metrics:")
            for key, value in self.test_result.metrics.items():
                if isinstance(value, float):
                    print(f"  {key}: {value:.2f}")
                else:
                    print(f"  {key}: {value}")

        print(f"{'='*70}")

        super().tearDown()

    def get_category(self) -> str:
        """Get test category - override in subclasses"""
        return "general"

    def log_info(self, message: str):
        """Log info message"""
        self.logger.info(message)
        self.test_result.add_output(message, "INFO")

    def log_error(self, message: str):
        """Log error message"""
        self.logger.error(message)
        self.test_result.add_output(message, "ERROR")

    def log_warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
        self.test_result.add_output(message, "WARNING")

    def add_metric(self, key: str, value: Any):
        """Add performance metric"""
        self.test_result.add_metric(key, value)

    def ensure_services(self, services: List[str] = None):
        """Ensure required services are running with enhanced diagnostics"""
        TestFixtures.ensure_services_running(services)

    def enable_retries(self, max_attempts: int = 3, delay: float = 1.0):
        """Enable retry mechanism for this test class"""
        self._retry_config = {
            'max_attempts': max_attempts,
            'delay': delay
        }

    def create_test_contribution(self, title: str = None, contributor: str = None):
        """Create a test contribution for testing"""
        return TestFixtures.create_test_contribution(title, contributor)

    def cleanup_files(self, file_paths: List[str]):
        """Clean up test files"""
        TestFixtures.cleanup_test_files(file_paths)

    def ensure_dependency(self, package_name: str, max_attempts: int = 3):
        """Ensure a Python dependency is available, installing it if necessary"""
        return ensure_dependency(package_name, max_attempts)

    def ensure_service(self, service_name: str, startup_command: list = None, health_url: str = None,
                      startup_timeout: int = 60, health_check_interval: float = 2.0):
        """Ensure a service is running, starting it if necessary"""
        return ensure_service_running(service_name, startup_command, health_url,
                                     startup_timeout, health_check_interval)

    def ensure_module(self, module_name: str, package_name: str = None, max_attempts: int = 3):
        """Ensure a Python module is available, installing the package if necessary"""
        return ensure_module_available(module_name, package_name, max_attempts)

class TestConfig:
    """Test configuration management"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.test_dir = Path(__file__).parent
        self.config_file = self.test_dir / "test_config.json"

        # Default configuration
        self.config = {
            "api_urls": {
                "poc_api": "http://localhost:5001",
                "rag_api": "http://localhost:8000",
                "frontend": "http://localhost:3001",
                "legacy_ui": "http://localhost:5000"
            },
            "timeouts": {
                "api_call": 30,
                "page_load": 10,
                "test_overall": 300
            },
            "test_data": {
                "sample_pdf": "sample_contribution.pdf",
                "test_contributor": "test-researcher-001",
                "test_category": "scientific"
            }
        }

        self.load_config()

    def load_config(self):
        """Load configuration from file if it exists"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                    self.config.update(file_config)
            except Exception as e:
                print(f"Warning: Could not load test config: {e}")

    def save_config(self):
        """Save current configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def get(self, key: str, default=None):
        """Get configuration value"""
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

# Global test configuration instance
test_config = TestConfig()

class TestFixtures:
    """Common test fixtures and setup utilities"""

    @staticmethod
    def ensure_services_running(services_to_check: List[str] = None):
        """Ensure required services are running before tests"""
        if services_to_check is None:
            services_to_check = ["poc_api", "rag_api", "frontend"]

        unavailable = []

        for service in services_to_check:
            url = test_config.get(f"api_urls.{service}")
            if url:
                healthy, _ = TestUtils.check_service_health(url, timeout=5)
                if not healthy:
                    unavailable.append(service)

        if unavailable:
            raise RuntimeError(f"Required services not available: {', '.join(unavailable)}")

    @staticmethod
    def generate_test_pdf():
        """Generate a simple test PDF file for testing"""
        import tempfile
        import os

        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter

            # Create temporary PDF
            fd, pdf_path = tempfile.mkstemp(suffix='.pdf')
            os.close(fd)

            c = canvas.Canvas(pdf_path, pagesize=letter)
            c.drawString(100, 750, "Test PDF for Syntheverse PoC")
            c.drawString(100, 730, "This is a test document for evaluation.")
            c.drawString(100, 710, "Generated by test framework.")
            c.save()

            return pdf_path
        except ImportError:
            # Fallback: create a text file that looks like a PDF
            fd, pdf_path = tempfile.mkstemp(suffix='.pdf')
            with os.fdopen(fd, 'w') as f:
                f.write("%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n")
            return pdf_path

    @staticmethod
    def cleanup_test_files(file_paths: List[str]):
        """Clean up test files"""
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Warning: Could not clean up {file_path}: {e}")

    @staticmethod
    def create_test_contribution(title: str = None, contributor: str = None, **overrides):
        """Create a test contribution data structure with optional overrides"""
        base_contribution = {
            "title": title or test_config.get("test_data.sample_title"),
            "content": test_config.get("test_data.sample_content", "This is a test research paper on fractal structures in cognitive systems."),
            "category": test_config.get("test_data.sample_category"),
            "contributor": contributor or test_config.get("test_data.sample_contributor"),
            "email": test_config.get("test_data.test_email"),
            "timestamp": datetime.now().isoformat(),
            "pdf_path": None,
            "submission_hash": None
        }

        # Apply overrides
        base_contribution.update(overrides)
        return base_contribution


class ErrorReporting:
    """Error reporting utilities with enhanced diagnostics"""

    @staticmethod
    def format_exception_chain(exc: Exception) -> str:
        """Format a complete exception chain for reporting"""
        import traceback

        tb_lines = traceback.format_exception(type(exc), exc, exc.__traceback__)
        return "".join(tb_lines)

    @staticmethod
    def create_error_report(test_name: str, exception: Exception, context: dict = None) -> dict:
        """Create a comprehensive error report with system information"""
        error_report = {
            "test_name": test_name,
            "error_type": type(exception).__name__,
            "error_message": str(exception),
            "traceback": ErrorReporting.format_exception_chain(exception),
            "timestamp": datetime.now().isoformat(),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "platform": sys.platform
        }

        if context:
            error_report["context"] = context

        return error_report

    @staticmethod
    def log_test_error(test_name: str, exception: Exception, logger=None):
        """Log a test error with comprehensive details and suggestions"""
        error_report = ErrorReporting.create_error_report(test_name, exception)

        error_msg = f"❌ Test {test_name} failed: {error_report['error_message']}"

        if logger:
            logger.error(error_msg)
            logger.error(f"Traceback: {error_report['traceback']}")
        else:
            print(error_msg)
            print(f"   Traceback: {error_report['traceback'][:500]}...")

        # Add helpful suggestions based on error type
        if "ImportError" in error_report['error_type']:
            print("   💡 Suggestion: Check if required modules are installed or paths are correct")
        elif "ConnectionError" in error_report['error_type'] or "Timeout" in error_report['error_type']:
            print("   💡 Suggestion: Check if services are running and network connectivity")
        elif "AssertionError" in error_report['error_type']:
            print("   💡 Suggestion: Review test assertions and expected vs actual values")

    @staticmethod
    def analyze_error_patterns(error_reports: list) -> dict:
        """Analyze error patterns across multiple test failures"""
        patterns = {
            "error_types": {},
            "common_messages": {},
            "temporal_distribution": {}
        }

        for report in error_reports:
            error_type = report.get("error_type", "Unknown")
            error_msg = report.get("error_message", "")

            patterns["error_types"][error_type] = patterns["error_types"].get(error_type, 0) + 1

            # Extract common message patterns (first 50 chars)
            msg_key = error_msg[:50] + "..." if len(error_msg) > 50 else error_msg
            patterns["common_messages"][msg_key] = patterns["common_messages"].get(msg_key, 0) + 1

        return patterns

class TestUtils:
    """Utility functions for tests"""

    @staticmethod
    def check_service_health(url: str, timeout: int = 10, retries: int = 2) -> tuple[bool, str]:
        """Check if a service is healthy with retry mechanism"""
        import time

        # For frontend (Next.js), check root URL; for APIs, check /health
        check_url = url if "localhost:3001" in url else f"{url}/health"

        for attempt in range(retries + 1):
            try:
                import requests
                response = requests.get(check_url, timeout=timeout, allow_redirects=True)
                # Accept 200 for APIs, and redirects (3xx) for Next.js frontend
                if response.status_code == 200 or (response.status_code >= 300 and response.status_code < 400):
                    return True, "Service is healthy"
                else:
                    status_msg = f"Service returned status {response.status_code}"
                    if attempt < retries:
                        time.sleep(0.5)
                        continue
                    return False, status_msg
            except requests.exceptions.RequestException as e:
                error_msg = f"Service unreachable: {e}"
                if attempt < retries:
                    time.sleep(0.5)
                    continue
                return False, error_msg
            except ImportError:
                return False, "requests library not available"

        return False, "Service health check failed after retries"

    @staticmethod
    def wait_for_service(url: str, timeout: int = 30) -> bool:
        """Wait for a service to become available"""
        import time

        start_time = time.time()
        while time.time() - start_time < timeout:
            healthy, _ = TestUtils.check_service_health(url, timeout=5)
            if healthy:
                return True
            time.sleep(2)

        return False

    @staticmethod
    def print_test_header(test_name: str, description: str = ""):
        """Print standardized test header"""
        print(f"\n{'='*70}")
        print(f"🧪 {test_name.upper()}")
        if description:
            print(f"📝 {description}")
        print(f"{'='*70}")

    @staticmethod
    def run_tests_parallel(test_loader, test_suite, max_workers: int = 4):
        """Run tests in parallel using multiprocessing"""
        import concurrent.futures
        import multiprocessing

        # Convert test suite to list of individual test cases
        test_cases = []
        for test_group in test_suite:
            for test_case in test_group:
                test_cases.append(test_case)

        results = []

        def run_single_test(test_case):
            """Run a single test and return its result"""
            try:
                result = unittest.TestResult()
                test_case.run(result)
                return {
                    'test': test_case,
                    'result': result,
                    'success': result.wasSuccessful(),
                    'errors': len(result.errors),
                    'failures': len(result.failures)
                }
            except Exception as e:
                return {
                    'test': test_case,
                    'result': None,
                    'success': False,
                    'errors': 1,
                    'failures': 0,
                    'exception': str(e)
                }

        # Run tests in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_test = {executor.submit(run_single_test, test): test for test in test_cases}
            for future in concurrent.futures.as_completed(future_to_test):
                result = future.result()
                results.append(result)

        return results

    @staticmethod
    def validate_json_data(data: dict, schema: dict) -> tuple[bool, str]:
        """Validate JSON data against a simple schema"""
        try:
            for key, expected_type in schema.items():
                if key not in data:
                    return False, f"Missing required key: {key}"

                actual_value = data[key]
                if not isinstance(actual_value, expected_type):
                    return False, f"Key '{key}' has wrong type. Expected {expected_type.__name__}, got {type(actual_value).__name__}"

            return True, "Validation successful"
        except Exception as e:
            return False, f"Validation error: {e}"

    @staticmethod
    def generate_performance_report(metrics: list) -> dict:
        """Generate a performance analysis report from test metrics"""
        if not metrics:
            return {"error": "No metrics provided"}

        report = {
            "summary": {},
            "details": {},
            "recommendations": []
        }

        # Analyze response times
        response_times = [m.get("response_time", 0) for m in metrics if "response_time" in m]
        if response_times:
            report["summary"]["avg_response_time"] = sum(response_times) / len(response_times)
            report["summary"]["max_response_time"] = max(response_times)
            report["summary"]["min_response_time"] = min(response_times)

            # Performance recommendations
            avg_time = report["summary"]["avg_response_time"]
            if avg_time > 5.0:
                report["recommendations"].append("Consider optimizing API response times (>5s average)")
            elif avg_time > 2.0:
                report["recommendations"].append("Response times are acceptable but could be improved")

        # Analyze memory usage
        memory_usage = [m.get("memory_mb", 0) for m in metrics if "memory_mb" in m]
        if memory_usage:
            report["summary"]["avg_memory_usage"] = sum(memory_usage) / len(memory_usage)
            report["summary"]["peak_memory_usage"] = max(memory_usage)

        return report

    @staticmethod
    def create_test_data_generator(template: dict, variations: dict = None):
        """Create a test data generator with variations"""
        def generator(**overrides):
            data = template.copy()
            data.update(overrides)

            if variations:
                for key, variation_func in variations.items():
                    if callable(variation_func):
                        data[key] = variation_func()

            return data

        return generator

    @staticmethod
    def print_test_summary(results: List[TestResult]):
        """Print comprehensive test summary with metrics and parallel execution support"""
        total = len(results)
        passed = sum(1 for r in results if r.success)
        failed = total - passed
        skipped = sum(1 for r in results if hasattr(r, 'skipped') and r.skipped)

        # Calculate retry statistics
        total_retries = sum(getattr(r, 'retry_count', 0) for r in results)
        avg_retries = total_retries / total if total > 0 else 0

        print(f"\n{'='*70}")
        print("📊 TEST SUMMARY")
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Skipped: {skipped}")
        print(f"Total Retries: {total_retries} (avg: {avg_retries:.1f} per test)")

        if total > 0:
            success_rate = (passed / total) * 100
            print(f"Success Rate: {success_rate:.1f}%")

        # Calculate average duration
        if results:
            avg_duration = sum(r.duration for r in results) / len(results)
            total_duration = sum(r.duration for r in results)
            print(f"Average Duration: {avg_duration:.2f}s")
            print(f"Total Duration: {total_duration:.2f}s")

        # Show failed tests with details
        if failed > 0:
            print("\n❌ Failed Tests:")
            for result in results:
                if not result.success:
                    print(f"   - {result.test_name}: {result.error_message}")
                    if result.duration > 0:
                        print(f"     Duration: {result.duration:.2f}s")
                    if hasattr(result, 'retry_count') and result.retry_count > 0:
                        print(f"     Retries: {result.retry_count}")

        # Show performance metrics if available
        metrics_found = False
        for result in results:
            if result.metrics:
                if not metrics_found:
                    print("\n📈 Performance Metrics:")
                    metrics_found = True
                print(f"   {result.test_name}:")
                for key, value in result.metrics.items():
                    if isinstance(value, float):
                        print(f"     {key}: {value:.2f}")
                    else:
                        print(f"     {key}: {value}")

        print(f"{'='*70}")


class APITestCase(SyntheverseTestCase):
    """Base test case for API-related tests with service availability checking"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.services_available = {}

    def setUp(self):
        """Set up API test with service availability checking"""
        super().setUp()

        # Check service availability for common services
        services_to_check = ["poc_api", "rag_api", "frontend"]
        for service in services_to_check:
            url = test_config.get(f"api_urls.{service}")
            if url:
                healthy, status = TestUtils.check_service_health(url, timeout=5)
                self.services_available[service] = healthy
                if not healthy:
                    self.log_warning(f"{service} not available: {status}")
            else:
                self.services_available[service] = False

    def require_service(self, service_name: str):
        """Require a specific service to be available for this test"""
        if not self.services_available.get(service_name, False):
            self.fail(f"{service_name} service not available - tests should ensure services are started")

    def get_service_url(self, service: str) -> str:
        """Get the URL for a service"""
        return test_config.get(f"api_urls.{service}", "")

    def make_api_request(self, service: str, endpoint: str, method: str = "GET",
                        expected_status: int = 200, **kwargs) -> Optional[Dict]:
        """Make an API request with error handling and status validation"""
        try:
            import requests
            url = f"{self.get_service_url(service)}{endpoint}"

            # Set default timeout if not provided
            timeout = kwargs.pop('timeout', 10)

            if method.upper() == "GET":
                response = requests.get(url, timeout=timeout, **kwargs)
            elif method.upper() == "POST":
                response = requests.post(url, timeout=timeout, **kwargs)
            elif method.upper() == "PUT":
                response = requests.put(url, timeout=timeout, **kwargs)
            elif method.upper() == "DELETE":
                response = requests.delete(url, timeout=timeout, **kwargs)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            # Add response time metric
            self.add_metric(f"{service}_api_response_time", response.elapsed.total_seconds())

            if response.status_code == expected_status:
                try:
                    return response.json()
                except ValueError:
                    # Response is not JSON
                    return {"text_response": response.text}
            else:
                self.log_warning(f"API request failed: {response.status_code} (expected {expected_status}) - {response.text}")
                return {"error": f"HTTP {response.status_code}", "response": response.text}

        except Exception as e:
            self.log_warning(f"API request exception: {e}")
            return {"error": str(e)}

    def assert_api_response_structure(self, response: dict, required_fields: list, response_name: str = "API response"):
        """Assert that an API response has the required structure"""
        self.assertIsInstance(response, dict, f"{response_name} should be a dictionary")

        for field in required_fields:
            self.assertIn(field, response, f"{response_name} missing required field: {field}")

    def make_api_request_with_retries(self, service: str, endpoint: str, method: str = "GET",
                                      max_retries: int = 3, **kwargs) -> Optional[Dict]:
        """Test an API endpoint with retry logic"""
        import time

        for attempt in range(max_retries):
            result = self.make_api_request(service, endpoint, method, **kwargs)
            if result and "error" not in result:
                return result

            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                self.log_info(f"API call failed, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)

        self.fail(f"API endpoint {endpoint} failed after {max_retries} attempts")
        return None


class DataTestCase(SyntheverseTestCase):
    """Base test case for data-related tests with temporary file management"""

    def setUp(self):
        """Set up data test with temporary directory"""
        super().setUp()

        # Create temporary directory for testing
        import tempfile
        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_data_dir = self.temp_dir / "test_data"
        self.test_data_dir.mkdir(exist_ok=True)

    def tearDown(self):
        """Clean up temporary files"""
        super().tearDown()

        # Clean up temporary directory
        if hasattr(self, 'temp_dir') and self.temp_dir.exists():
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_temp_file(self, content: str = "", filename: str = None, suffix: str = ".txt") -> Path:
        """Create a temporary file with content"""
        if filename is None:
            import tempfile
            fd, filename = tempfile.mkstemp(suffix=suffix, dir=self.test_data_dir)
            os.close(fd)

        file_path = self.test_data_dir / filename
        with open(file_path, 'w') as f:
            f.write(content)

        return file_path


def main():
    """Run test framework validation"""
    print("Syntheverse Test Framework Validation")
    print("="*50)

    # Test configuration loading
    config = TestConfig()
    print(f"✅ Config loaded: {len(config.config)} settings")

    # Test service health check
    print("\nTesting service health checks...")
    services = [
        ("PoC API", config.get("api_urls.poc_api")),
        ("RAG API", config.get("api_urls.rag_api")),
        ("Frontend", config.get("api_urls.frontend")),
    ]

    for name, url in services:
        healthy, status = TestUtils.check_service_health(url)
        status_icon = "✅" if healthy else "❌"
        print(f"{status_icon} {name}: {status}")

    print("\n✅ Test framework validation complete")

if __name__ == "__main__":
    main()
