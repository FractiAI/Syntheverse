"""
Web3 Integration Module for Syntheverse
Provides real blockchain connectivity, wallet integration, and transaction handling
"""

import json
import logging
import os
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

# Set up logger
logger = logging.getLogger(__name__)

try:
    from web3 import Web3
    from web3.middleware import geth_poa_middleware
    from web3.gas_strategies.time_based import medium_gas_price_strategy
    from eth_account import Account
    from eth_account.signers.local import LocalAccount
    import eth_utils
except ImportError as e:
    logger.error(f"Web3 dependencies not installed: {e}")
    logger.info("Install with: pip install web3 eth-account")
    raise

from .layer1.contracts.synth_token import SYNTHToken
from .layer1.contracts.poc_contract import POCContract


class Network(Enum):
    """Supported blockchain networks"""
    ANVIL_LOCAL = "anvil_local"
    BASE_SEPOLIA = "base_sepolia"
    BASE_MAINNET = "base_mainnet"
    ETHEREUM_SEPOLIA = "ethereum_sepolia"
    ETHEREUM_MAINNET = "ethereum_mainnet"


@dataclass
class NetworkConfig:
    """Network configuration"""
    name: str
    chain_id: int
    rpc_url: str
    block_explorer: Optional[str] = None
    currency_symbol: str = "ETH"


class WalletConnectionError(Exception):
    """Raised when wallet connection fails"""
    pass


class TransactionError(Exception):
    """Raised when transaction fails"""
    pass


