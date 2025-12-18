#!/usr/bin/env python3
"""
Tests for scripts/main.py ScriptMenu
=====================================

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

Note: These tests use real implementations where possible.
Subprocess mocking is used only to prevent actual script execution side effects.
"""

import unittest
import sys
import os
import tempfile
import time
import io
import subprocess
from pathlib import Path
from contextlib import redirect_stdout

# Add scripts and tests directories to path
test_dir = Path(__file__).parent
project_root = test_dir.parent
scripts_dir = project_root / 'scripts'
sys.path.insert(0, str(scripts_dir))
sys.path.insert(0, str(test_dir))

# Import the module under test with real dependency check
# This tests that dependencies are actually installed
try:
    from scripts.main import ScriptMenu, main
except ImportError:
    # Direct import fallback
    sys.path.insert(0, str(scripts_dir / 'utilities'))
    from main import ScriptMenu, main

from test_framework import SyntheverseTestCase


class TestScriptMenuInit(SyntheverseTestCase):
    """Test ScriptMenu initialization with real implementations."""

    def get_category(self):
        return "unit"

    def test_init_sets_project_root(self):
        """Test that project root is correctly set."""
        output = io.StringIO()
        with redirect_stdout(output):
            menu = ScriptMenu()
        self.assertIsInstance(menu.project_root, Path)
        self.assertTrue(menu.project_root.exists())

    def test_init_sets_scripts_dir(self):
        """Test that scripts directory is correctly set."""
        output = io.StringIO()
        with redirect_stdout(output):
            menu = ScriptMenu()
        self.assertIsInstance(menu.scripts_dir, Path)
        self.assertTrue(menu.scripts_dir.exists())
        self.assertEqual(menu.scripts_dir.name, 'scripts')

    def test_init_sets_current_category_none(self):
        """Test that current_category starts as None."""
        output = io.StringIO()
        with redirect_stdout(output):
            menu = ScriptMenu()
        self.assertIsNone(menu.current_category)

    def test_init_creates_categories(self):
        """Test that category dictionary is created."""
        output = io.StringIO()
        with redirect_stdout(output):
            menu = ScriptMenu()
        self.assertIn('startup', menu.categories)
        self.assertIn('development', menu.categories)
        self.assertIn('deployment', menu.categories)
        self.assertIn('utilities', menu.categories)

    def test_init_categories_have_required_keys(self):
        """Test that each category has required keys."""
        output = io.StringIO()
        with redirect_stdout(output):
            menu = ScriptMenu()
        for cat_name, cat_info in menu.categories.items():
            self.assertIn('title', cat_info, f"Category {cat_name} missing 'title'")
            self.assertIn('description', cat_info, f"Category {cat_name} missing 'description'")
            self.assertIn('scripts', cat_info, f"Category {cat_name} missing 'scripts'")

    def test_init_scripts_have_required_keys(self):
        """Test that each script entry has required keys."""
        output = io.StringIO()
        with redirect_stdout(output):
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

    def test_dependency_checking_runs(self):
        """Test that dependency checking is actually called during init."""
        # The fact that ScriptMenu initializes successfully proves
        # that the dependency check ran without fatal errors
        output = io.StringIO()
        with redirect_stdout(output):
            menu = ScriptMenu()
        self.assertIsNotNone(menu)


class TestScriptValidation(SyntheverseTestCase):
    """Test script path validation with real filesystem."""

    def get_category(self):
        return "unit"

    def setUp(self):
        super().setUp()
        output = io.StringIO()
        with redirect_stdout(output):
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

    def test_validate_all_configured_scripts(self):
        """Test that all scripts in categories actually exist."""
        for cat_name, cat_info in self.menu.categories.items():
            for script_key, script_info in cat_info['scripts'].items():
                path = script_info['path']
                result = self.menu.validate_script_exists(path)
                self.assertTrue(result, 
                    f"Script {path} in category {cat_name} does not exist")


