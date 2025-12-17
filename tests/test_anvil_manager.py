#!/usr/bin/env python3
"""
Unit tests for the Anvil Management Module
Tests Anvil startup, shutdown, health checks, and status monitoring
"""

import unittest
import time
import subprocess
import requests
from unittest.mock import patch, MagicMock, call
from pathlib import Path

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from scripts.startup.anvil_manager import (
    AnvilManager,
    AnvilStatus,
    anvil_manager,
    check_anvil_running,
    get_anvil_status,
    start_anvil,
    stop_anvil,
    wait_for_anvil,
    restart_anvil
)

class TestAnvilManager(unittest.TestCase):
    """Test cases for AnvilManager class"""

    def setUp(self):
        """Set up test fixtures"""
        self.anvil_manager = AnvilManager()
        # Ensure we don't interfere with real Anvil processes
        self.anvil_manager.anvil_port = 18545  # Use a different port for testing

    def tearDown(self):
        """Clean up after tests"""
        # Stop any test Anvil processes
        try:
            self.anvil_manager.stop_anvil()
        except:
            pass

    def test_initialization(self):
        """Test AnvilManager initialization"""
        manager = AnvilManager()
        self.assertIsNotNone(manager.port_manager)
        self.assertEqual(manager.anvil_port, 8545)
        self.assertIsNone(manager.anvil_process)
        self.assertIsNone(manager.start_time)

    @patch('requests.post')
    def test_check_anvil_running_success(self, mock_post):
        """Test successful Anvil running check"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'result': '0x1'}
        mock_post.return_value = mock_response

        result = self.anvil_manager.check_anvil_running()
        self.assertTrue(result)

    @patch('requests.post')
    def test_check_anvil_running_failure(self, mock_post):
        """Test Anvil running check failure"""
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")

        result = self.anvil_manager.check_anvil_running()
        self.assertFalse(result)

    @patch('requests.post')
    def test_check_anvil_running_invalid_response(self, mock_post):
        """Test Anvil running check with invalid response"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'error': 'Invalid request'}
        mock_post.return_value = mock_response

        result = self.anvil_manager.check_anvil_running()
        self.assertFalse(result)

    @patch('scripts.startup.anvil_manager.AnvilManager.check_anvil_running')
    @patch('scripts.startup.anvil_manager.PortManager')
    def test_get_anvil_status_not_running(self, mock_port_manager, mock_check_running):
        """Test getting Anvil status when not running"""
        mock_check_running.return_value = False

        status = self.anvil_manager.get_anvil_status()

        self.assertFalse(status.running)
        self.assertEqual(status.port, 18545)
        self.assertIsNone(status.pid)
        self.assertIsNone(status.block_number)

    @patch('scripts.startup.anvil_manager.AnvilManager.check_anvil_running')
    @patch('requests.post')
    def test_get_anvil_status_running(self, mock_post, mock_check_running):
        """Test getting Anvil status when running"""
        # Mock running check
        mock_check_running.return_value = True

        # Create a proper mock process info object
        from scripts.startup.port_manager import ProcessInfo
        mock_process = ProcessInfo(
            pid=12345,
            name='anvil',
            command='/usr/bin/anvil',
            user='testuser'
        )

        # Mock RPC responses
        def mock_rpc_response(*args, **kwargs):
            request_data = args[1] if len(args) > 1 else kwargs.get('json', {})
            method = request_data.get('method')

            mock_response = MagicMock()
            mock_response.status_code = 200

            if method == 'eth_blockNumber':
                mock_response.json.return_value = {'result': '0x64'}  # 100 in hex
            elif method == 'eth_accounts':
                mock_response.json.return_value = {'result': ['0x123', '0x456']}  # 2 accounts
            elif method == 'eth_gasPrice':
                mock_response.json.return_value = {'result': '0x3b9aca00'}  # 1 gwei

            return mock_response

        mock_post.side_effect = mock_rpc_response

        # Set start time for uptime calculation
        self.anvil_manager.start_time = time.time() - 60  # 60 seconds ago

        # Mock the port_manager's get_process_info method
        with patch.object(self.anvil_manager.port_manager, 'get_process_info', return_value=[mock_process]):
            status = self.anvil_manager.get_anvil_status()

        self.assertTrue(status.running)
        self.assertEqual(status.port, 18545)
        self.assertEqual(status.pid, 12345)
        self.assertEqual(status.block_number, 100)
        self.assertEqual(status.accounts, 2)
        self.assertEqual(status.gas_price, '0x3b9aca00')
        self.assertIsInstance(status.uptime, float)
        self.assertGreater(status.uptime, 50)  # Should be around 60 seconds

    @patch('scripts.startup.anvil_manager.AnvilManager.check_anvil_running')
    def test_wait_for_anvil_success(self, mock_check_running):
        """Test successful wait for Anvil"""
        # Anvil becomes available on second check
        mock_check_running.side_effect = [False, True]

        result = self.anvil_manager.wait_for_anvil(timeout=5, interval=1)

        self.assertTrue(result)
        self.assertEqual(mock_check_running.call_count, 2)

    @patch('scripts.startup.anvil_manager.AnvilManager.check_anvil_running')
    def test_wait_for_anvil_timeout(self, mock_check_running):
        """Test wait for Anvil timeout"""
        mock_check_running.return_value = False

        result = self.anvil_manager.wait_for_anvil(timeout=2, interval=1)

        self.assertFalse(result)
        # Should have been called multiple times
        self.assertGreater(mock_check_running.call_count, 1)

    @patch('scripts.startup.anvil_manager.free_port')
    @patch('scripts.startup.anvil_manager.AnvilManager.check_anvil_running')
    @patch('subprocess.Popen')
    @patch('scripts.startup.anvil_manager.AnvilManager.wait_for_anvil')
    def test_start_anvil_success(self, mock_wait, mock_popen, mock_check_running, mock_free_port):
        """Test successful Anvil startup"""
        # Mock not already running
        mock_check_running.return_value = False
        mock_free_port.return_value = True

        # Mock process creation
        mock_process = MagicMock()
        mock_process.pid = 12345
        mock_popen.return_value = mock_process

        # Mock successful wait
        mock_wait.return_value = True

        result = self.anvil_manager.start_anvil()

        self.assertTrue(result)
        mock_popen.assert_called_once()
        mock_wait.assert_called_once_with(timeout=60)
        self.assertIsNotNone(self.anvil_manager.anvil_process)
        self.assertIsNotNone(self.anvil_manager.start_time)

    @patch('scripts.startup.anvil_manager.free_port')
    @patch('scripts.startup.anvil_manager.AnvilManager.check_anvil_running')
    def test_start_anvil_already_running(self, mock_check_running, mock_free_port):
        """Test starting Anvil when already running"""
        mock_check_running.return_value = True

        result = self.anvil_manager.start_anvil()

        self.assertTrue(result)
        mock_free_port.assert_not_called()

    @patch('scripts.startup.anvil_manager.free_port')
    @patch('scripts.startup.anvil_manager.AnvilManager.check_anvil_running')
    def test_start_anvil_port_conflict(self, mock_check_running, mock_free_port):
        """Test starting Anvil with port conflict"""
        mock_check_running.return_value = False
        mock_free_port.return_value = False  # Port cannot be freed

        result = self.anvil_manager.start_anvil()

        self.assertFalse(result)

    @patch('scripts.startup.anvil_manager.free_port')
    @patch('scripts.startup.anvil_manager.AnvilManager.check_anvil_running')
    @patch('subprocess.Popen')
    @patch('scripts.startup.anvil_manager.AnvilManager.wait_for_anvil')
    def test_start_anvil_startup_failure(self, mock_wait, mock_popen, mock_check_running, mock_free_port):
        """Test Anvil startup failure during wait"""
        mock_check_running.return_value = False
        mock_free_port.return_value = True

        mock_process = MagicMock()
        mock_popen.return_value = mock_process
        mock_wait.return_value = False  # Wait fails

        result = self.anvil_manager.start_anvil()

        self.assertFalse(result)

    def test_stop_anvil_no_process(self):
        """Test stopping Anvil when no process is tracked"""
        self.anvil_manager.anvil_process = None

        result = self.anvil_manager.stop_anvil()

        # Should still attempt port cleanup
        self.assertIsInstance(result, bool)

    @patch('subprocess.Popen')
    def test_stop_anvil_with_tracked_process(self, mock_popen_class):
        """Test stopping Anvil with a tracked process"""
        # Mock process
        mock_process = MagicMock()
        mock_process.poll.return_value = None  # Process is running
        mock_process.pid = 12345
        mock_process.terminate.return_value = None
        mock_process.wait.return_value = None

        self.anvil_manager.anvil_process = mock_process

        with patch('scripts.startup.anvil_manager.free_port', return_value=True):
            result = self.anvil_manager.stop_anvil()

        mock_process.terminate.assert_called_once()
        mock_process.wait.assert_called_once()
        self.assertIsNone(self.anvil_manager.anvil_process)
        self.assertIsNone(self.anvil_manager.start_time)

    @patch('scripts.startup.anvil_manager.AnvilManager.stop_anvil')
    @patch('scripts.startup.anvil_manager.AnvilManager.start_anvil')
    def test_restart_anvil(self, mock_start, mock_stop):
        """Test restarting Anvil"""
        mock_stop.return_value = True
        mock_start.return_value = True

        result = self.anvil_manager.restart_anvil(accounts=5)

        self.assertTrue(result)
        mock_stop.assert_called_once()
        mock_start.assert_called_once_with(accounts=5)

