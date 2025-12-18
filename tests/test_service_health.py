#!/usr/bin/env python3
"""
Unit tests for the Service Health Check Module
Tests health checking for all Syntheverse services
"""

import unittest
import requests
import time
import threading
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from scripts.startup.service_health import (
    ServiceHealthChecker,
    ServiceInfo,
    HealthCheckResult,
    ServiceStatus,
    HealthCheckType,
    ErrorCategory,
    CircuitBreakerState,
    ServiceMetrics,
    health_checker,
    check_service_health,
    check_all_services,
    get_service_status,
    wait_for_service,
    wait_for_all_services,
    print_health_report,
    add_service_dependency,
    get_startup_order,
    get_service_metrics
)

class TestServiceHealthChecker(unittest.TestCase):
    """Test cases for ServiceHealthChecker class"""

    def setUp(self):
        """Set up test fixtures"""
        self.health_checker = ServiceHealthChecker()

    def test_initialization(self):
        """Test ServiceHealthChecker initialization"""
        checker = ServiceHealthChecker()
        self.assertIsNotNone(checker.services)
        self.assertIn('poc_api', checker.services)
        self.assertIn('rag_api', checker.services)
        self.assertIn('anvil', checker.services)

    def test_check_service_health_unknown_service(self):
        """Test checking health of unknown service"""
        result = self.health_checker.check_service_health('unknown_service')

        self.assertEqual(result.status, ServiceStatus.UNKNOWN)
        self.assertIn('not defined', result.error_message)

    @patch('requests.get')
    def test_check_http_service_healthy(self, mock_get):
        """Test checking health of healthy HTTP service"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'OK'
        mock_get.return_value = mock_response

        service_info = ServiceInfo(name='Test API', port=5001, endpoint='/health')
        result = self.health_checker._check_http_health(service_info, 0.0)

        self.assertEqual(result.status, ServiceStatus.HEALTHY)
        self.assertEqual(result.status_code, 200)
        self.assertIsNone(result.error_message)

    @patch('requests.get')
    def test_check_http_service_unhealthy(self, mock_get):
        """Test checking health of unhealthy HTTP service"""
        # Mock error response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.content = b'Internal Server Error'
        mock_get.return_value = mock_response

        service_info = ServiceInfo(name='Test API', port=5001, endpoint='/health')
        result = self.health_checker._check_http_health(service_info, 0.0)

        self.assertEqual(result.status, ServiceStatus.UNHEALTHY)
        self.assertEqual(result.status_code, 500)
        self.assertIn('Unexpected status code', result.error_message)

    @patch('requests.get')
    def test_check_http_service_connection_error(self, mock_get):
        """Test checking health with connection error"""
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")

        service_info = ServiceInfo(name='Test API', port=5001, endpoint='/health')
        result = self.health_checker._check_http_health(service_info, 0.0)

        self.assertEqual(result.status, ServiceStatus.UNHEALTHY)
        self.assertIn('Connection refused', result.error_message)

    @patch('requests.get')
    def test_check_http_service_timeout(self, mock_get):
        """Test checking health with timeout"""
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")

        service_info = ServiceInfo(name='Test API', port=5001, endpoint='/health')
        result = self.health_checker._check_http_health(service_info, 0.0)

        self.assertEqual(result.status, ServiceStatus.STARTING)
        self.assertIn('Request timeout', result.error_message)

    @patch('requests.post')
    def test_check_anvil_healthy(self, mock_post):
        """Test checking health of healthy Anvil service"""
        # Mock successful RPC responses
        def mock_rpc_response(*args, **kwargs):
            request_data = kwargs.get('json', {})
            method = request_data.get('method')

            mock_response = MagicMock()
            mock_response.status_code = 200

            if method == 'eth_blockNumber':
                mock_response.json.return_value = {'result': '0x64'}  # 100 in hex
            elif method == 'eth_accounts':
                mock_response.json.return_value = {'result': ['0x123', '0x456']}  # 2 accounts

            return mock_response

        mock_post.side_effect = mock_rpc_response

        service_info = ServiceInfo(name='Anvil', port=8545, endpoint=None)
        result = self.health_checker._check_anvil_health(service_info, 0.0)

        self.assertEqual(result.status, ServiceStatus.HEALTHY)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.details['block_number'], 100)
        self.assertEqual(result.details['accounts'], 2)

    @patch('requests.post')
    def test_check_anvil_unhealthy(self, mock_post):
        """Test checking health of unhealthy Anvil service"""
        # Mock invalid response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'error': 'Invalid request'}
        mock_post.return_value = mock_response

        service_info = ServiceInfo(name='Anvil', port=8545, endpoint=None)
        result = self.health_checker._check_anvil_health(service_info, 0.0)

        self.assertEqual(result.status, ServiceStatus.UNHEALTHY)
        self.assertIn('Invalid RPC response', result.error_message)

    @patch('requests.post')
    def test_check_anvil_connection_error(self, mock_post):
        """Test checking Anvil health with connection error"""
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection refused")

        service_info = ServiceInfo(name='Anvil', port=8545, endpoint=None)
        result = self.health_checker._check_anvil_health(service_info, 0.0)

        self.assertEqual(result.status, ServiceStatus.UNHEALTHY)
        self.assertIn('Connection refused', result.error_message)

    def test_check_all_services(self):
        """Test checking health of all services"""
        # This will test with real services, but they likely won't be running
        # So we just verify the method returns the expected structure
        results = self.health_checker.check_all_services()

        self.assertIsInstance(results, dict)
        expected_services = ['poc_api', 'rag_api', 'nextjs_frontend', 'legacy_web_ui', 'anvil']
        for service in expected_services:
            self.assertIn(service, results)
            self.assertIsInstance(results[service], HealthCheckResult)

    def test_get_service_status(self):
        """Test getting detailed service status"""
        status = self.health_checker.get_service_status('poc_api')

        expected_keys = ['name', 'port', 'status', 'response_time', 'description']
        for key in expected_keys:
            self.assertIn(key, status)

        self.assertEqual(status['name'], 'PoC API')
        self.assertEqual(status['port'], 5001)

    @patch.object(ServiceHealthChecker, 'check_service_health')
    def test_wait_for_service_success(self, mock_check):
        """Test successful wait for service"""
        # Service becomes healthy on second check
        mock_result1 = HealthCheckResult(
            service=ServiceInfo(name='Test', port=5001, endpoint='/health'),
            status=ServiceStatus.STARTING,
            response_time=0.1
        )
        mock_result2 = HealthCheckResult(
            service=ServiceInfo(name='Test', port=5001, endpoint='/health'),
            status=ServiceStatus.HEALTHY,
            response_time=0.1
        )

        mock_check.side_effect = [mock_result1, mock_result2]

        result = self.health_checker.wait_for_service('poc_api', timeout=5, interval=1)

        self.assertTrue(result)

    @patch.object(ServiceHealthChecker, 'check_service_health')
    def test_wait_for_service_timeout(self, mock_check):
        """Test wait for service timeout"""
        mock_result = HealthCheckResult(
            service=ServiceInfo(name='Test', port=5001, endpoint='/health'),
            status=ServiceStatus.UNHEALTHY,
            response_time=0.1,
            error_message='Connection refused'
        )

        mock_check.return_value = mock_result

        result = self.health_checker.wait_for_service('poc_api', timeout=2, interval=1)

        self.assertFalse(result)

    @patch('builtins.print')
    def test_print_health_report(self, mock_print):
        """Test printing health report"""
        # Create mock results
        results = {
            'poc_api': HealthCheckResult(
                service=ServiceInfo(name='PoC API', port=5001, endpoint='/health'),
                status=ServiceStatus.HEALTHY,
                response_time=0.5,
                status_code=200
            ),
            'anvil': HealthCheckResult(
                service=ServiceInfo(name='Anvil', port=8545, endpoint=None),
                status=ServiceStatus.UNHEALTHY,
                response_time=1.0,
                error_message='Connection refused'
            )
        }

        self.health_checker.print_health_report(results)

        # Verify print was called (exact output verification would be complex)
        self.assertTrue(mock_print.called)

class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions"""

    @patch.object(health_checker, 'check_service_health')
    def test_check_service_health_convenience(self, mock_method):
        """Test convenience function calls the method"""
        mock_result = HealthCheckResult(
            service=ServiceInfo(name='Test', port=5001, endpoint='/health'),
            status=ServiceStatus.HEALTHY,
            response_time=0.5
        )
        mock_method.return_value = mock_result

        result = check_service_health('poc_api')

        self.assertEqual(result.status, ServiceStatus.HEALTHY)
        mock_method.assert_called_once_with('poc_api')

    @patch.object(health_checker, 'check_all_services')
    def test_check_all_services_convenience(self, mock_method):
        """Test convenience function calls the method"""
        mock_method.return_value = {}

        result = check_all_services()

        self.assertEqual(result, {})
        mock_method.assert_called_once()

    @patch.object(health_checker, 'get_service_status')
    def test_get_service_status_convenience(self, mock_method):
        """Test convenience function calls the method"""
        mock_method.return_value = {'status': 'healthy'}

        result = get_service_status('poc_api')

        self.assertEqual(result['status'], 'healthy')
        mock_method.assert_called_once_with('poc_api')

    @patch.object(health_checker, 'wait_for_service')
    def test_wait_for_service_convenience(self, mock_method):
        """Test convenience function calls the method"""
        mock_method.return_value = True

        result = wait_for_service('poc_api', timeout=30)

        self.assertTrue(result)
        mock_method.assert_called_once_with('poc_api', 30)

    @patch.object(health_checker, 'wait_for_all_services')
    def test_wait_for_all_services_convenience(self, mock_method):
        """Test convenience function calls the method"""
        mock_method.return_value = {'poc_api': True, 'anvil': False}

        result = wait_for_all_services(timeout=60)

        self.assertEqual(result['poc_api'], True)
        self.assertEqual(result['anvil'], False)
        mock_method.assert_called_once_with(60)

    @patch.object(health_checker, 'print_health_report')
    def test_print_health_report_convenience(self, mock_method):
        """Test convenience function calls the method"""
        print_health_report()

        mock_method.assert_called_once_with(None)

