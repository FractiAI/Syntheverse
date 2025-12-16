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
from pathlib import Path

class CompleteUIStarter:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.processes = []
        self.ports = {
            'api': 5001,      # Flask PoC API
            'frontend': 3000  # Next.js frontend
        }
        self.system = platform.system().lower()

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

    def kill_process_on_port(self, port, name):
        """Kill any process running on the specified port"""
        try:
            if self.system in ['darwin', 'linux']:
                # Use lsof to find and kill process
                result = subprocess.run(['lsof', '-ti', f':{port}'],
                                      capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip():
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        if pid.strip():
                            try:
                                self.print_status(f"Killing {name} on port {port} (PID: {pid})", "⚠️")
                                os.kill(int(pid), signal.SIGKILL)
                            except (OSError, ValueError):
                                pass
                    time.sleep(2)  # Wait longer for processes to die
        except (subprocess.CalledProcessError, OSError, ValueError):
            pass  # Process might not exist or we can't kill it

    def check_port_available(self, port, name):
        """Check if a port is available"""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            result = sock.connect_ex(('127.0.0.1', port))
            if result == 0:
                self.print_status(f"Port {port} ({name}) is in use - will be freed", "⚠️")
                self.kill_process_on_port(port, name)
                time.sleep(1)
                return True  # We'll kill it and assume it's available
            else:
                self.print_status(f"Port {port} ({name}) is available", "✅")
                return True

    def start_flask_api(self):
        """Start the Flask PoC API server"""
        self.print_status("Starting Flask PoC API Server (Backend)...", "ℹ️")

        env = os.environ.copy()
        env['PYTHONPATH'] = f"{self.project_root}/src/core:{self.project_root}/src:{self.project_root}"
        env['FLASK_SKIP_DOTENV'] = '1'
        env['GROQ_API_KEY'] = 'YOUR_GROQ_API_KEY_HERE'

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
                env={**os.environ, "PORT": str(self.ports['frontend'])}
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
