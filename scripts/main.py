#!/usr/bin/env python3
"""
Syntheverse Scripts Menu
========================

Central menu-based runner for all Syntheverse scripts.
Provides organized access to startup, development, deployment, and utility scripts.

Usage:
    python scripts/main.py

    Or from the scripts directory:
    python main.py

Classes:
    ScriptMenu: Menu-based script runner with category organization.

Functions:
    main: Entry point that creates and runs the ScriptMenu.

Example - Adding a new script category:
    # Add to self.categories in __init__:
    "custom": {
        "title": "Custom Scripts",
        "description": "Custom workflow scripts",
        "scripts": {
            "1": {
                "name": "my_script.py",
                "description": "Description of script",
                "path": "custom/my_script.py",
                "type": "python",  # or "shell"
                "args": ["--option", "value"]  # optional
            }
        }
    }
"""

import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import dependency installer
try:
    from .utilities.install_deps import check_dependencies, auto_install_dependencies
except ImportError:
    # Fallback for direct execution
    sys.path.insert(0, str(Path(__file__).parent / 'utilities'))
    from install_deps import check_dependencies, auto_install_dependencies


class ScriptMenu:
    """
    Menu-based script runner for Syntheverse.

    Provides an interactive terminal menu for executing scripts organized
    by category (startup, development, deployment, utilities).

    Attributes:
        project_root: Path to the project root directory.
        scripts_dir: Path to the scripts directory.
        current_category: Currently selected category (None if at main menu).
        categories: Dictionary of script categories and their scripts.

    Example:
        menu = ScriptMenu()
        menu.run()  # Start interactive menu loop
    """

    def __init__(self) -> None:
        """
        Initialize the ScriptMenu.

        Sets up paths, checks dependencies, and initializes the category
        dictionary with all available scripts.

        Raises:
            No exceptions raised; dependency failures are handled gracefully.
        """
        self.project_root: Path = Path(__file__).parent.parent
        self.scripts_dir: Path = Path(__file__).parent
        self.current_category: Optional[str] = None

        logger.debug(f"Project root: {self.project_root}")
        logger.debug(f"Scripts directory: {self.scripts_dir}")

        # Check dependencies on startup
        self.check_dependencies_on_startup()

    def check_dependencies_on_startup(self) -> None:
        """
        Check and install dependencies on menu startup.

        Runs dependency checks and attempts auto-installation if any are
        missing. Failures are logged but do not prevent menu operation.
        """
        print("🔍 Checking system dependencies...")
        try:
            if not check_dependencies():
                print("⚠️  Missing dependencies detected. Installing...")
                logger.warning("Missing dependencies detected, attempting installation")
                if auto_install_dependencies():
                    print("✅ Dependencies installed successfully!")
                    logger.info("Dependencies installed successfully")
                else:
                    print("❌ Failed to install dependencies. Some features may not work.")
                    logger.error("Failed to install dependencies")
                print()
        except Exception as e:
            print(f"⚠️  Dependency check failed: {e}")
            logger.exception(f"Dependency check failed: {e}")
            print()

        # Script categories and their contents
        self.categories: Dict[str, Dict[str, Any]] = {
            "startup": {
                "title": "🚀 STARTUP SCRIPTS",
                "description": "Server startup, management, and orchestration",
                "scripts": {
                    "1": {
                        "name": "start_servers.py (full)",
                        "description": "Full system startup (all services)",
                        "path": "startup/start_servers.py",
                        "type": "python",
                        "args": ["--mode", "full"]
                    },
                    "2": {
                        "name": "start_servers.py (poc)",
                        "description": "PoC system startup (API + Frontend)",
                        "path": "startup/start_servers.py",
                        "type": "python",
                        "args": ["--mode", "poc"]
                    },
                    "4": {
                        "name": "start_servers.py (minimal)",
                        "description": "Minimal startup (PoC API only)",
                        "path": "startup/start_servers.py",
                        "type": "python",
                        "args": ["--mode", "minimal"]
                    },
                    "5": {
                        "name": "anvil_manager.py",
                        "description": "Anvil blockchain manager",
                        "path": "startup/anvil_manager.py",
                        "type": "python"
                    },
                    "6": {
                        "name": "port_manager.py",
                        "description": "Port conflict resolution manager",
                        "path": "startup/port_manager.py",
                        "type": "python"
                    },
                    "7": {
                        "name": "service_health.py",
                        "description": "Service health monitoring",
                        "path": "startup/service_health.py",
                        "type": "python"
                    }
                }
            },
            "development": {
                "title": "🛠️  DEVELOPMENT SCRIPTS",
                "description": "Development workflow and service management",
                "scripts": {
                    "1": {
                        "name": "manage_services.sh (start poc)",
                        "description": "Start PoC UI development environment",
                        "path": "development/manage_services.sh",
                        "type": "shell",
                        "args": ["start", "poc"]
                    },
                    "2": {
                        "name": "manage_services.sh (start all)",
                        "description": "Start all development services",
                        "path": "development/manage_services.sh",
                        "type": "shell",
                        "args": ["start", "all"]
                    },
                    "3": {
                        "name": "manage_services.sh (stop poc)",
                        "description": "Stop PoC UI services",
                        "path": "development/manage_services.sh",
                        "type": "shell",
                        "args": ["stop", "poc"]
                    },
                    "4": {
                        "name": "manage_services.sh (stop all)",
                        "description": "Stop all development services",
                        "path": "development/manage_services.sh",
                        "type": "shell",
                        "args": ["stop", "all"]
                    },
                    "5": {
                        "name": "manage_services.sh (status)",
                        "description": "Show service status",
                        "path": "development/manage_services.sh",
                        "type": "shell",
                        "args": ["status"]
                    },
                }
            },
            "deployment": {
                "title": "📦 DEPLOYMENT SCRIPTS",
                "description": "Smart contract deployment and blockchain management",
                "scripts": {
                    "1": {
                        "name": "deploy_contracts.py",
                        "description": "Deploy SYNTH and POCRegistry contracts",
                        "path": "deployment/deploy_contracts.py",
                        "type": "python"
                    }
                }
            },
            "utilities": {
                "title": "🧹 UTILITY SCRIPTS",
                "description": "System maintenance and administration tools",
                "scripts": {
                    "1": {
                        "name": "install_deps.py",
                        "description": "Install system dependencies",
                        "path": "utilities/install_deps.py",
                        "type": "python"
                    },
                    "2": {
                        "name": "clear_state.py",
                        "description": "Clear system state files",
                        "path": "utilities/clear_state.py",
                        "type": "python"
                    }
                }
            }
        }

    def clear_screen(self) -> None:
        """
        Clear the terminal screen.

        Uses 'clear' on POSIX systems and 'cls' on Windows.
        """
        os.system('clear' if os.name == 'posix' else 'cls')

    def print_header(self, title: str = "", subtitle: str = "") -> None:
        """
        Print a formatted header.

        Args:
            title: Main title text to display below the menu banner.
            subtitle: Subtitle text to display below the title.
        """
        self.clear_screen()
        print("🌟 SYNTHVERSE SCRIPTS MENU")
        print("=" * 50)
        if title:
            print(f"\n{title}")
        if subtitle:
            print(f"{subtitle}")
        print()

    def print_menu(self, category: str) -> None:
        """
        Print the menu for a specific category.

        Args:
            category: Category key (e.g., 'startup', 'development').

        Raises:
            KeyError: If category does not exist in self.categories.
        """
        cat_info = self.categories[category]
        self.print_header(cat_info["title"], cat_info["description"])

        print("Available scripts:")
        print("-" * 30)

        for key, script in cat_info["scripts"].items():
            print(f"  {key}. {script['name']} - {script['description']}")

        print()
        print("Navigation:")
        print("  m. Main menu")
        print("  q. Quit")
        print()
        print("-" * 50)

    def print_main_menu(self) -> None:
        """
        Print the main category menu.

        Displays all available categories with their descriptions.
        """
        self.print_header("Choose a category:", "")

        print("Script Categories:")
        print("-" * 20)

        categories: List[tuple] = [
            ("1", "startup", "🚀 Startup Scripts"),
            ("2", "development", "🛠️  Development Scripts"),
            ("3", "deployment", "📦 Deployment Scripts"),
            ("4", "utilities", "🧹 Utility Scripts")
        ]

        for num, cat_key, cat_title in categories:
            cat_info = self.categories[cat_key]
            print(f"  {num}. {cat_title}")
            print(f"     {cat_info['description']}")

        print()
        print("Navigation:")
        print("  q. Quit")
        print()
        print("-" * 50)

    def validate_script_exists(self, script_path: str) -> bool:
        """
        Validate that a script file exists.

        Args:
            script_path: Relative path to script from scripts directory.

        Returns:
            True if the script file exists, False otherwise.
        """
        full_path = self.scripts_dir / script_path
        exists = full_path.exists()
        logger.debug(f"Validating script {script_path}: exists={exists}")
        return exists

    def run_script(self, script_info: Dict[str, Any]) -> bool:
        """
        Execute a script.

        Args:
            script_info: Dictionary containing script metadata:
                - name: Display name of the script
                - path: Relative path from scripts directory
                - type: Script type ('python' or 'shell')
                - args: Optional list of arguments

        Returns:
            True if script executed successfully (exit code 0), False otherwise.

        Raises:
            No exceptions raised; all errors are caught and logged.
        """
        script_path: str = script_info["path"]
        script_type: str = script_info["type"]
        script_name: str = script_info["name"]

        logger.info(f"Attempting to execute: {script_name}")

        # Validate script exists
        if not self.validate_script_exists(script_path):
            print(f"❌ Error: Script not found: {script_path}")
            logger.error(f"Script not found: {script_path}")
            return False

        full_path = self.scripts_dir / script_path

        print(f"🚀 Executing: {script_name}")
        print(f"📁 Path: {full_path}")
        print("-" * 50)

        try:
            # Change to project root directory
            os.chdir(self.project_root)
            logger.debug(f"Changed working directory to: {self.project_root}")

            if script_type == "python":
                # Run Python script
                cmd: List[str] = [sys.executable, str(full_path)]
                if "args" in script_info:
                    cmd.extend(script_info["args"])
                logger.info(f"Running Python command: {' '.join(cmd)}")
                result = subprocess.run(cmd, cwd=self.project_root)

            elif script_type == "shell":
                # Run shell script
                cmd = ["bash", str(full_path)]
                if "args" in script_info:
                    cmd.extend(script_info["args"])
                logger.info(f"Running shell command: {' '.join(cmd)}")
                result = subprocess.run(cmd, cwd=self.project_root)

            else:
                print(f"❌ Unknown script type: {script_type}")
                logger.error(f"Unknown script type: {script_type}")
                return False

            print("-" * 50)
            if result.returncode == 0:
                print(f"✅ {script_name} completed successfully")
                logger.info(f"{script_name} completed with exit code 0")
                return True
            else:
                print(f"❌ {script_name} failed with exit code {result.returncode}")
                logger.warning(f"{script_name} failed with exit code {result.returncode}")
                return False

        except KeyboardInterrupt:
            print(f"\n⚠️  {script_name} interrupted by user")
            logger.warning(f"{script_name} interrupted by user")
            return False
        except Exception as e:
            print(f"❌ Error executing {script_name}: {e}")
            logger.exception(f"Error executing {script_name}: {e}")
            return False

    def handle_category_menu(self, category: str) -> None:
        """
        Handle menu interaction for a specific category.

        Runs an interactive loop for the category menu, allowing the user
        to select and execute scripts, return to main menu, or quit.

        Args:
            category: Category key to display and handle.

        Raises:
            SystemExit: When user chooses to quit (exit code 0).
        """
        logger.debug(f"Entering category menu: {category}")
        while True:
            self.print_menu(category)
            choice = input("Enter your choice: ").strip().lower()
            logger.debug(f"User choice in {category}: {choice}")

            if choice == "m":
                logger.debug("Returning to main menu")
                return  # Back to main menu
            elif choice == "q":
                logger.info("User quit from category menu")
                sys.exit(0)
            elif choice in self.categories[category]["scripts"]:
                script_info = self.categories[category]["scripts"][choice]

                # Confirm execution
                confirm = input(f"Execute '{script_info['name']}'? (y/n): ").strip().lower()
                if confirm == "y":
                    logger.info(f"User confirmed execution of {script_info['name']}")
                    self.run_script(script_info)
                    input("\nPress Enter to continue...")
                else:
                    print("Execution cancelled.")
                    logger.info(f"User cancelled execution of {script_info['name']}")
                    time.sleep(1)
            else:
                print("❌ Invalid choice. Please try again.")
                logger.debug(f"Invalid choice: {choice}")
                time.sleep(1)

    def run(self) -> None:
        """
        Main menu loop.

        Validates all scripts on startup, shows warnings for missing scripts,
        then runs the interactive main menu until the user quits.

        Raises:
            SystemExit: When user chooses to quit (exit code 0).
        """
        print("🌟 Welcome to Syntheverse Scripts Menu!")
        print("Loading script inventory...")
        logger.info("Starting Syntheverse Scripts Menu")

        # Validate all scripts exist
        missing_scripts: List[str] = []
        for category, cat_info in self.categories.items():
            for script_key, script_info in cat_info["scripts"].items():
                if not self.validate_script_exists(script_info["path"]):
                    missing_scripts.append(script_info["path"])

        if missing_scripts:
            print("⚠️  Warning: Some scripts are missing:")
            for script in missing_scripts:
                print(f"   - {script}")
            logger.warning(f"Missing scripts: {missing_scripts}")
            print()

        input("Press Enter to continue...")

        while True:
            self.print_main_menu()
            choice = input("Enter your choice: ").strip().lower()
            logger.debug(f"Main menu choice: {choice}")

            if choice == "q":
                print("👋 Goodbye!")
                logger.info("User quit from main menu")
                sys.exit(0)
            elif choice in ["1", "2", "3", "4"]:
                category_map: Dict[str, str] = {
                    "1": "startup",
                    "2": "development",
                    "3": "deployment",
                    "4": "utilities"
                }
                category = category_map[choice]
                self.handle_category_menu(category)
            else:
                print("❌ Invalid choice. Please try again.")
                logger.debug(f"Invalid main menu choice: {choice}")
                time.sleep(1)


def main() -> None:
    """
    Entry point for the Scripts Menu.

    Creates a ScriptMenu instance and runs it. Handles keyboard interrupts
    and other exceptions gracefully.

    Raises:
        SystemExit: Always exits with code 0 (success) or 1 (error).
    """
    try:
        menu = ScriptMenu()
        menu.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        logger.info("Menu terminated by keyboard interrupt")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