class TestEnhancedServiceHealth(unittest.TestCase):
    """Test cases for enhanced service health features"""

    def setUp(self):
        """Set up test fixtures"""
        self.health_checker = ServiceHealthChecker()

    def test_service_dependency_management(self):
        """Test service dependency management"""
        # Add a dependency
        self.health_checker.add_dependency('frontend', 'new_service')

        # Check that dependency was added
        dependencies = self.health_checker._dependency_graph.get('frontend', set())
        self.assertIn('new_service', dependencies)

        # Get startup order
        order = self.health_checker.get_startup_order()
        self.assertIsInstance(order, list)
        self.assertIn('frontend', order)
        self.assertIn('new_service', order)

    def test_circuit_breaker_functionality(self):
        """Test circuit breaker functionality"""
        service_name = 'test_service'

        # Initially closed
        cb = self.health_checker._get_circuit_breaker(service_name)
        self.assertEqual(cb.state, "closed")
        self.assertEqual(cb.failures, 0)

        # Simulate failures
        for i in range(3):
            self.health_checker._update_circuit_breaker(service_name, False)

        # Should be open after 3 failures
        cb = self.health_checker._get_circuit_breaker(service_name)
        self.assertEqual(cb.state, "open")
        self.assertEqual(cb.failures, 3)

        # Success should close it
        self.health_checker._update_circuit_breaker(service_name, True)
        cb = self.health_checker._get_circuit_breaker(service_name)
        self.assertEqual(cb.state, "closed")
        self.assertEqual(cb.failures, 0)

    def test_circuit_breaker_open_check(self):
        """Test circuit breaker open state checking"""
        service_name = 'test_service'

        # Circuit should not be open initially
        self.assertFalse(self.health_checker._is_circuit_open(service_name))

        # Make it open
        for i in range(3):
            self.health_checker._update_circuit_breaker(service_name, False)

        # Should be open
        self.assertTrue(self.health_checker._is_circuit_open(service_name))

    def test_adaptive_health_check_intervals(self):
        """Test adaptive health check interval calculation"""
        service_name = 'test_service'

        # No metrics - should return base interval
        interval = self.health_checker._get_adaptive_interval(service_name)
        self.assertEqual(interval, self.health_checker._base_interval)

        # Add stable service metrics
        self.health_checker._metrics[service_name] = ServiceMetrics(
            service_name=service_name,
            total_checks=100,
            healthy_checks=95,  # 95% uptime
            consecutive_failures=0
        )

        # Should have longer interval for stable service
        interval = self.health_checker._get_adaptive_interval(service_name)
        self.assertGreater(interval, self.health_checker._base_interval)

        # Add unstable service metrics
        self.health_checker._metrics[service_name].uptime_percentage = 0.7  # 70% uptime
        self.health_checker._metrics[service_name].consecutive_failures = 2

        # Should have shorter interval for unstable service
        interval = self.health_checker._get_adaptive_interval(service_name)
        self.assertLess(interval, self.health_checker._base_interval)

    def test_error_categorization(self):
        """Test error categorization"""
        # Timeout error
        timeout_error = requests.exceptions.Timeout("Request timed out")
        category = self.health_checker._categorize_error(timeout_error, ServiceInfo("test", 5000, "/"))
        self.assertEqual(category, ErrorCategory.TIMEOUT)

        # Connection error
        conn_error = requests.exceptions.ConnectionError("Connection refused")
        category = self.health_checker._categorize_error(conn_error, ServiceInfo("test", 5000, "/"))
        self.assertEqual(category, ErrorCategory.NETWORK)

        # HTTP error
        response = MagicMock()
        response.status_code = 500
        http_error = requests.exceptions.HTTPError("Server Error")
        http_error.response = response
        category = self.health_checker._categorize_error(http_error, ServiceInfo("test", 5000, "/"))
        self.assertEqual(category, ErrorCategory.SERVICE_ERROR)

        # Unknown error
        unknown_error = ValueError("Unknown error")
        category = self.health_checker._categorize_error(unknown_error, ServiceInfo("test", 5000, "/"))
        self.assertEqual(category, ErrorCategory.UNKNOWN)

    def test_websocket_health_check(self):
        """Test WebSocket health check functionality"""
        # This would require a real WebSocket server, so we'll mock it
        with patch('asyncio.get_event_loop') as mock_loop:
            mock_loop_instance = MagicMock()
            mock_loop.return_value = mock_loop_instance
            mock_loop_instance.run_until_complete.return_value = (True, None)

            service_info = ServiceInfo(
                name='websocket_service',
                port=8080,
                endpoint='/ws',
                check_type=HealthCheckType.WEBSOCKET
            )

            result = self.health_checker._check_websocket_health(service_info, time.time())

            self.assertIsInstance(result, HealthCheckResult)
            # Result depends on the mock setup

    def test_rpc_health_check(self):
        """Test RPC health check functionality"""
        service_info = ServiceInfo(
            name='rpc_service',
            port=8545,
            endpoint=None,
            check_type=HealthCheckType.RPC
        )

        # Mock RPC response
        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'result': '0x1'}
            mock_post.return_value = mock_response

            result = self.health_checker._check_rpc_health(service_info, time.time())

            self.assertEqual(result.status, ServiceStatus.HEALTHY)
            self.assertEqual(result.status_code, 200)

    def test_health_check_caching(self):
        """Test health check result caching"""
        service_name = 'test_service'

        # Mock healthy response
        with patch.object(self.health_checker, '_check_single_service') as mock_check:
            mock_result = HealthCheckResult(
                service=ServiceInfo("test", 5000, "/"),
                status=ServiceStatus.HEALTHY,
                response_time=0.1,
                timestamp=time.time()
            )
            mock_check.return_value = mock_result

            # First call
            result1 = self.health_checker.check_service_health(service_name, use_cache=True)

            # Second call should use cache
            result2 = self.health_checker.check_service_health(service_name, use_cache=True)

            # Should be the same object (cached)
            self.assertIs(result1, result2)

            # With use_cache=False, should call again
            result3 = self.health_checker.check_service_health(service_name, use_cache=False)
            # Should be different object
            self.assertIsNot(result3, result1)

    def test_metrics_collection(self):
        """Test service metrics collection"""
        service_name = 'test_service'

        # Initially no metrics
        metrics = self.health_checker.get_service_metrics(service_name)
        self.assertIn(service_name, metrics)
        self.assertEqual(metrics[service_name].total_checks, 0)

        # Simulate health checks
        healthy_result = HealthCheckResult(
            service=ServiceInfo("test", 5000, "/"),
            status=ServiceStatus.HEALTHY,
            response_time=0.1,
            timestamp=time.time()
        )

        unhealthy_result = HealthCheckResult(
            service=ServiceInfo("test", 5000, "/"),
            status=ServiceStatus.UNHEALTHY,
            response_time=0.2,
            timestamp=time.time()
        )

        self.health_checker._record_metrics(service_name, healthy_result)
        self.health_checker._record_metrics(service_name, healthy_result)
        self.health_checker._record_metrics(service_name, unhealthy_result)

        metrics = self.health_checker.get_service_metrics(service_name)[service_name]
        self.assertEqual(metrics.total_checks, 3)
        self.assertEqual(metrics.healthy_checks, 2)
        self.assertEqual(metrics.total_failures, 1)
        self.assertEqual(metrics.consecutive_failures, 1)

    def test_enhanced_service_status(self):
        """Test enhanced service status information"""
        service_name = 'poc_api'

        # Mock some metrics
        self.health_checker._metrics[service_name] = ServiceMetrics(
            service_name=service_name,
            total_checks=10,
            healthy_checks=9,
            consecutive_failures=0,
            average_response_time=0.15
        )

        status = self.health_checker.get_service_status(service_name)

        expected_keys = [
            'name', 'port', 'status', 'response_time', 'description',
            'check_type', 'uptime_percentage', 'consecutive_failures',
            'total_checks', 'adaptive_interval', 'circuit_breaker', 'dependencies'
        ]

        for key in expected_keys:
            self.assertIn(key, status)

        self.assertEqual(status['name'], 'PoC API')
        self.assertEqual(status['port'], 5001)
        self.assertEqual(status['check_type'], 'http')

