#!/usr/bin/env python3
"""
Comprehensive tests for scripts/main.py ScriptMenu
===================================================

Tests the menu-based script runner with:
- Unit tests for core methods
- Integration tests for menu workflows
- Error scenario tests
- Performance benchmarks

Test Categories:
- TestScriptMenuInit: Initialization and dependency checking
- TestScriptValidation: Script path validation
- TestScriptExecution: Script execution logic
- TestMenuDisplay: Output formatting methods
- TestMenuNavigation: Menu interaction and navigation
- TestErrorHandling: Error scenarios and recovery
- TestPerformance: Initialization and execution performance
"""

import unittest
import sys
import os
import tempfile
import time
import io
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from contextlib import redirect_stdout

# Add scripts and tests directories to path
test_dir = Path(__file__).parent
project_root = test_dir.parent
scripts_dir = project_root / 'scripts'
sys.path.insert(0, str(scripts_dir))
sys.path.insert(0, str(test_dir))

# Import the module under test
# Mock dependency functions during import to avoid side effects
with patch('scripts.utilities.install_deps.check_dependencies', return_value=True):
    with patch('scripts.utilities.install_deps.auto_install_dependencies', return_value=True):
        try:
            from scripts.main import ScriptMenu, main
        except ImportError:
            # Direct import fallback
            sys.path.insert(0, str(scripts_dir / 'utilities'))
            from main import ScriptMenu, main

from test_framework import SyntheverseTestCase


class TestScriptMenuInit(SyntheverseTestCase):
    """Test ScriptMenu initialization."""

    def get_category(self):
        return "unit"

    @patch('scripts.main.check_dependencies', return_value=True)
    @patch('scripts.main.auto_install_dependencies', return_value=True)
    def test_init_sets_project_root(self, mock_auto, mock_check):
        """Test that project root is correctly set."""
        menu = ScriptMenu()
        self.assertIsInstance(menu.project_root, Path)
        self.assertTrue(menu.project_root.exists())

    @patch('scripts.main.check_dependencies', return_value=True)
    @patch('scripts.main.auto_install_dependencies', return_value=True)
    def test_init_sets_scripts_dir(self, mock_auto, mock_check):
        """Test that scripts directory is correctly set."""
        menu = ScriptMenu()
        self.assertIsInstance(menu.scripts_dir, Path)
        self.assertTrue(menu.scripts_dir.exists())
        self.assertEqual(menu.scripts_dir.name, 'scripts')

    @patch('scripts.main.check_dependencies', return_value=True)
    @patch('scripts.main.auto_install_dependencies', return_value=True)
    def test_init_sets_current_category_none(self, mock_auto, mock_check):
        """Test that current_category starts as None."""
        menu = ScriptMenu()
        self.assertIsNone(menu.current_category)

    @patch('scripts.main.check_dependencies', return_value=True)
    @patch('scripts.main.auto_install_dependencies', return_value=True)
    def test_init_creates_categories(self, mock_auto, mock_check):
        """Test that category dictionary is created."""
        menu = ScriptMenu()
        self.assertIn('startup', menu.categories)
        self.assertIn('development', menu.categories)
        self.assertIn('deployment', menu.categories)
        self.assertIn('utilities', menu.categories)

    @patch('scripts.main.check_dependencies', return_value=True)
    @patch('scripts.main.auto_install_dependencies', return_value=True)
    def test_init_categories_have_required_keys(self, mock_auto, mock_check):
        """Test that each category has required keys."""
        menu = ScriptMenu()
        for cat_name, cat_info in menu.categories.items():
            self.assertIn('title', cat_info, f"Category {cat_name} missing 'title'")
            self.assertIn('description', cat_info, f"Category {cat_name} missing 'description'")
            self.assertIn('scripts', cat_info, f"Category {cat_name} missing 'scripts'")

    @patch('scripts.main.check_dependencies', return_value=True)
    @patch('scripts.main.auto_install_dependencies', return_value=True)
    def test_init_scripts_have_required_keys(self, mock_auto, mock_check):
        """Test that each script entry has required keys."""
        menu = ScriptMenu()
        for cat_name, cat_info in menu.categories.items():
            for script_key, script_info in cat_info['scripts'].items():
                self.assertIn('name', script_info, 
                    f"Script {script_key} in {cat_name} missing 'name'")
                self.assertIn('description', script_info,
                    f"Script {script_key} in {cat_name} missing 'description'")
                self.assertIn('path', script_info,
                    f"Script {script_key} in {cat_name} missing 'path'")
                self.assertIn('type', script_info,
                    f"Script {script_key} in {cat_name} missing 'type'")

    @patch('scripts.main.check_dependencies', return_value=False)
    @patch('scripts.main.auto_install_dependencies', return_value=True)
    def test_init_installs_missing_dependencies(self, mock_auto, mock_check):
        """Test that missing dependencies trigger installation."""
        with redirect_stdout(io.StringIO()):
            menu = ScriptMenu()
        mock_auto.assert_called_once()

    @patch('scripts.main.check_dependencies', return_value=False)
    @patch('scripts.main.auto_install_dependencies', return_value=False)
    def test_init_handles_installation_failure(self, mock_auto, mock_check):
        """Test that installation failure is handled gracefully."""
        output = io.StringIO()
        with redirect_stdout(output):
            menu = ScriptMenu()
        self.assertIn('Failed to install', output.getvalue())

    @patch('scripts.main.check_dependencies', side_effect=Exception("Check failed"))
    @patch('scripts.main.auto_install_dependencies', return_value=True)
    def test_init_handles_check_exception(self, mock_auto, mock_check):
        """Test that dependency check exception is handled."""
        output = io.StringIO()
        with redirect_stdout(output):
            menu = ScriptMenu()
        self.assertIn('Dependency check failed', output.getvalue())


