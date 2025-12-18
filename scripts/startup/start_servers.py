#!/usr/bin/env python3
"""
Syntheverse PoC System Startup Script
Cross-platform server launcher for the Syntheverse PoC ecosystem
"""

import os
import sys
import time
import signal
import subprocess
import webbrowser
import logging
import argparse
import json
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
from dataclasses import dataclass
from enum import Enum

# Set up logger
logger = logging.getLogger(__name__)

# Import port management module
try:
    from .port_manager import PortManager, free_port
except ImportError:
    # Fallback for direct execution
    sys.path.insert(0, str(Path(__file__).parent))
    from port_manager import PortManager, free_port

# Import dependency installer
try:
    from ..utilities.install_deps import auto_install_dependencies
except ImportError:
    # Fallback for direct execution
    sys.path.insert(0, str(Path(__file__).parent.parent / 'utilities'))
    from install_deps import auto_install_dependencies

# Import health checker for dependencies
try:
    from .service_health import ServiceHealthChecker, ServiceStatus, get_startup_order
except ImportError:
    # Fallback for direct execution
    sys.path.insert(0, str(Path(__file__).parent))
    from service_health import ServiceHealthChecker, ServiceStatus, get_startup_order

class ServiceProfile(Enum):
    """Service startup profiles"""
    DEVELOPMENT = "dev"
    TESTING = "test"
    PRODUCTION = "prod"
    MINIMAL = "minimal"

@dataclass
class ServiceState:
    """State information for a running service"""
    name: str
    pid: int
    port: int
    start_time: float
    command: str
    status: str = "running"
    restart_count: int = 0
    last_restart: Optional[float] = None

@dataclass
class StartupResult:
    """Result of a service startup attempt"""
    service_name: str
    success: bool
    pid: Optional[int] = None
    port: Optional[int] = None
    error_message: Optional[str] = None
    start_time: Optional[float] = None

class StartupMetrics:
    """Performance metrics for startup process"""
    def __init__(self):
        self.start_time = time.time()
        self.services_started = 0
        self.services_failed = 0
        self.total_startup_time = 0.0
        self.port_cleanup_time = 0.0
        self.health_check_time = 0.0
        self.parallel_startup = False

