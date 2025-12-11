"""
POD Smart Contract
Handles Proof-of-Discovery submissions and token rewards on the Syntheverse blockchain.
"""

from typing import Dict, List, Optional
from datetime import datetime
import hashlib
import json


class PODContract:
    """
    Smart contract for managing POD submissions and rewards.
    """
    
    def __init__(self):
        """Initialize POD contract."""
        self.submissions = {}
        self.rewards = {}
        self.contributors = {}
    
    def submit_pod(self, submission: Dict) -> str:
        """
        Submit a new POD to the blockchain.
        
        Args:
            submission: POD submission data
        
        Returns:
            Submission hash/ID
        """
        # Generate submission hash
        submission_data = json.dumps(submission, sort_keys=True)
        submission_hash = hashlib.sha256(submission_data.encode()).hexdigest()
        
        # Store submission
        self.submissions[submission_hash] = {
            "hash": submission_hash,
            "data": submission,
            "timestamp": datetime.now().isoformat(),
            "status": "pending",
            "block_number": None,  # Will be set when included in block
        }
        
        return submission_hash
    
    def record_evaluation(self, submission_hash: str, evaluation: Dict) -> bool:
        """
        Record POD evaluation result.
        
        Args:
            submission_hash: Submission hash
            evaluation: Evaluation report
        
        Returns:
            True if successful
        """
        if submission_hash not in self.submissions:
            return False
        
        self.submissions[submission_hash]["evaluation"] = evaluation
        self.submissions[submission_hash]["status"] = evaluation.get("status", "pending")
        
        return True
    
    def allocate_tokens(self, submission_hash: str, allocation: Dict) -> bool:
        """
        Allocate SYNTH tokens based on POD evaluation.
        
        Args:
            submission_hash: Submission hash
            allocation: Token allocation details
        
        Returns:
            True if successful
        """
        if submission_hash not in self.submissions:
            return False
        
        contributor = self.submissions[submission_hash]["data"].get("contributor")
        total_tokens = allocation.get("total_tokens", 0.0)
        
        # Record reward
        self.rewards[submission_hash] = {
            "submission_hash": submission_hash,
            "contributor": contributor,
            "tokens": total_tokens,
            "timestamp": datetime.now().isoformat(),
        }
        
        # Update contributor balance
        if contributor not in self.contributors:
            self.contributors[contributor] = {"balance": 0.0, "submissions": []}
        
        self.contributors[contributor]["balance"] += total_tokens
        self.contributors[contributor]["submissions"].append(submission_hash)
        
        return True
    
    def get_submission(self, submission_hash: str) -> Optional[Dict]:
        """Get submission by hash."""
        return self.submissions.get(submission_hash)
    
    def get_contributor_balance(self, contributor: str) -> float:
        """Get contributor SYNTH token balance."""
        return self.contributors.get(contributor, {}).get("balance", 0.0)


if __name__ == "__main__":
    # Example usage
    contract = PODContract()
    
    sample_submission = {
        "title": "Novel Discovery",
        "description": "A significant finding",
        "contributor": "researcher-001",
    }
    
    submission_hash = contract.submit_pod(sample_submission)
    print(f"Submitted POD: {submission_hash}")
    
    evaluation = {
        "overall_score": 0.85,
        "status": "approved",
    }
    
    contract.record_evaluation(submission_hash, evaluation)
    
    allocation = {
        "total_tokens": 150.0,
    }
    
    contract.allocate_tokens(submission_hash, allocation)
    
    balance = contract.get_contributor_balance("researcher-001")
    print(f"Contributor balance: {balance} SYNTH")

