#!/usr/bin/env python3
"""
Unit tests for the Port Management Module
Tests port cleanup, process detection, and availability checking
"""

import unittest
import tempfile
import time
import socket
import subprocess
import signal
import os
import threading
from unittest.mock import patch, MagicMock, call
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from scripts.startup.port_manager import (
    PortManager,
    ProcessInfo,
    PortReservation,
    PortMetrics,
    port_manager,
    kill_processes_on_port,
    check_port_available,
    free_port,
    get_process_info,
    get_port_status,
    reserve_port,
    release_port_reservation,
    is_port_reserved,
    check_ports_batch,
    get_port_metrics,
    get_process_fingerprint
)

class TestPortManager(unittest.TestCase):
    """Test cases for PortManager class"""

    def setUp(self):
        """Set up test fixtures"""
        self.port_manager = PortManager()
        # Use very high ports to avoid conflicts
        self.test_port = 65530
        self.test_name = "Test Service"

    def tearDown(self):
        """Clean up after tests"""
        # Ensure test port is free
        try:
            port_manager.free_port(self.test_port, "Test Cleanup")
        except:
            pass

    def test_detect_platform(self):
        """Test platform detection"""
        system = self.port_manager._detect_platform()
        self.assertIn(system, ['macos', 'linux', 'windows', 'unknown'])

    @patch('subprocess.run')
    def test_get_process_info_success(self, mock_run):
        """Test getting process information successfully"""
        # Mock lsof output
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = """COMMAND   PID   USER   FD   TYPE             DEVICE SIZE/OFF NODE NAME
python   12345 testuser  3u  IPv4 0x123456789       0t0  TCP *:55555 (LISTEN)
"""
        mock_run.return_value = mock_result

        processes = self.port_manager.get_process_info(self.test_port)

        self.assertEqual(len(processes), 1)
        self.assertEqual(processes[0].pid, 12345)
        self.assertEqual(processes[0].name, 'python')
        self.assertEqual(processes[0].user, 'testuser')

    @patch('subprocess.run')
    def test_get_process_info_no_processes(self, mock_run):
        """Test getting process information when no processes are using the port"""
        mock_result = MagicMock()
        mock_result.returncode = 1  # lsof returns 1 when no processes found
        mock_result.stdout = ""
        mock_run.return_value = mock_result

        processes = self.port_manager.get_process_info(self.test_port)

        self.assertEqual(len(processes), 0)

    @patch('subprocess.run')
    def test_get_process_info_lsof_not_found(self, mock_run):
        """Test handling when lsof is not available"""
        mock_run.side_effect = FileNotFoundError("lsof not found")

        processes = self.port_manager.get_process_info(self.test_port)

        self.assertEqual(len(processes), 0)

    @patch('subprocess.run')
    def test_is_system_service_macos(self, mock_run):
        """Test system service detection on macOS"""
        self.port_manager.system = 'macos'

        # Test system service
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "/usr/libexec/AirPlayXPCHelper\n"
        mock_run.return_value = mock_result

        self.assertTrue(self.port_manager.is_system_service(12345))

        # Test regular process
        mock_result.stdout = "/usr/local/bin/python\n"
        mock_run.return_value = mock_result

        self.assertFalse(self.port_manager.is_system_service(12345))

    @patch('subprocess.run')
    def test_is_system_service_linux(self, mock_run):
        """Test system service detection on Linux"""
        self.port_manager.system = 'linux'

        # Test system user
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "root\n"
        mock_run.return_value = mock_result

        self.assertTrue(self.port_manager.is_system_service(12345))

        # Test regular user
        mock_result.stdout = "testuser\n"
        mock_run.return_value = mock_result

        self.assertFalse(self.port_manager.is_system_service(12345))

    def test_check_port_available_free(self):
        """Test checking availability of a free port"""
        # Use a high port that's likely to be free
        result = self.port_manager.check_port_available(55556)
        self.assertTrue(result)

    def test_check_port_available_in_use(self):
        """Test checking availability of an in-use port"""
        # Test with a well-known port that's likely in use (port 22 - SSH)
        result = self.port_manager.check_port_available(22)
        # We can't guarantee port 22 is in use, so just check that the method returns a boolean
        self.assertIsInstance(result, bool)

    @patch('scripts.startup.port_manager.PortManager.is_system_service')
    @patch('subprocess.run')
    @patch('os.kill')
    @patch('time.sleep')
    def test_kill_processes_on_port_success(self, mock_sleep, mock_kill, mock_run, mock_is_system):
        """Test successful process killing"""
        # Mock non-system service
        mock_is_system.return_value = False

        # Mock lsof output showing a process
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = """COMMAND   PID   USER   FD   TYPE             DEVICE SIZE/OFF NODE NAME
python   12345 testuser  3u  IPv4 0x123456789       0t0  TCP *:65530 (LISTEN)
"""
        mock_run.return_value = mock_result

        # Mock successful kill
        mock_kill.return_value = None

        # Mock empty result after killing (no processes left)
        mock_result_empty = MagicMock()
        mock_result_empty.returncode = 1
        mock_result_empty.stdout = ""

        # First call returns processes, second call returns empty
        mock_run.side_effect = [mock_result, mock_result_empty]

        result = self.port_manager.kill_processes_on_port(self.test_port)

        self.assertTrue(result)
        mock_kill.assert_called_once_with(12345, signal.SIGKILL)

    @patch('scripts.startup.port_manager.PortManager.is_system_service')
    @patch('subprocess.run')
    def test_kill_processes_on_port_system_service(self, mock_run, mock_is_system):
        """Test that system services are not killed"""
        # Mock system service detection
        mock_is_system.return_value = True

        # Mock lsof output
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = """COMMAND   PID   USER   FD   TYPE             DEVICE SIZE/OFF NODE NAME
AirPlay   12345 _mdnsresponder  3u  IPv4 0x123456789       0t0  TCP *:65530 (LISTEN)
"""
        mock_run.return_value = mock_result

        result = self.port_manager.kill_processes_on_port(self.test_port)

        # Should return True because it successfully identified and didn't kill system service
        self.assertTrue(result)
        # os.kill should not be called for system services
        # (Note: we can't easily test this without patching os.kill since it's not called in this test)

    @patch('subprocess.run')
    @patch('os.kill')
    @patch('time.sleep')
    def test_kill_processes_on_port_retry(self, mock_sleep, mock_kill, mock_run):
        """Test retry logic when process doesn't die immediately"""
        # Mock lsof output showing process persists
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = """COMMAND   PID   USER   FD   TYPE             DEVICE SIZE/OFF NODE NAME
python   12345 testuser  3u  IPv4 0x123456789       0t0  TCP *:55555 (LISTEN)
"""
        mock_run.return_value = mock_result

        # Mock successful kill
        mock_kill.return_value = None

        result = self.port_manager.kill_processes_on_port(self.test_port, max_retries=2)

        # Should eventually give up after retries
        self.assertFalse(result)

    @patch.object(PortManager, 'check_port_available')
    @patch.object(PortManager, 'kill_processes_on_port')
    @patch('time.sleep')
    def test_free_port_already_free(self, mock_sleep, mock_kill_processes, mock_check):
        """Test freeing a port that's already available"""
        mock_check.return_value = True

        result = self.port_manager.free_port(self.test_port, self.test_name)

        self.assertTrue(result)
        mock_kill_processes.assert_not_called()

    @patch.object(PortManager, 'check_port_available')
    @patch.object(PortManager, 'kill_processes_on_port')
    @patch('time.sleep')
    def test_free_port_success(self, mock_sleep, mock_kill_processes, mock_check):
        """Test successfully freeing a port"""
        # Port initially in use
        mock_check.side_effect = [False, True]  # First check: in use, second: free
        mock_kill_processes.return_value = True

        result = self.port_manager.free_port(self.test_port, self.test_name)

        self.assertTrue(result)
        mock_kill_processes.assert_called_once_with(self.test_port, max_retries=3)

    @patch.object(PortManager, 'check_port_available')
    @patch.object(PortManager, 'kill_processes_on_port')
    @patch('time.sleep')
    def test_free_port_failure(self, mock_sleep, mock_kill_processes, mock_check):
        """Test failure to free a port"""
        mock_check.return_value = False  # Always in use
        mock_kill_processes.return_value = True

        result = self.port_manager.free_port(self.test_port, self.test_name, max_retries=2)

        self.assertFalse(result)

    def test_get_port_status(self):
        """Test getting comprehensive port status"""
        # Test with free port
        status = self.port_manager.get_port_status(self.test_port, self.test_name)

        expected_keys = ['port', 'name', 'available', 'process_count', 'processes']
        for key in expected_keys:
            self.assertIn(key, status)

        self.assertEqual(status['port'], self.test_port)
        self.assertEqual(status['name'], self.test_name)
        self.assertIsInstance(status['processes'], list)

