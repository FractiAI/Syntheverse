#!/usr/bin/env python3
"""
SYNTHVERSE SCRIPTS MENU
=======================

Central menu-based runner for all Syntheverse scripts.
Provides organized access to startup, development, deployment, and utility scripts.
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Import dependency installer
try:
    from .utilities.install_deps import check_dependencies, auto_install_dependencies
except ImportError:
    # Fallback for direct execution
    sys.path.insert(0, str(Path(__file__).parent / 'utilities'))
    from install_deps import check_dependencies, auto_install_dependencies

class ScriptMenu:
    """Menu-based script runner for Syntheverse."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.scripts_dir = Path(__file__).parent
        self.current_category: Optional[str] = None

        # Check dependencies on startup
        self.check_dependencies_on_startup()

    def check_dependencies_on_startup(self):
        """Check and install dependencies on menu startup."""
        print("🔍 Checking system dependencies...")
        try:
            if not check_dependencies():
                print("⚠️  Missing dependencies detected. Installing...")
                if auto_install_dependencies():
                    print("✅ Dependencies installed successfully!")
                else:
                    print("❌ Failed to install dependencies. Some features may not work.")
                print()
        except Exception as e:
            print(f"⚠️  Dependency check failed: {e}")
            print()

        # Script categories and their contents
        self.categories = {
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

    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('clear' if os.name == 'posix' else 'cls')

    def print_header(self, title: str = "", subtitle: str = ""):
        """Print a formatted header."""
        self.clear_screen()
        print("🌟 SYNTHVERSE SCRIPTS MENU")
        print("=" * 50)
        if title:
            print(f"\n{title}")
        if subtitle:
            print(f"{subtitle}")
        print()

    def print_menu(self, category: str):
        """Print the menu for a specific category."""
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

    def print_main_menu(self):
        """Print the main category menu."""
        self.print_header("Choose a category:", "")

        print("Script Categories:")
        print("-" * 20)

        categories = [
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
        """Validate that a script file exists."""
        full_path = self.scripts_dir / script_path
        return full_path.exists()

    def run_script(self, script_info: Dict) -> bool:
        """Execute a script."""
        script_path = script_info["path"]
        script_type = script_info["type"]
        script_name = script_info["name"]

        # Validate script exists
        if not self.validate_script_exists(script_path):
            print(f"❌ Error: Script not found: {script_path}")
            return False

        full_path = self.scripts_dir / script_path

        print(f"🚀 Executing: {script_name}")
        print(f"📁 Path: {full_path}")
        print("-" * 50)

        try:
            # Change to project root directory
            os.chdir(self.project_root)

            if script_type == "python":
                # Run Python script
                cmd = [sys.executable, str(full_path)]
                if "args" in script_info:
                    cmd.extend(script_info["args"])
                result = subprocess.run(cmd, cwd=self.project_root)

            elif script_type == "shell":
                # Run shell script
                result = subprocess.run(["bash", str(full_path)], cwd=self.project_root)

            else:
                print(f"❌ Unknown script type: {script_type}")
                return False

            print("-" * 50)
            if result.returncode == 0:
                print(f"✅ {script_name} completed successfully")
                return True
            else:
                print(f"❌ {script_name} failed with exit code {result.returncode}")
                return False

        except KeyboardInterrupt:
            print(f"\n⚠️  {script_name} interrupted by user")
            return False
        except Exception as e:
            print(f"❌ Error executing {script_name}: {e}")
            return False

    def handle_category_menu(self, category: str):
        """Handle menu interaction for a specific category."""
        while True:
            self.print_menu(category)
            choice = input("Enter your choice: ").strip().lower()

            if choice == "m":
                return  # Back to main menu
            elif choice == "q":
                sys.exit(0)
            elif choice in self.categories[category]["scripts"]:
                script_info = self.categories[category]["scripts"][choice]

                # Confirm execution
                confirm = input(f"Execute '{script_info['name']}'? (y/n): ").strip().lower()
                if confirm == "y":
                    self.run_script(script_info)
                    input("\nPress Enter to continue...")
                else:
                    print("Execution cancelled.")
                    time.sleep(1)
            else:
                print("❌ Invalid choice. Please try again.")
                time.sleep(1)

    def run(self):
        """Main menu loop."""
        print("🌟 Welcome to Syntheverse Scripts Menu!")
        print("Loading script inventory...")

        # Validate all scripts exist
        missing_scripts = []
        for category, cat_info in self.categories.items():
            for script_key, script_info in cat_info["scripts"].items():
                if not self.validate_script_exists(script_info["path"]):
                    missing_scripts.append(script_info["path"])

        if missing_scripts:
            print("⚠️  Warning: Some scripts are missing:")
            for script in missing_scripts:
                print(f"   - {script}")
            print()

        input("Press Enter to continue...")

        while True:
            self.print_main_menu()
            choice = input("Enter your choice: ").strip().lower()

            if choice == "q":
                print("👋 Goodbye!")
                sys.exit(0)
            elif choice in ["1", "2", "3", "4"]:
                category_map = {
                    "1": "startup",
                    "2": "development",
                    "3": "deployment",
                    "4": "utilities"
                }
                category = category_map[choice]
                self.handle_category_menu(category)
            else:
                print("❌ Invalid choice. Please try again.")
                time.sleep(1)

def main():
    """Entry point."""
    try:
        menu = ScriptMenu()
        menu.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