class TestScriptValidation(SyntheverseTestCase):
    """Test script path validation."""

    def get_category(self):
        return "unit"

    def setUp(self):
        super().setUp()
        with patch('scripts.main.check_dependencies', return_value=True):
            with patch('scripts.main.auto_install_dependencies', return_value=True):
                with redirect_stdout(io.StringIO()):
                    self.menu = ScriptMenu()

    def test_validate_existing_script(self):
        """Test validation of existing script path."""
        result = self.menu.validate_script_exists("startup/start_servers.py")
        self.assertTrue(result)

    def test_validate_nonexistent_script(self):
        """Test validation of nonexistent script path."""
        result = self.menu.validate_script_exists("nonexistent/fake_script.py")
        self.assertFalse(result)

    def test_validate_empty_path(self):
        """Test validation of empty path."""
        result = self.menu.validate_script_exists("")
        # Empty path should still evaluate based on directory existence
        self.assertIsInstance(result, bool)

    def test_validate_relative_path(self):
        """Test validation with relative path components."""
        result = self.menu.validate_script_exists("startup/../startup/start_servers.py")
        # Path normalization should still find the file
        self.assertTrue(result)

    def test_validate_shell_script(self):
        """Test validation of shell script."""
        result = self.menu.validate_script_exists("development/manage_services.sh")
        self.assertTrue(result)

    def test_validate_utility_script(self):
        """Test validation of utility scripts."""
        result = self.menu.validate_script_exists("utilities/install_deps.py")
        self.assertTrue(result)


