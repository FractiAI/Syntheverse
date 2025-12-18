"""
Enhanced Contract Interface for Syntheverse
Provides high-level interface to smart contracts with real Web3 integration
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# Set up logger
logger = logging.getLogger(__name__)

try:
    from web3 import Web3
    from eth_account import Account
except ImportError as e:
    logger.error(f"Web3 dependencies not installed: {e}")
    logger.info("Install with: pip install web3 eth-account")
    raise

from .web3_integration import Web3Manager, Network, SyntheverseWeb3Client
from .layer1.contracts.synth_token import SYNTHToken
from .layer1.contracts.poc_contract import POCContract


@dataclass
class ContractCallResult:
    """Result of a contract call"""
    success: bool
    data: Any = None
    error: str = ""
    gas_used: Optional[int] = None
    block_number: Optional[int] = None


@dataclass
class TransactionResult:
    """Result of a contract transaction"""
    success: bool
    transaction_hash: str = ""
    receipt: Optional[Dict[str, Any]] = None
    error: str = ""
    gas_used: int = 0
    block_number: int = 0
    explorer_url: Optional[str] = None


class SyntheverseContractInterface:
    """
    High-level interface to Syntheverse smart contracts
    Combines Web3 functionality with contract-specific logic
    """

    def __init__(
        self,
        web3_client: Optional[SyntheverseWeb3Client] = None,
        network: Network = Network.ANVIL_LOCAL,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize contract interface

        Args:
            web3_client: Optional pre-configured Web3 client
            network: Blockchain network to connect to
            logger: Optional logger
        """
        self.logger = logger or logging.getLogger(__name__)

        if web3_client:
            self.web3_client = web3_client
            self.web3_manager = web3_client.web3_manager
        else:
            self.web3_client = SyntheverseWeb3Client(network=network, logger=logger)
            self.web3_manager = self.web3_client.web3_manager

        # Initialize Python contract instances for logic
        self.synth_contract = SYNTHToken()
        self.poc_contract = POCContract(self.synth_contract)

        # Load contract ABIs and addresses
        self._load_contract_artifacts()

    def _load_contract_artifacts(self):
        """Load contract artifacts from filesystem"""
        try:
            project_root = Path(__file__).parent.parent.parent
            contracts_dir = project_root / "src" / "blockchain" / "contracts"

            # Load SYNTH contract
            synth_path = contracts_dir / "artifacts" / "src" / "SYNTH.sol" / "SYNTH.json"
            if synth_path.exists():
                with open(synth_path) as f:
                    synth_data = json.load(f)
                    self.synth_abi = synth_data.get('abi', [])
                    self.synth_address = synth_data.get('address', '')

            # Load POCRegistry contract
            poc_path = contracts_dir / "artifacts" / "src" / "POCRegistry.sol" / "POCRegistry.json"
            if poc_path.exists():
                with open(poc_path) as f:
                    poc_data = json.load(f)
                    self.poc_abi = poc_data.get('abi', [])
                    self.poc_address = poc_data.get('address', '')

            self.logger.info("Contract artifacts loaded successfully")

        except Exception as e:
            self.logger.error(f"Failed to load contract artifacts: {e}")
            self.synth_abi = []
            self.poc_abi = []
            self.synth_address = ""
            self.poc_address = ""

    # SYNTH Token Methods

    def get_synth_total_supply(self) -> ContractCallResult:
        """
        Get total SYNTH token supply

        Returns:
            Contract call result
        """
        try:
            if self.synth_address and self.synth_abi:
                result = self.web3_manager.call_contract_method(
                    'synth',
                    'totalSupply'
                )
                return ContractCallResult(success=True, data=result)
            else:
                # Fallback to Python implementation
                total_supply = self.synth_contract.TOTAL_SUPPLY
                return ContractCallResult(success=True, data=total_supply)

        except Exception as e:
            self.logger.error(f"Failed to get SYNTH total supply: {e}")
            return ContractCallResult(success=False, error=str(e))

    def get_synth_balance(self, address: str) -> ContractCallResult:
        """
        Get SYNTH token balance for address

        Args:
            address: Wallet address

        Returns:
            Contract call result
        """
        try:
            if self.synth_address and self.synth_abi:
                result = self.web3_manager.call_contract_method(
                    'synth',
                    'balanceOf',
                    address
                )
                return ContractCallResult(success=True, data=result)
            else:
                # Fallback to Python implementation
                balance = self.synth_contract.get_balance(address)
                return ContractCallResult(success=True, data=balance)

        except Exception as e:
            self.logger.error(f"Failed to get SYNTH balance: {e}")
            return ContractCallResult(success=False, error=str(e))

    def get_synth_epoch_balance(self, epoch: str) -> ContractCallResult:
        """
        Get SYNTH balance for specific epoch

        Args:
            epoch: Epoch name

        Returns:
            Contract call result
        """
        try:
            # Use Python implementation (blockchain storage would be different)
            from .layer1.contracts.synth_token import Epoch
            epoch_enum = Epoch(epoch.lower())
            balance = self.synth_contract.get_epoch_balance(epoch_enum)
            return ContractCallResult(success=True, data=balance)

        except Exception as e:
            self.logger.error(f"Failed to get epoch balance: {e}")
            return ContractCallResult(success=False, error=str(e))

    # PoC Registry Methods

    def submit_poc_contribution(
        self,
        title: str,
        description: str,
        contributor: str,
        category: str = "scientific"
    ) -> TransactionResult:
        """
        Submit a PoC contribution to the blockchain

        Args:
            title: Contribution title
            description: Contribution description
            contributor: Contributor address
            category: Contribution category

        Returns:
            Transaction result
        """
        try:
            # Use Web3 client method
            contribution_data = {
                "title": title,
                "description": description,
                "contributor": contributor,
                "category": category
            }

            evaluation_data = {
                "status": "pending"  # Initial status
            }

            result = self.web3_client.submit_contribution(contribution_data, evaluation_data)

            if result["success"]:
                return TransactionResult(
                    success=True,
                    transaction_hash=result["transaction_hash"],
                    receipt={"blockNumber": result.get("block_number")},
                    gas_used=result.get("gas_used", 0),
                    block_number=result.get("block_number", 0),
                    explorer_url=result.get("explorer_url")
                )
            else:
                return TransactionResult(
                    success=False,
                    error=result.get("error", "Unknown error")
                )

        except Exception as e:
            self.logger.error(f"Failed to submit PoC contribution: {e}")
            return TransactionResult(success=False, error=str(e))

    def get_poc_contribution(self, submission_hash: str) -> ContractCallResult:
        """
        Get PoC contribution details

        Args:
            submission_hash: Submission hash

        Returns:
            Contract call result
        """
        try:
            if self.poc_address and self.poc_abi:
                result = self.web3_manager.call_contract_method(
                    'poc_registry',
                    'getContribution',
                    submission_hash
                )
                return ContractCallResult(success=True, data=result)
            else:
                # Fallback to Python implementation
                contribution = self.poc_contract.get_submission(submission_hash)
                return ContractCallResult(success=True, data=contribution)

        except Exception as e:
            self.logger.error(f"Failed to get PoC contribution: {e}")
            return ContractCallResult(success=False, error=str(e))

    def evaluate_poc_contribution(
        self,
        submission_hash: str,
        coherence: float,
        density: float,
        novelty: float,
        status: str = "approved"
    ) -> TransactionResult:
        """
        Evaluate a PoC contribution

        Args:
            submission_hash: Submission hash
            coherence: Coherence score (0-100)
            density: Density score (0-100)
            novelty: Novelty score (0-100)
            status: Evaluation status

        Returns:
            Transaction result
        """
        try:
            # For now, this is handled by the Python implementation
            # In a real implementation, this would be a contract call
            evaluation = {
                "coherence": coherence * 10000,  # Scale to 0-10000
                "density": density * 10000,
                "novelty": novelty * 10000,
                "status": status
            }

            success = self.poc_contract.record_evaluation(submission_hash, evaluation)

            if success:
                return TransactionResult(
                    success=True,
                    transaction_hash=f"eval_{submission_hash}_{datetime.now().timestamp()}",
                    receipt={"status": 1}
                )
            else:
                return TransactionResult(
                    success=False,
                    error="Evaluation recording failed"
                )

        except Exception as e:
            self.logger.error(f"Failed to evaluate PoC contribution: {e}")
            return TransactionResult(success=False, error=str(e))

    def allocate_synth_reward(
        self,
        submission_hash: str,
        recipient: str,
        pod_score: float,
        epoch: str,
        tier: str
    ) -> TransactionResult:
        """
        Allocate SYNTH token reward

        Args:
            submission_hash: Submission hash
            recipient: Recipient address
            pod_score: PoD score
            epoch: Epoch name
            tier: Tier name

        Returns:
            Transaction result
        """
        try:
            # Use Python implementation for allocation logic
            from .layer1.contracts.synth_token import Epoch as EpochEnum, ContributionTier

            epoch_enum = EpochEnum(epoch.lower())
            tier_enum = ContributionTier(tier.lower())

            result = self.poc_contract.allocate_tokens(submission_hash)

            if result["success"]:
                allocation = result["allocation"]
                return TransactionResult(
                    success=True,
                    transaction_hash=f"alloc_{submission_hash}_{datetime.now().timestamp()}",
                    receipt={
                        "status": 1,
                        "blockNumber": 0,  # Would be real block number
                        "gasUsed": 0
                    },
                    gas_used=0,
                    block_number=0
                )
            else:
                return TransactionResult(
                    success=False,
                    error=result.get("reason", "Allocation failed")
                )

        except Exception as e:
            self.logger.error(f"Failed to allocate SYNTH reward: {e}")
            return TransactionResult(success=False, error=str(e))

    def register_poc_certificate(
        self,
        submission_hash: str,
        metal_type: str,
        reward_amount: int
    ) -> TransactionResult:
        """
        Register PoC certificate on blockchain

        Args:
            submission_hash: Submission hash
            metal_type: Certificate metal (gold, silver, copper)
            reward_amount: SYNTH reward amount

        Returns:
            Transaction result
        """
        try:
            result = self.web3_manager.submit_poc_to_blockchain(
                {"hash": submission_hash},
                {"metal": metal_type, "reward": reward_amount}
            )

            if result["success"]:
                return TransactionResult(
                    success=True,
                    transaction_hash=result["transaction_hash"],
                    receipt={"blockNumber": result.get("block_number")},
                    gas_used=result.get("gas_used", 0),
                    block_number=result.get("block_number", 0),
                    explorer_url=result.get("explorer_url")
                )
            else:
                return TransactionResult(
                    success=False,
                    error=result.get("error", "Registration failed")
                )

        except Exception as e:
            self.logger.error(f"Failed to register certificate: {e}")
            return TransactionResult(success=False, error=str(e))

    # Analytics and Statistics Methods

    def get_poc_statistics(self) -> ContractCallResult:
        """
        Get PoC system statistics

        Returns:
            Contract call result with statistics
        """
        try:
            # Get statistics from Python implementations
            synth_stats = self.synth_contract.get_statistics()
            poc_epoch_stats = self.poc_contract.get_epoch_statistics()

            combined_stats = {
                "synth_token": synth_stats,
                "poc_epochs": poc_epoch_stats,
                "total_contributions": len(self.poc_contract.submissions),
                "approved_contributions": len([
                    s for s in self.poc_contract.submissions.values()
                    if s.get("status") == "approved"
                ]),
                "total_rewards_allocated": sum(
                    reward.get("tokens", 0)
                    for reward in self.poc_contract.rewards.values()
                )
            }

            return ContractCallResult(success=True, data=combined_stats)

        except Exception as e:
            self.logger.error(f"Failed to get PoC statistics: {e}")
            return ContractCallResult(success=False, error=str(e))

    def get_contributor_dashboard(self, contributor_address: str) -> ContractCallResult:
        """
        Get contributor dashboard data

        Args:
            contributor_address: Contributor address

        Returns:
            Contract call result with dashboard data
        """
        try:
            # Get data from Python implementations
            synth_balance = self.get_synth_balance(contributor_address)
            contributor_stats = self.poc_contract.get_contributor_stats(contributor_address)

            dashboard_data = {
                "address": contributor_address,
                "synth_balance": synth_balance.data if synth_balance.success else 0,
                "submission_count": contributor_stats.get("submission_count", 0),
                "tier_breakdown": contributor_stats.get("tier_breakdown", {}),
                "submissions": contributor_stats.get("submissions", []),
                "total_rewards": sum(contributor_stats.get("tier_breakdown", {}).values())
            }

            return ContractCallResult(success=True, data=dashboard_data)

        except Exception as e:
            self.logger.error(f"Failed to get contributor dashboard: {e}")
            return ContractCallResult(success=False, error=str(e))

    # Utility Methods

    def wait_for_transaction_confirmation(
        self,
        tx_hash: str,
        timeout: int = 120
    ) -> Optional[Dict[str, Any]]:
        """
        Wait for transaction confirmation

        Args:
            tx_hash: Transaction hash
            timeout: Timeout in seconds

        Returns:
            Transaction receipt or None
        """
        try:
            return self.web3_manager.wait_for_transaction(tx_hash, timeout)
        except Exception as e:
            self.logger.error(f"Failed to wait for transaction: {e}")
            return None

    def get_transaction_receipt(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """
        Get transaction receipt

        Args:
            tx_hash: Transaction hash

        Returns:
            Transaction receipt or None
        """
        try:
            return self.web3_manager.get_transaction_receipt(tx_hash)
        except Exception as e:
            self.logger.error(f"Failed to get transaction receipt: {e}")
            return None

    def get_block_explorer_url(self, tx_hash: str) -> Optional[str]:
        """
        Get block explorer URL for transaction

        Args:
            tx_hash: Transaction hash

        Returns:
            Block explorer URL or None
        """
        return self.web3_manager.get_block_explorer_url(tx_hash)

    def get_network_info(self) -> Dict[str, Any]:
        """
        Get current network information

        Returns:
            Network information
        """
        return self.web3_manager.get_network_info()

    def is_contract_deployed(self, contract_name: str) -> bool:
        """
        Check if contract is deployed on current network

        Args:
            contract_name: Contract name ('synth' or 'poc_registry')

        Returns:
            True if contract is deployed
        """
        if contract_name == 'synth':
            return bool(self.synth_address)
        elif contract_name == 'poc_registry':
            return bool(self.poc_address)
        return False


# Convenience functions

def create_contract_interface(
    network: Network = Network.ANVIL_LOCAL,
    private_key: Optional[str] = None,
    mnemonic: Optional[str] = None
) -> SyntheverseContractInterface:
    """
    Create a contract interface instance

    Args:
        network: Blockchain network
        private_key: Optional private key for wallet
        mnemonic: Optional mnemonic for wallet

    Returns:
        Contract interface instance
    """
    web3_client = SyntheverseWeb3Client(
        network=network,
        private_key=private_key,
        mnemonic=mnemonic
    )

    return SyntheverseContractInterface(web3_client=web3_client)


def get_contract_address(contract_name: str, network: Network = Network.ANVIL_LOCAL) -> Optional[str]:
    """
    Get deployed contract address for network

    Args:
        contract_name: Contract name
        network: Network

    Returns:
        Contract address or None
    """
    # This would load from a configuration file or registry
    # For now, return testnet addresses
    addresses = {
        Network.BASE_SEPOLIA: {
            'synth': '0x742d35Cc6634C0532925a3b844Bc454e4438f44e',
            'poc_registry': '0x742d35Cc6634C0532925a3b844Bc454e4438f44f'
        },
        Network.ANVIL_LOCAL: {
            'synth': '',  # Load from artifacts
            'poc_registry': ''
        }
    }

    network_addresses = addresses.get(network, {})
    return network_addresses.get(contract_name)


if __name__ == "__main__":
    # Example usage
    import os

    logger.info("Syntheverse Contract Interface")
    logger.info("=" * 40)

    # Create interface
    interface = create_contract_interface(network=Network.ANVIL_LOCAL)

    logger.info(f"Network: {interface.get_network_info()}")

    # Get SYNTH total supply
    supply_result = interface.get_synth_total_supply()
    if supply_result.success:
        logger.info(f"Total SYNTH supply: {supply_result.data:,}")
    else:
        logger.error(f"Failed to get supply: {supply_result.error}")

    # Example contribution submission
    contribution_result = interface.submit_poc_contribution(
        title="Test Contribution",
        description="A test scientific contribution",
        contributor="0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
    )

    if contribution_result.success:
        logger.info(f"Contribution submitted: {contribution_result.transaction_hash}")
    else:
        logger.error(f"Contribution failed: {contribution_result.error}")

    # Get statistics
    stats_result = interface.get_poc_statistics()
    if stats_result.success:
        stats = stats_result.data
        logger.info("System Statistics:")
        logger.info(f"  Total Contributions: {stats['total_contributions']}")
        logger.info(f"  Approved Contributions: {stats['approved_contributions']}")
        logger.info(f"  Total Token Supply: {stats.get('total_supply', 0):,}")
    else:
        logger.error(f"Failed to get statistics: {stats_result.error}")