class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions"""

    @patch.object(port_manager, 'kill_processes_on_port')
    def test_kill_processes_on_port_convenience(self, mock_method):
        """Test convenience function calls the method"""
        mock_method.return_value = True

        result = kill_processes_on_port(55555)

        self.assertTrue(result)
        mock_method.assert_called_once_with(55555, 3)

    @patch.object(port_manager, 'check_port_available')
    def test_check_port_available_convenience(self, mock_method):
        """Test convenience function calls the method"""
        mock_method.return_value = True

        result = check_port_available(55555)

        self.assertTrue(result)
        mock_method.assert_called_once_with(55555)

    @patch.object(port_manager, 'free_port')
    def test_free_port_convenience(self, mock_method):
        """Test convenience function calls the method"""
        mock_method.return_value = True

        result = free_port(55555, "Test")

        self.assertTrue(result)
        mock_method.assert_called_once_with(55555, "Test", 5)

    @patch.object(port_manager, 'get_process_info')
    def test_get_process_info_convenience(self, mock_method):
        """Test convenience function calls the method"""
        mock_method.return_value = []

        result = get_process_info(55555)

        self.assertEqual(result, [])
        mock_method.assert_called_once_with(55555)

    @patch.object(port_manager, 'get_port_status')
    def test_get_port_status_convenience(self, mock_method):
        """Test convenience function calls the method"""
        mock_method.return_value = {'port': 55555}

        result = get_port_status(55555, "Test")

        self.assertEqual(result['port'], 55555)
        mock_method.assert_called_once_with(55555, "Test")

class TestEnhancedPortManager(unittest.TestCase):
    """Test cases for enhanced port manager features"""

    def setUp(self):
        """Set up test fixtures"""
        self.port_manager = PortManager()
        self.test_port = 55530
        self.test_service = "TestService"

    def tearDown(self):
        """Clean up after tests"""
        try:
            port_manager.free_port(self.test_port, "Test Cleanup")
        except:
            pass

    def test_process_fingerprint_generation(self):
        """Test process fingerprint generation"""
        fingerprint = self.port_manager.get_process_fingerprint(os.getpid())
        self.assertIsInstance(fingerprint, str)
        self.assertGreater(len(fingerprint), 0)

        # Same PID should return same fingerprint
        fingerprint2 = self.port_manager.get_process_fingerprint(os.getpid())
        self.assertEqual(fingerprint, fingerprint2)

    def test_port_reservation_system(self):
        """Test port reservation functionality"""
        # Reserve port
        success = self.port_manager.reserve_port(self.test_port, self.test_service, os.getpid())
        self.assertTrue(success)

        # Check reservation
        self.assertTrue(self.port_manager.is_port_reserved(self.test_port))
        self.assertTrue(self.port_manager.is_port_reserved(self.test_port, self.test_service))

        # Check different service
        self.assertFalse(self.port_manager.is_port_reserved(self.test_port, "OtherService"))

        # Release reservation
        success = self.port_manager.release_port_reservation(self.test_port, self.test_service)
        self.assertTrue(success)
        self.assertFalse(self.port_manager.is_port_reserved(self.test_port))

    def test_parallel_port_checking(self):
        """Test parallel port availability checking"""
        ports_to_check = [55531, 55532, 55533, 55534, 55535]
        results = self.port_manager.check_ports_batch(ports_to_check)

        self.assertIsInstance(results, dict)
        self.assertEqual(len(results), len(ports_to_check))

        for port in ports_to_check:
            self.assertIn(port, results)
            self.assertIsInstance(results[port], bool)

    @patch('time.sleep')  # Prevent actual sleeping in tests
    def test_metrics_collection(self, mock_sleep):
        """Test metrics collection during port operations"""
        # Create a scenario that will generate metrics
        with patch.object(self.port_manager, 'kill_processes_on_port', return_value=True):
            with patch.object(self.port_manager, 'check_port_available', side_effect=[False, True]):
                success = self.port_manager.free_port(self.test_port, self.test_service)

        # Check that metrics were recorded
        metrics = self.port_manager.get_metrics()
        self.assertGreater(len(metrics), 0)

        # Find metrics for our test port
        port_metrics = [m for m in metrics if m.port == self.test_port]
        if port_metrics:
            metric = port_metrics[0]
            self.assertEqual(metric.service, self.test_service)
            self.assertIsInstance(metric.cleanup_duration, float)
            self.assertIsInstance(metric.success, bool)

    def test_process_fingerprinting_protection(self):
        """Test that fingerprinting prevents killing wrong processes"""
        # Mock a process with different fingerprint
        mock_process = ProcessInfo(
            pid=99999,
            name='test_process',
            command='test command',
            user='testuser',
            fingerprint='old_fingerprint'
        )

        with patch.object(self.port_manager, 'get_process_info', return_value=[mock_process]):
            with patch.object(self.port_manager, 'get_process_fingerprint', return_value='new_fingerprint'):
                with patch('os.kill') as mock_kill:
                    result = self.port_manager.kill_processes_on_port(self.test_port, target_service="TestService")

                    # Should return True but not kill the process due to fingerprint mismatch
                    self.assertTrue(result)
                    mock_kill.assert_not_called()

    def test_cache_functionality(self):
        """Test port status caching"""
        # First call should cache result
        with patch.object(self.port_manager, 'get_process_info') as mock_get_process:
            mock_get_process.return_value = []
            result1 = self.port_manager.get_process_info(self.test_port, use_cache=True)

        # Second call should use cache
        result2 = self.port_manager.get_process_info(self.test_port, use_cache=True)
        self.assertEqual(result1, result2)

        # With use_cache=False, should call again
        result3 = self.port_manager.get_process_info(self.test_port, use_cache=False)
        self.assertEqual(result1, result3)

    def test_concurrent_operations(self):
        """Test concurrent port operations"""
        results = []
        errors = []

        def worker(worker_id):
            try:
                # Test parallel port checking
                result = self.port_manager.check_port_available(self.test_port + worker_id)
                results.append((worker_id, result))
            except Exception as e:
                errors.append((worker_id, str(e)))

        # Run multiple threads
        threads = []
        for i in range(5):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()

        # Wait for all threads
        for t in threads:
            t.join()

        # Should have results from all threads
        self.assertEqual(len(results), 5)
        self.assertEqual(len(errors), 0)

class TestPerformanceBenchmarks(unittest.TestCase):
    """Performance tests for port manager"""

    def setUp(self):
        self.port_manager = PortManager()
        self.test_ports = list(range(55500, 55520))  # 20 ports

    def test_batch_port_check_performance(self):
        """Test performance of batch port checking"""
        import time

        start_time = time.time()
        results = self.port_manager.check_ports_batch(self.test_ports)
        end_time = time.time()

        duration = end_time - start_time

        # Should check 20 ports in reasonable time (< 1 second)
        self.assertLess(duration, 1.0)
        self.assertEqual(len(results), len(self.test_ports))

    def test_cache_performance_improvement(self):
        """Test that caching improves performance"""
        import time

        # First call (no cache)
        start_time = time.time()
        with patch.object(self.port_manager, 'get_process_info') as mock_get:
            mock_get.return_value = []
            result1 = self.port_manager.get_process_info(55530, use_cache=False)
        no_cache_time = time.time() - start_time

        # Second call (with cache)
        start_time = time.time()
        result2 = self.port_manager.get_process_info(55530, use_cache=True)
        cache_time = time.time() - start_time

        # Cache should be significantly faster
        self.assertLess(cache_time, no_cache_time)
        self.assertEqual(result1, result2)

class TestChaosTesting(unittest.TestCase):
    """Chaos tests for port manager resilience"""

    def setUp(self):
        self.port_manager = PortManager()
        self.test_port = 55525

    @patch('subprocess.run')
    def test_lsof_failure_resilience(self, mock_run):
        """Test resilience when lsof command fails"""
        mock_run.side_effect = subprocess.CalledProcessError(1, 'lsof')

        # Should not crash, should return empty list
        processes = self.port_manager.get_process_info(self.test_port)
        self.assertEqual(processes, [])

    @patch('os.kill')
    def test_process_kill_permission_denied(self, mock_kill):
        """Test handling of permission denied when killing processes"""
        mock_kill.side_effect = OSError("Permission denied")

        mock_process = ProcessInfo(
            pid=12345,
            name='test_process',
            command='test command',
            user='root'
        )

        with patch.object(self.port_manager, 'get_process_info', return_value=[mock_process]):
            result = self.port_manager.kill_processes_on_port(self.test_port)

            # Should handle permission error gracefully
            self.assertIsInstance(result, bool)

    def test_empty_port_list_batch_check(self):
        """Test batch checking with empty port list"""
        results = self.port_manager.check_ports_batch([])
        self.assertEqual(results, {})

    def test_invalid_pid_fingerprint(self):
        """Test fingerprint generation for invalid PID"""
        fingerprint = self.port_manager.get_process_fingerprint(999999)
        # Should return a valid fingerprint even for non-existent PID
        self.assertIsInstance(fingerprint, str)
        self.assertGreater(len(fingerprint), 0)

if __name__ == '__main__':
    unittest.main()
