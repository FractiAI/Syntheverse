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
import hashlib
import threading
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

@dataclass
class ProcessInfo:
    """Information about a process using a port"""
    pid: int
    name: str
    command: str
    user: str
    is_system_service: bool = False
    fingerprint: Optional[str] = None  # Unique process fingerprint

@dataclass
class PortReservation:
    """Port reservation information"""
    port: int
    service: str
    pid: int
    fingerprint: str
    timestamp: float

@dataclass
class PortMetrics:
    """Port operation metrics"""
    port: int
    service: str
    cleanup_duration: float
    retry_count: int
    processes_killed: int
    system_processes_spared: int
    success: bool
    timestamp: float

class PortManager:
    """Manages port availability and process cleanup"""

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.system = self._detect_platform()

        # Port status caching
        self._port_cache: Dict[int, Dict[str, Any]] = {}
        self._cache_ttl = 30  # seconds

        # Port reservations
        self._reservations: Dict[int, PortReservation] = {}

        # Process fingerprinting cache
        self._process_fingerprints: Dict[int, str] = {}

        # Metrics collection
        self._metrics: List[PortMetrics] = []
        self._metrics_lock = threading.Lock()

        # Thread pool for parallel operations
        self._executor = ThreadPoolExecutor(max_workers=4)

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

    def get_process_fingerprint(self, pid: int) -> str:
        """Generate a unique fingerprint for a process"""
        if pid in self._process_fingerprints:
            return self._process_fingerprints[pid]

        try:
            # Get detailed process information
            fingerprint_data = []

            if self.system in ['macos', 'linux']:
                # Get command line and working directory
                try:
                    result = self._run_command(['ps', '-p', str(pid), '-o', 'comm=,args=,cwd='])
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')
                        if lines:
                            fingerprint_data.extend(lines[0].split())
                except (subprocess.CalledProcessError, FileNotFoundError):
                    pass

            elif self.system == 'windows':
                # Windows-specific process info
                try:
                    result = self._run_command(['tasklist', '/FI', f'PID eq {pid}', '/FO', 'CSV'])
                    if result.returncode == 0 and len(result.stdout.strip().split('\n')) > 1:
                        # Parse CSV output (skip header)
                        line = result.stdout.strip().split('\n')[1]
                        parts = line.split('","')
                        if len(parts) >= 3:
                            fingerprint_data.append(parts[0].strip('"'))  # Image name
                            fingerprint_data.append(parts[2].strip('"'))  # PID
                except (subprocess.CalledProcessError, FileNotFoundError):
                    pass

            # Add PID and timestamp for uniqueness
            fingerprint_data.extend([str(pid), str(int(time.time()))])

            # Generate hash
            fingerprint = hashlib.md5(' '.join(fingerprint_data).encode()).hexdigest()
            self._process_fingerprints[pid] = fingerprint
            return fingerprint

        except Exception as e:
            self.logger.debug(f"Could not generate fingerprint for PID {pid}: {e}")
            # Fallback to PID-based fingerprint
            fallback = hashlib.md5(f"pid:{pid}:{int(time.time())}".encode()).hexdigest()
            self._process_fingerprints[pid] = fallback
            return fallback

    def get_process_info(self, port: int, use_cache: bool = True) -> List[ProcessInfo]:
        """Get detailed information about processes using a port"""
        # Check cache first
        if use_cache and port in self._port_cache:
            cached = self._port_cache[port]
            if time.time() - cached['timestamp'] < self._cache_ttl:
                return cached['processes']

        processes = []

        try:
            if self.system in ['macos', 'linux']:
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

                                fingerprint = self.get_process_fingerprint(pid)

                                process_info = ProcessInfo(
                                    pid=pid,
                                    name=process_name,
                                    command=command,
                                    user=user,
                                    is_system_service=self.is_system_service(pid),
                                    fingerprint=fingerprint
                                )
                                processes.append(process_info)
                            except (ValueError, IndexError):
                                continue

            elif self.system == 'windows':
                # Use netstat for Windows
                result = self._run_command(['netstat', '-ano'])

                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')

                    for line in lines:
                        if ':LISTENING' in line or f':{port}' in line:
                            parts = line.split()
                            if len(parts) >= 5:
                                try:
                                    local_address = parts[1]
                                    if f':{port}' in local_address:
                                        pid = int(parts[4]) if len(parts) > 4 else 0

                                        if pid > 0:
                                            fingerprint = self.get_process_fingerprint(pid)

                                            # Get process name via tasklist
                                            process_name = "unknown"
                                            try:
                                                task_result = self._run_command(
                                                    ['tasklist', '/FI', f'PID eq {pid}', '/FO', 'CSV']
                                                )
                                                if task_result.returncode == 0:
                                                    task_lines = task_result.stdout.strip().split('\n')
                                                    if len(task_lines) > 1:
                                                        process_name = task_lines[1].split('","')[0].strip('"')
                                            except:
                                                pass

                                            process_info = ProcessInfo(
                                                pid=pid,
                                                name=process_name,
                                                command=f"{process_name} (PID: {pid})",
                                                user="unknown",  # Windows doesn't easily give user info
                                                is_system_service=False,  # Simplified for Windows
                                                fingerprint=fingerprint
                                            )
                                            processes.append(process_info)
                                except (ValueError, IndexError):
                                    continue

        except (subprocess.CalledProcessError, FileNotFoundError):
            # lsof/netstat not available or failed
            self.logger.debug(f"Could not get process info for port {port}")

        # Cache the result
        self._port_cache[port] = {
            'processes': processes,
            'timestamp': time.time()
        }

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

    def kill_processes_on_port(self, port: int, max_retries: int = 3, target_service: str = None) -> bool:
        """Kill all processes using a specific port with retry logic and fingerprinting"""
        self.logger.info(f"Attempting to kill processes on port {port}")

        for attempt in range(max_retries):
            try:
                # Get current processes on port
                processes = self.get_process_info(port)

                if not processes:
                    self.logger.debug(f"No processes found on port {port}")
                    return True

                # Kill each process (with fingerprinting protection)
                killed_pids = []
                system_services = []
                protected_processes = []

                for proc_info in processes:
                    if proc_info.is_system_service:
                        self.logger.warning(
                            f"Not killing system service {proc_info.name} (PID: {proc_info.pid}) on port {port}"
                        )
                        system_services.append(proc_info)
                        continue

                    # Check if this process is reserved for a different service
                    if self.is_port_reserved(port) and target_service:
                        reservation = self._reservations.get(port)
                        if reservation and reservation.service != target_service:
                            self.logger.warning(
                                f"Not killing process {proc_info.name} (PID: {proc_info.pid}) - "
                                f"port reserved for service '{reservation.service}'"
                            )
                            protected_processes.append(proc_info)
                            continue

                    # Verify process fingerprint matches before killing
                    current_fingerprint = self.get_process_fingerprint(proc_info.pid)
                    if proc_info.fingerprint and current_fingerprint != proc_info.fingerprint:
                        self.logger.warning(
                            f"Process fingerprint mismatch for PID {proc_info.pid} on port {port} - "
                            f"process may have changed, skipping kill"
                        )
                        protected_processes.append(proc_info)
                        continue

                    try:
                        self.logger.info(f"Killing process {proc_info.name} (PID: {proc_info.pid}) on port {port}")
                        os.kill(proc_info.pid, signal.SIGKILL)
                        killed_pids.append(proc_info.pid)
                    except (OSError, ProcessLookupError) as e:
                        self.logger.debug(f"Could not kill PID {proc_info.pid}: {e}")

                # Wait for processes to die
                if killed_pids:
                    time.sleep(1)  # Reduced wait time

                    # Check if port is still in use
                    remaining_processes = self.get_process_info(port, use_cache=False)  # Force fresh check
                    if remaining_processes:
                        # Filter out system services and protected processes we intentionally didn't kill
                        non_system_processes = [
                            p for p in remaining_processes
                            if not p.is_system_service and p not in protected_processes
                        ]

                        if non_system_processes:
                            if attempt < max_retries - 1:
                                self.logger.warning(
                                    f"Port {port} still in use after attempt {attempt + 1}, retrying..."
                                )
                                time.sleep(0.5)  # Reduced retry delay
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
                if protected_processes:
                    self.logger.warning(
                        f"Left {len(protected_processes)} protected processes running on port {port}"
                    )
                return True

            except Exception as e:
                self.logger.error(f"Error killing processes on port {port}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(0.5)
                    continue
                return False

        return False

    def reserve_port(self, port: int, service: str, pid: int) -> bool:
        """Reserve a port for a specific service and process"""
        fingerprint = self.get_process_fingerprint(pid)

        reservation = PortReservation(
            port=port,
            service=service,
            pid=pid,
            fingerprint=fingerprint,
            timestamp=time.time()
        )

        self._reservations[port] = reservation
        self.logger.debug(f"Reserved port {port} for service '{service}' (PID: {pid})")
        return True

    def release_port_reservation(self, port: int, service: str = None) -> bool:
        """Release a port reservation"""
        if port in self._reservations:
            reservation = self._reservations[port]
            if service is None or reservation.service == service:
                del self._reservations[port]
                self.logger.debug(f"Released reservation for port {port}")
                return True

        return False

    def is_port_reserved(self, port: int, service: str = None) -> bool:
        """Check if a port is reserved"""
        if port not in self._reservations:
            return False

        reservation = self._reservations[port]

        # Check if reservation is still valid (process is still running)
        if not self._is_process_running(reservation.pid, reservation.fingerprint):
            # Process died, clean up reservation
            del self._reservations[port]
            return False

        return service is None or reservation.service == service

    def _is_process_running(self, pid: int, expected_fingerprint: str) -> bool:
        """Check if a process is still running with the expected fingerprint"""
        try:
            current_fingerprint = self.get_process_fingerprint(pid)
            return current_fingerprint == expected_fingerprint
        except Exception:
            return False

    def check_ports_batch(self, ports: List[int]) -> Dict[int, bool]:
        """Check availability of multiple ports in parallel"""
        results = {}

        def check_single_port(port):
            return port, self.check_port_available(port)

        # Use ThreadPoolExecutor for parallel checking
        futures = [self._executor.submit(check_single_port, port) for port in ports]

        for future in as_completed(futures):
            try:
                port, available = future.result()
                results[port] = available
            except Exception as e:
                self.logger.debug(f"Error checking port in batch: {e}")

        return results

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

    def _record_metrics(self, port: int, name: str, cleanup_duration: float,
                       retry_count: int, processes_killed: int, system_processes_spared: int, success: bool):
        """Record port operation metrics"""
        metrics = PortMetrics(
            port=port,
            service=name,
            cleanup_duration=cleanup_duration,
            retry_count=retry_count,
            processes_killed=processes_killed,
            system_processes_spared=system_processes_spared,
            success=success,
            timestamp=time.time()
        )

        with self._metrics_lock:
            self._metrics.append(metrics)

            # Keep only last 100 metrics to prevent memory bloat
            if len(self._metrics) > 100:
                self._metrics = self._metrics[-100:]

    def get_metrics(self, port: int = None, service: str = None, limit: int = 10) -> List[PortMetrics]:
        """Get port operation metrics"""
        with self._metrics_lock:
            metrics = self._metrics.copy()

        # Filter by port and/or service
        if port is not None:
            metrics = [m for m in metrics if m.port == port]
        if service is not None:
            metrics = [m for m in metrics if m.service == service]

        # Return most recent metrics
        return sorted(metrics, key=lambda m: m.timestamp, reverse=True)[:limit]

    def free_port(self, port: int, name: str, max_retries: int = 5) -> bool:
        """Free a port by killing processes using it, with comprehensive retry logic and metrics"""
        start_time = time.time()
        self.logger.info(f"Attempting to free port {port} ({name})")

        # First check if port is already free
        if self.check_port_available(port):
            self.logger.debug(f"Port {port} ({name}) is already available")
            cleanup_duration = time.time() - start_time
            self._record_metrics(port, name, cleanup_duration, 0, 0, 0, True)
            return True

        processes_killed = 0
        system_processes_spared = 0

        # Try to kill processes with improved logic
        for attempt in range(max_retries):
            self.logger.info(f"Port cleanup attempt {attempt + 1}/{max_retries} for {name} on port {port}")

            # Get process info before killing to track metrics
            processes_before = self.get_process_info(port, use_cache=False)

            if self.kill_processes_on_port(port, max_retries=2, target_service=name):
                # Count killed processes (approximate)
                processes_after = self.get_process_info(port, use_cache=False)
                processes_killed = len(processes_before) - len(processes_after)
                system_processes_spared = len([p for p in processes_before if p.is_system_service])

                # Verify port is free
                if self.check_port_available(port):
                    cleanup_duration = time.time() - start_time
                    self.logger.info(f"✅ Port {port} ({name}) successfully freed")
                    self._record_metrics(port, name, cleanup_duration, attempt + 1,
                                       processes_killed, system_processes_spared, True)
                    return True
                else:
                    if attempt < max_retries - 1:
                        self.logger.warning(f"Port {port} still in use after cleanup attempt {attempt + 1}")
                        continue
                    else:
                        cleanup_duration = time.time() - start_time
                        self.logger.error(f"❌ Could not free port {port} ({name}) after {max_retries} attempts")
                        self._record_metrics(port, name, cleanup_duration, max_retries,
                                           processes_killed, system_processes_spared, False)
                        return False
            else:
                cleanup_duration = time.time() - start_time
                self.logger.error(f"Failed to kill processes on port {port}")
                self._record_metrics(port, name, cleanup_duration, attempt + 1,
                                   processes_killed, system_processes_spared, False)
                return False

        cleanup_duration = time.time() - start_time
        self._record_metrics(port, name, cleanup_duration, max_retries,
                           processes_killed, system_processes_spared, False)
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

# New convenience functions for enhanced features
def reserve_port(port: int, service: str, pid: int) -> bool:
    """Reserve a port for a service"""
    return port_manager.reserve_port(port, service, pid)

def release_port_reservation(port: int, service: str = None) -> bool:
    """Release a port reservation"""
    return port_manager.release_port_reservation(port, service)

def is_port_reserved(port: int, service: str = None) -> bool:
    """Check if a port is reserved"""
    return port_manager.is_port_reserved(port, service)

def check_ports_batch(ports: List[int]) -> Dict[int, bool]:
    """Check multiple ports in parallel"""
    return port_manager.check_ports_batch(ports)

def get_port_metrics(port: int = None, service: str = None, limit: int = 10) -> List[PortMetrics]:
    """Get port operation metrics"""
    return port_manager.get_metrics(port, service, limit)

def get_process_fingerprint(pid: int) -> str:
    """Get process fingerprint"""
    return port_manager.get_process_fingerprint(pid)







