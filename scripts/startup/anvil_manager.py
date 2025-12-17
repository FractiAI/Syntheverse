#!/usr/bin/env python3
"""
Anvil Management Module for Syntheverse
Handles Foundry Anvil startup, shutdown, health checks, and process management
"""

import os
import sys
import time
import signal
import subprocess
import logging
import requests
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

# Import port management module
try:
    from .port_manager import PortManager, free_port
except ImportError:
    # Fallback for direct execution
    sys.path.insert(0, str(Path(__file__).parent))
    from port_manager import PortManager, free_port

@dataclass
class AnvilStatus:
    """Anvil service status information"""
    running: bool
    port: int = 8545
    pid: Optional[int] = None
    block_number: Optional[int] = None
    accounts: Optional[int] = None
    gas_price: Optional[str] = None
    process_info: Optional[Dict[str, Any]] = None
    uptime: Optional[float] = None

class AnvilManager:
    """Manages Foundry Anvil Ethereum node"""

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.port_manager = PortManager(self.logger)
        self.anvil_port = 8545
        self.anvil_process: Optional[subprocess.Popen] = None
        self.start_time: Optional[float] = None

    def check_anvil_running(self) -> bool:
        """Check if Anvil is running by testing the RPC endpoint"""
        try:
            response = requests.post(
                f"http://127.0.0.1:{self.anvil_port}",
                json={"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1},
                timeout=5
            )
            return response.status_code == 200 and 'result' in response.json()
        except (requests.exceptions.RequestException, ValueError):
            return False

    def get_anvil_status(self) -> AnvilStatus:
        """Get comprehensive Anvil status information"""
        status = AnvilStatus(running=False, port=self.anvil_port)

        # Check if running
        if not self.check_anvil_running():
            return status

        status.running = True

        # Get process information
        process_info = self.port_manager.get_process_info(self.anvil_port)
        if process_info:
            anvil_processes = [p for p in process_info if 'anvil' in p.name.lower()]
            if anvil_processes:
                status.pid = anvil_processes[0].pid
                status.process_info = {
                    'name': anvil_processes[0].name,
                    'command': anvil_processes[0].command,
                    'user': anvil_processes[0].user
                }

        # Calculate uptime
        if self.start_time:
            status.uptime = time.time() - self.start_time

        # Get blockchain information
        try:
            # Block number
            response = requests.post(
                f"http://127.0.0.1:{self.anvil_port}",
                json={"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1},
                timeout=3
            )
            if response.status_code == 200:
                result = response.json()
                if 'result' in result:
                    status.block_number = int(result['result'], 16)

            # Accounts
            response = requests.post(
                f"http://127.0.0.1:{self.anvil_port}",
                json={"jsonrpc": "2.0", "method": "eth_accounts", "params": [], "id": 1},
                timeout=3
            )
            if response.status_code == 200:
                result = response.json()
                if 'result' in result:
                    status.accounts = len(result['result'])

            # Gas price
            response = requests.post(
                f"http://127.0.0.1:{self.anvil_port}",
                json={"jsonrpc": "2.0", "method": "eth_gasPrice", "params": [], "id": 1},
                timeout=3
            )
            if response.status_code == 200:
                result = response.json()
                if 'result' in result:
                    status.gas_price = result['result']

        except requests.exceptions.RequestException as e:
            self.logger.debug(f"Could not get Anvil blockchain info: {e}")

        return status

    def wait_for_anvil(self, timeout: int = 30, interval: int = 2) -> bool:
        """Wait for Anvil to become available with retry logic"""
        self.logger.info(f"Waiting for Anvil to be ready on port {self.anvil_port} (timeout: {timeout}s)")

        start_time = time.time()
        attempts = 0

        while time.time() - start_time < timeout:
            attempts += 1

            if self.check_anvil_running():
                elapsed = time.time() - start_time
                self.logger.info(f"✅ Anvil is ready after {elapsed:.1f}s ({attempts} attempts)")
                return True

            if attempts % 5 == 0:  # Log every 5 attempts
                elapsed = time.time() - start_time
                self.logger.info(f"⏳ Still waiting for Anvil... ({elapsed:.1f}s elapsed, {attempts} attempts)")

            time.sleep(interval)

        elapsed = time.time() - start_time
        self.logger.error(f"❌ Anvil failed to start within {timeout}s timeout ({attempts} attempts)")
        return False

    def start_anvil(self, accounts: int = 10, block_time: Optional[int] = None,
                   gas_limit: Optional[str] = None, silent: bool = True) -> bool:
        """Start Anvil in the background with proper configuration"""
        self.logger.info("Starting Anvil Ethereum node...")

        # Check if already running
        if self.check_anvil_running():
            self.logger.info("✅ Anvil is already running")
            return True

        # Free the port if needed
        if not free_port(self.anvil_port, "Anvil"):
            self.logger.error(f"❌ Could not free port {self.anvil_port} for Anvil")
            return False

        # Build command
        cmd = ["anvil"]

        # Add options
        if accounts:
            cmd.extend(["--accounts", str(accounts)])

        if block_time:
            cmd.extend(["--block-time", str(block_time)])

        if gas_limit:
            cmd.extend(["--gas-limit", gas_limit])

        if silent:
            cmd.append("--silent")

        # Set port explicitly
        cmd.extend(["--port", str(self.anvil_port)])

        self.logger.info(f"Running command: {' '.join(cmd)}")

        try:
            # Start Anvil process
            self.anvil_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE if not silent else subprocess.DEVNULL,
                stderr=subprocess.PIPE if not silent else subprocess.DEVNULL,
                preexec_fn=os.setsid if hasattr(os, 'setsid') else None  # Create new process group
            )

            self.start_time = time.time()
            self.logger.info(f"✅ Anvil process started (PID: {self.anvil_process.pid})")

            # Wait for Anvil to be ready
            if self.wait_for_anvil(timeout=60):
                self.logger.info("🎉 Anvil startup successful!")
                return True
            else:
                self.logger.error("❌ Anvil startup failed - health check timeout")
                self.stop_anvil()
                return False

        except (subprocess.SubprocessError, OSError) as e:
            self.logger.error(f"❌ Failed to start Anvil: {e}")
            return False

    def stop_anvil(self) -> bool:
        """Stop Anvil gracefully"""
        self.logger.info("Stopping Anvil...")

        success = False

        # Try to stop the tracked process first
        if self.anvil_process and self.anvil_process.poll() is None:
            try:
                # Terminate the process group if possible
                if hasattr(os, 'killpg'):
                    try:
                        os.killpg(os.getpgid(self.anvil_process.pid), signal.SIGTERM)
                    except (OSError, ProcessLookupError):
                        pass

                # Fallback to terminating individual process
                self.anvil_process.terminate()
                try:
                    self.anvil_process.wait(timeout=10)
                    self.logger.info("✅ Anvil terminated gracefully")
                    success = True
                except subprocess.TimeoutExpired:
                    self.logger.warning("Anvil did not terminate gracefully, forcing kill...")
                    self.anvil_process.kill()
                    self.anvil_process.wait()
                    self.logger.info("✅ Anvil killed")
                    success = True

            except (OSError, ProcessLookupError) as e:
                self.logger.debug(f"Could not terminate tracked Anvil process: {e}")

        # Also try to kill any anvil processes on the port
        if free_port(self.anvil_port, "Anvil"):
            self.logger.info("✅ Anvil port cleanup successful")
            success = True

        self.anvil_process = None
        self.start_time = None

        if success:
            self.logger.info("🎉 Anvil shutdown complete!")
        else:
            self.logger.warning("⚠️ Anvil may still be running")

        return success

    def restart_anvil(self, **kwargs) -> bool:
        """Restart Anvil with new configuration"""
        self.logger.info("Restarting Anvil...")

        if not self.stop_anvil():
            self.logger.warning("⚠️ Could not stop Anvil cleanly, proceeding with restart")

        time.sleep(2)  # Brief pause

        return self.start_anvil(**kwargs)

    def get_anvil_logs(self, lines: int = 50) -> Optional[str]:
        """Get recent Anvil logs if available"""
        if not self.anvil_process:
            return None

        try:
            # Try to read from stdout if available
            if self.anvil_process.stdout:
                # This is a simple implementation - in practice, you might want to use a pipe
                return f"Anvil process running (PID: {self.anvil_process.pid})"
        except Exception as e:
            self.logger.debug(f"Could not get Anvil logs: {e}")

        return None

# Global instance for convenience
anvil_manager = AnvilManager()

# Convenience functions
def check_anvil_running() -> bool:
    """Check if Anvil is running"""
    return anvil_manager.check_anvil_running()

def get_anvil_status() -> AnvilStatus:
    """Get Anvil status"""
    return anvil_manager.get_anvil_status()

def start_anvil(**kwargs) -> bool:
    """Start Anvil"""
    return anvil_manager.start_anvil(**kwargs)

def stop_anvil() -> bool:
    """Stop Anvil"""
    return anvil_manager.stop_anvil()

def wait_for_anvil(timeout: int = 30) -> bool:
    """Wait for Anvil to be ready"""
    return anvil_manager.wait_for_anvil(timeout)

def restart_anvil(**kwargs) -> bool:
    """Restart Anvil"""
    return anvil_manager.restart_anvil(**kwargs)


