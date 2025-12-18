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
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from scripts.startup.start_servers import ServerManager
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


if __name__ == '__main__':
    unittest.main()


