#!/usr/bin/env python3
"""
Port Management Module for Syntheverse Startup Scripts
Handles port cleanup, process killing, and availability checking across platforms
"""

import os
import sys
import time
import socket
import signal
import subprocess
import logging
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class ProcessInfo:
    """Information about a process using a port"""
    pid: int
    name: str
    command: str
    user: str
    is_system_service: bool = False

class PortManager:
    """Manages port availability and process cleanup"""

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.system = self._detect_platform()

    def _detect_platform(self) -> str:
        """Detect the current platform"""
        if sys.platform.startswith('darwin'):
            return 'macos'
        elif sys.platform.startswith('linux'):
            return 'linux'
        elif sys.platform.startswith('win'):
            return 'windows'
        else:
            return 'unknown'

    def _run_command(self, command: List[str], capture_output: bool = True) -> subprocess.CompletedProcess:
        """Run a command and handle errors"""
        try:
            return subprocess.run(
                command,
                capture_output=capture_output,
                text=True,
                timeout=10
            )
        except subprocess.TimeoutExpired:
            self.logger.error(f"Command timed out: {' '.join(command)}")
            raise
        except FileNotFoundError:
            self.logger.error(f"Command not found: {command[0]}")
            raise

    def get_process_info(self, port: int) -> List[ProcessInfo]:
        """Get detailed information about processes using a port"""
        processes = []

        try:
            # Use lsof to get process information
            result = self._run_command(['lsof', '-i', f':{port}'])

            if result.returncode == 0 and result.stdout.strip():
                lines = result.stdout.strip().split('\n')[1:]  # Skip header

                for line in lines:
                    parts = line.split()
                    if len(parts) >= 9:  # lsof output format
                        try:
                            pid = int(parts[1])
                            process_name = parts[0]
                            user = parts[2]
                            command = ' '.join(parts[8:]) if len(parts) > 8 else process_name

                            process_info = ProcessInfo(
                                pid=pid,
                                name=process_name,
                                command=command,
                                user=user,
                                is_system_service=self.is_system_service(pid)
                            )
                            processes.append(process_info)
                        except (ValueError, IndexError):
                            continue

        except (subprocess.CalledProcessError, FileNotFoundError):
            # lsof not available or failed
            self.logger.debug(f"Could not get process info for port {port}")

        return processes

    def is_system_service(self, pid: int) -> bool:
        """Check if a process is a system service that shouldn't be killed"""
        try:
            if self.system == 'macos':
                # Check for macOS system services
                system_processes = [
                    'AirPlay', 'ControlCenter', 'sharingd', 'coreservicesd',
                    'launchd', 'kernel_task', 'WindowServer'
                ]

                # Get process name using ps
                result = self._run_command(['ps', '-p', str(pid), '-o', 'comm='])
                if result.returncode == 0:
                    process_name = result.stdout.strip().split('/')[-1]
                    return any(sys_proc in process_name for sys_proc in system_processes)

            elif self.system == 'linux':
                # Check if process belongs to root or system users
                result = self._run_command(['ps', '-p', str(pid), '-o', 'user='])
                if result.returncode == 0:
                    user = result.stdout.strip()
                    return user in ['root', 'systemd+', 'dbus']

        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        return False

    def kill_processes_on_port(self, port: int, max_retries: int = 3) -> bool:
        """Kill all processes using a specific port with retry logic"""
        self.logger.info(f"Attempting to kill processes on port {port}")

        for attempt in range(max_retries):
            try:
                # Get current processes on port
                processes = self.get_process_info(port)

                if not processes:
                    self.logger.debug(f"No processes found on port {port}")
                    return True

                # Kill each process
                killed_pids = []
                system_services = []

                for proc_info in processes:
                    if proc_info.is_system_service:
                        self.logger.warning(
                            f"Not killing system service {proc_info.name} (PID: {proc_info.pid}) on port {port}"
                        )
                        system_services.append(proc_info)
                        continue

                    try:
                        self.logger.info(f"Killing process {proc_info.name} (PID: {proc_info.pid}) on port {port}")
                        os.kill(proc_info.pid, signal.SIGKILL)
                        killed_pids.append(proc_info.pid)
                    except (OSError, ProcessLookupError) as e:
                        self.logger.debug(f"Could not kill PID {proc_info.pid}: {e}")

                # Wait for processes to die
                if killed_pids:
                    time.sleep(2)

                    # Check if port is still in use
                    remaining_processes = self.get_process_info(port)
                    if remaining_processes:
                        # Filter out system services we intentionally didn't kill
                        non_system_processes = [
                            p for p in remaining_processes
                            if not p.is_system_service
                        ]

                        if non_system_processes:
                            if attempt < max_retries - 1:
                                self.logger.warning(
                                    f"Port {port} still in use after attempt {attempt + 1}, retrying..."
                                )
                                time.sleep(1)
                                continue
                            else:
                                self.logger.error(
                                    f"Could not free port {port} after {max_retries} attempts"
                                )
                                return False

                # Success
                if killed_pids:
                    self.logger.info(f"Successfully killed {len(killed_pids)} processes on port {port}")
                if system_services:
                    self.logger.warning(
                        f"Left {len(system_services)} system services running on port {port}"
                    )
                return True

            except Exception as e:
                self.logger.error(f"Error killing processes on port {port}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                return False

        return False

    def check_port_available(self, port: int) -> bool:
        """Check if a port is available for use"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(('127.0.0.1', port))
                return result != 0  # 0 means connection succeeded (port in use)
        except Exception as e:
            self.logger.debug(f"Error checking port {port}: {e}")
            return False

    def free_port(self, port: int, name: str, max_retries: int = 5) -> bool:
        """Free a port by killing processes using it, with comprehensive retry logic"""
        self.logger.info(f"Attempting to free port {port} ({name})")

        # First check if port is already free
        if self.check_port_available(port):
            self.logger.debug(f"Port {port} ({name}) is already available")
            return True

        # Try to kill processes with exponential backoff
        for attempt in range(max_retries):
            self.logger.info(f"Port cleanup attempt {attempt + 1}/{max_retries} for {name} on port {port}")

            if self.kill_processes_on_port(port, max_retries=3):
                # Wait and verify port is free
                wait_time = min(2 ** attempt, 5)  # Exponential backoff, max 5s
                self.logger.debug(f"Waiting {wait_time}s for port {port} to be freed")
                time.sleep(wait_time)

                if self.check_port_available(port):
                    self.logger.info(f"✅ Port {port} ({name}) successfully freed")
                    return True
                else:
                    if attempt < max_retries - 1:
                        self.logger.warning(f"Port {port} still in use after cleanup attempt {attempt + 1}")
                        continue
                    else:
                        self.logger.error(f"❌ Could not free port {port} ({name}) after {max_retries} attempts")
                        return False
            else:
                self.logger.error(f"Failed to kill processes on port {port}")
                return False

        return False

    def get_port_status(self, port: int, name: str) -> Dict[str, Any]:
        """Get comprehensive status information for a port"""
        available = self.check_port_available(port)
        processes = self.get_process_info(port)

        status = {
            'port': port,
            'name': name,
            'available': available,
            'process_count': len(processes),
            'processes': [
                {
                    'pid': p.pid,
                    'name': p.name,
                    'command': p.command,
                    'user': p.user,
                    'is_system_service': p.is_system_service
                }
                for p in processes
            ]
        }

        return status

# Global instance for convenience
port_manager = PortManager()

# Convenience functions for backward compatibility
def kill_processes_on_port(port: int, max_retries: int = 3) -> bool:
    """Convenience function to kill processes on a port"""
    return port_manager.kill_processes_on_port(port, max_retries)

def check_port_available(port: int) -> bool:
    """Convenience function to check port availability"""
    return port_manager.check_port_available(port)

def free_port(port: int, name: str, max_retries: int = 5) -> bool:
    """Convenience function to free a port"""
    return port_manager.free_port(port, name, max_retries)

def get_process_info(port: int) -> List[ProcessInfo]:
    """Convenience function to get process information"""
    return port_manager.get_process_info(port)

def get_port_status(port: int, name: str) -> Dict[str, Any]:
    """Convenience function to get port status"""
    return port_manager.get_port_status(port, name)