class TestScriptExecution(SyntheverseTestCase):
    """Test script execution logic."""

    def get_category(self):
        return "unit"

    def setUp(self):
        super().setUp()
        with patch('scripts.main.check_dependencies', return_value=True):
            with patch('scripts.main.auto_install_dependencies', return_value=True):
                with redirect_stdout(io.StringIO()):
                    self.menu = ScriptMenu()

    @patch('subprocess.run')
    def test_run_python_script_success(self, mock_run):
        """Test successful Python script execution."""
        mock_run.return_value = MagicMock(returncode=0)
        
        script_info = {
            "name": "test_script.py",
            "path": "startup/start_servers.py",
            "type": "python"
        }
        
        with redirect_stdout(io.StringIO()):
            result = self.menu.run_script(script_info)
        
        self.assertTrue(result)
        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_run_python_script_with_args(self, mock_run):
        """Test Python script execution with arguments."""
        mock_run.return_value = MagicMock(returncode=0)
        
        script_info = {
            "name": "test_script.py",
            "path": "startup/start_servers.py",
            "type": "python",
            "args": ["--mode", "minimal"]
        }
        
        with redirect_stdout(io.StringIO()):
            result = self.menu.run_script(script_info)
        
        self.assertTrue(result)
        # Verify args were passed
        call_args = mock_run.call_args[0][0]
        self.assertIn("--mode", call_args)
        self.assertIn("minimal", call_args)

    @patch('subprocess.run')
    def test_run_shell_script_success(self, mock_run):
        """Test successful shell script execution."""
        mock_run.return_value = MagicMock(returncode=0)
        
        script_info = {
            "name": "manage_services.sh",
            "path": "development/manage_services.sh",
            "type": "shell"
        }
        
        with redirect_stdout(io.StringIO()):
            result = self.menu.run_script(script_info)
        
        self.assertTrue(result)
        mock_run.assert_called_once()
        # Verify bash was used
        call_args = mock_run.call_args[0][0]
        self.assertEqual(call_args[0], "bash")

    @patch('subprocess.run')
    def test_run_script_failure(self, mock_run):
        """Test script execution failure handling."""
        mock_run.return_value = MagicMock(returncode=1)
        
        script_info = {
            "name": "failing_script.py",
            "path": "startup/start_servers.py",
            "type": "python"
        }
        
        output = io.StringIO()
        with redirect_stdout(output):
            result = self.menu.run_script(script_info)
        
        self.assertFalse(result)
        self.assertIn("failed with exit code", output.getvalue())

    def test_run_nonexistent_script(self):
        """Test running nonexistent script."""
        script_info = {
            "name": "fake.py",
            "path": "nonexistent/fake.py",
            "type": "python"
        }
        
        output = io.StringIO()
        with redirect_stdout(output):
            result = self.menu.run_script(script_info)
        
        self.assertFalse(result)
        self.assertIn("Script not found", output.getvalue())

    def test_run_unknown_script_type(self):
        """Test running script with unknown type."""
        # Create a temp script to pass validation
        with tempfile.NamedTemporaryFile(suffix='.xyz', dir=self.menu.scripts_dir, delete=False) as f:
            temp_path = Path(f.name)
            f.write(b"test content")
        
        try:
            script_info = {
                "name": "unknown.xyz",
                "path": temp_path.name,
                "type": "unknown"
            }
            
            output = io.StringIO()
            with redirect_stdout(output):
                result = self.menu.run_script(script_info)
            
            self.assertFalse(result)
            self.assertIn("Unknown script type", output.getvalue())
        finally:
            temp_path.unlink()

    @patch('subprocess.run', side_effect=Exception("Subprocess failed"))
    def test_run_script_exception(self, mock_run):
        """Test script execution with subprocess exception."""
        script_info = {
            "name": "test.py",
            "path": "startup/start_servers.py",
            "type": "python"
        }
        
        output = io.StringIO()
        with redirect_stdout(output):
            result = self.menu.run_script(script_info)
        
        self.assertFalse(result)
        self.assertIn("Error executing", output.getvalue())


class TestMenuDisplay(SyntheverseTestCase):
    """Test menu display methods."""

    def get_category(self):
        return "unit"

    def setUp(self):
        super().setUp()
        with patch('scripts.main.check_dependencies', return_value=True):
            with patch('scripts.main.auto_install_dependencies', return_value=True):
                with redirect_stdout(io.StringIO()):
                    self.menu = ScriptMenu()

    @patch('os.system')
    def test_clear_screen_posix(self, mock_system):
        """Test screen clearing on POSIX systems."""
        with patch('os.name', 'posix'):
            self.menu.clear_screen()
            mock_system.assert_called_with('clear')

    @patch('os.system')
    def test_clear_screen_windows(self, mock_system):
        """Test screen clearing on Windows."""
        with patch('os.name', 'nt'):
            self.menu.clear_screen()
            mock_system.assert_called_with('cls')

    @patch.object(ScriptMenu, 'clear_screen')
    def test_print_header_with_title(self, mock_clear):
        """Test header printing with title."""
        output = io.StringIO()
        with redirect_stdout(output):
            self.menu.print_header("Test Title", "Test Subtitle")
        
        result = output.getvalue()
        self.assertIn("SYNTHVERSE SCRIPTS MENU", result)
        self.assertIn("Test Title", result)
        self.assertIn("Test Subtitle", result)

    @patch.object(ScriptMenu, 'clear_screen')
    def test_print_header_empty(self, mock_clear):
        """Test header printing without title/subtitle."""
        output = io.StringIO()
        with redirect_stdout(output):
            self.menu.print_header()
        
        result = output.getvalue()
        self.assertIn("SYNTHVERSE SCRIPTS MENU", result)

    @patch.object(ScriptMenu, 'print_header')
    def test_print_menu_startup(self, mock_header):
        """Test printing startup category menu."""
        output = io.StringIO()
        with redirect_stdout(output):
            self.menu.print_menu("startup")
        
        result = output.getvalue()
        self.assertIn("Available scripts:", result)
        self.assertIn("start_servers.py", result)
        self.assertIn("Navigation:", result)
        self.assertIn("Main menu", result)

    @patch.object(ScriptMenu, 'print_header')
    def test_print_main_menu(self, mock_header):
        """Test printing main menu."""
        output = io.StringIO()
        with redirect_stdout(output):
            self.menu.print_main_menu()
        
        result = output.getvalue()
        self.assertIn("Script Categories:", result)
        self.assertIn("Startup Scripts", result)
        self.assertIn("Development Scripts", result)
        self.assertIn("Deployment Scripts", result)
        self.assertIn("Utility Scripts", result)


