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
from pathlib import Path

# Import port management module
try:
    from .port_manager import PortManager, free_port
except ImportError:
    # Fallback for direct execution
    sys.path.insert(0, str(Path(__file__).parent))
    from port_manager import PortManager, free_port

class ServerManager:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.processes = []
        self.ports = {
            'web_ui': 5000,      # Legacy Flask web UI
            'poc_api': 5001,     # PoC API
            'rag_api': 8000,     # RAG API (FastAPI)
            'frontend': 3001,    # Next.js frontend
            'demo': 8999         # Demo port (moved to avoid conflict)
        }

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

        # Initialize port manager
        self.port_manager = PortManager(self.logger)

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
            ("Legacy Web UI", self.project_root / "src" / "frontend" / "web-legacy" / "app.py"),
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

    def kill_process_on_port(self, port, name):
        """Kill any process running on the specified port (legacy method - use port_manager.free_port instead)"""
        self.logger.warning("kill_process_on_port is deprecated, use port_manager.free_port instead")
        return self.port_manager.free_port(port, name)

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

                # Test connectivity
                try:
                    import requests
                    url = f"http://127.0.0.1:{port}"
                    if port == self.ports['poc_api']:
                        url += "/api/status"

                    response = requests.get(url, timeout=5)
                    if response.status_code < 400:
                        self.print_status(f"{name} responding on port {port}", "✅")
                    else:
                        self.print_status(f"{name} started but returned status {response.status_code}", "⚠️")
                except ImportError:
                    self.print_status(f"{name} process running (connectivity test skipped)", "✅")
                except Exception:
                    self.print_status(f"{name} started but connectivity test failed", "⚠️")

                return True
            else:
                stdout, stderr = process.communicate()
                self.print_status(f"{name} failed to start", "❌")
                if stderr:
                    print(f"Error: {stderr.decode()[:200]}...")
                return False

        except Exception as e:
            self.print_status(f"Failed to start {name}: {str(e)}", "❌")
            return False

    def start_rag_api(self):
        """Start the RAG API server"""
        self.print_status("Starting RAG API Server...", "ℹ️")

        rag_api_dir = self.project_root / "src" / "api" / "rag-api" / "api"

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

        self.processes.clear()

    def validate_service_readiness(self, started_services, timeout=20):
        """Validate that started services are actually responding with improved retry logic"""
        import requests

        ready_services = []
        self.print_status(f"Validating service health (timeout: {timeout}s)...", "ℹ️")

        for service in started_services:
            if "PoC API" in service:
                urls = [
                    (f"http://127.0.0.1:{self.ports['poc_api']}/health", "API health endpoint"),
                    (f"http://127.0.0.1:{self.ports['poc_api']}/api/status", "API status endpoint")
                ]
            elif "RAG API" in service:
                urls = [
                    (f"http://127.0.0.1:{self.ports['rag_api']}/health", "RAG API health endpoint"),
                    (f"http://127.0.0.1:{self.ports['rag_api']}/", "RAG API root")
                ]
            elif "Web UI" in service:
                urls = [(f"http://127.0.0.1:{self.ports['web_ui']}/", "Web UI")]
            elif "Next.js" in service:
                urls = [(f"http://127.0.0.1:{self.ports['frontend']}/", "Next.js UI")]
            else:
                continue

            service_ready = False

            # Try each endpoint for this service
            for url, endpoint_name in urls:
                self.print_status(f"Checking {service} ({endpoint_name})...", "ℹ️")

                # Exponential backoff retry logic
                max_retries = min(timeout, 10)  # Max 10 retries
                for attempt in range(max_retries):
                    try:
                        response = requests.get(url, timeout=3)
                        if 200 <= response.status_code < 300:  # Accept 2xx status codes
                            ready_services.append(service)
                            self.print_status(f"✅ {service} is responding (status: {response.status_code})", "✅")
                            service_ready = True
                            break
                        else:
                            self.print_status(f"⚠️ {service} returned status {response.status_code}", "⚠️")
                    except requests.exceptions.ConnectionError:
                        # Connection failed - service might still be starting
                        if attempt < max_retries - 1:
                            wait_time = min(2 ** attempt, 5)  # Exponential backoff, max 5s
                            self.print_status(f"⏳ {service} not ready, retrying in {wait_time}s...", "ℹ️")
                            time.sleep(wait_time)
                        else:
                            self.print_status(f"❌ {service} connection failed after {max_retries} attempts", "❌")
                    except requests.exceptions.Timeout:
                        if attempt < max_retries - 1:
                            self.print_status(f"⏳ {service} timeout, retrying...", "ℹ️")
                            time.sleep(1)
                        else:
                            self.print_status(f"❌ {service} timeout after {max_retries} attempts", "❌")
                    except Exception as e:
                        self.print_status(f"❌ {service} health check error: {str(e)[:50]}...", "❌")
                        break

                if service_ready:
                    break

            if not service_ready:
                self.print_status(f"⚠️ {service} failed all health checks", "⚠️")

        return ready_services

    def run_demo(self):
        """Run the system demo"""
        os.chdir(self.project_root)
        subprocess.run([sys.executable, "demo_poc_system.py"])

    def main(self):
        """Main startup sequence"""
        self.print_header()

        print("\n" + "="*50)
        self.print_status("Step 0: Pre-startup cleanup...", "ℹ️")

        # Pre-startup cleanup: Always kill existing processes and free ports
        ports_to_free = [
            ("Web UI", self.ports['web_ui']),
            ("PoC API", self.ports['poc_api']),
            ("Next.js Frontend", self.ports['frontend']),
            ("Demo", self.ports['demo'])
        ]

        for name, port in ports_to_free:
            self.print_status(f"Freeing port {port} ({name})...", "ℹ️")
            if not self.port_manager.free_port(port, name):
                self.print_status(f"Could not free port {port} ({name}), but continuing...", "⚠️")

        # Additional cleanup using system commands if available
        try:
            self.print_status("Performing additional process cleanup...", "ℹ️")
            # Kill any lingering Python and Node processes
            cleanup_commands = [
                ["pkill", "-f", "python.*app.py"],
                ["pkill", "-f", "npm.*dev"],
                ["pkill", "-f", "next.*dev"],
                ["pkill", "-f", "flask"]
            ]

            for cmd in cleanup_commands:
                try:
                    result = subprocess.run(cmd, capture_output=True, timeout=5)
                    if result.returncode in [0, 1]:  # 0 = killed processes, 1 = no processes found
                        self.print_status(f"Cleanup command succeeded: {' '.join(cmd)}", "✅")
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    self.logger.debug(f"Cleanup command not available: {' '.join(cmd)}")

            # Wait for cleanup to complete
            time.sleep(2)
            self.print_status("Pre-startup cleanup completed", "✅")

        except Exception as e:
            self.print_status(f"Additional cleanup failed: {e}", "⚠️")

        print("\n" + "="*50)
        self.print_status("Step 0: Loading environment configuration...", "ℹ️")

        # Load and validate environment variables
        if not self.load_environment():
            self.print_status("Environment validation failed. Please configure required variables.", "❌")
            return

        print("\n" + "="*50)
        self.print_status("Step 0.5: Validating dependencies...", "ℹ️")

        # Validate dependencies
        if not self.validate_dependencies():
            self.print_status("Dependency validation failed. Please resolve issues above.", "❌")
            return

        print("\n" + "="*50)
        self.print_status("Step 1: Cleaning up existing processes...", "ℹ️")

        # Kill existing processes
        for port, name in [("Web UI", self.ports['web_ui']),
                          ("PoC API", self.ports['poc_api']),
                          ("Next.js Frontend", self.ports['frontend']),
                          ("Demo", self.ports['demo'])]:
            self.kill_process_on_port(port, name)

        print("\n" + "="*50)
        self.print_status("Step 2: Checking port availability...", "ℹ️")

        # Check port availability (with force cleanup)
        if not self.check_port_available(self.ports['web_ui'], "Web UI", force_cleanup=True):
            return
        if not self.check_port_available(self.ports['poc_api'], "PoC API", force_cleanup=True):
            return
        if not self.check_port_available(self.ports['frontend'], "Next.js Frontend", force_cleanup=True):
            return

        print("\n" + "="*50)
        self.print_status("Step 3: Starting Syntheverse servers...", "ℹ️")

        # Start servers
        servers_started = []

        # Start PoC API
        poc_api_cmd = f"{sys.executable} src/api/poc-api/app.py"
        if self.start_server(poc_api_cmd, "PoC API Server", self.ports['poc_api']):
            servers_started.append("PoC API")

        # Start RAG API
        if self.start_rag_api():
            servers_started.append("RAG API")

        # Start Web UI (legacy) - for blockchain registration
        web_ui_cmd = f"{sys.executable} src/frontend/web-legacy/app.py"
        if self.start_server(web_ui_cmd, "Web UI Server (Legacy)", self.ports['web_ui']):
            servers_started.append("Web UI")

        # Start Next.js Frontend
        frontend_dir = self.project_root / "src" / "frontend" / "poc-frontend"
        if frontend_dir.exists():
            nextjs_cmd = f"PORT=3001 npm run dev"
            if self.start_server(nextjs_cmd, "Next.js Frontend", self.ports['frontend'], cwd=frontend_dir):
                servers_started.append("Next.js Frontend")

        print("\n" + "="*50)

        if servers_started:
            # Validate that services are actually responding
            self.print_status("Validating service readiness...", "ℹ️")
            ready_services = self.validate_service_readiness(servers_started)

            if ready_services:
                self.print_status("🎉 System startup complete!", "✅")
                print("\n🌐 SYNTHVERSE SERVERS RUNNING:")
                print("=" * 40)

                for service in ready_services:
                    if "Web UI" in service:
                        self.print_status(f"Web UI (Legacy): http://127.0.0.1:{self.ports['web_ui']}", "✅")
                    elif "PoC API" in service:
                        self.print_status(f"PoC API:         http://127.0.0.1:{self.ports['poc_api']}", "✅")
                        self.print_status(f"API Health:      http://127.0.0.1:{self.ports['poc_api']}/health", "✅")
                    elif "RAG API" in service:
                        self.print_status(f"RAG API:         http://127.0.0.1:{self.ports['rag_api']}", "✅")
                        self.print_status(f"RAG Docs:        http://127.0.0.1:{self.ports['rag_api']}/docs", "✅")
                    elif "Next.js" in service:
                        self.print_status(f"Next.js UI:      http://127.0.0.1:{self.ports['frontend']}", "✅")
            else:
                self.print_status("⚠️ Services started but some may not be responding yet", "⚠️")
                print("\n🌐 SYNTHVERSE SERVERS ATTEMPTED:")
                print("=" * 40)
                self.print_status(f"Web UI (Legacy): http://127.0.0.1:{self.ports['web_ui']}", "ℹ️")
                self.print_status(f"PoC API:         http://127.0.0.1:{self.ports['poc_api']}", "ℹ️")
                if "RAG API" in servers_started:
                    self.print_status(f"RAG API:         http://127.0.0.1:{self.ports['rag_api']}", "ℹ️")
                if "Next.js Frontend" in servers_started:
                    self.print_status(f"Next.js UI:      http://127.0.0.1:{self.ports['frontend']}", "ℹ️")

            print("\n" + "="*50)
            self.print_status("SERVERS ARE RUNNING!", "🎯")
            print("\n📋 INSTRUCTIONS:")
            print("1. Open your browser")
            if "Next.js Frontend" in servers_started:
                print(f"2. Go to: http://127.0.0.1:{self.ports['frontend']} (Next.js UI)")
            else:
                print(f"2. Go to: http://127.0.0.1:{self.ports['web_ui']} (Legacy UI)")
            print("3. Upload PDFs and test the PoC evaluation system!")
            print("\nPress Ctrl+C to stop all servers...")

            # Open browser automatically
            try:
                if "Next.js Frontend" in servers_started:
                    webbrowser.open(f"http://127.0.0.1:{self.ports['frontend']}")
                else:
                    webbrowser.open(f"http://127.0.0.1:{self.ports['web_ui']}")
            except:
                pass

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

    # Run server manager
    manager = ServerManager()
    manager.main()

if __name__ == "__main__":
    main()
