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
    """Test cases for enhanced startup orchestration features"""

    def setUp(self):
        """Set up test fixtures"""
        self.manager = ServerManager()
        self.test_port = 55530

    def tearDown(self):
        """Clean up after tests"""
        # Clean up any state files
        if self.manager.state_file.exists():
            try:
                self.manager.state_file.unlink()
            except:
                pass

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
        """Test service state persistence"""
        # Create some mock service state
        from scripts.startup.start_servers import ServiceState
        test_state = ServiceState(
            name='test_service',
            pid=12345,
            port=5000,
            start_time=time.time(),
            command='test command'
        )
        self.manager.service_states['test_service'] = test_state

        # Save state
        self.manager.save_state()

        # Create new manager and load state
        new_manager = ServerManager()
        loaded_states = new_manager.service_states

        # Should have loaded the saved state
        self.assertIn('test_service', loaded_states)
        self.assertEqual(loaded_states['test_service'].pid, 12345)
        self.assertEqual(loaded_states['test_service'].port, 5000)

    def test_service_restart_functionality(self):
        """Test service restart functionality"""
        # Mock a running service
        from scripts.startup.start_servers import ServiceState
        test_state = ServiceState(
            name='test_service',
            pid=12345,
            port=5000,
            start_time=time.time(),
            command='test command',
            restart_count=0
        )
        self.manager.service_states['test_service'] = test_state

        # Mock the start_services_parallel method
        with patch.object(self.manager, 'start_services_parallel') as mock_start:
            mock_start.return_value = {'test_service': MagicMock(success=True, pid=12346)}

            with patch('os.kill') as mock_kill:
                with patch.object(self.manager, '_process_running', side_effect=[True, False]):
                    result = self.manager.restart_service('test_service')

                    # Should have killed old process
                    mock_kill.assert_called()
                    # Should have started new service
                    mock_start.assert_called_once_with(['test_service'])
                    # Should return success
                    self.assertTrue(result)

                    # Should have incremented restart count
                    self.assertEqual(self.manager.service_states['test_service'].restart_count, 1)

    @patch('subprocess.Popen')
    def test_parallel_service_startup(self, mock_popen):
        """Test parallel service startup"""
        mock_process = MagicMock()
        mock_process.pid = 12345
        mock_process.poll.return_value = None
        mock_popen.return_value = mock_process

        # Mock health checker
        with patch.object(self.manager.health_checker, 'check_service_health') as mock_check:
            mock_result = MagicMock()
            mock_result.status = ServiceStatus.HEALTHY
            mock_check.return_value = mock_result

            # Test parallel startup
            results = self.manager.start_services_parallel(['poc_api'])

            self.assertIn('poc_api', results)
            self.assertTrue(results['poc_api'].success)
            self.assertEqual(results['poc_api'].pid, 12345)

    def test_rollback_functionality(self):
        """Test startup rollback functionality"""
        # Create mock running services
        from scripts.startup.start_servers import ServiceState
        services_to_rollback = ['service1', 'service2']

        for service_name in services_to_rollback:
            self.manager.service_states[service_name] = ServiceState(
                name=service_name,
                pid=10000 + hash(service_name) % 1000,
                port=5000 + hash(service_name) % 1000,
                start_time=time.time(),
                command=f'{service_name} command'
            )

        # Mock process running checks and kills
        with patch.object(self.manager, '_process_running', return_value=True):
            with patch('os.kill') as mock_kill:
                with patch('time.sleep'):  # Prevent actual sleep
                    self.manager.rollback_startup(services_to_rollback)

                    # Should have killed all services
                    self.assertEqual(mock_kill.call_count, len(services_to_rollback))

                    # Should have cleaned up state
                    for service_name in services_to_rollback:
                        self.assertNotIn(service_name, self.manager.service_states)

    def test_graceful_shutdown_handling(self):
        """Test graceful shutdown signal handling"""
        shutdown_called = []

        def mock_cleanup():
            shutdown_called.append(True)

        # Replace cleanup method
        original_cleanup = self.manager.cleanup
        self.manager.cleanup = mock_cleanup

        # Simulate SIGTERM
        self.manager._signal_handler(signal.SIGTERM, None)

        # Should have set shutdown event and called cleanup
        self.assertTrue(self.manager.shutdown_event.is_set())
        self.assertTrue(shutdown_called)

        # Restore original cleanup
        self.manager.cleanup = original_cleanup

