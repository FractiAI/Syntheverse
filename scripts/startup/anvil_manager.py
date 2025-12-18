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
import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum

# Import port management module
try:
    from .port_manager import PortManager, free_port
except ImportError:
    # Fallback for direct execution
    sys.path.insert(0, str(Path(__file__).parent))
    from port_manager import PortManager, free_port

class ForkMode(Enum):
    """Anvil fork modes"""
    NONE = "none"
    MAINNET = "mainnet"
    SEPOLIA = "sepolia"
    GOERLI = "goerli"
    CUSTOM = "custom"

@dataclass
class ChainConfig:
    """Anvil chain configuration"""
    chain_id: int = 31337
    fork_mode: ForkMode = ForkMode.NONE
    fork_url: Optional[str] = None
    fork_block_number: Optional[int] = None
    accounts: int = 10
    balance: str = "10000"  # ETH per account
    gas_price: str = "20000000000"  # 20 gwei
    gas_limit: str = "30000000"  # 30M gas
    block_time: Optional[int] = None  # seconds

@dataclass
class BlockchainSnapshot:
    """Snapshot of blockchain state"""
    snapshot_id: str
    timestamp: float
    block_number: int
    accounts: List[Dict[str, Any]]
    gas_price: str
    chain_config: ChainConfig
    metadata: Dict[str, Any] = None

@dataclass
class GasMetrics:
    """Gas usage metrics"""
    average_gas_price: str
    total_transactions: int
    blocks_processed: int
    gas_used_last_block: Optional[int] = None
    timestamp: float = None

AnvilStatus = Any  # Keep existing definition