class TestMenuNavigation(SyntheverseTestCase):
    """Test menu navigation and interaction."""

    def get_category(self):
        return "integration"

    def setUp(self):
        super().setUp()
        with patch('scripts.main.check_dependencies', return_value=True):
            with patch('scripts.main.auto_install_dependencies', return_value=True):
                with redirect_stdout(io.StringIO()):
                    self.menu = ScriptMenu()

    @patch.object(ScriptMenu, 'print_menu')
    @patch('builtins.input', return_value='m')
    def test_handle_category_menu_back(self, mock_input, mock_print):
        """Test returning to main menu."""
        # Should return without error
        self.menu.handle_category_menu("startup")

    @patch.object(ScriptMenu, 'print_menu')
    @patch('builtins.input', return_value='q')
    def test_handle_category_menu_quit(self, mock_input, mock_print):
        """Test quitting from category menu."""
        with self.assertRaises(SystemExit) as cm:
            self.menu.handle_category_menu("startup")
        self.assertEqual(cm.exception.code, 0)

    @patch.object(ScriptMenu, 'print_menu')
    @patch.object(ScriptMenu, 'run_script', return_value=True)
    @patch('builtins.input', side_effect=['1', 'y', '', 'm'])
    def test_handle_category_menu_execute(self, mock_input, mock_run, mock_print):
        """Test executing a script from menu."""
        self.menu.handle_category_menu("startup")
        mock_run.assert_called_once()

    @patch.object(ScriptMenu, 'print_menu')
    @patch('builtins.input', side_effect=['1', 'n', 'm'])
    @patch('time.sleep')
    def test_handle_category_menu_cancel_execution(self, mock_sleep, mock_input, mock_print):
        """Test cancelling script execution."""
        output = io.StringIO()
        with redirect_stdout(output):
            self.menu.handle_category_menu("startup")
        self.assertIn("cancelled", output.getvalue())

    @patch.object(ScriptMenu, 'print_menu')
    @patch('builtins.input', side_effect=['invalid', 'm'])
    @patch('time.sleep')
    def test_handle_category_menu_invalid_choice(self, mock_sleep, mock_input, mock_print):
        """Test invalid menu choice."""
        output = io.StringIO()
        with redirect_stdout(output):
            self.menu.handle_category_menu("startup")
        self.assertIn("Invalid choice", output.getvalue())


class TestErrorHandling(SyntheverseTestCase):
    """Test error scenarios and recovery."""

    def get_category(self):
        return "error"

    def setUp(self):
        super().setUp()
        with patch('scripts.main.check_dependencies', return_value=True):
            with patch('scripts.main.auto_install_dependencies', return_value=True):
                with redirect_stdout(io.StringIO()):
                    self.menu = ScriptMenu()

    @patch('subprocess.run', side_effect=KeyboardInterrupt)
    def test_script_execution_keyboard_interrupt(self, mock_run):
        """Test handling keyboard interrupt during script execution."""
        script_info = {
            "name": "test.py",
            "path": "startup/start_servers.py",
            "type": "python"
        }
        
        output = io.StringIO()
        with redirect_stdout(output):
            result = self.menu.run_script(script_info)
        
        self.assertFalse(result)
        self.assertIn("interrupted", output.getvalue())

    @patch('subprocess.run', side_effect=PermissionError("Permission denied"))
    def test_script_execution_permission_error(self, mock_run):
        """Test handling permission error during script execution."""
        script_info = {
            "name": "test.py",
            "path": "startup/start_servers.py",
            "type": "python"
        }
        
        output = io.StringIO()
        with redirect_stdout(output):
            result = self.menu.run_script(script_info)
        
        self.assertFalse(result)
        self.assertIn("Error executing", output.getvalue())

    @patch('subprocess.run', side_effect=FileNotFoundError("bash not found"))
    def test_shell_script_bash_not_found(self, mock_run):
        """Test handling missing bash for shell scripts."""
        script_info = {
            "name": "test.sh",
            "path": "development/manage_services.sh",
            "type": "shell"
        }
        
        output = io.StringIO()
        with redirect_stdout(output):
            result = self.menu.run_script(script_info)
        
        self.assertFalse(result)

    @patch('scripts.main.check_dependencies', return_value=True)
    @patch('scripts.main.auto_install_dependencies', return_value=True)
    def test_run_with_missing_scripts_warning(self, mock_auto, mock_check):
        """Test warning for missing scripts during run."""
        with redirect_stdout(io.StringIO()):
            menu = ScriptMenu()
        
        # Temporarily add a fake script
        menu.categories['startup']['scripts']['99'] = {
            'name': 'fake.py',
            'description': 'Fake script',
            'path': 'nonexistent/fake.py',
            'type': 'python'
        }
        
        output = io.StringIO()
        with redirect_stdout(output):
            with patch('builtins.input', return_value='q'):
                with self.assertRaises(SystemExit):
                    menu.run()
        
        self.assertIn("scripts are missing", output.getvalue())