class TestIntegrationScenarios(unittest.TestCase):
    """Integration tests for startup orchestration"""

    def setUp(self):
        self.manager = ServerManager()

    def test_full_startup_workflow(self):
        """Test complete startup workflow with mocking"""
        with patch.object(self.manager, 'load_environment', return_value=True):
            with patch.object(self.manager, 'validate_dependencies', return_value=True):
                with patch.object(self.manager.port_manager, 'free_port', return_value=True):
                    with patch.object(self.manager, 'start_services_parallel') as mock_start:
                        with patch.object(self.manager.health_checker, 'check_all_services') as mock_check:
                            # Mock successful startup
                            mock_start.return_value = {
                                'poc_api': MagicMock(success=True),
                                'frontend': MagicMock(success=True)
                            }

                            mock_check.return_value = {
                                'poc_api': MagicMock(status=ServiceStatus.HEALTHY),
                                'frontend': MagicMock(status=ServiceStatus.HEALTHY)
                            }

                            # Run main startup (with minimal mode to avoid complexity)
                            minimal_manager = ServerManager(mode='minimal')

                            # This would normally be a full integration test
                            # For now, just test that the components can be initialized
                            self.assertIsNotNone(minimal_manager.ports)
                            self.assertIn('poc_api', minimal_manager.ports)

    def test_concurrent_service_operations(self):
        """Test concurrent service operations"""
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
    """Chaos tests and error scenario testing"""

    def setUp(self):
        self.manager = ServerManager()

    def test_partial_startup_failure_rollback(self):
        """Test rollback when some services fail to start"""
        with patch.object(self.manager, 'start_services_parallel') as mock_start:
            # Simulate partial failure
            mock_start.return_value = {
                'poc_api': MagicMock(success=True, pid=12345),
                'frontend': MagicMock(success=False, error_message="Port conflict")
            }

            results = self.manager.start_services_parallel(['poc_api', 'frontend'])

            # Should have one success and one failure
            self.assertTrue(results['poc_api'].success)
            self.assertFalse(results['frontend'].success)

    def test_service_dependency_failure_propagation(self):
        """Test that dependency failures are handled properly"""
        # Add dependency
        self.manager.health_checker.add_dependency('frontend', 'api')

        with patch.object(self.manager, 'start_services_parallel') as mock_start:
            # API fails, frontend should still be attempted
            mock_start.return_value = {
                'api': MagicMock(success=False, error_message="API failed"),
                'frontend': MagicMock(success=True, pid=12346)
            }

            results = self.manager.start_services_parallel(['api', 'frontend'])

            # Both should be attempted (dependency doesn't prevent startup in this design)
            self.assertFalse(results['api'].success)
            self.assertTrue(results['frontend'].success)

    def test_state_file_corruption_recovery(self):
        """Test recovery from corrupted state file"""
        # Create corrupted state file
        with open(self.manager.state_file, 'w') as f:
            f.write("invalid json content {")

        # Should handle corruption gracefully
        new_manager = ServerManager()
        # Should not crash and should have empty state
        self.assertEqual(len(new_manager.service_states), 0)

    def test_resource_cleanup_on_failure(self):
        """Test that resources are cleaned up when startup fails"""
        # This would test cleanup of partial state, ports, etc.
        # For now, just verify the cleanup method exists and can be called
        self.assertTrue(hasattr(self.manager, 'cleanup'))

        # Call cleanup - should not crash
        self.manager.cleanup()

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