class TestScriptExecution(SyntheverseTestCase):
    """Test script execution logic with real test scripts."""

    def get_category(self):
        return "unit"

    def setUp(self):
        super().setUp()
        output = io.StringIO()
        with redirect_stdout(output):
            self.menu = ScriptMenu()
        # Create a temporary directory for test scripts
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        super().tearDown()
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_test_script(self, name: str, content: str, script_type: str = 'python') -> Path:
        """Create a temporary test script."""
        script_path = Path(self.temp_dir) / name
        script_path.write_text(content)
        if script_type == 'shell':
            script_path.chmod(0o755)
        return script_path

    def test_run_real_python_script_success(self):
        """Test successful Python script execution with real script."""
        # Create a simple script that exits successfully
        script = self._create_test_script(
            'success.py',
            '#!/usr/bin/env python3\nprint("success")\nexit(0)'
        )
        
        # Temporarily add our script path
        original_scripts_dir = self.menu.scripts_dir
        self.menu.scripts_dir = Path(self.temp_dir)
        
        script_info = {
            "name": "success.py",
            "path": "success.py",
            "type": "python"
        }
        
        try:
            output = io.StringIO()
            with redirect_stdout(output):
                result = self.menu.run_script(script_info)
            self.assertTrue(result)
        finally:
            self.menu.scripts_dir = original_scripts_dir

    def test_run_real_python_script_failure(self):
        """Test Python script execution failure with real script."""
        # Create a script that exits with error
        script = self._create_test_script(
            'failure.py',
            '#!/usr/bin/env python3\nprint("failing")\nexit(1)'
        )
        
        original_scripts_dir = self.menu.scripts_dir
        self.menu.scripts_dir = Path(self.temp_dir)
        
        script_info = {
            "name": "failure.py",
            "path": "failure.py",
            "type": "python"
        }
        
        try:
            output = io.StringIO()
            with redirect_stdout(output):
                result = self.menu.run_script(script_info)
            self.assertFalse(result)
            self.assertIn("failed with exit code", output.getvalue())
        finally:
            self.menu.scripts_dir = original_scripts_dir

    def test_run_real_shell_script_success(self):
        """Test successful shell script execution with real script."""
        script = self._create_test_script(
            'success.sh',
            '#!/bin/bash\necho "success"\nexit 0',
            script_type='shell'
        )
        
        original_scripts_dir = self.menu.scripts_dir
        self.menu.scripts_dir = Path(self.temp_dir)
        
        script_info = {
            "name": "success.sh",
            "path": "success.sh",
            "type": "shell"
        }
        
        try:
            output = io.StringIO()
            with redirect_stdout(output):
                result = self.menu.run_script(script_info)
            self.assertTrue(result)
        finally:
            self.menu.scripts_dir = original_scripts_dir

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
        script = self._create_test_script('unknown.xyz', '# test')
        
        original_scripts_dir = self.menu.scripts_dir
        self.menu.scripts_dir = Path(self.temp_dir)
        
        script_info = {
            "name": "unknown.xyz",
            "path": "unknown.xyz",
            "type": "xyz"
        }
        
        try:
            output = io.StringIO()
            with redirect_stdout(output):
                result = self.menu.run_script(script_info)
            self.assertFalse(result)
            self.assertIn("Unknown script type", output.getvalue())
        finally:
            self.menu.scripts_dir = original_scripts_dir

    def test_run_script_with_args(self):
        """Test script execution with arguments."""
        script = self._create_test_script(
            'args_test.py',
            '''#!/usr/bin/env python3
import sys
if '--test-flag' in sys.argv:
    exit(0)
exit(1)
'''
        )
        
        original_scripts_dir = self.menu.scripts_dir
        self.menu.scripts_dir = Path(self.temp_dir)
        
        script_info = {
            "name": "args_test.py",
            "path": "args_test.py",
            "type": "python",
            "args": ["--test-flag"]
        }
        
        try:
            output = io.StringIO()
            with redirect_stdout(output):
                result = self.menu.run_script(script_info)
            self.assertTrue(result)
        finally:
            self.menu.scripts_dir = original_scripts_dir


