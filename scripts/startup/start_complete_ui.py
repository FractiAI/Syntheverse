#!/usr/bin/env python3
"""
Complete Syntheverse UI Startup Script
Starts both Flask API backend and Next.js frontend for full collaborator experience
"""

import os
import sys
import time
import signal
import subprocess
import webbrowser
import platform
import logging
from pathlib import Path

# Import port management module
try:
    from .port_manager import PortManager, free_port
except ImportError:
    # Fallback for direct execution
    sys.path.insert(0, str(Path(__file__).parent))
    from port_manager import PortManager, free_port

class CompleteUIStarter:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.processes = []
        self.ports = {
            'api': 5001,      # Flask PoC API
            'rag_api': 8000,  # RAG API
            'frontend': 3001  # Next.js frontend
        }
        self.system = platform.system().lower()

        # Set up logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # Remove existing handlers to avoid duplicates
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        # Add console handler
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        # Initialize port manager
        self.port_manager = PortManager(self.logger)

    def print_header(self):
        print("🚀 SYNTHVERSE COMPLETE UI STARTUP")
        print("=" * 60)
        print("Starting: Flask API Backend + Next.js Frontend")
        print("Features: Dashboard, Sandbox Map, Registry, Explorer, Submission")

    def print_status(self, message, status="✅"):
        colors = {
            "✅": "\033[0;32m",  # Green
            "❌": "\033[0;31m",  # Red
            "⚠️": "\033[1;33m",   # Yellow
            "ℹ️": "\033[0;34m",   # Blue
            "🎯": "\033[0;35m",   # Magenta
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

        # Load environment variables from .env file if it exists
        if env_file.exists():
            self.print_status("Loading environment configuration from .env file...", "ℹ️")
            try:
                with open(env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            if '=' in line:
                                key, value = line.split('=', 1)
                                key = key.strip()
                                value = value.strip()
                                # Remove quotes if present
                                if value.startswith('"') and value.endswith('"'):
                                    value = value[1:-1]
                                elif value.startswith("'") and value.endswith("'"):
                                    value = value[1:-1]
                                os.environ[key] = value
                self.print_status("Environment variables loaded from .env file", "✅")
            except Exception as e:
                self.print_status(f"Warning: Failed to load .env file: {e}", "⚠️")

        # Validate required environment variables
        required_vars = ['GROQ_API_KEY']
        missing_vars = []

        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            self.print_status(f"Missing required environment variables: {', '.join(missing_vars)}", "❌")
            self.print_status("Please set the missing variables in your .env file or environment", "ℹ️")
            self.print_status("Example: GROQ_API_KEY=your-api-key-here", "ℹ️")
            return False

        # Show GROQ_API_KEY status (masked for security)
        groq_key = os.getenv('GROQ_API_KEY', '')
        if groq_key:
            masked_key = groq_key[:15] + "..." if len(groq_key) > 15 else groq_key
            self.print_status(f"GROQ_API_KEY configured ({masked_key})", "✅")
        else:
            self.print_status("GROQ_API_KEY not found", "❌")
            return False

        return True

    def validate_dependencies(self):
        """Validate that required files and dependencies exist"""
        validation_passed = True

        # Check required Python files exist
        required_files = [
            ("Flask PoC API", self.project_root / "src" / "api" / "poc-api" / "app.py"),
        ]

        for service_name, file_path in required_files:
            if not file_path.exists():
                self.print_status(f"Required file not found: {file_path}", "❌")
                validation_passed = False
            else:
                self.print_status(f"{service_name} file found: {file_path.name}", "✅")

        # Check Next.js frontend directory (required for this script)
        frontend_dir = self.project_root / "src" / "frontend" / "poc-frontend"
        if not frontend_dir.exists():
            self.print_status("Next.js frontend directory not found - required for complete UI", "❌")
            validation_passed = False
        else:
            self.print_status("Next.js frontend directory found", "✅")

            # Check if node_modules exists
            if not (frontend_dir / "node_modules").exists():
                self.print_status("Next.js dependencies not installed - run 'npm install' in frontend directory", "❌")
                self.print_status("Command: cd src/frontend/poc-frontend && npm install", "ℹ️")
                validation_passed = False
            else:
                self.print_status("Next.js dependencies installed", "✅")

            # Check if package.json exists
            if not (frontend_dir / "package.json").exists():
                self.print_status("Next.js package.json not found", "❌")
                validation_passed = False
            else:
                self.print_status("Next.js package.json found", "✅")

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

        # Check Node.js availability (required for Next.js frontend)
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                self.print_status(f"Node.js available: {result.stdout.strip()}", "✅")

                result = subprocess.run(['npm', '--version'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    self.print_status(f"npm available: {result.stdout.strip()}", "✅")
                else:
                    self.print_status("npm not available - Next.js frontend cannot start", "❌")
                    validation_passed = False
            else:
                self.print_status("Node.js not available - Next.js frontend cannot start", "❌")
                validation_passed = False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.print_status("Node.js/npm not available - Next.js frontend cannot start", "❌")
            validation_passed = False

        return validation_passed

    def kill_process_on_port(self, port, name):
        """Kill any process running on the specified port (legacy method - use port_manager.free_port instead)"""
        self.logger.warning("kill_process_on_port is deprecated, use port_manager.free_port instead")
        return self.port_manager.free_port(port, name)

    def check_port_available(self, port, name):
        """Check if a port is available and attempt to free it if needed"""
        if self.port_manager.free_port(port, name):
            self.print_status(f"Port {port} ({name}) is available", "✅")
            return True
        else:
            self.print_status(f"Port {port} ({name}) could not be freed", "❌")
            return False

    def start_flask_api(self):
        """Start the Flask PoC API server"""
        self.print_status("Starting Flask PoC API Server (Backend)...", "ℹ️")

        env = os.environ.copy()
        env['PYTHONPATH'] = f"{self.project_root}/src/core:{self.project_root}/src:{self.project_root}"
        env['FLASK_SKIP_DOTENV'] = '1'
        # GROQ_API_KEY should already be loaded from environment

        cmd = [sys.executable, "src/api/poc-api/app.py"]

        try:
            process = subprocess.Popen(
                cmd,
                cwd=self.project_root,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            self.processes.append((process, "Flask API", self.ports['api']))

            # Wait for Flask to start
            time.sleep(5)

            if process.poll() is None:
                self.print_status("Flask PoC API started successfully", "✅")

                # Test API connectivity
                try:
                    import requests
                    response = requests.get(f"http://127.0.0.1:{self.ports['api']}/api/status", timeout=3)
                    self.print_status(f"Flask API responding on port {self.ports['api']}", "✅")
                    return True
                except ImportError:
                    self.print_status("Flask API process running (connectivity test skipped)", "✅")
                    return True
                except Exception:
                    self.print_status("Flask API started but connectivity test failed", "⚠️")
                    return True
            else:
                stdout, stderr = process.communicate()
                self.print_status("Flask API failed to start", "❌")
                if stderr:
                    print(f"Error: {stderr.decode()[:200]}...")
                return False

        except Exception as e:
            self.print_status(f"Failed to start Flask API: {e}", "❌")
            return False

    def start_rag_api(self):
        """Start the RAG API server"""
        self.print_status("Starting RAG API Server...", "ℹ️")

        rag_api_dir = self.project_root / "src" / "api" / "rag-api" / "api"

        if not rag_api_dir.exists():
            self.print_status("RAG API directory not found - skipping", "⚠️")
            return False

        env = os.environ.copy()
        env['PYTHONPATH'] = f"{self.project_root}/src:{self.project_root}"

        cmd = [sys.executable, "rag_api.py"]

        try:
            process = subprocess.Popen(
                cmd,
                cwd=rag_api_dir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            self.processes.append((process, "RAG API", self.ports['rag_api']))

            # Wait for RAG API to start
            time.sleep(5)

            if process.poll() is None:
                self.print_status("RAG API started successfully", "✅")

                # Test connectivity
                try:
                    import requests
                    response = requests.get(f"http://127.0.0.1:{self.ports['rag_api']}/health", timeout=3)
                    if response.status_code < 400:
                        self.print_status(f"RAG API responding on port {self.ports['rag_api']}", "✅")
                        return True
                    else:
                        self.print_status(f"RAG API started but returned status {response.status_code}", "⚠️")
                        return True
                except ImportError:
                    self.print_status("RAG API process running (connectivity test skipped)", "✅")
                    return True
                except Exception:
                    self.print_status("RAG API started but connectivity test failed", "⚠️")
                    return True
            else:
                stdout, stderr = process.communicate()
                self.print_status("RAG API failed to start", "❌")
                if stderr:
                    print(f"Error: {stderr.decode()[:200]}...")
                return False

        except Exception as e:
            self.print_status(f"Failed to start RAG API: {str(e)}", "❌")
            return False

    def start_nextjs_frontend(self):
        """Start the Next.js frontend server"""
        self.print_status("Starting Next.js Frontend (Complete UI)...", "ℹ️")

        frontend_dir = self.project_root / "src" / "frontend" / "poc-frontend"

        if not frontend_dir.exists():
            self.print_status("Next.js frontend directory not found", "❌")
            return False

        # Check if node_modules exists
        if not (frontend_dir / "node_modules").exists():
            self.print_status("Installing Next.js dependencies...", "ℹ️")
            try:
                subprocess.run(["npm", "install"],
                             cwd=frontend_dir, check=True, capture_output=True)
            except subprocess.CalledProcessError:
                self.print_status("Failed to install dependencies", "❌")
                return False

        cmd = ["npm", "run", "dev"]

        try:
            process = subprocess.Popen(
                cmd,
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={**os.environ, "PORT": "3001"}
            )

            self.processes.append((process, "Next.js Frontend", self.ports['frontend']))

            # Wait for Next.js to start (takes longer)
            time.sleep(10)

            if process.poll() is None:
                self.print_status("Next.js Frontend started successfully", "✅")

                # Test frontend connectivity
                try:
                    import requests
                    response = requests.get(f"http://127.0.0.1:{self.ports['frontend']}", timeout=5)
                    self.print_status(f"Next.js Frontend responding on port {self.ports['frontend']}", "✅")
                    return True
                except ImportError:
                    self.print_status("Next.js process running (connectivity test skipped)", "✅")
                    return True
                except Exception as e:
                    self.print_status(f"Next.js started but connectivity test failed: {str(e)[:50]}...", "⚠️")
                    return True
            else:
                stdout, stderr = process.communicate()
                self.print_status("Next.js Frontend failed to start", "❌")
                if stderr:
                    error_msg = stderr.decode()
                    # Look for common error patterns
                    if "EADDRINUSE" in error_msg:
                        self.print_status("Port already in use - try killing existing processes", "⚠️")
                    else:
                        print(f"Error: {error_msg[:300]}...")
                return False

        except Exception as e:
            self.print_status(f"Failed to start Next.js Frontend: {e}", "❌")
            return False

    def cleanup(self):
        """Clean up all running processes"""
        self.print_status("Shutting down servers...", "ℹ️")

        for process, name, port in self.processes:
            try:
                if process.poll() is None:
                    process.terminate()
                    time.sleep(2)
                    if process.poll() is None:
                        process.kill()
                self.print_status(f"{name} stopped", "✅")
            except Exception as e:
                self.print_status(f"Error stopping {name}: {e}", "❌")

        self.processes.clear()

    def main(self):
        """Main startup sequence"""
        # Handle keyboard interrupt gracefully
        def signal_handler(sig, frame):
            print("\n\n🛑 Shutdown requested by user...")
            self.cleanup()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)

        self.print_header()

        print("\n" + "="*60)
        self.print_status("Step 0: Loading environment configuration...", "ℹ️")

        # Load and validate environment variables
        if not self.load_environment():
            self.print_status("Environment validation failed. Please configure required variables.", "❌")
            return

        print("\n" + "="*60)
        self.print_status("Step 0.5: Validating dependencies...", "ℹ️")

        # Validate dependencies
        if not self.validate_dependencies():
            self.print_status("Dependency validation failed. Please resolve issues above.", "❌")
            return

        print("\n" + "="*60)
        self.print_status("Step 1: Preparing environment...", "ℹ️")

        # Check port availability
        api_ok = self.check_port_available(self.ports['api'], "Flask API")
        frontend_ok = self.check_port_available(self.ports['frontend'], "Next.js Frontend")

        if not api_ok or not frontend_ok:
            self.print_status("Port conflicts detected. Please close conflicting applications.", "❌")
            return

        print("\n" + "="*60)
        self.print_status("Step 2: Starting Syntheverse servers...", "ℹ️")

        servers_started = []

        # Start Flask API first
        if self.start_flask_api():
            servers_started.append("Flask API")

        # Start RAG API
        if self.start_rag_api():
            servers_started.append("RAG API")

        # Start Next.js frontend
        if self.start_nextjs_frontend():
            servers_started.append("Next.js Frontend")

        print("\n" + "="*60)

        if len(servers_started) >= 1:  # At least Flask API should start
            self.print_status("🎉 Syntheverse UI Startup Complete!", "✅")
            print("\n🌐 SYNTHVERSE SERVERS RUNNING:")
            print("=" * 50)

            if "Flask API" in servers_started:
                self.print_status(f"Flask API (Backend): http://127.0.0.1:{self.ports['api']}", "✅")
                self.print_status(f"API Status: http://127.0.0.1:{self.ports['api']}/api/status", "✅")

            if "RAG API" in servers_started:
                self.print_status(f"RAG API: http://127.0.0.1:{self.ports['rag_api']}", "🤖")
                self.print_status(f"RAG Docs: http://127.0.0.1:{self.ports['rag_api']}/docs", "🤖")

            if "Next.js Frontend" in servers_started:
                self.print_status(f"Next.js UI (Complete): http://127.0.0.1:{self.ports['frontend']}", "🎯")
            else:
                self.print_status("Next.js UI: Run manually - see instructions below", "⚠️")

            print("\n" + "="*60)
            self.print_status("COMPLETE UI FEATURES AVAILABLE:", "🎯")
            print("  🏠 Dashboard - System statistics & metrics")
            print("  🕸️  Sandbox Map - Interactive network visualization")
            print("  📋 Registry - Contribution timeline & certificates")
            print("  🔍 Explorer - Advanced contribution browsing")
            print("  📝 Submission - PDF upload & AI evaluation")
            print("\n" + "="*60)

            if "Next.js Frontend" in servers_started:
                # Open browser automatically
                try:
                    webbrowser.open(f"http://127.0.0.1:{self.ports['frontend']}")
                    self.print_status("Browser opened automatically!", "✅")
                except:
                    pass

                self.print_status("🎮 READY FOR TESTING!", "🚀")
                print("\nNavigate through:")
                print("• Dashboard → System overview")
                print("• Sandbox Map → Network visualization")
                print("• Registry → Certificate timeline")
                print("• Explorer → Contribution browser")
                print("• Submission → PDF upload & evaluation")
                print("\nPress Ctrl+C to stop all servers...")

            # Wait for user
            try:
                input()
            except (EOFError, KeyboardInterrupt):
                pass

        else:
            self.print_status("No servers could be started", "❌")

        # Cleanup
        self.cleanup()
        self.print_status("All servers stopped. Goodbye! 👋", "✅")

def main():
    """Entry point"""
    try:
        starter = CompleteUIStarter()
        starter.main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Cleaning up...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