class TestIntegrationScenarios(unittest.TestCase):
    """Integration tests for service health checker"""

    def setUp(self):
        self.health_checker = ServiceHealthChecker()

    def test_full_service_lifecycle(self):
        """Test full service lifecycle with dependencies"""
        # Add a complex dependency chain
        self.health_checker.add_dependency('frontend', 'api')
        self.health_checker.add_dependency('api', 'database')

        # Get startup order
        order = self.health_checker.get_startup_order()

        # Database should come before API, API before frontend
        db_index = order.index('database')
        api_index = order.index('api')
        frontend_index = order.index('frontend')

        self.assertLess(db_index, api_index)
        self.assertLess(api_index, frontend_index)

    def test_concurrent_health_checks(self):
        """Test concurrent health check operations"""
        results = []
        errors = []

        def check_service(service_name):
            try:
                result = self.health_checker.check_service_health(service_name)
                results.append((service_name, result.status))
            except Exception as e:
                errors.append((service_name, str(e)))

        services = ['poc_api', 'rag_api', 'nextjs_frontend']

        # Run checks concurrently
        threads = []
        for service in services:
            t = threading.Thread(target=check_service, args=(service,))
            threads.append(t)
            t.start()

        # Wait for completion
        for t in threads:
            t.join()

        # Should have results for all services
        self.assertEqual(len(results), len(services))
        self.assertEqual(len(errors), 0)

class TestPerformanceBenchmarks(unittest.TestCase):
    """Performance tests for service health checker"""

    def setUp(self):
        self.health_checker = ServiceHealthChecker()

    def test_bulk_health_check_performance(self):
        """Test performance of checking all services"""
        import time

        start_time = time.time()
        results = self.health_checker.check_all_services()
        end_time = time.time()

        duration = end_time - start_time

        # Should complete in reasonable time (< 5 seconds for all services)
        self.assertLess(duration, 5.0)
        self.assertIsInstance(results, dict)
        self.assertGreater(len(results), 0)

    def test_metrics_aggregation_performance(self):
        """Test performance of metrics aggregation"""
        import time

        # Add some test metrics
        for i in range(100):
            service_name = f'test_service_{i}'
            self.health_checker._metrics[service_name] = ServiceMetrics(
                service_name=service_name,
                total_checks=10,
                healthy_checks=8
            )

        start_time = time.time()
        metrics = self.health_checker.get_service_metrics()
        end_time = time.time()

        duration = end_time - start_time

        # Should aggregate 100 services quickly (< 0.1 seconds)
        self.assertLess(duration, 0.1)
        self.assertEqual(len(metrics), 100)

if __name__ == '__main__':
    unittest.main()