class Web3Manager:
    """
    Comprehensive Web3 integration manager for Syntheverse
    Handles network connections, wallet management, and contract interactions
    """

    # Network configurations
    NETWORK_CONFIGS = {
        Network.ANVIL_LOCAL: NetworkConfig(
            name="Anvil Local",
            chain_id=31337,
            rpc_url="http://127.0.0.1:8545",
            currency_symbol="ETH"
        ),
        Network.BASE_SEPOLIA: NetworkConfig(
            name="Base Sepolia",
            chain_id=84532,
            rpc_url="https://sepolia.base.org",
            block_explorer="https://sepolia.basescan.org",
            currency_symbol="ETH"
        ),
        Network.BASE_MAINNET: NetworkConfig(
            name="Base Mainnet",
            chain_id=8453,
            rpc_url="https://mainnet.base.org",
            block_explorer="https://basescan.org",
            currency_symbol="ETH"
        ),
        Network.ETHEREUM_SEPOLIA: NetworkConfig(
            name="Ethereum Sepolia",
            chain_id=11155111,
            rpc_url="https://rpc.sepolia.org",
            block_explorer="https://sepolia.etherscan.io",
            currency_symbol="ETH"
        ),
        Network.ETHEREUM_MAINNET: NetworkConfig(
            name="Ethereum Mainnet",
            chain_id=1,
            rpc_url="https://rpc.ankr.com/eth",
            block_explorer="https://etherscan.io",
            currency_symbol="ETH"
        )
    }

    def __init__(self, network: Network = Network.ANVIL_LOCAL, logger: Optional[logging.Logger] = None):
        """
        Initialize Web3 manager

        Args:
            network: Target blockchain network
            logger: Optional logger instance
        """
        self.network = network
        self.config = self.NETWORK_CONFIGS[network]
        self.logger = logger or logging.getLogger(__name__)
        self.w3: Optional[Web3] = None
        self.account: Optional[LocalAccount] = None
        self.contracts: Dict[str, Any] = {}

        # Contract addresses (loaded from artifacts or environment)
        self.contract_addresses: Dict[str, str] = {}

        # Initialize connection
        self._connect()

    def _connect(self) -> bool:
        """
        Establish connection to blockchain network

        Returns:
            True if connection successful
        """
        try:
            self.w3 = Web3(Web3.HTTPProvider(self.config.rpc_url))

            # Add middleware for PoA networks
            if self.network in [Network.BASE_SEPOLIA, Network.BASE_MAINNET]:
                self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

            # Set gas strategy
            self.w3.eth.set_gas_price_strategy(medium_gas_price_strategy)

            # Test connection
            if not self.w3.is_connected():
                raise ConnectionError(f"Cannot connect to {self.config.name}")

            # Verify chain ID
            actual_chain_id = self.w3.eth.chain_id
            if actual_chain_id != self.config.chain_id:
                self.logger.warning(
                    f"Chain ID mismatch: expected {self.config.chain_id}, got {actual_chain_id}"
                )

            self.logger.info(f"Connected to {self.config.name} (Chain ID: {actual_chain_id})")
            return True

        except Exception as e:
            self.logger.error(f"Failed to connect to {self.config.name}: {e}")
            return False

    def connect_wallet_from_private_key(self, private_key: str) -> bool:
        """
        Connect wallet using private key

        Args:
            private_key: Private key (with or without 0x prefix)

        Returns:
            True if connection successful
        """
        try:
            if not private_key.startswith('0x'):
                private_key = '0x' + private_key

            self.account = Account.from_key(private_key)
            self.logger.info(f"Wallet connected: {self.account.address}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to connect wallet: {e}")
            raise WalletConnectionError(f"Invalid private key: {e}")

    def connect_wallet_from_mnemonic(self, mnemonic: str, account_index: int = 0) -> bool:
        """
        Connect wallet using mnemonic phrase

        Args:
            mnemonic: Mnemonic phrase
            account_index: Account index to derive (default: 0)

        Returns:
            True if connection successful
        """
        try:
            Account.enable_unaudited_hdwallet_features()
            self.account = Account.from_mnemonic(mnemonic, account_path=f"m/44'/60'/0'/0/{account_index}")
            self.logger.info(f"Wallet connected from mnemonic: {self.account.address}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to connect wallet from mnemonic: {e}")
            raise WalletConnectionError(f"Invalid mnemonic: {e}")

    def get_wallet_balance(self) -> float:
        """
        Get wallet balance in native currency

        Returns:
            Balance in native currency units
        """
        if not self.account or not self.w3:
            raise WalletConnectionError("Wallet not connected")

        balance_wei = self.w3.eth.get_balance(self.account.address)
        balance_eth = self.w3.from_wei(balance_wei, 'ether')
        return float(balance_eth)

    def load_contracts_from_artifacts(self, contracts_dir: Optional[Path] = None) -> bool:
        """
        Load deployed contract addresses and ABIs from artifact files

        Args:
            contracts_dir: Directory containing contract artifacts

        Returns:
            True if contracts loaded successfully
        """
        if not contracts_dir:
            # Default path relative to this file
            contracts_dir = Path(__file__).parent / "contracts"

        try:
            # Load SYNTH contract
            synth_path = contracts_dir / "artifacts" / "src" / "SYNTH.sol" / "SYNTH.json"
            if synth_path.exists():
                with open(synth_path) as f:
                    synth_data = json.load(f)
                    self.contract_addresses['synth'] = synth_data.get('address', '')
                    self.contracts['synth'] = self.w3.eth.contract(
                        address=self.contract_addresses['synth'],
                        abi=synth_data['abi']
                    )
                    self.logger.info(f"SYNTH contract loaded: {self.contract_addresses['synth']}")

            # Load POCRegistry contract
            poc_path = contracts_dir / "artifacts" / "src" / "POCRegistry.sol" / "POCRegistry.json"
            if poc_path.exists():
                with open(poc_path) as f:
                    poc_data = json.load(f)
                    self.contract_addresses['poc_registry'] = poc_data.get('address', '')
                    self.contracts['poc_registry'] = self.w3.eth.contract(
                        address=self.contract_addresses['poc_registry'],
                        abi=poc_data['abi']
                    )
                    self.logger.info(f"POCRegistry contract loaded: {self.contract_addresses['poc_registry']}")

            return True

        except Exception as e:
            self.logger.error(f"Failed to load contracts: {e}")
            return False

    def send_transaction(
        self,
        to_address: str,
        value_wei: int = 0,
        data: str = "",
        gas_limit: Optional[int] = None
    ) -> str:
        """
        Send a transaction

        Args:
            to_address: Recipient address
            value_wei: Value in wei
            data: Transaction data (hex string)
            gas_limit: Gas limit override

        Returns:
            Transaction hash
        """
        if not self.account or not self.w3:
            raise WalletConnectionError("Wallet not connected")

        try:
            # Build transaction
            nonce = self.w3.eth.get_transaction_count(self.account.address)

            tx = {
                'nonce': nonce,
                'to': to_address,
                'value': value_wei,
                'gas': gas_limit or 21000,
                'gasPrice': self.w3.eth.generate_gas_price(),
                'chainId': self.config.chain_id
            }

            if data:
                tx['data'] = data
                # Estimate gas for contract calls
                if not gas_limit:
                    try:
                        tx['gas'] = self.w3.eth.estimate_gas(tx)
                    except Exception:
                        tx['gas'] = 200000  # Default for contract calls

            # Sign and send transaction
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

            self.logger.info(f"Transaction sent: {tx_hash.hex()}")
            return tx_hash.hex()

        except Exception as e:
            self.logger.error(f"Transaction failed: {e}")
            raise TransactionError(f"Transaction failed: {e}")

    def call_contract_method(
        self,
        contract_name: str,
        method_name: str,
        *args,
        **kwargs
    ) -> Any:
        """
        Call a contract method (read-only)

        Args:
            contract_name: Name of contract ('synth' or 'poc_registry')
            method_name: Method name to call
            *args: Method arguments
            **kwargs: Additional options (from_address, etc.)

        Returns:
            Method result
        """
        if contract_name not in self.contracts:
            raise ValueError(f"Contract {contract_name} not loaded")

        contract = self.contracts[contract_name]
        method = getattr(contract.functions, method_name)

        try:
            if 'from_address' in kwargs:
                # Call with specific from address
                result = method(*args).call({'from': kwargs['from_address']})
            else:
                result = method(*args).call()

            return result

        except Exception as e:
            self.logger.error(f"Contract call failed: {e}")
            raise

    def transact_contract_method(
        self,
        contract_name: str,
        method_name: str,
        *args,
        gas_limit: Optional[int] = None,
        value_wei: int = 0
    ) -> str:
        """
        Execute a contract method transaction

        Args:
            contract_name: Name of contract ('synth' or 'poc_registry')
            method_name: Method name to call
            *args: Method arguments
            gas_limit: Gas limit override
            value_wei: Value in wei to send

        Returns:
            Transaction hash
        """
        if contract_name not in self.contracts:
            raise ValueError(f"Contract {contract_name} not loaded")

        if not self.account:
            raise WalletConnectionError("Wallet not connected")

        contract = self.contracts[contract_name]
        method = getattr(contract.functions, method_name)

        try:
            # Build transaction
            tx_data = method(*args).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gasPrice': self.w3.eth.generate_gas_price(),
                'chainId': self.config.chain_id,
                'value': value_wei
            })

            # Override gas limit if provided
            if gas_limit:
                tx_data['gas'] = gas_limit
            elif 'gas' not in tx_data:
                try:
                    tx_data['gas'] = method(*args).estimate_gas({'from': self.account.address})
                except Exception:
                    tx_data['gas'] = 200000

            # Sign and send
            signed_tx = self.account.sign_transaction(tx_data)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

            self.logger.info(f"Contract transaction sent: {tx_hash.hex()}")
            return tx_hash.hex()

        except Exception as e:
            self.logger.error(f"Contract transaction failed: {e}")
            raise TransactionError(f"Contract transaction failed: {e}")

    def wait_for_transaction(self, tx_hash: str, timeout: int = 120) -> Dict[str, Any]:
        """
        Wait for transaction confirmation

        Args:
            tx_hash: Transaction hash
            timeout: Timeout in seconds

        Returns:
            Transaction receipt
        """
        try:
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
            self.logger.info(f"Transaction confirmed: {tx_hash}")
            return dict(receipt)

        except Exception as e:
            self.logger.error(f"Transaction confirmation failed: {e}")
            raise

    def get_transaction_receipt(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """
        Get transaction receipt

        Args:
            tx_hash: Transaction hash

        Returns:
            Transaction receipt or None if not found
        """
        try:
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            return dict(receipt) if receipt else None

        except Exception as e:
            self.logger.error(f"Failed to get transaction receipt: {e}")
            return None

    def get_block_explorer_url(self, tx_hash: str) -> Optional[str]:
        """
        Get block explorer URL for transaction

        Args:
            tx_hash: Transaction hash

        Returns:
            Block explorer URL or None if not supported
        """
        if self.config.block_explorer:
            return f"{self.config.block_explorer}/tx/{tx_hash}"
        return None

    def get_network_info(self) -> Dict[str, Any]:
        """
        Get current network information

        Returns:
            Network information dictionary
        """
        if not self.w3:
            return {"connected": False}

        try:
            return {
                "connected": True,
                "network": self.config.name,
                "chain_id": self.w3.eth.chain_id,
                "block_number": self.w3.eth.block_number,
                "gas_price": self.w3.from_wei(self.w3.eth.gas_price, 'gwei'),
                "wallet_connected": self.account is not None,
                "wallet_address": self.account.address if self.account else None,
                "contracts_loaded": list(self.contracts.keys())
            }

        except Exception as e:
            self.logger.error(f"Failed to get network info: {e}")
            return {"connected": False, "error": str(e)}

    def submit_poc_to_blockchain(
        self,
        contribution_data: Dict[str, Any],
        evaluation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Submit complete PoC contribution to blockchain

        Args:
            contribution_data: Contribution details
            evaluation_data: Evaluation results

        Returns:
            Submission result
        """
        try:
            # Prepare contribution data for contract
            title = contribution_data.get('title', '')
            description = contribution_data.get('description', '')
            contributor = contribution_data.get('contributor', '')

            # Submit to POCRegistry contract
            tx_hash = self.transact_contract_method(
                'poc_registry',
                'submitContribution',
                title,
                description,
                contributor
            )

            # Wait for confirmation
            receipt = self.wait_for_transaction(tx_hash)

            return {
                "success": True,
                "transaction_hash": tx_hash,
                "block_number": receipt['blockNumber'],
                "gas_used": receipt['gasUsed'],
                "explorer_url": self.get_block_explorer_url(tx_hash)
            }

        except Exception as e:
            self.logger.error(f"PoC submission failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def register_certificate_on_blockchain(
        self,
        submission_hash: str,
        metal_type: str,
        reward_amount: int
    ) -> Dict[str, Any]:
        """
        Register PoC certificate on blockchain

        Args:
            submission_hash: Submission hash
            metal_type: Certificate metal (gold, silver, copper)
            reward_amount: SYNTH reward amount

        Returns:
            Registration result
        """
        try:
            # Register certificate on POCRegistry
            tx_hash = self.transact_contract_method(
                'poc_registry',
                'registerCertificate',
                submission_hash,
                metal_type,
                reward_amount
            )

            # Wait for confirmation
            receipt = self.wait_for_transaction(tx_hash)

            return {
                "success": True,
                "transaction_hash": tx_hash,
                "certificate_registered": True,
                "block_number": receipt['blockNumber'],
                "explorer_url": self.get_block_explorer_url(tx_hash)
            }

        except Exception as e:
            self.logger.error(f"Certificate registration failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }


class SyntheverseWeb3Client:
    """
    High-level client for Syntheverse Web3 operations
    Combines Web3Manager with Syntheverse-specific logic
    """

    def __init__(
        self,
        network: Network = Network.ANVIL_LOCAL,
        private_key: Optional[str] = None,
        mnemonic: Optional[str] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize Syntheverse Web3 client

        Args:
            network: Target network
            private_key: Optional private key for wallet
            mnemonic: Optional mnemonic for wallet
            logger: Optional logger
        """
        self.web3_manager = Web3Manager(network, logger)
        self.logger = logger or logging.getLogger(__name__)

        # Connect wallet if provided
        if private_key:
            self.web3_manager.connect_wallet_from_private_key(private_key)
        elif mnemonic:
            self.web3_manager.connect_wallet_from_mnemonic(mnemonic)

        # Load contracts
        project_root = Path(__file__).parent.parent.parent
        contracts_dir = project_root / "src" / "blockchain" / "contracts"
        self.web3_manager.load_contracts_from_artifacts(contracts_dir)

    def submit_contribution(
        self,
        contribution: Dict[str, Any],
        evaluation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Submit a complete contribution to the blockchain

        Args:
            contribution: Contribution data
            evaluation: Evaluation results

        Returns:
            Submission result
        """
        return self.web3_manager.submit_poc_to_blockchain(contribution, evaluation)

    def get_contribution_status(self, submission_hash: str) -> Dict[str, Any]:
        """
        Get contribution status from blockchain

        Args:
            submission_hash: Submission hash

        Returns:
            Status information
        """
        try:
            # Call contract method to get contribution status
            status = self.web3_manager.call_contract_method(
                'poc_registry',
                'getContribution',
                submission_hash
            )

            return {
                "found": True,
                "status": status
            }

        except Exception as e:
            return {
                "found": False,
                "error": str(e)
            }

    def get_wallet_info(self) -> Dict[str, Any]:
        """
        Get wallet information

        Returns:
            Wallet information
        """
        if not self.web3_manager.account:
            return {"connected": False}

        try:
            balance = self.web3_manager.get_wallet_balance()
            network_info = self.web3_manager.get_network_info()

            return {
                "connected": True,
                "address": self.web3_manager.account.address,
                "balance": balance,
                "network": network_info
            }

        except Exception as e:
            return {
                "connected": False,
                "error": str(e)
            }


# Utility functions
def setup_web3_logging(level: int = logging.INFO) -> logging.Logger:
    """Set up logging for Web3 operations"""
    logger = logging.getLogger('syntheverse_web3')
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def create_web3_client_from_env() -> SyntheverseWeb3Client:
    """
    Create Web3 client from environment variables

    Environment variables:
    - SYNTHVERSE_NETWORK: Network name (default: anvil_local)
    - SYNTHVERSE_PRIVATE_KEY: Private key for wallet
    - SYNTHVERSE_MNEMONIC: Mnemonic for wallet

    Returns:
        Configured Web3 client
    """
    # Get network from env
    network_name = os.getenv('SYNTHVERSE_NETWORK', 'anvil_local')
    try:
        network = Network(network_name.lower())
    except ValueError:
        network = Network.ANVIL_LOCAL

    # Get wallet credentials
    private_key = os.getenv('SYNTHVERSE_PRIVATE_KEY')
    mnemonic = os.getenv('SYNTHVERSE_MNEMONIC')

    # Set up logging
    logger = setup_web3_logging()

    return SyntheverseWeb3Client(
        network=network,
        private_key=private_key,
        mnemonic=mnemonic,
        logger=logger
    )


if __name__ == "__main__":
    # Example usage
    import os

    # Set up logging
    logger = setup_web3_logging()

    # Create client
    client = SyntheverseWeb3Client(
        network=Network.ANVIL_LOCAL,
        logger=logger
    )

    logger.info("Web3 Client initialized")
    logger.info(f"Network info: {client.web3_manager.get_network_info()}")

    # Example contribution submission
    contribution = {
        "title": "Test Contribution",
        "description": "A test scientific contribution",
        "contributor": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
        "category": "scientific"
    }

    evaluation = {
        "coherence": 8500,
        "density": 9000,
        "novelty": 8000,
        "status": "approved"
    }

    # Only submit if wallet is connected
    if client.web3_manager.account:
        result = client.submit_contribution(contribution, evaluation)
        logger.info(f"Submission result: {result}")
    else:
        logger.warning("No wallet connected - skipping submission example")






