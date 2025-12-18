"""
Wallet Integration Module for Syntheverse
Provides browser-based wallet connection, transaction signing, and user interaction
"""

import json
import logging
from typing import Dict, List, Optional, Any, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import time
from pathlib import Path

# Set up logger
logger = logging.getLogger(__name__)

try:
    from web3 import Web3
    from eth_account import Account
    from eth_account.messages import encode_defunct
except ImportError as e:
    logger.error(f"Web3 dependencies not installed: {e}")
    logger.info("Install with: pip install web3 eth-account")
    raise


class WalletType(Enum):
    """Supported wallet types"""
    METAMASK = "metamask"
    COINBASE_WALLET = "coinbase_wallet"
    WALLET_CONNECT = "wallet_connect"
    TRUST_WALLET = "trust_wallet"
    RAINBOW = "rainbow"
    ZERION = "zerion"


class WalletError(Exception):
    """Base wallet error"""
    pass


class WalletConnectionError(WalletError):
    """Raised when wallet connection fails"""
    pass


class WalletNotFoundError(WalletError):
    """Raised when requested wallet is not available"""
    pass


class TransactionSigningError(WalletError):
    """Raised when transaction signing fails"""
    pass


@dataclass
class WalletInfo:
    """Wallet connection information"""
    address: str
    chain_id: int
    wallet_type: WalletType
    connected: bool = True
    balance: float = 0.0
    network_name: str = ""
    is_metamask: bool = False
    is_coinbase_wallet: bool = False


@dataclass
class TransactionRequest:
    """Transaction request data"""
    to: str
    value: int = 0
    data: str = ""
    gas_limit: Optional[int] = None
    gas_price: Optional[int] = None
    nonce: Optional[int] = None


@dataclass
class SignedTransaction:
    """Signed transaction data"""
    raw_transaction: str
    transaction_hash: str
    signature: str


