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
from pathlib import Path

class ServerManager:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.processes = []
        self.ports = {
            'web_ui': 5000,
            'poc_api': 5001,
            'demo': 8000
        }

    def print_header(self):
        print("🌟 SYNTHVERSE PoC SYSTEM STARTUP")
        print("=" * 50)

    def print_status(self, message, status="✅"):
        colors = {
            "✅": "\033[0;32m",  # Green
            "❌": "\033[0;31m",  # Red
            "⚠️": "\033[1;33m",   # Yellow
            "ℹ️": "\033[0;34m",   # Blue
        }
        color = colors.get(status, "")
        reset = "\033[0m" if color else ""
        print(f"{color}{status} {message}{reset}")

    def kill_process_on_port(self, port, name):
        """Kill any process running on the specified port"""
        try:
            if sys.platform == "darwin" or sys.platform == "linux":
                # Use lsof to find and kill process
                result = subprocess.run(['lsof', '-ti', f':{port}'],
                                      capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip():
                    pid = result.stdout.strip()
                    self.print_status(f"Killing {name} on port {port} (PID: {pid})", "⚠️")
                    os.kill(int(pid), signal.SIGKILL)
                    time.sleep(1)
        except (subprocess.CalledProcessError, OSError, ValueError):
            pass  # Process might not exist or we can't kill it

    def check_port_available(self, port, name):
        """Check if a port is available"""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            result = sock.connect_ex(('127.0.0.1', port))
            if result == 0:
                self.print_status(f"Port {port} ({name}) is in use", "❌")
                return False
            else:
                self.print_status(f"Port {port} ({name}) is available", "✅")
                return True

    def start_server(self, command, name, port):
        """Start a server process"""
        self.print_status(f"Starting {name} on port {port}...", "ℹ️")

        try:
            # Set environment variables
            env = os.environ.copy()
            env['FLASK_SKIP_DOTENV'] = '1'
            if 'poc' in name.lower():
                env['GROQ_API_KEY'] = 'YOUR_GROQ_API_KEY_HERE'

            # Start process
            process = subprocess.Popen(
                command,
                shell=True,
                cwd=self.project_root,
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

    def run_demo(self):
        """Run the system demo"""
        os.chdir(self.project_root)
        subprocess.run([sys.executable, "demo_poc_system.py"])

    def main(self):
        """Main startup sequence"""
        self.print_header()

        print("\n" + "="*50)
        self.print_status("Step 1: Cleaning up existing processes...", "ℹ️")

        # Kill existing processes
        for port, name in [("Web UI", self.ports['web_ui']),
                          ("PoC API", self.ports['poc_api']),
                          ("Demo", self.ports['demo'])]:
            self.kill_process_on_port(port, name)

        print("\n" + "="*50)
        self.print_status("Step 2: Checking port availability...", "ℹ️")

        # Check port availability
        if not self.check_port_available(self.ports['web_ui'], "Web UI"):
            return
        if not self.check_port_available(self.ports['poc_api'], "PoC API"):
            return

        print("\n" + "="*50)
        self.print_status("Step 3: Starting Syntheverse servers...", "ℹ️")

        # Start servers
        servers_started = []

        # Start PoC API
        poc_api_cmd = f"cd {self.project_root} && PYTHONPATH={self.project_root}/src/core:{self.project_root}/src:{self.project_root} # GROQ_API_KEY=your-groq-api-key-here {sys.executable} src/api/poc-api/app.py"
        if self.start_server(poc_api_cmd, "PoC API Server", self.ports['poc_api']):
            servers_started.append("PoC API")

        # Start Web UI
        web_ui_cmd = f"{sys.executable} src/frontend/web-legacy/app.py"
        if self.start_server(web_ui_cmd, "Web UI Server", self.ports['web_ui']):
            servers_started.append("Web UI")

        print("\n" + "="*50)

        if servers_started:
            self.print_status("🎉 System startup complete!", "✅")
            print("\n🌐 SYNTHVERSE SERVERS RUNNING:")
            print("=" * 40)
            self.print_status(f"Web UI:        http://127.0.0.1:{self.ports['web_ui']}", "✅")
            self.print_status(f"PoC API:       http://127.0.0.1:{self.ports['poc_api']}", "✅")
            self.print_status(f"API Status:    http://127.0.0.1:{self.ports['poc_api']}/api/status", "✅")

            print("\n" + "="*50)
            self.print_status("SERVERS ARE RUNNING!", "🎯")
            print("\n📋 INSTRUCTIONS:")
            print("1. Open your browser")
            print(f"2. Go to: http://127.0.0.1:{self.ports['web_ui']}")
            print("3. Upload PDFs and test the PoC evaluation system!")
            print("\nPress Ctrl+C to stop all servers...")

            # Open browser automatically
            try:
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