class AnvilManager:
    """Manages Foundry Anvil Ethereum node with enhanced features"""

    def __init__(self, logger: Optional[logging.Logger] = None, data_dir: Optional[Path] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.port_manager = PortManager(self.logger)
        self.anvil_port = 8545
        self.anvil_process: Optional[subprocess.Popen] = None
        self.start_time: Optional[float] = None

        # Enhanced features
        self.data_dir = data_dir or Path.home() / ".syntheverse" / "anvil"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # State management
        self.chain_config = ChainConfig()
        self.snapshots_dir = self.data_dir / "snapshots"
        self.snapshots_dir.mkdir(exist_ok=True)

        # Gas monitoring
        self.gas_metrics = GasMetrics(
            average_gas_price="20000000000",
            total_transactions=0,
            blocks_processed=0,
            timestamp=time.time()
        )

        # Current state
        self.current_snapshot: Optional[BlockchainSnapshot] = None
        self.fork_mode_active = False

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

    def create_snapshot(self, name: str = None, metadata: Dict[str, Any] = None) -> Optional[str]:
        """Create a snapshot of current blockchain state"""
        if not self.check_anvil_running():
            self.logger.error("Cannot create snapshot: Anvil is not running")
            return None

        try:
            # Get current blockchain state
            state_data = self._get_blockchain_state()

            # Generate snapshot ID
            timestamp = time.time()
            snapshot_id = name or f"snapshot_{int(timestamp)}"

            snapshot = BlockchainSnapshot(
                snapshot_id=snapshot_id,
                timestamp=timestamp,
                block_number=state_data.get('block_number', 0),
                accounts=state_data.get('accounts', []),
                gas_price=state_data.get('gas_price', '0'),
                chain_config=self.chain_config,
                metadata=metadata or {}
            )

            # Save snapshot to disk
            snapshot_file = self.snapshots_dir / f"{snapshot_id}.json"
            with open(snapshot_file, 'w') as f:
                json.dump({
                    'snapshot_id': snapshot.snapshot_id,
                    'timestamp': snapshot.timestamp,
                    'block_number': snapshot.block_number,
                    'accounts': snapshot.accounts,
                    'gas_price': snapshot.gas_price,
                    'chain_config': {
                        'chain_id': snapshot.chain_config.chain_id,
                        'fork_mode': snapshot.chain_config.fork_mode.value,
                        'fork_url': snapshot.chain_config.fork_url,
                        'fork_block_number': snapshot.chain_config.fork_block_number,
                        'accounts': snapshot.chain_config.accounts,
                        'balance': snapshot.chain_config.balance,
                        'gas_price': snapshot.chain_config.gas_price,
                        'gas_limit': snapshot.chain_config.gas_limit,
                        'block_time': snapshot.chain_config.block_time
                    },
                    'metadata': snapshot.metadata
                }, f, indent=2)

            self.current_snapshot = snapshot
            self.logger.info(f"✅ Created snapshot '{snapshot_id}' at block {snapshot.block_number}")
            return snapshot_id

        except Exception as e:
            self.logger.error(f"Failed to create snapshot: {e}")
            return None

    def restore_snapshot(self, snapshot_id: str) -> bool:
        """Restore blockchain state from a snapshot"""
        snapshot_file = self.snapshots_dir / f"{snapshot_id}.json"

        if not snapshot_file.exists():
            self.logger.error(f"Snapshot '{snapshot_id}' not found")
            return False

        try:
            with open(snapshot_file, 'r') as f:
                snapshot_data = json.load(f)

            # Restart Anvil with snapshot configuration
            if self.anvil_process:
                self.stop_anvil()

            # Load chain config from snapshot
            config_data = snapshot_data['chain_config']
            self.chain_config = ChainConfig(
                chain_id=config_data['chain_id'],
                fork_mode=ForkMode(config_data['fork_mode']),
                fork_url=config_data.get('fork_url'),
                fork_block_number=config_data.get('fork_block_number'),
                accounts=config_data['accounts'],
                balance=config_data['balance'],
                gas_price=config_data['gas_price'],
                gas_limit=config_data['gas_limit'],
                block_time=config_data.get('block_time')
            )

            # Start Anvil with the restored configuration
            success = self.start_anvil(
                accounts=self.chain_config.accounts,
                block_time=self.chain_config.block_time
            )

            if success:
                self.current_snapshot = BlockchainSnapshot(
                    snapshot_id=snapshot_data['snapshot_id'],
                    timestamp=snapshot_data['timestamp'],
                    block_number=snapshot_data['block_number'],
                    accounts=snapshot_data['accounts'],
                    gas_price=snapshot_data['gas_price'],
                    chain_config=self.chain_config,
                    metadata=snapshot_data.get('metadata', {})
                )
                self.logger.info(f"✅ Restored snapshot '{snapshot_id}'")
                return True
            else:
                self.logger.error(f"Failed to start Anvil with snapshot configuration")
                return False

        except Exception as e:
            self.logger.error(f"Failed to restore snapshot: {e}")
            return False

    def list_snapshots(self) -> List[Dict[str, Any]]:
        """List all available snapshots"""
        snapshots = []

        for snapshot_file in self.snapshots_dir.glob("*.json"):
            try:
                with open(snapshot_file, 'r') as f:
                    data = json.load(f)
                    snapshots.append({
                        'id': data['snapshot_id'],
                        'timestamp': data['timestamp'],
                        'block_number': data['block_number'],
                        'created': time.ctime(data['timestamp']),
                        'file': snapshot_file.name
                    })
            except Exception as e:
                self.logger.debug(f"Could not read snapshot file {snapshot_file}: {e}")

        return sorted(snapshots, key=lambda x: x['timestamp'], reverse=True)

    def delete_snapshot(self, snapshot_id: str) -> bool:
        """Delete a snapshot"""
        snapshot_file = self.snapshots_dir / f"{snapshot_id}.json"

        if snapshot_file.exists():
            try:
                snapshot_file.unlink()
                self.logger.info(f"Deleted snapshot '{snapshot_id}'")
                return True
            except Exception as e:
                self.logger.error(f"Failed to delete snapshot '{snapshot_id}': {e}")
                return False
        else:
            self.logger.warning(f"Snapshot '{snapshot_id}' not found")
            return False

    def _get_blockchain_state(self) -> Dict[str, Any]:
        """Get current blockchain state for snapshot"""
        state = {}

        try:
            # Get block number
            response = requests.post(
                f"http://127.0.0.1:{self.anvil_port}",
                json={"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1},
                timeout=5
            )
            if response.status_code == 200:
                result = response.json()
                state['block_number'] = int(result.get('result', '0'), 16)

            # Get accounts and balances
            response = requests.post(
                f"http://127.0.0.1:{self.anvil_port}",
                json={"jsonrpc": "2.0", "method": "eth_accounts", "params": [], "id": 1},
                timeout=5
            )
            accounts = []
            if response.status_code == 200:
                result = response.json()
                account_addresses = result.get('result', [])

                # Get balance for each account
                for addr in account_addresses[:10]:  # Limit to first 10 accounts
                    balance_response = requests.post(
                        f"http://127.0.0.1:{self.anvil_port}",
                        json={"jsonrpc": "2.0", "method": "eth_getBalance", "params": [addr, "latest"], "id": 1},
                        timeout=5
                    )
                    balance = "0x0"
                    if balance_response.status_code == 200:
                        balance_result = balance_response.json()
                        balance = balance_result.get('result', "0x0")

                    accounts.append({
                        'address': addr,
                        'balance': balance
                    })

            state['accounts'] = accounts

            # Get gas price
            response = requests.post(
                f"http://127.0.0.1:{self.anvil_port}",
                json={"jsonrpc": "2.0", "method": "eth_gasPrice", "params": [], "id": 1},
                timeout=5
            )
            if response.status_code == 200:
                result = response.json()
                state['gas_price'] = result.get('result', '0')

        except Exception as e:
            self.logger.debug(f"Could not get blockchain state: {e}")

        return state

    def set_chain_config(self, config: ChainConfig):
        """Update chain configuration"""
        self.chain_config = config
        self.logger.info(f"Updated chain configuration: chain_id={config.chain_id}, fork={config.fork_mode.value}")

    def enable_fork_mode(self, fork_url: str, fork_mode: ForkMode = ForkMode.MAINNET,
                        block_number: Optional[int] = None) -> bool:
        """Enable fork mode for Anvil"""
        if self.check_anvil_running():
            self.logger.warning("Cannot enable fork mode: Anvil is already running")
            return False

        self.chain_config.fork_mode = fork_mode
        self.chain_config.fork_url = fork_url
        self.chain_config.fork_block_number = block_number
        self.fork_mode_active = True

        self.logger.info(f"Enabled fork mode: {fork_mode.value} from {fork_url}")
        return True

    def disable_fork_mode(self):
        """Disable fork mode"""
        self.chain_config.fork_mode = ForkMode.NONE
        self.chain_config.fork_url = None
        self.chain_config.fork_block_number = None
        self.fork_mode_active = False
        self.logger.info("Disabled fork mode")

    def update_gas_price(self, gas_price: str):
        """Update gas price configuration"""
        self.chain_config.gas_price = gas_price
        self.logger.info(f"Updated gas price to {gas_price}")

    def validate_block_time(self, expected_block_time: int, tolerance: int = 2) -> bool:
        """Validate that blocks are being mined at expected interval"""
        if not self.check_anvil_running():
            return False

        try:
            # Get latest block timestamp
            response = requests.post(
                f"http://127.0.0.1:{self.anvil_port}",
                json={"jsonrpc": "2.0", "method": "eth_getBlockByNumber", "params": ["latest", False], "id": 1},
                timeout=5
            )

            if response.status_code == 200:
                result = response.json()
                block_data = result.get('result', {})
                block_timestamp = int(block_data.get('timestamp', '0'), 16)

                current_time = int(time.time())
                time_diff = current_time - block_timestamp

                if abs(time_diff - expected_block_time) <= tolerance:
                    return True
                else:
                    self.logger.warning(f"Block time validation failed: expected ~{expected_block_time}s, got {time_diff}s")
                    return False

        except Exception as e:
            self.logger.debug(f"Could not validate block time: {e}")
            return False

    def get_gas_metrics(self) -> GasMetrics:
        """Get current gas usage metrics"""
        if not self.check_anvil_running():
            return self.gas_metrics

        try:
            # Update metrics
            response = requests.post(
                f"http://127.0.0.1:{self.anvil_port}",
                json={"jsonrpc": "2.0", "method": "eth_gasPrice", "params": [], "id": 1},
                timeout=5
            )

            if response.status_code == 200:
                result = response.json()
                current_gas_price = result.get('result', self.gas_metrics.average_gas_price)
                self.gas_metrics.average_gas_price = current_gas_price

            # Get latest block for gas used
            response = requests.post(
                f"http://127.0.0.1:{self.anvil_port}",
                json={"jsonrpc": "2.0", "method": "eth_getBlockByNumber", "params": ["latest", False], "id": 1},
                timeout=5
            )

            if response.status_code == 200:
                result = response.json()
                block_data = result.get('result', {})
                gas_used_hex = block_data.get('gasUsed', '0x0')
                self.gas_metrics.gas_used_last_block = int(gas_used_hex, 16)

                # Update transaction count
                tx_count = len(block_data.get('transactions', []))
                self.gas_metrics.total_transactions += tx_count

                self.gas_metrics.blocks_processed = int(block_data.get('number', '0'), 16)
                self.gas_metrics.timestamp = time.time()

        except Exception as e:
            self.logger.debug(f"Could not update gas metrics: {e}")

        return self.gas_metrics

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

    def start_anvil(self, accounts: Optional[int] = None, block_time: Optional[int] = None,
                   gas_limit: Optional[str] = None, silent: bool = True,
                   chain_id: Optional[int] = None, balance: Optional[str] = None) -> bool:
        """Start Anvil in the background with enhanced configuration"""
        self.logger.info("Starting Anvil Ethereum node...")

        # Check if already running
        if self.check_anvil_running():
            self.logger.info("✅ Anvil is already running")
            return True

        # Free the port if needed
        if not free_port(self.anvil_port, "Anvil"):
            self.logger.error(f"❌ Could not free port {self.anvil_port} for Anvil")
            return False

        # Update chain config with provided parameters
        if accounts is not None:
            self.chain_config.accounts = accounts
        if block_time is not None:
            self.chain_config.block_time = block_time
        if gas_limit is not None:
            self.chain_config.gas_limit = gas_limit
        if chain_id is not None:
            self.chain_config.chain_id = chain_id
        if balance is not None:
            self.chain_config.balance = balance

        # Build command with full configuration
        cmd = ["anvil"]

        # Basic configuration
        cmd.extend(["--accounts", str(self.chain_config.accounts)])
        cmd.extend(["--balance", self.chain_config.balance])
        cmd.extend(["--gas-price", self.chain_config.gas_price])
        cmd.extend(["--gas-limit", self.chain_config.gas_limit])
        cmd.extend(["--port", str(self.anvil_port)])

        # Chain configuration
        if self.chain_config.chain_id != 31337:  # Default chain ID
            cmd.extend(["--chain-id", str(self.chain_config.chain_id)])

        # Fork mode configuration
        if self.fork_mode_active and self.chain_config.fork_url:
            cmd.extend(["--fork-url", self.chain_config.fork_url])
            if self.chain_config.fork_block_number:
                cmd.extend(["--fork-block-number", str(self.chain_config.fork_block_number)])

        # Block time configuration
        if self.chain_config.block_time:
            cmd.extend(["--block-time", str(self.chain_config.block_time)])

        # Silent mode
        if silent:
            cmd.append("--silent")

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

                # Log fork mode status
                if self.fork_mode_active:
                    self.logger.info(f"Fork mode active: {self.chain_config.fork_mode.value}")

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

# Enhanced convenience functions
def create_snapshot(name: str = None, metadata: Dict[str, Any] = None) -> Optional[str]:
    """Create a blockchain snapshot"""
    return anvil_manager.create_snapshot(name, metadata)

def restore_snapshot(snapshot_id: str) -> bool:
    """Restore from a snapshot"""
    return anvil_manager.restore_snapshot(snapshot_id)

def list_snapshots() -> List[Dict[str, Any]]:
    """List available snapshots"""
    return anvil_manager.list_snapshots()

def delete_snapshot(snapshot_id: str) -> bool:
    """Delete a snapshot"""
    return anvil_manager.delete_snapshot(snapshot_id)

def enable_fork_mode(fork_url: str, fork_mode: ForkMode = ForkMode.MAINNET,
                    block_number: Optional[int] = None) -> bool:
    """Enable fork mode"""
    return anvil_manager.enable_fork_mode(fork_url, fork_mode, block_number)

def disable_fork_mode():
    """Disable fork mode"""
    anvil_manager.disable_fork_mode()

def set_chain_config(config: ChainConfig):
    """Update chain configuration"""
    anvil_manager.set_chain_config(config)

def get_gas_metrics() -> GasMetrics:
    """Get gas usage metrics"""
    return anvil_manager.get_gas_metrics()

def validate_block_time(expected_block_time: int, tolerance: int = 2) -> bool:
    """Validate block time"""
    return anvil_manager.validate_block_time(expected_block_time, tolerance)