class TestMainFunction(SyntheverseTestCase):
    """Test the main() entry point."""

    def get_category(self):
        return "integration"

    @patch('scripts.main.ScriptMenu')
    def test_main_creates_menu(self, mock_menu_class):
        """Test that main creates a ScriptMenu instance."""
        mock_instance = MagicMock()
        mock_menu_class.return_value = mock_instance
        
        try:
            main()
        except SystemExit:
            pass
        
        mock_menu_class.assert_called_once()

    @patch('scripts.main.ScriptMenu')
    def test_main_handles_keyboard_interrupt(self, mock_menu_class):
        """Test that main handles keyboard interrupt gracefully."""
        mock_menu_class.side_effect = KeyboardInterrupt()
        
        output = io.StringIO()
        with redirect_stdout(output):
            with self.assertRaises(SystemExit) as cm:
                main()
        
        self.assertEqual(cm.exception.code, 0)
        self.assertIn("Goodbye", output.getvalue())

    @patch('scripts.main.ScriptMenu')
    def test_main_handles_exception(self, mock_menu_class):
        """Test that main handles exceptions gracefully."""
        mock_menu_class.side_effect = Exception("Fatal error")
        
        output = io.StringIO()
        with redirect_stdout(output):
            with self.assertRaises(SystemExit) as cm:
                main()
        
        self.assertEqual(cm.exception.code, 1)
        self.assertIn("Fatal error", output.getvalue())


class TestPerformance(SyntheverseTestCase):
    """Performance benchmarks for ScriptMenu."""

    def get_category(self):
        return "performance"

    def test_initialization_performance(self):
        """Test menu initialization is fast."""
        start_time = time.time()
        
        with patch('scripts.main.check_dependencies', return_value=True):
            with patch('scripts.main.auto_install_dependencies', return_value=True):
                with redirect_stdout(io.StringIO()):
                    menu = ScriptMenu()
        
        duration = time.time() - start_time
        self.assertLess(duration, 0.5, f"Initialization took {duration:.2f}s, expected < 0.5s")

    def test_validation_performance(self):
        """Test script validation is fast."""
        with patch('scripts.main.check_dependencies', return_value=True):
            with patch('scripts.main.auto_install_dependencies', return_value=True):
                with redirect_stdout(io.StringIO()):
                    menu = ScriptMenu()
        
        start_time = time.time()
        
        # Validate all scripts
        for cat_name, cat_info in menu.categories.items():
            for script_key, script_info in cat_info['scripts'].items():
                menu.validate_script_exists(script_info['path'])
        
        duration = time.time() - start_time
        self.assertLess(duration, 0.1, f"Validation took {duration:.2f}s, expected < 0.1s")

    def test_multiple_initializations(self):
        """Test multiple menu initializations are consistent."""
        with patch('scripts.main.check_dependencies', return_value=True):
            with patch('scripts.main.auto_install_dependencies', return_value=True):
                with redirect_stdout(io.StringIO()):
                    start_time = time.time()
                    
                    for _ in range(10):
                        menu = ScriptMenu()
                    
                    duration = time.time() - start_time
        
        self.assertLess(duration, 2.0, f"10 initializations took {duration:.2f}s")


if __name__ == '__main__':
    unittest.main()

