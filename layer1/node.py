"""
Syntheverse Blockchain Node
Full node implementation with consensus and contract integration.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import os

from .blockchain import Blockchain, Transaction, TransactionType, Block
from .contracts.pod_contract import PODContract
from .contracts.synth_token import SYNTHToken
from .epoch_manager import EpochManager


class SyntheverseNode:
    """
    Syntheverse blockchain node.
    Handles block creation, consensus, and contract execution.
    """
    
    def __init__(self, node_id: str, difficulty: int = 1, data_dir: str = "data/blockchain"):
        """
        Initialize blockchain node.
        
        Args:
            node_id: Unique identifier for this node
            difficulty: Mining difficulty
            data_dir: Directory for blockchain data persistence
        """
        self.node_id = node_id
        self.blockchain = Blockchain(difficulty=difficulty)
        self.synth_token = SYNTHToken()
        self.pod_contract = PODContract(synth_token=self.synth_token)
        self.epoch_manager = EpochManager(synth_token=self.synth_token)
        self.data_dir = data_dir
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        # Load blockchain state if exists
        self._load_state()
    
    def submit_pod(self, submission: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit a Proof-of-Discovery submission.
        
        Args:
            submission: POD submission data
        
        Returns:
            Submission result with hash
        """
        # Submit to POD contract
        submission_hash = self.pod_contract.submit_pod(submission)
        
        # Create transaction
        tx = Transaction(
            tx_type=TransactionType.POD_SUBMISSION,
            data={
                "submission_hash": submission_hash,
                "submission": submission,
            },
            sender=submission.get("contributor", "unknown")
        )
        
        # Add to pending transactions
        self.blockchain.add_transaction(tx)
        
        return {
            "success": True,
            "submission_hash": submission_hash,
            "transaction_hash": tx.hash,
        }
    
    def evaluate_pod(self, submission_hash: str, evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Record POD evaluation result.
        
        Args:
            submission_hash: Submission hash
            evaluation: Evaluation report
        
        Returns:
            Evaluation result
        """
        # Record evaluation in contract
        success = self.pod_contract.record_evaluation(submission_hash, evaluation)
        
        if success:
            # Create transaction
            tx = Transaction(
                tx_type=TransactionType.POD_EVALUATION,
                data={
                    "submission_hash": submission_hash,
                    "evaluation": evaluation,
                },
                sender="evaluator"
            )
            
            self.blockchain.add_transaction(tx)
            
            # Check for epoch transitions
            self.epoch_manager.auto_transition()
        
        return {
            "success": success,
            "submission_hash": submission_hash,
        }
    
    def allocate_tokens(self, submission_hash: str) -> Dict[str, Any]:
        """
        Allocate tokens for an approved POD submission.
        
        Args:
            submission_hash: Submission hash
        
        Returns:
            Allocation result
        """
        # Allocate tokens through contract
        result = self.pod_contract.allocate_tokens(submission_hash)
        
        if result["success"]:
            # Create transaction
            tx = Transaction(
                tx_type=TransactionType.TOKEN_ALLOCATION,
                data={
                    "submission_hash": submission_hash,
                    "allocation": result["allocation"],
                },
                sender="allocator"
            )
            
            self.blockchain.add_transaction(tx)
        
        return result
    
    def mine_block(self, pod_score: float = 0.0) -> Block:
        """
        Mine pending transactions into a new block.
        
        Args:
            pod_score: Proof-of-Discovery score for this block
        
        Returns:
            Newly mined block
        """
        block = self.blockchain.mine_pending_transactions(
            validator=self.node_id,
            pod_score=pod_score
        )
        
        # Save state after mining
        self._save_state()
        
        return block
    
    def get_blockchain_info(self) -> Dict[str, Any]:
        """Get blockchain information."""
        return {
            "chain_length": self.blockchain.get_chain_length(),
            "pending_transactions": len(self.blockchain.pending_transactions),
            "difficulty": self.blockchain.difficulty,
            "latest_block": self.blockchain.get_latest_block().to_dict(),
            "is_valid": self.blockchain.is_chain_valid(),
        }
    
    def get_token_statistics(self) -> Dict[str, Any]:
        """Get SYNTH token statistics."""
        return self.synth_token.get_statistics()
    
    def get_epoch_info(self) -> Dict[str, Any]:
        """Get epoch information."""
        return {
            "current_epoch": self.epoch_manager.get_current_epoch().value,
            "epochs": self.epoch_manager.get_all_epochs_info(),
            "transition_history": self.epoch_manager.get_transition_history(),
        }
    
    def get_pod_statistics(self) -> Dict[str, Any]:
        """Get POD contract statistics."""
        return {
            "total_submissions": len(self.pod_contract.submissions),
            "approved_submissions": sum(
                1 for s in self.pod_contract.submissions.values()
                if s.get("status") == "approved"
            ),
            "total_rewards": len(self.pod_contract.rewards),
            "epoch_statistics": self.pod_contract.get_epoch_statistics(),
        }
    
    def get_node_status(self) -> Dict[str, Any]:
        """Get comprehensive node status."""
        return {
            "node_id": self.node_id,
            "blockchain": self.get_blockchain_info(),
            "token": self.get_token_statistics(),
            "epoch": self.get_epoch_info(),
            "pod": self.get_pod_statistics(),
        }
    
    def _save_state(self):
        """Save blockchain and contract state to disk."""
        try:
            # Save blockchain
            blockchain_file = os.path.join(self.data_dir, "blockchain.json")
            with open(blockchain_file, "w") as f:
                json.dump(self.blockchain.to_dict(), f, indent=2, default=str)
            
            # Save token contract
            token_file = os.path.join(self.data_dir, "synth_token.json")
            with open(token_file, "w") as f:
                json.dump(self.synth_token.to_dict(), f, indent=2, default=str)
            
            # Save POD contract (simplified - just submissions and rewards)
            pod_file = os.path.join(self.data_dir, "pod_contract.json")
            pod_data = {
                "submissions": self.pod_contract.submissions,
                "rewards": self.pod_contract.rewards,
                "contributors": self.pod_contract.contributors,
                "tier_assignments": {
                    k: v.value for k, v in self.pod_contract.tier_assignments.items()
                },
            }
            with open(pod_file, "w") as f:
                json.dump(pod_data, f, indent=2, default=str)
        except Exception as e:
            print(f"Warning: Failed to save state: {e}")
    
    def _load_state(self):
        """Load blockchain and contract state from disk."""
        try:
            # Load blockchain
            blockchain_file = os.path.join(self.data_dir, "blockchain.json")
            if os.path.exists(blockchain_file):
                with open(blockchain_file, "r") as f:
                    data = json.load(f)
                    self.blockchain = Blockchain.from_dict(data)
            
            # Load token contract
            token_file = os.path.join(self.data_dir, "synth_token.json")
            if os.path.exists(token_file):
                with open(token_file, "r") as f:
                    data = json.load(f)
                    self.synth_token = SYNTHToken.from_dict(data)
                    # Recreate POD contract with loaded token
                    self.pod_contract = PODContract(synth_token=self.synth_token)
                    self.epoch_manager = EpochManager(synth_token=self.synth_token)
            
            # Load POD contract data
            pod_file = os.path.join(self.data_dir, "pod_contract.json")
            if os.path.exists(pod_file):
                with open(pod_file, "r") as f:
                    data = json.load(f)
                    self.pod_contract.submissions = data.get("submissions", {})
                    self.pod_contract.rewards = data.get("rewards", {})
                    self.pod_contract.contributors = data.get("contributors", {})
                    # Restore tier assignments
                    tier_data = data.get("tier_assignments", {})
                    from .blockchain import ContributionTier
                    self.pod_contract.tier_assignments = {
                        k: ContributionTier(v) for k, v in tier_data.items()
                    }
        except Exception as e:
            print(f"Warning: Failed to load state: {e}")