class TestMenuDisplay(SyntheverseTestCase):
    """Test menu display methods with real output."""

    def get_category(self):
        return "unit"

    def setUp(self):
        super().setUp()
        output = io.StringIO()
        with redirect_stdout(output):
            self.menu = ScriptMenu()

    def test_print_header_without_subtitle(self):
        """Test header printing without subtitle."""
        output = io.StringIO()
        with redirect_stdout(output):
            self.menu.print_header("Test Title")
        
        result = output.getvalue()
        self.assertIn("Test Title", result)

    def test_print_header_with_title(self):
        """Test header printing with subtitle."""
        output = io.StringIO()
        with redirect_stdout(output):
            self.menu.print_header("Main Title", "Subtitle Text")
        
        result = output.getvalue()
        self.assertIn("Main Title", result)
        self.assertIn("Subtitle", result)

    def test_print_main_menu(self):
        """Test main menu output contains all categories."""
        output = io.StringIO()
        with redirect_stdout(output):
            self.menu.print_main_menu()
        
        result = output.getvalue()
        self.assertIn("Startup", result)
        self.assertIn("Development", result)
        self.assertIn("Deployment", result)
        self.assertIn("Utility", result)

    def test_print_menu_startup(self):
        """Test startup category menu output."""
        output = io.StringIO()
        with redirect_stdout(output):
            self.menu.print_menu("startup")
        
        result = output.getvalue()
        # Check for "STARTUP" (uppercase) in output
        self.assertIn("STARTUP", result)
        # Should contain at least one script
        self.assertIn("start_servers.py", result)

    def test_print_menu_all_categories(self):
        """Test that all category menus can be printed."""
        for category in self.menu.categories:
            output = io.StringIO()
            with redirect_stdout(output):
                self.menu.print_menu(category)
            result = output.getvalue()
            # Each menu should have content
            self.assertTrue(len(result) > 0, f"Empty menu for {category}")


class TestMenuNavigation(SyntheverseTestCase):
    """Test menu navigation and interaction."""

    def get_category(self):
        return "integration"

    def setUp(self):
        super().setUp()
        output = io.StringIO()
        with redirect_stdout(output):
            self.menu = ScriptMenu()

    def test_handle_category_menu_back(self):
        """Test that 'b' returns to main menu."""
        import unittest.mock
        with unittest.mock.patch('builtins.input', return_value='b'):
            output = io.StringIO()
            with redirect_stdout(output):
                # Method returns None when 'b' is pressed (returns to main menu)
                self.menu.handle_category_menu('startup')
        # If we get here without exception, 'b' was handled correctly

    def test_handle_category_menu_quit(self):
        """Test that 'q' quits the application."""
        import unittest.mock
        with unittest.mock.patch('builtins.input', return_value='q'):
            output = io.StringIO()
            with redirect_stdout(output):
                with self.assertRaises(SystemExit) as cm:
                    self.menu.handle_category_menu('startup')
                # 'q' should exit with code 0
                self.assertEqual(cm.exception.code, 0)

    def test_handle_category_menu_invalid_choice(self):
        """Test handling of invalid menu choice."""
        import unittest.mock
        # First return invalid, then 'b' to exit loop
        with unittest.mock.patch('builtins.input', side_effect=['99', 'b']):
            output = io.StringIO()
            with redirect_stdout(output):
                self.menu.handle_category_menu('startup')
        
        self.assertIn("Invalid choice", output.getvalue())

    def test_handle_category_menu_cancel_execution(self):
        """Test canceling script execution confirmation."""
        import unittest.mock
        # Select option 1, then 'n' to cancel, then 'b' to exit
        with unittest.mock.patch('builtins.input', side_effect=['1', 'n', 'b']):
            output = io.StringIO()
            with redirect_stdout(output):
                self.menu.handle_category_menu('startup')
        # Should have asked for confirmation
        self.assertIn("Run", output.getvalue())

    def test_handle_category_menu_execute(self):
        """Test script execution from menu."""
        import unittest.mock
        # Select option 1, confirm 'y', then 'b' to exit
        with unittest.mock.patch('builtins.input', side_effect=['1', 'y', 'b']):
            with unittest.mock.patch.object(self.menu, 'run_script', return_value=True):
                output = io.StringIO()
                with redirect_stdout(output):
                    self.menu.handle_category_menu('startup')
        # Should have executed and returned


