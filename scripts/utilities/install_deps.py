#!/usr/bin/env python3
"""
Dependency Installer for Syntheverse Scripts
Auto-detects and installs required Python packages and Node.js dependencies
"""

import os
import sys
import subprocess
import importlib.util
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Set

class DependencyInstaller:
    """Handles automatic installation of Python and Node.js dependencies"""

    def __init__(self, logger: logging.Logger = None):
        self.logger = logger or logging.getLogger(__name__)
        self.project_root = Path(__file__).parent.parent.parent

        # Required Python packages for Syntheverse
        self.python_packages = {
            'flask': 'Flask web framework',
            'flask-cors': 'Flask CORS support',
            'werkzeug': 'WSGI utility library',
            'requests': 'HTTP library',
            'web3': 'Web3.py for blockchain',
            'pathlib': 'Path handling (built-in)',
            'typing': 'Type hints (built-in)',
            'subprocess': 'Process management (built-in)',
            'logging': 'Logging (built-in)',
            'json': 'JSON handling (built-in)',
            'time': 'Time utilities (built-in)',
            'os': 'OS interface (built-in)',
            'sys': 'System-specific parameters (built-in)',
            'argparse': 'Command line argument parsing (built-in)',
            'socket': 'Network socket interface (built-in)',
            'signal': 'Signal handling (built-in)',
            'platform': 'Platform information (built-in)',
            'threading': 'Threading support (built-in)',
        }

        # Node.js directories that need npm install
        self.nodejs_dirs = [
            'src/frontend/poc-frontend',
        ]

    def check_python_version(self) -> bool:
        """Check if Python version is 3.8+"""
        if sys.version_info < (3, 8):
            self.logger.error(f"Python {sys.version_info.major}.{sys.version_info.minor} detected. Need Python 3.8+")
            return False
        self.logger.info(f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} detected")
        return True

    def check_system_dependencies(self) -> bool:
        """Check for required system dependencies"""
        success = True

        # Check for Node.js
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version = result.stdout.strip()
                self.logger.info(f"Node.js available: {version}")
            else:
                self.logger.warning("Node.js not found - Next.js frontend will not work")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.logger.warning("Node.js not available - Next.js frontend will not work")

        # Check for npm
        try:
            result = subprocess.run(['npm', '--version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version = result.stdout.strip()
                self.logger.info(f"npm available: {version}")
            else:
                self.logger.warning("npm not found - Node.js dependencies cannot be installed")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.logger.warning("npm not available - Node.js dependencies cannot be installed")

        # Check for lsof (used by port manager)
        try:
            result = subprocess.run(['lsof', '-v'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                self.logger.info("lsof available for port management")
            else:
                self.logger.warning("lsof not available - port management may be limited")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.logger.warning("lsof not available - port management may be limited")

        return success

    def check_python_package(self, package_name: str) -> bool:
        """Check if a Python package is available"""
        try:
            if package_name in ['pathlib', 'typing', 'subprocess', 'logging', 'json', 'time', 'os', 'sys', 'argparse', 'socket', 'signal', 'platform', 'threading']:
                # Built-in modules - always available in Python 3.8+
                return True

            # Try to import the package
            importlib.import_module(package_name.replace('-', '_'))
            return True
        except ImportError:
            return False

    def install_python_package(self, package_name: str) -> bool:
        """Install a Python package using pip"""
        try:
            self.logger.info(f"Installing Python package: {package_name}")

            # Use pip to install
            cmd = [sys.executable, '-m', 'pip', 'install', package_name]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                self.logger.info(f"Successfully installed {package_name}")
                return True
            else:
                self.logger.error(f"Failed to install {package_name}")
                if result.stderr:
                    self.logger.error(f"Error: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            self.logger.error(f"Timeout installing {package_name}")
            return False
        except Exception as e:
            self.logger.error(f"Error installing {package_name}: {e}")
            return False

    def check_nodejs_dependencies(self, dir_path: str) -> bool:
        """Check if Node.js dependencies are installed in a directory"""
        package_json = self.project_root / dir_path / 'package.json'
        node_modules = self.project_root / dir_path / 'node_modules'

        if not package_json.exists():
            return True  # No package.json, so no dependencies to install

        return node_modules.exists() and node_modules.is_dir()

    def install_nodejs_dependencies(self, dir_path: str) -> bool:
        """Install Node.js dependencies in a directory"""
        try:
            full_path = self.project_root / dir_path
            package_json = full_path / 'package.json'

            if not package_json.exists():
                self.logger.debug(f"No package.json in {dir_path}, skipping")
                return True

            if self.check_nodejs_dependencies(dir_path):
                self.logger.debug(f"Dependencies already installed in {dir_path}")
                return True

            self.logger.info(f"Installing Node.js dependencies in {dir_path}")

            # Run npm install
            cmd = ['npm', 'install']
            result = subprocess.run(cmd, cwd=full_path, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                self.logger.info(f"Successfully installed dependencies in {dir_path}")
                return True
            else:
                self.logger.error(f"Failed to install dependencies in {dir_path}")
                if result.stderr:
                    self.logger.error(f"Error: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            self.logger.error(f"Timeout installing dependencies in {dir_path}")
            return False
        except Exception as e:
            self.logger.error(f"Error installing dependencies in {dir_path}: {e}")
            return False

    def check_all_python_packages(self) -> Tuple[List[str], List[str]]:
        """Check which Python packages are available and which are missing"""
        available = []
        missing = []

        for package, description in self.python_packages.items():
            if self.check_python_package(package):
                available.append(package)
            else:
                missing.append(package)

        return available, missing

    def install_missing_python_packages(self, missing_packages: List[str]) -> bool:
        """Install all missing Python packages"""
        success = True

        for package in missing_packages:
            if not self.install_python_package(package):
                success = False

        return success

    def check_all_nodejs_dependencies(self) -> Tuple[List[str], List[str]]:
        """Check Node.js dependencies in all directories"""
        installed = []
        missing = []

        for dir_path in self.nodejs_dirs:
            if self.check_nodejs_dependencies(dir_path):
                installed.append(dir_path)
            else:
                missing.append(dir_path)

        return installed, missing

    def install_missing_nodejs_dependencies(self, missing_dirs: List[str]) -> bool:
        """Install Node.js dependencies in all missing directories"""
        success = True

        for dir_path in missing_dirs:
            if not self.install_nodejs_dependencies(dir_path):
                success = False

        return success

    def auto_install(self, force: bool = False) -> bool:
        """
        Automatically check and install all required dependencies

        Args:
            force: If True, reinstall everything even if already installed

        Returns:
            bool: True if all dependencies are available
        """
        self.logger.info("Checking and installing dependencies...")

        # Check Python version
        if not self.check_python_version():
            return False

        # Check system dependencies
        self.check_system_dependencies()

        # Check Python packages
        available_python, missing_python = self.check_all_python_packages()

        if available_python:
            self.logger.info(f"Python packages available: {', '.join(available_python)}")

        if missing_python:
            self.logger.info(f"Installing missing Python packages: {', '.join(missing_python)}")
            if not self.install_missing_python_packages(missing_python):
                self.logger.error("Failed to install some Python packages")
                return False
        else:
            self.logger.info("All Python packages are available")

        # Check Node.js dependencies
        installed_nodejs, missing_nodejs = self.check_all_nodejs_dependencies()

        if installed_nodejs:
            self.logger.info(f"Node.js dependencies installed in: {', '.join(installed_nodejs)}")

        if missing_nodejs or force:
            if missing_nodejs:
                self.logger.info(f"Installing Node.js dependencies in: {', '.join(missing_nodejs)}")
            elif force:
                self.logger.info("Force reinstalling Node.js dependencies")
                missing_nodejs = self.nodejs_dirs

            if not self.install_missing_nodejs_dependencies(missing_nodejs):
                self.logger.warning("Failed to install some Node.js dependencies - frontend may not work")
                # Don't fail completely for Node.js issues

        self.logger.info("Dependency check complete")
        return True

def auto_install_dependencies(force: bool = False) -> bool:
    """Convenience function to auto-install all dependencies"""
    installer = DependencyInstaller()
    return installer.auto_install(force)

def check_dependencies() -> bool:
    """Check if all dependencies are available without installing"""
    installer = DependencyInstaller()
    installer.logger.info("Checking dependencies (no installation)...")

    # Check Python version
    if not installer.check_python_version():
        return False

    # Check system dependencies
    installer.check_system_dependencies()

    # Check Python packages
    _, missing_python = installer.check_all_python_packages()
    if missing_python:
        installer.logger.error(f"Missing Python packages: {', '.join(missing_python)}")
        return False

    # Check Node.js dependencies
    _, missing_nodejs = installer.check_all_nodejs_dependencies()
    if missing_nodejs:
        installer.logger.warning(f"Missing Node.js dependencies in: {', '.join(missing_nodejs)}")
        # Don't fail for Node.js issues

    return True

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Install Syntheverse dependencies')
    parser.add_argument('--force', action='store_true', help='Force reinstall all dependencies')
    parser.add_argument('--check-only', action='store_true', help='Check dependencies without installing')

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    if args.check_only:
        success = check_dependencies()
    else:
        success = auto_install_dependencies(force=args.force)

    sys.exit(0 if success else 1)
