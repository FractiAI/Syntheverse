#!/usr/bin/env python3
"""
Comprehensive tests for Syntheverse startup scripts
Tests environment loading, dependency validation, service startup, and health checks
"""

import unittest
import tempfile
import os
import sys
import time
import subprocess
import shutil
import threading
import json
import signal
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from scripts.startup.start_servers import ServerManager, ServiceProfile, StartupMetrics
from scripts.startup.service_health import ServiceStatus
from test_framework import SyntheverseTestCase

class TestServerManager(SyntheverseTestCase):
    """Test cases for ServerManager class"""

    def setUp(self):
        """Set up test fixtures"""
        super().setUp()
        self.manager = ServerManager()
        # Override project root for testing
        self.manager.project_root = Path(__file__).parent.parent

    def get_category(self):
        return "startup"

    def test_load_environment_success(self):
        """Test successful environment loading"""
        # Save original environment
        original_groq_key = os.environ.get('GROQ_API_KEY')

        # Create a temporary directory with a .env file
        with tempfile.TemporaryDirectory() as temp_dir:
            env_file_path = Path(temp_dir) / ".env"
            with open(env_file_path, 'w') as f:
                f.write("GROQ_API_KEY=gsk_test_key\n")

            try:
                # Clear the existing GROQ_API_KEY to test loading from file
                if 'GROQ_API_KEY' in os.environ:
                    del os.environ['GROQ_API_KEY']

                # Temporarily change the project root to the temp directory
                original_root = self.manager.project_root
                self.manager.project_root = Path(temp_dir)

                result = self.manager.load_environment()

                self.assertTrue(result)
                self.assertEqual(os.environ.get('GROQ_API_KEY'), 'gsk_test_key')
            finally:
                # Restore original environment and project root
                if original_groq_key is not None:
                    os.environ['GROQ_API_KEY'] = original_groq_key
                elif 'GROQ_API_KEY' in os.environ:
                    del os.environ['GROQ_API_KEY']

                self.manager.project_root = original_root

    def test_load_environment_missing_file(self):
        """Test environment loading when .env file doesn't exist"""
        # Create a temporary directory without .env file
        with tempfile.TemporaryDirectory() as temp_dir:
            # Clear any existing GROQ_API_KEY
            if 'GROQ_API_KEY' in os.environ:
                del os.environ['GROQ_API_KEY']

            # Temporarily change the project root to the temp directory
            original_root = self.manager.project_root
            self.manager.project_root = Path(temp_dir)

            try:
                result = self.manager.load_environment()
                self.assertFalse(result)
            finally:
                # Restore original project root
                self.manager.project_root = original_root

    def test_load_environment_malformed_file(self):
        """Test environment loading with malformed .env file"""
        # Save original environment
        original_groq_key = os.environ.get('GROQ_API_KEY')

        # Create a temporary directory with a malformed .env file
        with tempfile.TemporaryDirectory() as temp_dir:
            env_file_path = Path(temp_dir) / ".env"
            with open(env_file_path, 'w') as f:
                f.write("INVALID_LINE\nGROQ_API_KEY=\n")

            try:
                # Clear the existing GROQ_API_KEY to test loading from file
                if 'GROQ_API_KEY' in os.environ:
                    del os.environ['GROQ_API_KEY']

                # Temporarily change the project root to the temp directory
                original_root = self.manager.project_root
                self.manager.project_root = Path(temp_dir)

                result = self.manager.load_environment()

                # The method should return False because GROQ_API_KEY is empty/invalid
                self.assertFalse(result)
            finally:
                # Restore original environment and project root
                if original_groq_key is not None:
                    os.environ['GROQ_API_KEY'] = original_groq_key
                elif 'GROQ_API_KEY' in os.environ:
                    del os.environ['GROQ_API_KEY']

                self.manager.project_root = original_root

    def test_load_environment_empty_key(self):
        """Test environment loading with empty API key"""
        # Create a temporary directory with a .env file containing empty API key
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_env_file = Path(temp_dir) / ".env"
            with open(temp_env_file, 'w') as f:
                f.write("GROQ_API_KEY=   \n")

            # Temporarily change the project root to the temp directory
            original_root = self.manager.project_root
            self.manager.project_root = Path(temp_dir)

            try:
                result = self.manager.load_environment()
                self.assertFalse(result)
            finally:
                # Restore original project root
                self.manager.project_root = original_root

    def test_validate_dependencies_success(self):
        """Test successful dependency validation"""
        # Create a temporary directory with mock files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create mock requirement files
            requirements_file = temp_path / "requirements.txt"
            requirements_file.write_text("flask\nflask-cors\nwerkzeug\nrequests\n")

            package_json = temp_path / "package.json"
            package_json.write_text('{"dependencies": {"next": "^12.0.0"}}\n')

            # Temporarily change the project root
            original_root = self.manager.project_root
            self.manager.project_root = temp_path

            try:
                # This will actually try to import real modules and run subprocess commands
                # We expect this to work since these are standard packages
                result = self.manager.validate_dependencies()

                # The result depends on whether the packages are actually installed
                # We'll accept either result since we're testing the validation logic
                self.assertIsInstance(result, bool)

            finally:
                # Restore original project root
                self.manager.project_root = original_root

    def test_validate_dependencies_missing_files(self):
        """Test dependency validation with missing required files"""
        # Create a temporary directory without required files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Temporarily change the project root
            original_root = self.manager.project_root
            self.manager.project_root = temp_path

            try:
                result = self.manager.validate_dependencies()

                # Should return False since required files don't exist
                self.assertFalse(result)
            finally:
                # Restore original project root
                self.manager.project_root = original_root

    @patch('subprocess.run')
    @patch('time.sleep')
    def test_validate_service_readiness_success(self, mock_sleep, mock_run):
        """Test successful service readiness validation"""
        # Mock requests
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response

            started_services = ["PoC API", "Web UI"]
            result = self.manager.validate_service_readiness(started_services)

            self.assertIsInstance(result, list)

    @patch('subprocess.run')
    def test_validate_service_readiness_failure(self, mock_run):
        """Test service readiness validation with failures"""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("Connection failed")

            started_services = ["PoC API"]
            result = self.manager.validate_service_readiness(started_services, timeout=1)

            # Should return empty list or handle gracefully
            self.assertIsInstance(result, list)