class BrowserWalletConnector:
    """
    Browser-based wallet connector for Syntheverse
    Handles MetaMask, Coinbase Wallet, and other Web3 wallets
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize wallet connector

        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        self.w3: Optional[Web3] = None
        self.wallet_info: Optional[WalletInfo] = None
        self._event_handlers: Dict[str, List[Callable]] = {}

    def _setup_web3(self):
        """Set up Web3 connection"""
        if not self.w3:
            # Try to connect to injected provider (MetaMask, etc.)
            try:
                from web3.auto import w3 as auto_w3
                if auto_w3 and auto_w3.is_connected():
                    self.w3 = auto_w3
                else:
                    # Fallback to window.ethereum
                    self.w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))  # Anvil fallback
            except Exception as e:
                self.logger.warning(f"Could not connect to Web3 provider: {e}")
                self.w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))

    def _detect_available_wallets(self) -> List[WalletType]:
        """
        Detect available wallets in browser

        Returns:
            List of available wallet types
        """
        available_wallets = []

        try:
            # Check for MetaMask
            if hasattr(self.w3.provider, 'isMetaMask') and self.w3.provider.isMetaMask:
                available_wallets.append(WalletType.METAMASK)

            # Check for Coinbase Wallet
            if hasattr(self.w3.provider, 'isCoinbaseWallet') and self.w3.provider.isCoinbaseWallet:
                available_wallets.append(WalletType.COINBASE_WALLET)

            # Check for other wallet indicators
            if hasattr(self.w3.provider, 'isTrust') and self.w3.provider.isTrust:
                available_wallets.append(WalletType.TRUST_WALLET)

        except Exception as e:
            self.logger.warning(f"Error detecting wallets: {e}")

        return available_wallets

    async def connect_wallet(self, wallet_type: WalletType) -> WalletInfo:
        """
        Connect to specified wallet

        Args:
            wallet_type: Type of wallet to connect to

        Returns:
            Wallet connection information

        Raises:
            WalletNotFoundError: If wallet is not available
            WalletConnectionError: If connection fails
        """
        self._setup_web3()

        # Check if wallet is available
        available_wallets = self._detect_available_wallets()
        if wallet_type not in available_wallets:
            raise WalletNotFoundError(f"{wallet_type.value} wallet not detected")

        try:
            # Request wallet connection
            if wallet_type == WalletType.METAMASK:
                await self._connect_metamask()
            elif wallet_type == WalletType.COINBASE_WALLET:
                await self._connect_coinbase_wallet()
            else:
                await self._connect_generic_wallet(wallet_type)

            # Get wallet information
            accounts = await self._get_accounts()
            chain_id = await self._get_chain_id()

            if not accounts:
                raise WalletConnectionError("No accounts available")

            address = accounts[0]
            balance = await self._get_balance(address)
            network_name = await self._get_network_name(chain_id)

            self.wallet_info = WalletInfo(
                address=address,
                chain_id=chain_id,
                wallet_type=wallet_type,
                balance=balance,
                network_name=network_name,
                is_metamask=(wallet_type == WalletType.METAMASK),
                is_coinbase_wallet=(wallet_type == WalletType.COINBASE_WALLET)
            )

            self.logger.info(f"Connected to {wallet_type.value}: {address}")
            self._emit_event('connected', self.wallet_info)

            return self.wallet_info

        except Exception as e:
            self.logger.error(f"Wallet connection failed: {e}")
            raise WalletConnectionError(f"Failed to connect to {wallet_type.value}: {e}")

    async def _connect_metamask(self):
        """Connect to MetaMask"""
        try:
            # Request account access
            accounts = await self.w3.provider.request({
                "method": "eth_requestAccounts"
            })

            # Switch to Base network if needed
            await self._ensure_correct_network()

        except Exception as e:
            raise WalletConnectionError(f"MetaMask connection failed: {e}")

    async def _connect_coinbase_wallet(self):
        """Connect to Coinbase Wallet"""
        try:
            # Request account access
            accounts = await self.w3.provider.request({
                "method": "eth_requestAccounts"
            })

            # Coinbase Wallet automatically handles network switching

        except Exception as e:
            raise WalletConnectionError(f"Coinbase Wallet connection failed: {e}")

    async def _connect_generic_wallet(self, wallet_type: WalletType):
        """Connect to generic Web3 wallet"""
        try:
            accounts = await self.w3.provider.request({
                "method": "eth_requestAccounts"
            })

        except Exception as e:
            raise WalletConnectionError(f"{wallet_type.value} connection failed: {e}")

    async def _ensure_correct_network(self, target_chain_id: int = 84532):
        """
        Ensure wallet is on correct network (Base Sepolia by default)

        Args:
            target_chain_id: Target chain ID
        """
        try:
            current_chain_id = await self._get_chain_id()

            if current_chain_id != target_chain_id:
                # Try to switch network
                try:
                    await self.w3.provider.request({
                        "method": "wallet_switchEthereumChain",
                        "params": [{"chainId": hex(target_chain_id)}],
                    })
                except Exception:
                    # Network not added, try to add it
                    network_params = self._get_network_params(target_chain_id)
                    if network_params:
                        await self.w3.provider.request({
                            "method": "wallet_addEthereumChain",
                            "params": [network_params],
                        })

        except Exception as e:
            self.logger.warning(f"Network switching failed: {e}")

    def _get_network_params(self, chain_id: int) -> Optional[Dict[str, Any]]:
        """Get network parameters for adding to wallet"""
        networks = {
            84532: {  # Base Sepolia
                "chainId": "0x14A34",
                "chainName": "Base Sepolia",
                "nativeCurrency": {
                    "name": "Ethereum",
                    "symbol": "ETH",
                    "decimals": 18
                },
                "rpcUrls": ["https://sepolia.base.org"],
                "blockExplorerUrls": ["https://sepolia.basescan.org"]
            },
            8453: {  # Base Mainnet
                "chainId": "0x2105",
                "chainName": "Base",
                "nativeCurrency": {
                    "name": "Ethereum",
                    "symbol": "ETH",
                    "decimals": 18
                },
                "rpcUrls": ["https://mainnet.base.org"],
                "blockExplorerUrls": ["https://basescan.org"]
            }
        }
        return networks.get(chain_id)

    async def _get_accounts(self) -> List[str]:
        """Get connected accounts"""
        try:
            accounts = await self.w3.provider.request({
                "method": "eth_accounts"
            })
            return accounts
        except Exception:
            return []

    async def _get_chain_id(self) -> int:
        """Get current chain ID"""
        try:
            chain_id_hex = await self.w3.provider.request({
                "method": "eth_chainId"
            })
            return int(chain_id_hex, 16)
        except Exception:
            return 1  # Ethereum mainnet fallback

    async def _get_balance(self, address: str) -> float:
        """Get account balance"""
        try:
            balance_wei = await self.w3.eth.get_balance(address)
            balance_eth = self.w3.from_wei(balance_wei, 'ether')
            return float(balance_eth)
        except Exception:
            return 0.0

    async def _get_network_name(self, chain_id: int) -> str:
        """Get network name from chain ID"""
        network_names = {
            1: "Ethereum Mainnet",
            11155111: "Ethereum Sepolia",
            8453: "Base Mainnet",
            84532: "Base Sepolia",
            31337: "Anvil Local"
        }
        return network_names.get(chain_id, f"Chain {chain_id}")

    async def sign_transaction(self, tx_request: TransactionRequest) -> SignedTransaction:
        """
        Sign a transaction using connected wallet

        Args:
            tx_request: Transaction request data

        Returns:
            Signed transaction data

        Raises:
            TransactionSigningError: If signing fails
        """
        if not self.wallet_info:
            raise WalletConnectionError("Wallet not connected")

        try:
            # Build transaction object
            tx = {
                'from': self.wallet_info.address,
                'to': tx_request.to,
                'value': tx_request.value,
                'data': tx_request.data,
                'chainId': self.wallet_info.chain_id
            }

            # Add optional fields
            if tx_request.gas_limit:
                tx['gas'] = tx_request.gas_limit
            if tx_request.gas_price:
                tx['gasPrice'] = tx_request.gas_price
            if tx_request.nonce is not None:
                tx['nonce'] = tx_request.nonce

            # Request signature from wallet
            signed_tx = await self.w3.provider.request({
                "method": "eth_sendTransaction",
                "params": [tx]
            })

            # For MetaMask, eth_sendTransaction returns the tx hash directly
            transaction_hash = signed_tx

            return SignedTransaction(
                raw_transaction="",  # Not available from wallet
                transaction_hash=transaction_hash,
                signature=""  # Not available from wallet
            )

        except Exception as e:
            self.logger.error(f"Transaction signing failed: {e}")
            raise TransactionSigningError(f"Failed to sign transaction: {e}")

    async def sign_message(self, message: str) -> str:
        """
        Sign a message using connected wallet

        Args:
            message: Message to sign

        Returns:
            Signature

        Raises:
            TransactionSigningError: If signing fails
        """
        if not self.wallet_info:
            raise WalletConnectionError("Wallet not connected")

        try:
            # Request message signature from wallet
            signature = await self.w3.provider.request({
                "method": "personal_sign",
                "params": [message, self.wallet_info.address]
            })

            return signature

        except Exception as e:
            self.logger.error(f"Message signing failed: {e}")
            raise TransactionSigningError(f"Failed to sign message: {e}")

    def add_event_listener(self, event: str, callback: Callable):
        """
        Add event listener for wallet events

        Args:
            event: Event name ('connected', 'disconnected', 'chainChanged', 'accountsChanged')
            callback: Event callback function
        """
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(callback)

    def remove_event_listener(self, event: str, callback: Callable):
        """
        Remove event listener

        Args:
            event: Event name
            callback: Callback function to remove
        """
        if event in self._event_handlers:
            self._event_handlers[event] = [
                cb for cb in self._event_handlers[event] if cb != callback
            ]

    def _emit_event(self, event: str, data: Any = None):
        """Emit event to listeners"""
        if event in self._event_handlers:
            for callback in self._event_handlers[event]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        asyncio.create_task(callback(data))
                    else:
                        callback(data)
                except Exception as e:
                    self.logger.error(f"Event callback error: {e}")

    def disconnect_wallet(self):
        """Disconnect wallet"""
        self.wallet_info = None
        self._emit_event('disconnected')
        self.logger.info("Wallet disconnected")

    def get_wallet_info(self) -> Optional[WalletInfo]:
        """Get current wallet information"""
        return self.wallet_info

    async def switch_network(self, chain_id: int):
        """
        Switch to different network

        Args:
            chain_id: Target chain ID
        """
        await self._ensure_correct_network(chain_id)

        # Update wallet info
        if self.wallet_info:
            self.wallet_info.chain_id = chain_id
            self.wallet_info.network_name = await self._get_network_name(chain_id)

            # Refresh balance
            self.wallet_info.balance = await self._get_balance(self.wallet_info.address)

            self._emit_event('chainChanged', self.wallet_info)


class SyntheverseWalletManager:
    """
    High-level wallet manager for Syntheverse operations
    Combines wallet connection with Syntheverse-specific functionality
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize Syntheverse wallet manager

        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        self.wallet_connector = BrowserWalletConnector(logger)
        self.contracts: Dict[str, Any] = {}
        self.contract_addresses: Dict[str, str] = {}

    def setup_event_listeners(self):
        """Set up wallet event listeners"""
        self.wallet_connector.add_event_listener('connected', self._on_wallet_connected)
        self.wallet_connector.add_event_listener('disconnected', self._on_wallet_disconnected)
        self.wallet_connector.add_event_listener('chainChanged', self._on_chain_changed)

    def _on_wallet_connected(self, wallet_info: WalletInfo):
        """Handle wallet connection event"""
        self.logger.info(f"Wallet connected: {wallet_info.address}")
        self.load_contracts()

    def _on_wallet_disconnected(self):
        """Handle wallet disconnection event"""
        self.logger.info("Wallet disconnected")
        self.contracts = {}

    def _on_chain_changed(self, wallet_info: WalletInfo):
        """Handle chain change event"""
        self.logger.info(f"Chain changed to {wallet_info.network_name}")
        self.load_contracts()  # Reload contracts for new chain

    async def connect_wallet(self, wallet_type: WalletType = WalletType.METAMASK) -> WalletInfo:
        """
        Connect to wallet

        Args:
            wallet_type: Type of wallet to connect to

        Returns:
            Wallet information
        """
        return await self.wallet_connector.connect_wallet(wallet_type)

    def load_contracts(self):
        """Load deployed contracts for current network"""
        if not self.wallet_connector.wallet_info:
            return

        try:
            # Load contract addresses based on network
            chain_id = self.wallet_connector.wallet_info.chain_id

            # For now, use hardcoded addresses (should be loaded from config)
            if chain_id == 84532:  # Base Sepolia
                self.contract_addresses = {
                    'synth': '0x742d35Cc6634C0532925a3b844Bc454e4438f44e',
                    'poc_registry': '0x742d35Cc6634C0532925a3b844Bc454e4438f44f'
                }
            elif chain_id == 31337:  # Anvil Local
                # Try to load from artifacts
                contracts_dir = Path(__file__).parent / "contracts"
                try:
                    synth_path = contracts_dir / "artifacts" / "src" / "SYNTH.sol" / "SYNTH.json"
                    poc_path = contracts_dir / "artifacts" / "src" / "POCRegistry.sol" / "POCRegistry.json"

                    if synth_path.exists():
                        with open(synth_path) as f:
                            synth_data = json.load(f)
                            self.contract_addresses['synth'] = synth_data.get('address', '')

                    if poc_path.exists():
                        with open(poc_path) as f:
                            poc_data = json.load(f)
                            self.contract_addresses['poc_registry'] = poc_data.get('address', '')
                except Exception as e:
                    self.logger.warning(f"Could not load contract addresses: {e}")

            # Create contract instances
            for name, address in self.contract_addresses.items():
                if address and self.wallet_connector.w3:
                    # Load ABI (would normally be from artifacts)
                    abi = self._get_contract_abi(name)
                    if abi:
                        self.contracts[name] = self.wallet_connector.w3.eth.contract(
                            address=address,
                            abi=abi
                        )
                        self.logger.info(f"Loaded contract {name}: {address}")

        except Exception as e:
            self.logger.error(f"Failed to load contracts: {e}")

    def _get_contract_abi(self, contract_name: str) -> Optional[List[Dict]]:
        """Get contract ABI (simplified - would load from artifacts)"""
        # This would normally load from the artifact files
        # For now, return minimal ABIs for demonstration
        abis = {
            'synth': [
                {"inputs": [], "name": "totalSupply", "outputs": [{"type": "uint256"}], "stateMutability": "view", "type": "function"},
                {"inputs": [{"name": "account", "type": "address"}], "name": "balanceOf", "outputs": [{"type": "uint256"}], "stateMutability": "view", "type": "function"}
            ],
            'poc_registry': [
                {"inputs": [{"name": "title", "type": "string"}, {"name": "description", "type": "string"}, {"name": "contributor", "type": "address"}], "name": "submitContribution", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
                {"inputs": [{"name": "submissionHash", "type": "bytes32"}], "name": "getContribution", "outputs": [{"components": [{"name": "title", "type": "string"}, {"name": "contributor", "type": "address"}, {"name": "status", "type": "uint8"}], "type": "tuple"}], "stateMutability": "view", "type": "function"}
            ]
        }
        return abis.get(contract_name)

    async def submit_contribution(
        self,
        title: str,
        description: str,
        contributor_address: str
    ) -> str:
        """
        Submit a contribution to the blockchain

        Args:
            title: Contribution title
            description: Contribution description
            contributor_address: Contributor wallet address

        Returns:
            Transaction hash
        """
        if 'poc_registry' not in self.contracts:
            raise WalletError("POC Registry contract not loaded")

        # Create transaction request
        tx_request = TransactionRequest(
            to=self.contract_addresses['poc_registry'],
            data=self.contracts['poc_registry'].encodeABI(
                fn_name='submitContribution',
                args=[title, description, contributor_address]
            )
        )

        # Sign and send transaction
        signed_tx = await self.wallet_connector.sign_transaction(tx_request)

        self.logger.info(f"Contribution submitted: {signed_tx.transaction_hash}")
        return signed_tx.transaction_hash

    def get_wallet_info(self) -> Optional[WalletInfo]:
        """Get current wallet information"""
        return self.wallet_connector.get_wallet_info()

    def disconnect_wallet(self):
        """Disconnect wallet"""
        self.wallet_connector.disconnect_wallet()


# HTML/JavaScript integration helpers
def generate_wallet_connection_html() -> str:
    """
    Generate HTML/JavaScript for wallet connection in browser

    Returns:
        HTML string with wallet connection code
    """
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Syntheverse Wallet Connection</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; }
        .wallet-button { background: #2196F3; color: white; border: none; padding: 12px 24px; margin: 10px; border-radius: 8px; cursor: pointer; }
        .wallet-button:hover { background: #1976D2; }
        .wallet-button:disabled { background: #ccc; cursor: not-allowed; }
        .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .status.connected { background: #4CAF50; color: white; }
        .status.error { background: #f44336; color: white; }
        .info { background: #e3f2fd; padding: 15px; border-radius: 8px; }
    </style>
</head>
<body>
    <h1>🌟 Syntheverse Wallet Connection</h1>

    <div class="info">
        <h3>Connect Your Wallet</h3>
        <p>Connect your Web3 wallet to interact with Syntheverse on the blockchain.</p>
    </div>

    <div id="walletStatus" class="status" style="display: none;"></div>

    <div id="walletButtons">
        <button class="wallet-button" onclick="connectWallet('metamask')">
            🦊 Connect MetaMask
        </button>
        <button class="wallet-button" onclick="connectWallet('coinbase_wallet')">
            🟫 Connect Coinbase Wallet
        </button>
    </div>

    <div id="walletInfo" style="display: none;">
        <h3>Wallet Information</h3>
        <p><strong>Address:</strong> <span id="walletAddress"></span></p>
        <p><strong>Network:</strong> <span id="networkName"></span></p>
        <p><strong>Balance:</strong> <span id="balance"></span> ETH</p>

        <button class="wallet-button" onclick="submitContribution()">
            📄 Submit Contribution
        </button>
        <button class="wallet-button" onclick="disconnectWallet()">
            ❌ Disconnect
        </button>
    </div>

    <script>
        let walletManager = null;
        let currentWallet = null;

        async function connectWallet(walletType) {
            try {
                // Disable buttons during connection
                document.querySelectorAll('.wallet-button').forEach(btn => btn.disabled = true);
                showStatus('Connecting to wallet...', 'info');

                // Initialize wallet manager (this would be handled by Python backend)
                const response = await fetch('/api/connect-wallet', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ wallet_type: walletType })
                });

                const result = await response.json();

                if (result.success) {
                    currentWallet = result.wallet_info;
                    showWalletInfo(result.wallet_info);
                    showStatus('Wallet connected successfully!', 'connected');
                } else {
                    throw new Error(result.error);
                }

            } catch (error) {
                showStatus('Connection failed: ' + error.message, 'error');
                document.querySelectorAll('.wallet-button').forEach(btn => btn.disabled = false);
            }
        }

        function showStatus(message, type) {
            const statusDiv = document.getElementById('walletStatus');
            statusDiv.textContent = message;
            statusDiv.className = 'status ' + type;
            statusDiv.style.display = 'block';
        }

        function showWalletInfo(walletInfo) {
            document.getElementById('walletAddress').textContent = walletInfo.address;
            document.getElementById('networkName').textContent = walletInfo.network_name;
            document.getElementById('balance').textContent = walletInfo.balance.toFixed(4);

            document.getElementById('walletButtons').style.display = 'none';
            document.getElementById('walletInfo').style.display = 'block';
        }

        async function submitContribution() {
            try {
                const response = await fetch('/api/submit-contribution', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        title: 'Test Contribution from Wallet',
                        description: 'A contribution submitted via wallet connection',
                        contributor_address: currentWallet.address
                    })
                });

                const result = await response.json();

                if (result.success) {
                    showStatus(`Contribution submitted! TX: ${result.transaction_hash}`, 'connected');
                } else {
                    throw new Error(result.error);
                }

            } catch (error) {
                showStatus('Submission failed: ' + error.message, 'error');
            }
        }

        async function disconnectWallet() {
            try {
                await fetch('/api/disconnect-wallet', { method: 'POST' });

                document.getElementById('walletInfo').style.display = 'none';
                document.getElementById('walletButtons').style.display = 'block';
                document.getElementById('walletStatus').style.display = 'none';

                currentWallet = null;

            } catch (error) {
                console.error('Disconnect error:', error);
            }
        }

        // Check if wallet is already connected on page load
        window.addEventListener('load', async () => {
            try {
                const response = await fetch('/api/wallet-info');
                const result = await response.json();

                if (result.connected) {
                    showWalletInfo(result);
                }
            } catch (error) {
                console.error('Wallet check error:', error);
            }
        });
    </script>
</body>
</html>
    """


if __name__ == "__main__":
    # Example usage (would run in browser environment)
    logger.info("Wallet integration module for Syntheverse")
    logger.info("This module provides browser-based wallet connection capabilities")
    logger.info("To use:")
    logger.info("1. Include the generated HTML in your web interface")
    logger.info("2. Set up API endpoints for wallet operations")
    logger.info("3. Handle wallet events and user interactions")