class ServerManager:
    def __init__(self, mode: str = 'full', profile: ServiceProfile = ServiceProfile.DEVELOPMENT):
        """
        Initialize server manager with enhanced startup orchestration.

        Args:
            mode: Startup mode - 'full' (all services), 'poc' (PoC system only), 'minimal' (PoC API only)
            profile: Service profile for configuration (dev/test/prod/minimal)
        """
        self.mode = mode
        self.profile = profile
        self.project_root = Path(__file__).parent.parent.parent
        self.processes: List[Tuple[subprocess.Popen, str, int]] = []
        self.service_states: Dict[str, ServiceState] = {}

        # State persistence
        self.state_file = self.project_root / ".syntheverse" / "startup_state.json"
        self.state_file.parent.mkdir(exist_ok=True)

        # Performance metrics
        self.metrics = StartupMetrics()

        # Thread pool for parallel startup
        self.executor = ThreadPoolExecutor(max_workers=4)

        # Service profiles configuration
        self._service_profiles = self._build_service_profiles()

        # Define ports based on mode and profile
        self.ports = self._get_ports_for_mode(mode, profile)

        # Set up logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # Remove existing handlers to avoid duplicates
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        # Add console handler with colored output
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        # Initialize port manager and health checker
        self.port_manager = PortManager(self.logger)
        self.health_checker = ServiceHealthChecker(self.logger)

        # Load previous state if exists
        self._load_state()

        # Graceful shutdown handling
        self.shutdown_event = threading.Event()
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    def _build_service_profiles(self) -> Dict[ServiceProfile, Dict[str, Any]]:
        """Build service profiles with different configurations"""
        return {
            ServiceProfile.DEVELOPMENT: {
                'parallel_startup': True,
                'health_check_timeout': 30,
                'auto_restart': True,
                'log_level': 'DEBUG',
                'env_overrides': {}
            },
            ServiceProfile.TESTING: {
                'parallel_startup': False,  # Sequential for testing predictability
                'health_check_timeout': 60,
                'auto_restart': False,
                'log_level': 'INFO',
                'env_overrides': {'FLASK_ENV': 'testing'}
            },
            ServiceProfile.PRODUCTION: {
                'parallel_startup': True,
                'health_check_timeout': 120,
                'auto_restart': True,
                'log_level': 'WARNING',
                'env_overrides': {'FLASK_ENV': 'production'}
            },
            ServiceProfile.MINIMAL: {
                'parallel_startup': False,
                'health_check_timeout': 15,
                'auto_restart': False,
                'log_level': 'INFO',
                'env_overrides': {}
            }
        }

    def _get_ports_for_mode(self, mode: str, profile: ServiceProfile) -> Dict[str, int]:
        """Get port configuration based on mode and profile"""
        base_ports = {
            'poc_api': 5001,     # PoC API
            'rag_api': 8000,     # RAG API (FastAPI)
            'frontend': 3001,    # Next.js frontend
            'demo': 8999         # Demo port
        }

        # Profile-specific port adjustments
        if profile == ServiceProfile.TESTING:
            # Use different ports for testing to avoid conflicts
            base_ports = {k: v + 1000 for k, v in base_ports.items()}

        # Mode-based filtering
        if mode == 'poc':
            # PoC system only: API + Frontend
            ports = {k: v for k, v in base_ports.items() if k in ['poc_api', 'frontend']}
        elif mode == 'minimal':
            # Minimal mode: PoC API only
            ports = {k: v for k, v in base_ports.items() if k in ['poc_api']}
        else:  # 'full' mode
            ports = base_ports

        return ports

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.shutdown_event.set()
        self.cleanup()

    def _load_state(self):
        """Load previous startup state from disk"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    state_data = json.load(f)

                # Restore service states
                for service_name, state_dict in state_data.get('services', {}).items():
                    self.service_states[service_name] = ServiceState(**state_dict)

                self.logger.info(f"Loaded previous state for {len(self.service_states)} services")

            except (json.JSONDecodeError, KeyError) as e:
                self.logger.warning(f"Could not load startup state: {e}")

    def save_state(self):
        """Save current startup state to disk"""
        state_data = {
            'timestamp': time.time(),
            'mode': self.mode,
            'profile': self.profile.value,
            'services': {
                name: {
                    'name': state.name,
                    'pid': state.pid,
                    'port': state.port,
                    'start_time': state.start_time,
                    'command': state.command,
                    'status': state.status,
                    'restart_count': state.restart_count,
                    'last_restart': state.last_restart
                }
                for name, state in self.service_states.items()
            }
        }

        try:
            with open(self.state_file, 'w') as f:
                json.dump(state_data, f, indent=2)
            self.logger.debug(f"Saved state for {len(self.service_states)} services")
        except Exception as e:
            self.logger.warning(f"Could not save startup state: {e}")

    def get_service_status(self, service_name: str) -> Optional[ServiceState]:
        """Get status of a specific service"""
        return self.service_states.get(service_name)

    def print_header(self):
        print("🌟 SYNTHVERSE PoC SYSTEM STARTUP")
        print("=" * 50)

    def print_status(self, message, status="✅"):
        """Print colored status message"""
        colors = {
            "✅": "\033[0;32m",  # Green
            "❌": "\033[0;31m",  # Red
            "⚠️": "\033[1;33m",   # Yellow
            "ℹ️": "\033[0;34m",   # Blue
        }
        color = colors.get(status, "")
        reset = "\033[0m" if color else ""
        print(f"{color}{status} {message}{reset}")

        # Also log the message
        if status == "✅":
            self.logger.info(message)
        elif status == "❌":
            self.logger.error(message)
        elif status == "⚠️":
            self.logger.warning(message)
        else:
            self.logger.info(message)

    def load_environment(self):
        """Load environment variables from .env file and validate required variables"""
        env_file = self.project_root / ".env"
        loaded_vars = 0

        # Load environment variables from .env file if it exists
        if env_file.exists():
            self.print_status("Loading environment configuration from .env file...", "ℹ️")
            try:
                with open(env_file, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue

                        if '=' not in line:
                            self.logger.warning(f"Skipping malformed line {line_num} in .env file: {line}")
                            continue

                        try:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip()

                            # Validate key format
                            if not key:
                                self.logger.warning(f"Skipping line {line_num}: empty key")
                                continue

                            # Remove quotes if present
                            if (value.startswith('"') and value.endswith('"')) or \
                               (value.startswith("'") and value.endswith("'")):
                                value = value[1:-1]

                            os.environ[key] = value
                            loaded_vars += 1
                            self.logger.debug(f"Loaded environment variable: {key}")

                        except ValueError as e:
                            self.logger.warning(f"Error parsing line {line_num} in .env file: {e}")
                            continue

                self.print_status(f"Environment variables loaded from .env file ({loaded_vars} variables)", "✅")

            except (IOError, OSError) as e:
                self.print_status(f"Failed to read .env file: {e}", "❌")
                return False
            except UnicodeDecodeError as e:
                self.print_status(f"Invalid encoding in .env file: {e}", "❌")
                return False
            except Exception as e:
                self.print_status(f"Unexpected error loading .env file: {e}", "❌")
                return False

        # Validate required environment variables
        required_vars = ['GROQ_API_KEY']
        missing_vars = []
        invalid_vars = []

        for var in required_vars:
            value = os.getenv(var)
            if not value:
                missing_vars.append(var)
            elif not value.strip():
                invalid_vars.append(var)
            elif var == 'GROQ_API_KEY' and not value.startswith(('gsk_', 'sk-')):
                self.logger.warning(f"GROQ_API_KEY doesn't appear to be a valid API key format")

        if missing_vars:
            self.print_status(f"Missing required environment variables: {', '.join(missing_vars)}", "❌")
            self.print_status("Please set the missing variables in your .env file or environment", "ℹ️")
            self.print_status("Example: GROQ_API_KEY=gsk_your-api-key-here", "ℹ️")
            return False

        if invalid_vars:
            self.print_status(f"Empty required environment variables: {', '.join(invalid_vars)}", "❌")
            return False

        # Show GROQ_API_KEY status (masked for security)
        groq_key = os.getenv('GROQ_API_KEY', '')
        if groq_key:
            masked_key = groq_key[:15] + "..." if len(groq_key) > 15 else groq_key
            self.print_status(f"GROQ_API_KEY configured ({masked_key})", "✅")
            return True
        else:
            self.print_status("GROQ_API_KEY not found", "❌")
            return False

    def validate_dependencies(self):
        """Validate that required files and dependencies exist"""
        validation_passed = True

        # Check required Python files exist
        required_files = [
            ("PoC API", self.project_root / "src" / "api" / "poc-api" / "app.py"),
        ]

        for service_name, file_path in required_files:
            if not file_path.exists():
                self.print_status(f"Required file not found: {file_path}", "❌")
                validation_passed = False
            else:
                self.print_status(f"{service_name} file found: {file_path.name}", "✅")

        # Check Next.js frontend directory (optional)
        frontend_dir = self.project_root / "src" / "frontend" / "poc-frontend"
        if frontend_dir.exists():
            self.print_status("Next.js frontend directory found", "✅")

            # Check if node_modules exists
            if (frontend_dir / "node_modules").exists():
                self.print_status("Next.js dependencies installed", "✅")
            else:
                self.print_status("Next.js dependencies not installed - run 'npm install' in frontend directory", "⚠️")

            # Check if package.json exists
            if (frontend_dir / "package.json").exists():
                self.print_status("Next.js package.json found", "✅")
            else:
                self.print_status("Next.js package.json not found", "⚠️")
        else:
            self.print_status("Next.js frontend directory not found - Next.js UI will not be available", "⚠️")

        # Check Python dependencies
        required_packages = ['flask', 'flask_cors', 'werkzeug', 'requests']
        missing_packages = []

        for package in required_packages:
            try:
                # Handle special import cases
                if package == 'flask_cors':
                    import flask_cors
                else:
                    __import__(package)
                self.print_status(f"Python package '{package}' available", "✅")
            except ImportError:
                missing_packages.append(package)
                validation_passed = False

        if missing_packages:
            self.print_status(f"Missing Python packages: {', '.join(missing_packages)}", "❌")
            self.print_status("Install with: pip install flask flask-cors werkzeug requests", "ℹ️")

        # Check Node.js availability (for Next.js frontend)
        if frontend_dir.exists():
            try:
                result = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    self.print_status(f"Node.js available: {result.stdout.strip()}", "✅")

                    result = subprocess.run(['npm', '--version'], capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        self.print_status(f"npm available: {result.stdout.strip()}", "✅")
                    else:
                        self.print_status("npm not available - Next.js frontend may not start", "⚠️")
                else:
                    self.print_status("Node.js not available - Next.js frontend will not start", "⚠️")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                self.print_status("Node.js/npm not available - Next.js frontend will not start", "⚠️")

        return validation_passed


    def check_port_available(self, port, name, force_cleanup=True):
        """Check if a port is available, with optional force cleanup"""
        if force_cleanup:
            # Use port manager for comprehensive port management
            success = self.port_manager.free_port(port, name)
            if success:
                self.print_status(f"Port {port} ({name}) is available", "✅")
                return True
            else:
                self.print_status(f"Port {port} ({name}) could not be freed", "❌")
                return False
        else:
            # Just check availability without cleanup
            available = self.port_manager.check_port_available(port)
            if available:
                self.print_status(f"Port {port} ({name}) is available", "✅")
                return True
            else:
                self.print_status(f"Port {port} ({name}) is in use", "❌")
                return False

    def start_server(self, command, name, port, cwd=None, env=None):
        """Start a server process"""
        self.print_status(f"Starting {name} on port {port}...", "ℹ️")

        try:
            # Set environment variables - inherit from current environment or use provided env
            if env is None:
                env = os.environ.copy()
            env['FLASK_SKIP_DOTENV'] = '1'

            # Ensure PYTHONPATH is set correctly for Python services
            pythonpath = f"{self.project_root}/src/core:{self.project_root}/src:{self.project_root}"
            if 'PYTHONPATH' in env:
                env['PYTHONPATH'] = f"{pythonpath}:{env['PYTHONPATH']}"
            else:
                env['PYTHONPATH'] = pythonpath

            # Ensure GROQ_API_KEY is available for PoC services
            if 'poc' in name.lower() and 'GROQ_API_KEY' not in env:
                groq_key = os.getenv('GROQ_API_KEY')
                if groq_key:
                    env['GROQ_API_KEY'] = groq_key

            # Handle command - convert list to string if needed for shell=True
            if isinstance(command, list):
                command = ' '.join(command)

            # Start process
            working_dir = cwd if cwd is not None else self.project_root
            process = subprocess.Popen(
                command,
                shell=True,
                cwd=working_dir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            self.processes.append((process, name, port))

            # Wait for server to start
            time.sleep(3)

            # Check if process is still running
            if process.poll() is None:
                self.print_status(f"{name} started successfully", "✅")

                # Test connectivity with correct endpoints
                try:
                    import requests
                    url = f"http://127.0.0.1:{port}"
                    
                    # Use correct health check endpoints for each service
                    if port == self.ports.get('poc_api'):
                        url += "/health"
                    elif port == self.ports.get('rag_api'):
                        url += "/health"
                    # For frontend, just check root endpoint

                    response = requests.get(url, timeout=5)
                    if 200 <= response.status_code < 400:
                        self.print_status(f"{name} responding on port {port}", "✅")
                    else:
                        self.print_status(f"{name} started but returned status {response.status_code}", "⚠️")
                except ImportError:
                    self.print_status(f"{name} process running (connectivity test skipped)", "✅")
                except Exception as e:
                    self.print_status(f"{name} started but connectivity test failed ({str(e)[:30]}...)", "⚠️")

                return True
            else:
                stdout, stderr = process.communicate()
                self.print_status(f"{name} failed to start", "❌")
                if stderr:
                    logger.error(f"Service startup error: {stderr.decode()[:200]}...")
                return False

        except Exception as e:
            self.print_status(f"Failed to start {name}: {str(e)}", "❌")
            return False

    def start_services_parallel(self, services: List[str]) -> Dict[str, StartupResult]:
        """Start services in parallel respecting dependencies"""
        self.logger.info(f"Starting {len(services)} services in parallel")
        self.metrics.parallel_startup = True

        # Get optimal startup order based on dependencies
        startup_order = get_startup_order()
        ordered_services = [s for s in startup_order if s in services]

        results = {}
        futures = {}

        # Submit all services for parallel startup
        for service_name in ordered_services:
            future = self.executor.submit(self._start_service_async, service_name)
            futures[future] = service_name

        # Collect results as they complete
        for future in as_completed(futures):
            service_name = futures[future]
            try:
                result = future.result()
                results[service_name] = result

                if result.success:
                    self.metrics.services_started += 1
                    self.print_status(f"✅ {service_name} started successfully", "✅")
                else:
                    self.metrics.services_failed += 1
                    self.print_status(f"❌ {service_name} failed: {result.error_message}", "❌")

            except Exception as e:
                self.metrics.services_failed += 1
                results[service_name] = StartupResult(
                    service_name=service_name,
                    success=False,
                    error_message=f"Exception during startup: {str(e)}"
                )
                self.print_status(f"❌ {service_name} failed with exception: {str(e)}", "❌")

        return results

    def _start_service_async(self, service_name: str) -> StartupResult:
        """Start a single service asynchronously"""
        start_time = time.time()
        command = None  # Initialize command for tracking

        try:
            if service_name == 'poc_api':
                command = f"{sys.executable} src/api/poc-api/app.py"
                success = self.start_server(command, "PoC API Server", self.ports['poc_api'])
                port = self.ports['poc_api'] if success else None

            elif service_name == 'rag_api':
                success = self.start_rag_api()
                port = self.ports['rag_api'] if success else None
                command = f"{sys.executable} rag_api.py"  # Track command for state

            elif service_name == 'frontend':
                frontend_dir = self.project_root / "src" / "frontend" / "poc-frontend"
                if frontend_dir.exists():
                    # Check if node_modules exist
                    if not (frontend_dir / "node_modules").exists():
                        self.logger.info("Installing Next.js dependencies...")
                        install_result = subprocess.run(
                            ["npm", "install"],
                            cwd=frontend_dir,
                            capture_output=True,
                            text=True,
                            timeout=120
                        )
                        if install_result.returncode != 0:
                            return StartupResult(
                                service_name=service_name,
                                success=False,
                                error_message=f"npm install failed: {install_result.stderr[:100]}"
                            )
                    
                    # Use next dev with proper port configuration
                    # Set PORT via environment variable for Next.js
                    env = os.environ.copy()
                    env['PORT'] = str(self.ports['frontend'])
                    env['NODE_ENV'] = 'development'
                    
                    # Start Next.js in development mode
                    command = "npm run dev"
                    success = self.start_server(
                        command, 
                        "Next.js Frontend", 
                        self.ports['frontend'], 
                        cwd=frontend_dir,
                        env=env
                    )
                    port = self.ports['frontend'] if success else None
                else:
                    self.logger.warning(f"Frontend directory not found: {frontend_dir}")
                    success = False
                    port = None
                    command = "npm run dev"  # Track attempted command

            else:
                return StartupResult(
                    service_name=service_name,
                    success=False,
                    error_message=f"Unknown service: {service_name}"
                )

            # Track service state if successful
            if success and port:
                # Find the process that was just started
                for process, name, proc_port in self.processes:
                    if proc_port == port and process.poll() is None:
                        self.service_states[service_name] = ServiceState(
                            name=service_name,
                            pid=process.pid,
                            port=port,
                            start_time=start_time,
                            command=command or f"Service: {service_name}"
                        )
                        break

            return StartupResult(
                service_name=service_name,
                success=success,
                pid=self.service_states.get(service_name).pid if success and service_name in self.service_states else None,
                port=port,
                start_time=start_time
            )

        except Exception as e:
            return StartupResult(
                service_name=service_name,
                success=False,
                error_message=str(e),
                start_time=start_time
            )

    def rollback_startup(self, started_services: List[str]):
        """Rollback partially started services"""
        self.logger.info(f"Rolling back {len(started_services)} services")

        for service_name in reversed(started_services):  # Reverse order for dependencies
            if service_name in self.service_states:
                state = self.service_states[service_name]

                try:
                    # Kill the process
                    os.kill(state.pid, signal.SIGTERM)

                    # Wait for process to terminate
                    for _ in range(10):  # Wait up to 1 second
                        if not self._process_running(state.pid):
                            break
                        time.sleep(0.1)

                    # Force kill if still running
                    if self._process_running(state.pid):
                        os.kill(state.pid, signal.SIGKILL)

                    self.print_status(f"✅ Rolled back {service_name}", "✅")

                except (OSError, ProcessLookupError):
                    self.print_status(f"⚠️ {service_name} already stopped", "⚠️")

                # Clean up state
                del self.service_states[service_name]

        # Save updated state
        self.save_state()

    def _process_running(self, pid: int) -> bool:
        """Check if a process is still running"""
        try:
            os.kill(pid, 0)  # Signal 0 doesn't kill, just checks if process exists
            return True
        except OSError:
            return False

    def restart_service(self, service_name: str) -> bool:
        """Restart a specific service"""
        if service_name not in self.service_states:
            self.logger.warning(f"Service {service_name} is not currently running")
            return False

        state = self.service_states[service_name]

        # Increment restart count
        state.restart_count += 1
        state.last_restart = time.time()

        self.logger.info(f"Restarting {service_name} (attempt {state.restart_count})")

        # Stop the service
        try:
            os.kill(state.pid, signal.SIGTERM)
            time.sleep(1)

            if self._process_running(state.pid):
                os.kill(state.pid, signal.SIGKILL)
                time.sleep(0.5)
        except (OSError, ProcessLookupError):
            pass  # Process already dead

        # Clean up old state
        del self.service_states[service_name]

        # Restart the service
        results = self.start_services_parallel([service_name])
        result = results.get(service_name)

        if result and result.success:
            self.save_state()
            self.print_status(f"✅ {service_name} restarted successfully", "✅")
            return True
        else:
            self.print_status(f"❌ {service_name} restart failed", "❌")
            return False

    def start_rag_api(self):
        """Start the RAG API server"""
        self.print_status("Starting RAG API Server...", "ℹ️")

        rag_api_dir = self.project_root / "src" / "api" / "rag_api" / "api"

        if not rag_api_dir.exists():
            self.print_status("RAG API directory not found - skipping", "⚠️")
            self.logger.warning("RAG API directory not found")
            return False

        # Set environment variables for RAG API
        env = os.environ.copy()
        env['PYTHONPATH'] = f"{self.project_root}/src:{self.project_root}"

        # Check for GROQ API key
        if not os.getenv('GROQ_API_KEY'):
            self.print_status("GROQ_API_KEY not set - RAG API may have limited functionality", "⚠️")
            self.logger.warning("GROQ_API_KEY not set for RAG API")

        cmd = [sys.executable, "rag_api.py"]
        return self.start_server(cmd, "RAG API Server", self.ports['rag_api'],
                                cwd=rag_api_dir)

    def cleanup(self):
        """Clean up all running processes"""
        self.print_status("Shutting down servers...", "ℹ️")

        for process, name, port in self.processes:
            try:
                if process.poll() is None:
                    process.terminate()
                    time.sleep(1)
                    if process.poll() is None:
                        process.kill()
                self.print_status(f"{name} stopped", "✅")
            except Exception as e:
                self.print_status(f"Error stopping {name}: {e}", "❌")

        # Clean up service states for stopped processes
        for service_name in list(self.service_states.keys()):
            state = self.service_states[service_name]
            if not self._process_running(state.pid):
                del self.service_states[service_name]

        self.processes.clear()
        self.save_state()

    def _print_startup_metrics(self):
        """Print startup performance metrics"""
        print("\n📊 STARTUP PERFORMANCE METRICS:")
        print("=" * 40)
        print(f"Profile:           {self.profile.value}")
        print(f"Mode:              {self.mode}")
        print(f"Parallel Startup:  {self.metrics.parallel_startup}")
        print(f"Total Time:        {self.metrics.total_startup_time:.2f}s")
        print(f"Port Cleanup:      {self.metrics.port_cleanup_time:.2f}s")
        print(f"Health Check:      {self.metrics.health_check_time:.2f}s")
        print(f"Services Started:  {self.metrics.services_started}")
        print(f"Services Failed:   {self.metrics.services_failed}")

        if self.service_states:
            print(f"Active Services:   {len(self.service_states)}")
            for name, state in self.service_states.items():
                uptime = time.time() - state.start_time
                print(f"  - {name}: PID {state.pid}, {uptime:.1f}s uptime")

        print("=" * 40)

    def validate_service_readiness(self, started_services, timeout=20):
        """Validate that started services are actually responding with improved retry logic"""
        import requests

        ready_services = []
        self.print_status(f"Validating service health (timeout: {timeout}s)...", "ℹ️")

        for service in started_services:
            # Determine URLs based on service name
            urls = []
            if "poc_api" in service.lower() or "poc api" in service.lower():
                urls = [
                    (f"http://127.0.0.1:{self.ports.get('poc_api', 5001)}/health", "PoC API health endpoint")
                ]
            elif "rag_api" in service.lower() or "rag api" in service.lower():
                urls = [
                    (f"http://127.0.0.1:{self.ports.get('rag_api', 8000)}/health", "RAG API health endpoint"),
                    (f"http://127.0.0.1:{self.ports.get('rag_api', 8000)}/", "RAG API root")
                ]
            elif "next" in service.lower() or "frontend" in service.lower():
                urls = [(f"http://127.0.0.1:{self.ports.get('frontend', 3001)}/", "Next.js UI")]
            else:
                self.logger.warning(f"Unknown service type: {service}")
                continue

            service_ready = False

            # Try each endpoint for this service
            for url, endpoint_name in urls:
                # Exponential backoff retry logic
                max_retries = min(timeout // 2, 10)  # Max 10 retries
                for attempt in range(max_retries):
                    try:
                        response = requests.get(url, timeout=3)
                        if 200 <= response.status_code < 300:  # Accept 2xx status codes
                            ready_services.append(service)
                            self.print_status(f"✅ {service} is responding (status: {response.status_code})", "✅")
                            service_ready = True
                            break
                        elif response.status_code == 404:
                            # 404 means server is running but endpoint doesn't exist
                            # This is OK for some services (e.g. checking wrong endpoint)
                            continue
                        else:
                            self.logger.debug(f"{service} returned status {response.status_code}")
                    except requests.exceptions.ConnectionError:
                        # Connection failed - service might still be starting
                        if attempt < max_retries - 1:
                            wait_time = min(2 ** (attempt // 2), 3)  # Slower exponential backoff, max 3s
                            self.logger.debug(f"{service} not ready, retrying in {wait_time}s...")
                            time.sleep(wait_time)
                        else:
                            self.logger.debug(f"{service} connection failed after {max_retries} attempts")
                    except requests.exceptions.Timeout:
                        if attempt < max_retries - 1:
                            self.logger.debug(f"{service} timeout, retrying...")
                            time.sleep(1)
                        else:
                            self.logger.debug(f"{service} timeout after {max_retries} attempts")
                    except Exception as e:
                        self.logger.debug(f"{service} health check error: {str(e)[:50]}...")
                        break

                if service_ready:
                    break

            if not service_ready:
                self.print_status(f"⚠️ {service} not responding yet (may still be starting)", "⚠️")

        return ready_services

    def run_demo(self):
        """Run the system demo"""
        os.chdir(self.project_root)
        subprocess.run([sys.executable, "demo_poc_system.py"])

    def main(self):
        """Main startup sequence"""
        self.print_header()

        print("\n" + "="*50)
        self.print_status("Step 0: Loading environment configuration...", "ℹ️")

        # Load and validate environment variables
        if not self.load_environment():
            self.print_status("Environment validation failed. Please configure required variables.", "❌")
            return

        print("\n" + "="*50)
        self.print_status("Step 0.5: Installing dependencies...", "ℹ️")

        # Auto-install dependencies
        if not auto_install_dependencies():
            self.print_status("Dependency installation failed. Please resolve issues above.", "❌")
            return

        print("\n" + "="*50)
        self.print_status("Step 0.6: Validating dependencies...", "ℹ️")

        # Validate dependencies
        if not self.validate_dependencies():
            self.print_status("Dependency validation failed. Please resolve issues above.", "❌")
            return

        print("\n" + "="*50)
        self.print_status("Step 1: Cleaning up existing processes...", "ℹ️")

        # Kill existing processes - only cleanup ports that exist in current mode
        port_cleanup_start = time.time()
        for port_name, port_number in self.ports.items():
            service_display_name = port_name.replace('_', ' ').title()
            self.port_manager.free_port(port_number, service_display_name)
        self.metrics.port_cleanup_time = time.time() - port_cleanup_start

        print("\n" + "="*50)
        self.print_status("Step 2: Checking port availability...", "ℹ️")

        # Check port availability (with force cleanup) - only check ports in current mode
        all_ports_available = True
        for port_name, port_number in self.ports.items():
            service_display_name = port_name.replace('_', ' ').title()
            if not self.check_port_available(port_number, service_display_name, force_cleanup=True):
                all_ports_available = False
        
        if not all_ports_available:
            self.print_status("Port conflicts could not be resolved", "❌")
            return

        print("\n" + "="*50)
        self.print_status("Step 3: Starting Syntheverse servers...", "ℹ️")

        # Determine which services to start based on mode
        services_to_start = []
        if 'poc_api' in self.ports:
            services_to_start.append('poc_api')
        if 'rag_api' in self.ports:
            services_to_start.append('rag_api')
        if 'frontend' in self.ports:
            services_to_start.append('frontend')

        # Use parallel startup if profile allows it
        profile_config = self._service_profiles[self.profile]
        startup_start = time.time()

        if profile_config['parallel_startup'] and len(services_to_start) > 1:
            self.logger.info("Using parallel startup")
            startup_results = self.start_services_parallel(services_to_start)
            servers_started = [name for name, result in startup_results.items() if result.success]
            failed_services = [name for name, result in startup_results.items() if not result.success]

            # Rollback if any critical services failed
            if failed_services and self.profile != ServiceProfile.DEVELOPMENT:
                self.logger.warning(f"Rolling back due to failed services: {failed_services}")
                self.rollback_startup(servers_started)
                servers_started = []
        else:
            # Sequential startup for compatibility/testing
            self.logger.info("Using sequential startup")
            servers_started = []
            failed_services = []

            for service_name in services_to_start:
                results = self.start_services_parallel([service_name])
                result = results.get(service_name)
                if result and result.success:
                    servers_started.append(service_name.replace('_', ' ').title())
                else:
                    failed_services.append(service_name)

        self.metrics.total_startup_time = time.time() - startup_start

        print("\n" + "="*50)

        if servers_started:
            # Validate that services are actually responding
            health_check_start = time.time()
            self.print_status("Validating service readiness...", "ℹ️")

            # Use enhanced health checker with correct service names
            health_results = self.health_checker.check_all_services()
            ready_services = []

            for service_name, result in health_results.items():
                service_display_name = service_name.replace('_', ' ').title()
                # Check if this service was supposed to start in this mode
                if service_name in services_to_start:
                    if result.status == ServiceStatus.HEALTHY:
                        ready_services.append(service_display_name)
                        self.logger.debug(f"{service_display_name} is healthy")
                    else:
                        self.logger.warning(f"{service_display_name} is {result.status.value}: {result.error_message}")

            self.metrics.health_check_time = time.time() - health_check_start

            if ready_services:
                self.print_status("🎉 System startup complete!", "✅")

                # Save successful state
                self.save_state()

                # Print performance metrics
                self._print_startup_metrics()

                print("\n🌐 SYNTHEVERSE SERVICES RUNNING:")
                print("=" * 40)

                for service in ready_services:
                    if "poc" in service.lower() and "api" in service.lower():
                        self.print_status(f"PoC API:         http://127.0.0.1:{self.ports.get('poc_api', 5001)}", "ℹ️")
                        self.print_status(f"  Health:        http://127.0.0.1:{self.ports.get('poc_api', 5001)}/health", "ℹ️")
                    elif "rag" in service.lower():
                        self.print_status(f"RAG API:         http://127.0.0.1:{self.ports.get('rag_api', 8000)}", "ℹ️")
                        self.print_status(f"  Docs:          http://127.0.0.1:{self.ports.get('rag_api', 8000)}/docs", "ℹ️")
                    elif "next" in service.lower() or "frontend" in service.lower():
                        self.print_status(f"Next.js UI:      http://127.0.0.1:{self.ports.get('frontend', 3001)}", "ℹ️")
            else:
                self.print_status("⚠️ Services started but health checks pending", "⚠️")
                print("\n🌐 SYNTHEVERSE SERVICES ATTEMPTED:")
                print("=" * 40)
                if 'poc_api' in services_to_start:
                    self.print_status(f"PoC API:         http://127.0.0.1:{self.ports.get('poc_api', 5001)}", "ℹ️")
                if 'rag_api' in services_to_start:
                    self.print_status(f"RAG API:         http://127.0.0.1:{self.ports.get('rag_api', 8000)}", "ℹ️")
                if 'frontend' in services_to_start:
                    self.print_status(f"Next.js UI:      http://127.0.0.1:{self.ports.get('frontend', 3001)}", "ℹ️")

            print("\n" + "="*50)
            self.print_status("SERVERS ARE RUNNING!", "🎯")
            print("\n📋 INSTRUCTIONS:")
            print("1. Services are starting up and will be available shortly")
            
            # Determine which UI to reference
            if 'frontend' in services_to_start and self.ports.get('frontend'):
                print(f"2. Open your browser to: http://127.0.0.1:{self.ports['frontend']} (Next.js UI)")
            elif 'poc_api' in services_to_start and self.ports.get('poc_api'):
                print(f"2. PoC API is running at: http://127.0.0.1:{self.ports['poc_api']}")
            
            print("3. Upload PDFs and test the PoC evaluation system!")
            print("\nPress Ctrl+C to stop all servers...")

            # Open browser automatically for frontend
            try:
                if 'frontend' in services_to_start and self.ports.get('frontend'):
                    # Give Next.js a moment to fully start
                    time.sleep(2)
                    webbrowser.open(f"http://127.0.0.1:{self.ports['frontend']}")
            except Exception as e:
                self.logger.debug(f"Could not auto-open browser: {e}")

            # Wait for user to stop
            try:
                input()
            except KeyboardInterrupt:
                pass

        else:
            self.print_status("No servers could be started", "❌")

        # Cleanup
        self.cleanup()
        self.print_status("All servers stopped. Goodbye! 👋", "✅")

def main():
    """Entry point"""
    # Handle keyboard interrupt gracefully
    def signal_handler(sig, frame):
        print("\n\nShutting down servers...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Start Syntheverse services')
    parser.add_argument('--mode', choices=['full', 'poc', 'minimal'],
                       default='full',
                       help='Startup mode: full (all services), poc (PoC system only), minimal (PoC API only)')
    parser.add_argument('--profile', choices=['dev', 'test', 'prod', 'minimal'],
                       default='dev',
                       help='Service profile: dev (development), test (testing), prod (production), minimal')
    parser.add_argument('--no-browser', action='store_true',
                       help='Do not open browser automatically')
    parser.add_argument('--restart', nargs='*',
                       help='Restart specific services (if not specified, starts all)')

    args = parser.parse_args()

    # Convert profile string to enum
    profile_map = {
        'dev': ServiceProfile.DEVELOPMENT,
        'test': ServiceProfile.TESTING,
        'prod': ServiceProfile.PRODUCTION,
        'minimal': ServiceProfile.MINIMAL
    }
    profile = profile_map.get(args.profile, ServiceProfile.DEVELOPMENT)

    # Run server manager with specified mode and profile
    manager = ServerManager(mode=args.mode, profile=profile)

    # Handle restart requests
    if args.restart:
        for service_name in args.restart:
            success = manager.restart_service(service_name)
            if success:
                print(f"✅ Successfully restarted {service_name}")
            else:
                print(f"❌ Failed to restart {service_name}")
        return

    # Normal startup
    if hasattr(manager, 'auto_open_browser'):
        manager.auto_open_browser = not args.no_browser
    manager.main()

if __name__ == "__main__":
    main()