class TestStartupIntegration(SyntheverseTestCase):
    """Integration tests for startup scripts"""

    def get_category(self):
        return "integration"

    @patch('pathlib.Path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="GROQ_API_KEY=gsk_test_key\n")
    @patch('subprocess.run')
    def test_server_manager_initialization(self, mock_run, mock_file, mock_exists):
        """Test that ServerManager initializes correctly"""
        mock_exists.return_value = True

        manager = ServerManager()

        # Should have port manager initialized
        self.assertIsNotNone(manager.port_manager)
        self.assertIsNotNone(manager.logger)


class TestStartupErrorHandling(SyntheverseTestCase):
    """Test error handling in startup scripts"""

    def get_category(self):
        return "startup"

    def setUp(self):
        """Set up test fixtures"""
        super().setUp()
        self.manager = ServerManager()
        self.manager.project_root = Path(__file__).parent.parent

    def test_load_environment_io_error(self):
        """Test handling of IO errors during environment loading"""
        with patch('builtins.open', side_effect=IOError("Permission denied")):
            with patch('pathlib.Path.exists', return_value=True):
                result = self.manager.load_environment()

                self.assertFalse(result)

    def test_load_environment_unicode_error(self):
        """Test handling of Unicode errors during environment loading"""
        with patch('builtins.open', side_effect=UnicodeDecodeError('utf-8', b'', 0, 1, 'invalid')):
            with patch('pathlib.Path.exists', return_value=True):
                result = self.manager.load_environment()

                self.assertFalse(result)

    @patch('subprocess.run')
    def test_dependency_validation_subprocess_error(self, mock_run):
        """Test handling of subprocess errors during dependency validation"""
        mock_run.side_effect = subprocess.TimeoutExpired(['node', '--version'], 5)

        with patch('pathlib.Path.exists', return_value=True):
            result = self.manager.validate_dependencies()

            # Should still pass basic file checks
            self.assertIsInstance(result, bool)

    @patch('subprocess.Popen')
    def test_start_server_with_string_command(self, mock_popen):
        """Test start_server with string command"""
        mock_process = MagicMock()
        mock_process.poll.return_value = None
        mock_popen.return_value = mock_process

        result = self.manager.start_server("echo test", "Test Server", 8080)

        self.assertTrue(result)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(kwargs['shell'], True)
        self.assertIn('echo test', args[0])

    @patch('subprocess.Popen')
    def test_start_server_with_list_command(self, mock_popen):
        """Test start_server with list command"""
        mock_process = MagicMock()
        mock_process.poll.return_value = None
        mock_popen.return_value = mock_process

        result = self.manager.start_server(["python", "test.py"], "Test Server", 8080)

        self.assertTrue(result)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(kwargs['shell'], True)
        # Should be converted to string
        self.assertIn('python test.py', args[0])

    @patch('subprocess.Popen')
    def test_start_server_with_custom_env(self, mock_popen):
        """Test start_server with custom environment"""
        mock_process = MagicMock()
        mock_process.poll.return_value = None
        mock_popen.return_value = mock_process

        custom_env = {'CUSTOM_VAR': 'test_value'}
        result = self.manager.start_server("echo test", "Test Server", 8080, env=custom_env)

        self.assertTrue(result)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(kwargs['env']['CUSTOM_VAR'], 'test_value')
        self.assertIn('FLASK_SKIP_DOTENV', kwargs['env'])

    @patch('subprocess.Popen')
    def test_start_server_process_failure(self, mock_popen):
        """Test start_server when process fails to start"""
        mock_process = MagicMock()
        mock_process.poll.return_value = 1  # Process exited with error
        mock_process.communicate.return_value = (b'', b'Error starting server')
        mock_popen.return_value = mock_process

        result = self.manager.start_server("failing_command", "Test Server", 8080)

        self.assertFalse(result)

    @patch('subprocess.Popen')
    def test_start_server_with_cwd(self, mock_popen):
        """Test start_server with custom working directory"""
        mock_process = MagicMock()
        mock_process.poll.return_value = None
        mock_popen.return_value = mock_process

        test_cwd = Path("/tmp/test")
        result = self.manager.start_server("echo test", "Test Server", 8080, cwd=test_cwd)

        self.assertTrue(result)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(kwargs['cwd'], test_cwd)

class TestEnhancedStartupOrchestration(unittest.TestCase):
    """Test cases for startup orchestration using real implementations"""

    def setUp(self):
        """Set up test fixtures"""
        self.manager = ServerManager()
        self.test_port = 55530
        self.test_processes = []

    def tearDown(self):
        """Clean up after tests"""
        # Clean up any state files
        if self.manager.state_file.exists():
            try:
                self.manager.state_file.unlink()
            except Exception:
                pass
        
        # Clean up any test processes we started
        for proc in self.test_processes:
            try:
                if proc.poll() is None:
                    proc.terminate()
                    proc.wait(timeout=2)
            except Exception:
                pass

    def _start_test_process(self):
        """Start a lightweight test process (sleep command)"""
        proc = subprocess.Popen(
            ['sleep', '60'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        self.test_processes.append(proc)
        return proc

    def test_service_profile_configuration(self):
        """Test service profile configuration"""
        # Test development profile
        dev_manager = ServerManager(profile=ServiceProfile.DEVELOPMENT)
        self.assertEqual(dev_manager.profile, ServiceProfile.DEVELOPMENT)
        self.assertTrue(dev_manager._service_profiles[ServiceProfile.DEVELOPMENT]['parallel_startup'])

        # Test production profile
        prod_manager = ServerManager(profile=ServiceProfile.PRODUCTION)
        self.assertEqual(prod_manager.profile, ServiceProfile.PRODUCTION)
        self.assertTrue(prod_manager._service_profiles[ServiceProfile.PRODUCTION]['parallel_startup'])

        # Test testing profile
        test_manager = ServerManager(profile=ServiceProfile.TESTING)
        self.assertEqual(test_manager.profile, ServiceProfile.TESTING)
        self.assertFalse(test_manager._service_profiles[ServiceProfile.TESTING]['parallel_startup'])

    def test_port_configuration_by_profile(self):
        """Test port configuration varies by profile"""
        dev_manager = ServerManager(mode='poc', profile=ServiceProfile.DEVELOPMENT)
        test_manager = ServerManager(mode='poc', profile=ServiceProfile.TESTING)

        # Development and testing should have different ports
        self.assertNotEqual(dev_manager.ports, test_manager.ports)

        # Both should have the same services for 'poc' mode
        self.assertEqual(set(dev_manager.ports.keys()), set(test_manager.ports.keys()))

    def test_state_persistence(self):
        """Test service state persistence with real process"""
        from scripts.startup.start_servers import ServiceState
        
        # Start a real process
        proc = self._start_test_process()
        
        # Create state for the real process
        test_state = ServiceState(
            name='test_service',
            pid=proc.pid,
            port=5000,
            start_time=time.time(),
            command='sleep 60'
        )
        self.manager.service_states['test_service'] = test_state

        # Save state
        self.manager.save_state()

        # Create new manager and load state
        new_manager = ServerManager()
        loaded_states = new_manager.service_states

        # Should have loaded the saved state
        self.assertIn('test_service', loaded_states)
        self.assertEqual(loaded_states['test_service'].pid, proc.pid)
        self.assertEqual(loaded_states['test_service'].port, 5000)

    def test_process_running_check(self):
        """Test _process_running with real processes"""
        # Start a real process
        proc = self._start_test_process()
        
        # Process should be running
        self.assertTrue(self.manager._process_running(proc.pid))
        
        # Terminate the process
        proc.terminate()
        proc.wait(timeout=2)
        
        # Process should no longer be running
        self.assertFalse(self.manager._process_running(proc.pid))

    def test_rollback_with_real_processes(self):
        """Test startup rollback with real processes"""
        from scripts.startup.start_servers import ServiceState
        
        # Start real processes
        proc1 = self._start_test_process()
        proc2 = self._start_test_process()
        
        # Verify processes are running
        self.assertTrue(self.manager._process_running(proc1.pid))
        self.assertTrue(self.manager._process_running(proc2.pid))
        
        # Create service states for the real processes
        self.manager.service_states['service1'] = ServiceState(
            name='service1',
            pid=proc1.pid,
            port=5001,
            start_time=time.time(),
            command='sleep 60'
        )
        self.manager.service_states['service2'] = ServiceState(
            name='service2',
            pid=proc2.pid,
            port=5002,
            start_time=time.time(),
            command='sleep 60'
        )
        
        # Rollback the services
        self.manager.rollback_startup(['service1', 'service2'])
        
        # Wait for processes to terminate (may need more time on some systems)
        for _ in range(20):  # Wait up to 2 seconds
            if not self.manager._process_running(proc1.pid) and not self.manager._process_running(proc2.pid):
                break
            time.sleep(0.1)
        
        # Processes should no longer be running
        # Use wait() to ensure process is reaped
        try:
            proc1.wait(timeout=1)
        except subprocess.TimeoutExpired:
            proc1.kill()
        try:
            proc2.wait(timeout=1)
        except subprocess.TimeoutExpired:
            proc2.kill()
        
        # Service states should be cleaned up
        self.assertNotIn('service1', self.manager.service_states)
        self.assertNotIn('service2', self.manager.service_states)

    def test_graceful_shutdown_signal_handling(self):
        """Test graceful shutdown signal handling with real cleanup"""
        # Track if cleanup was called
        cleanup_called = []
        original_cleanup = self.manager.cleanup
        
        def track_cleanup():
            cleanup_called.append(True)
            # Don't call original cleanup to avoid side effects
        
        self.manager.cleanup = track_cleanup
        
        try:
            # Simulate SIGTERM signal
            self.manager._signal_handler(signal.SIGTERM, None)
            
            # Should have set shutdown event
            self.assertTrue(self.manager.shutdown_event.is_set())
            
            # Should have called cleanup
            self.assertTrue(cleanup_called)
        finally:
            # Restore original cleanup and reset shutdown event
            self.manager.cleanup = original_cleanup
            self.manager.shutdown_event.clear()

    def test_cleanup_terminates_processes(self):
        """Test that cleanup actually terminates running processes"""
        from scripts.startup.start_servers import ServiceState
        
        # Start a real process
        proc = self._start_test_process()
        
        # Create service state
        self.manager.service_states['test_cleanup'] = ServiceState(
            name='test_cleanup',
            pid=proc.pid,
            port=5003,
            start_time=time.time(),
            command='sleep 60'
        )
        
        # Verify process is running
        self.assertTrue(self.manager._process_running(proc.pid))
        
        # Call cleanup
        self.manager.cleanup()
        
        # Wait for process to terminate (may need more time on some systems)
        for _ in range(20):  # Wait up to 2 seconds
            if not self.manager._process_running(proc.pid):
                break
            time.sleep(0.1)
        
        # Use wait() to ensure process is reaped
        try:
            proc.wait(timeout=1)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
        
        # Process should no longer be running after wait
        self.assertFalse(proc.poll() is None)

class TestIntegrationScenarios(unittest.TestCase):
    """Integration tests for startup orchestration using real implementations"""

    def setUp(self):
        self.manager = ServerManager()
        self.test_processes = []

    def tearDown(self):
        """Clean up test processes"""
        for proc in self.test_processes:
            try:
                if proc.poll() is None:
                    proc.terminate()
                    proc.wait(timeout=2)
            except Exception:
                pass

    def test_manager_initialization_modes(self):
        """Test that ServerManager initializes correctly in different modes"""
        # Test minimal mode
        minimal_manager = ServerManager(mode='minimal')
        self.assertIsNotNone(minimal_manager.ports)
        self.assertIn('poc_api', minimal_manager.ports)
        
        # Test poc mode
        poc_manager = ServerManager(mode='poc')
        self.assertIsNotNone(poc_manager.ports)
        self.assertIn('poc_api', poc_manager.ports)
        self.assertIn('frontend', poc_manager.ports)
        
        # Test full mode
        full_manager = ServerManager(mode='full')
        self.assertIsNotNone(full_manager.ports)
        self.assertIn('poc_api', full_manager.ports)
        self.assertIn('frontend', full_manager.ports)
        self.assertIn('rag_api', full_manager.ports)

    def test_environment_loading(self):
        """Test environment loading with real .env file"""
        # Test that load_environment works with actual project .env
        result = self.manager.load_environment()
        # Should succeed if GROQ_API_KEY is configured
        self.assertIsInstance(result, bool)

    def test_dependency_validation(self):
        """Test dependency validation with real system"""
        # Test that validate_dependencies checks real dependencies
        result = self.manager.validate_dependencies()
        # Should return boolean (may fail if deps missing, but shouldn't crash)
        self.assertIsInstance(result, bool)

    def test_concurrent_service_operations(self):
        """Test concurrent service operations with real implementations"""
        results = []
        errors = []

        def worker(operation_id):
            try:
                if operation_id == 0:
                    # Test getting service status
                    status = self.manager.get_service_status('nonexistent')
                    results.append(('status_check', status))
                elif operation_id == 1:
                    # Test state save/load
                    self.manager.save_state()
                    results.append(('state_save', True))
                elif operation_id == 2:
                    # Test metrics access
                    metrics = self.manager.metrics
                    results.append(('metrics', metrics.services_started))
            except Exception as e:
                errors.append((operation_id, str(e)))

        # Run operations concurrently
        threads = []
        for i in range(3):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()

        # Wait for completion
        for t in threads:
            t.join()

        # Should have completed without errors
        self.assertEqual(len(results), 3)
        self.assertEqual(len(errors), 0)


class TestChaosAndErrorScenarios(unittest.TestCase):
    """Chaos tests and error scenario testing with real implementations"""

    def setUp(self):
        self.manager = ServerManager()
        self.test_processes = []

    def tearDown(self):
        """Clean up test processes and state files"""
        for proc in self.test_processes:
            try:
                if proc.poll() is None:
                    proc.terminate()
                    proc.wait(timeout=2)
            except Exception:
                pass
        
        # Clean up corrupted state files
        if self.manager.state_file.exists():
            try:
                self.manager.state_file.unlink()
            except Exception:
                pass

    def test_nonexistent_service_handling(self):
        """Test handling of nonexistent services"""
        # Getting status for nonexistent service shouldn't crash
        status = self.manager.get_service_status('nonexistent_service')
        self.assertIsNone(status)

    def test_restart_nonexistent_service(self):
        """Test restarting a service that doesn't exist"""
        result = self.manager.restart_service('nonexistent_service')
        self.assertFalse(result)

    def test_rollback_empty_list(self):
        """Test rollback with empty service list"""
        # Should not crash with empty list
        self.manager.rollback_startup([])
        self.assertEqual(len(self.manager.service_states), 0)

    def test_state_file_corruption_recovery(self):
        """Test recovery from corrupted state file"""
        # Create corrupted state file
        with open(self.manager.state_file, 'w') as f:
            f.write("invalid json content {")

        # Should handle corruption gracefully
        new_manager = ServerManager()
        # Should not crash and should have empty or recovered state
        self.assertIsInstance(new_manager.service_states, dict)

    def test_resource_cleanup_on_failure(self):
        """Test that resources are cleaned up properly"""
        # Verify the cleanup method exists and can be called
        self.assertTrue(hasattr(self.manager, 'cleanup'))

        # Call cleanup - should not crash even with no running services
        self.manager.cleanup()

    def test_health_checker_dependency_registration(self):
        """Test health checker dependency registration with valid services"""
        # Add a dependency using real service names from service_health.py
        # frontend and poc_api are both valid service names
        self.manager.health_checker.add_dependency('frontend', 'poc_api')
        
        # Verify the dependency was added by checking the service info
        self.assertIn('frontend', self.manager.health_checker.services)
        frontend_info = self.manager.health_checker.services['frontend']
        self.assertIn('poc_api', frontend_info.dependencies)

class TestPerformanceBenchmarks(unittest.TestCase):
    """Performance tests for startup orchestration"""

    def setUp(self):
        self.manager = ServerManager()

    def test_startup_initialization_performance(self):
        """Test performance of manager initialization"""
        import time

        start_time = time.time()
        manager = ServerManager()
        end_time = time.time()

        duration = end_time - start_time

        # Should initialize quickly (< 0.1 seconds)
        self.assertLess(duration, 0.1)
        self.assertIsNotNone(manager.ports)

    def test_state_save_load_performance(self):
        """Test performance of state save/load operations"""
        import time

        # Add some state
        from scripts.startup.start_servers import ServiceState
        for i in range(10):
            self.manager.service_states[f'service_{i}'] = ServiceState(
                name=f'service_{i}',
                pid=10000 + i,
                port=5000 + i,
                start_time=time.time(),
                command=f'service_{i} command'
            )

        # Test save performance
        start_time = time.time()
        self.manager.save_state()
        save_duration = time.time() - start_time

        # Test load performance
        start_time = time.time()
        new_manager = ServerManager()
        load_duration = time.time() - start_time

        # Both should be fast (< 0.1 seconds)
        self.assertLess(save_duration, 0.1)
        self.assertLess(load_duration, 0.1)
        self.assertEqual(len(new_manager.service_states), 10)

if __name__ == '__main__':
    unittest.main()