class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions"""

    @patch.object(anvil_manager, 'check_anvil_running')
    def test_check_anvil_running_convenience(self, mock_method):
        """Test convenience function calls the method"""
        mock_method.return_value = True

        result = check_anvil_running()

        self.assertTrue(result)
        mock_method.assert_called_once()

    @patch.object(anvil_manager, 'get_anvil_status')
    def test_get_anvil_status_convenience(self, mock_method):
        """Test convenience function calls the method"""
        mock_status = AnvilStatus(running=True, port=8545)
        mock_method.return_value = mock_status

        result = get_anvil_status()

        self.assertEqual(result.port, 8545)
        mock_method.assert_called_once()

    @patch.object(anvil_manager, 'start_anvil')
    def test_start_anvil_convenience(self, mock_method):
        """Test convenience function calls the method"""
        mock_method.return_value = True

        result = start_anvil(accounts=10)

        self.assertTrue(result)
        mock_method.assert_called_once_with(accounts=10)

    @patch.object(anvil_manager, 'stop_anvil')
    def test_stop_anvil_convenience(self, mock_method):
        """Test convenience function calls the method"""
        mock_method.return_value = True

        result = stop_anvil()

        self.assertTrue(result)
        mock_method.assert_called_once()

    @patch.object(anvil_manager, 'wait_for_anvil')
    def test_wait_for_anvil_convenience(self, mock_method):
        """Test convenience function calls the method"""
        mock_method.return_value = True

        result = wait_for_anvil(timeout=30)

        self.assertTrue(result)
        mock_method.assert_called_once_with(30)

    @patch.object(anvil_manager, 'restart_anvil')
    def test_restart_anvil_convenience(self, mock_method):
        """Test convenience function calls the method"""
        mock_method.return_value = True

        result = restart_anvil(block_time=5)

        self.assertTrue(result)
        mock_method.assert_called_once_with(block_time=5)

if __name__ == '__main__':
    unittest.main()