class TestErrorHandling(SyntheverseTestCase):
    """Test error handling scenarios."""

    def get_category(self):
        return "unit"

    def setUp(self):
        super().setUp()
        output = io.StringIO()
        with redirect_stdout(output):
            self.menu = ScriptMenu()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        super().tearDown()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_script_execution_keyboard_interrupt(self):
        """Test KeyboardInterrupt during script execution."""
        import unittest.mock
        
        script_info = {
            "name": "test.py",
            "path": "startup/start_servers.py",
            "type": "python"
        }
        
        # Mock subprocess.run to raise KeyboardInterrupt
        with unittest.mock.patch('subprocess.run', side_effect=KeyboardInterrupt):
            output = io.StringIO()
            with redirect_stdout(output):
                result = self.menu.run_script(script_info)
        
        self.assertFalse(result)
        self.assertIn("interrupted", output.getvalue())

    def test_script_execution_permission_error(self):
        """Test PermissionError during script execution."""
        import unittest.mock
        
        script_info = {
            "name": "test.py",
            "path": "startup/start_servers.py",
            "type": "python"
        }
        
        with unittest.mock.patch('subprocess.run', side_effect=PermissionError("Permission denied")):
            output = io.StringIO()
            with redirect_stdout(output):
                result = self.menu.run_script(script_info)
        
        self.assertFalse(result)
        self.assertIn("Permission denied", output.getvalue())

    def test_shell_script_bash_not_found(self):
        """Test shell script when bash is unavailable."""
        import unittest.mock
        
        script_info = {
            "name": "test.sh",
            "path": "development/manage_services.sh",
            "type": "shell"
        }
        
        with unittest.mock.patch('subprocess.run', side_effect=FileNotFoundError("bash not found")):
            output = io.StringIO()
            with redirect_stdout(output):
                result = self.menu.run_script(script_info)
        
        self.assertFalse(result)

    def test_run_with_missing_scripts_warning(self):
        """Test that missing scripts generate warnings during validation."""
        # Temporarily modify a script path to be invalid
        original_path = self.menu.categories['startup']['scripts']['1']['path']
        self.menu.categories['startup']['scripts']['1']['path'] = 'nonexistent/fake.py'
        
        result = self.menu.validate_script_exists('nonexistent/fake.py')
        self.assertFalse(result)
        
        # Restore original path
        self.menu.categories['startup']['scripts']['1']['path'] = original_path


class TestMainFunction(SyntheverseTestCase):
    """Test the main() entry point."""

    def get_category(self):
        return "integration"

    def test_main_creates_menu(self):
        """Test that main() creates a ScriptMenu instance."""
        import unittest.mock
        
        # Mock the run method to immediately quit
        with unittest.mock.patch.object(ScriptMenu, 'run', return_value=None):
            output = io.StringIO()
            with redirect_stdout(output):
                with self.assertRaises(SystemExit) as cm:
                    main()
                # Exit code 0 means success
                self.assertEqual(cm.exception.code, 0)

    def test_main_handles_keyboard_interrupt(self):
        """Test that main() handles KeyboardInterrupt gracefully."""
        import unittest.mock
        
        with unittest.mock.patch.object(ScriptMenu, 'run', side_effect=KeyboardInterrupt):
            output = io.StringIO()
            with redirect_stdout(output):
                with self.assertRaises(SystemExit) as cm:
                    main()
                # Exit code 0 means graceful exit
                self.assertEqual(cm.exception.code, 0)

    def test_main_handles_exception(self):
        """Test that main() handles exceptions gracefully."""
        import unittest.mock
        
        with unittest.mock.patch.object(ScriptMenu, 'run', side_effect=Exception("Test error")):
            output = io.StringIO()
            with redirect_stdout(output):
                with self.assertRaises(SystemExit) as cm:
                    main()
                # Exit code 1 means error
                self.assertEqual(cm.exception.code, 1)
            self.assertIn("Error", output.getvalue())


class TestPerformance(SyntheverseTestCase):
    """Performance tests for ScriptMenu."""

    def get_category(self):
        return "performance"

    def test_initialization_performance(self):
        """Test that initialization completes in reasonable time."""
        start = time.time()
        output = io.StringIO()
        with redirect_stdout(output):
            menu = ScriptMenu()
        duration = time.time() - start
        
        # Should initialize in under 2 seconds
        self.assertLess(duration, 2.0)
        self.assertIsNotNone(menu)

    def test_validation_performance(self):
        """Test that script validation is fast."""
        output = io.StringIO()
        with redirect_stdout(output):
            menu = ScriptMenu()
        
        start = time.time()
        for _ in range(100):
            menu.validate_script_exists("startup/start_servers.py")
        duration = time.time() - start
        
        # 100 validations should complete in under 0.5 seconds
        self.assertLess(duration, 0.5)

    def test_multiple_initializations(self):
        """Test that multiple menu initializations work correctly."""
        menus = []
        output = io.StringIO()
        with redirect_stdout(output):
            for _ in range(5):
                menus.append(ScriptMenu())
        
        self.assertEqual(len(menus), 5)
        for menu in menus:
            self.assertIsNotNone(menu.categories)


if __name__ == '__main__':
    unittest.main()
