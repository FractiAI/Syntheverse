#!/usr/bin/env python3
"""
Unit tests for the Service Health Check Module
Tests health checking for all Syntheverse services
"""

import unittest
import requests
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
    health_checker,
    check_service_health,
    check_all_services,
    get_service_status,
    wait_for_service,
    wait_for_all_services,
    print_health_report
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

if __name__ == '__main__':
    unittest.main()







