"""
POD Smart Contract
Handles Proof-of-Discovery submissions and token rewards on the Syntheverse blockchain.
Enhanced with epoch and tier support.
"""

from typing import Dict, List, Optional
from datetime import datetime
import hashlib
import json

from ..blockchain import Epoch, ContributionTier
from .synth_token import SYNTHToken


class PODContract:
    """
    Smart contract for managing POD submissions and rewards.
    Integrates with epochs (Founder, Pioneer, Community, Ecosystem)
    and tiers (Gold: scientific, Silver: tech, Copper: alignment).
    """
    
    def __init__(self, synth_token: Optional[SYNTHToken] = None):
        """
        Initialize POD contract.
        
        Args:
            synth_token: SYNTH token contract instance (creates new if None)
        """
        self.submissions = {}
        self.rewards = {}
        self.contributors = {}
        self.synth_token = synth_token or SYNTHToken()
        
        # Track tier assignments
        self.tier_assignments: Dict[str, ContributionTier] = {}
    
    def submit_pod(self, submission: Dict) -> str:
        """
        Submit a new POD to the blockchain.
        
        Args:
            submission: POD submission data with fields:
                - title: Title of discovery
                - description: Description
                - category: "scientific", "tech", or "alignment"
                - contributor: Contributor address/ID
                - evidence: Evidence/documentation
                - coherence: Coherence score (optional, set during evaluation)
                - density: Density score (optional, set during evaluation)
                - novelty: Novelty score (optional, set during evaluation)
        
        Returns:
            Submission hash/ID
        """
        # Generate submission hash
        submission_data = json.dumps(submission, sort_keys=True)
        submission_hash = hashlib.sha256(submission_data.encode()).hexdigest()
        
        # Determine tier based on category
        category = submission.get("category", "").lower()
        if category in ["scientific", "science", "research"]:
            tier = ContributionTier.GOLD
        elif category in ["tech", "technology", "technical", "engineering"]:
            tier = ContributionTier.SILVER
        elif category in ["alignment", "ai-alignment", "safety"]:
            tier = ContributionTier.COPPER
        else:
            # Default to copper for alignment contributions
            tier = ContributionTier.COPPER
        
        # Store submission
        self.submissions[submission_hash] = {
            "hash": submission_hash,
            "data": submission,
            "tier": tier.value,
            "timestamp": datetime.now().isoformat(),
            "status": "pending",
            "block_number": None,  # Will be set when included in block
            "epoch": None,  # Will be set during evaluation
            "pod_score": None,  # Will be set during evaluation
        }
        
        # Store tier assignment
        self.tier_assignments[submission_hash] = tier
        
        return submission_hash
    
    def record_evaluation(self, submission_hash: str, evaluation: Dict) -> bool:
        """
        Record POD evaluation result and determine epoch qualification.
        
        Args:
            submission_hash: Submission hash
            evaluation: Evaluation report with fields:
                - coherence: Coherence score (0-10000)
                - density: Density score (0-10000)
                - novelty: Novelty score (0-10000)
                - status: "approved" or "rejected"
        
        Returns:
            True if successful
        """
        if submission_hash not in self.submissions:
            return False
        
        # Update submission with evaluation
        self.submissions[submission_hash]["evaluation"] = evaluation
        self.submissions[submission_hash]["status"] = evaluation.get("status", "pending")
        
        # Calculate PoD score and determine epoch
        if evaluation.get("status") == "approved":
            coherence = evaluation.get("coherence", 0.0)
            density = evaluation.get("density", 0.0)
            novelty = evaluation.get("novelty", 0.0)
            
            # Calculate PoD score
            pod_score = self.synth_token.calculate_pod_score(coherence, density, novelty)
            self.submissions[submission_hash]["pod_score"] = pod_score
            
            # Determine qualified epoch based on density
            qualified_epoch = self.synth_token.qualify_epoch(density)
            if qualified_epoch:
                self.submissions[submission_hash]["epoch"] = qualified_epoch.value
                
                # Update coherence density for halving calculations
                self.synth_token.update_coherence_density(coherence)
        
        return True
    
    def allocate_tokens(self, submission_hash: str, allocation: Optional[Dict] = None) -> Dict:
        """
        Allocate SYNTH tokens based on POD evaluation, epoch, and tier.
        
        Args:
            submission_hash: Submission hash
            allocation: Optional allocation override (uses evaluation data if None)
        
        Returns:
            Allocation result dictionary
        """
        if submission_hash not in self.submissions:
            return {"success": False, "reason": "Submission not found"}
        
        submission = self.submissions[submission_hash]
        
        if submission["status"] != "approved":
            return {"success": False, "reason": "Submission not approved"}
        
        # Get evaluation data
        evaluation = submission.get("evaluation", {})
        pod_score = submission.get("pod_score", 0.0)
        epoch_str = submission.get("epoch")
        tier = self.tier_assignments.get(submission_hash, ContributionTier.COPPER)
        
        if not epoch_str:
            return {"success": False, "reason": "Epoch not determined"}
        
        epoch = Epoch(epoch_str)
        contributor = submission["data"].get("contributor")
        
        # Check if tier is available in this epoch
        if not self.synth_token.is_tier_available_in_epoch(tier, epoch):
            return {
                "success": False,
                "reason": f"Tier {tier.value} is not available in {epoch.value} epoch",
            }
        
        # Allocate tokens through SYNTH token contract
        result = self.synth_token.allocate_reward(
            recipient=contributor,
            pod_score=pod_score,
            epoch=epoch,
            tier=tier,
            submission_hash=submission_hash
        )
        
        if result["success"]:
            # Record reward in POD contract
            allocation_data = result["allocation"]
            self.rewards[submission_hash] = {
                "submission_hash": submission_hash,
                "contributor": contributor,
                "tokens": allocation_data["reward"],
                "pod_score": pod_score,
                "epoch": epoch.value,
                "tier": tier.value,
                "timestamp": allocation_data["timestamp"],
            }
            
            # Update contributor tracking
            if contributor not in self.contributors:
                self.contributors[contributor] = {
                    "balance": 0.0,
                    "submissions": [],
                    "tier_breakdown": {
                        ContributionTier.GOLD.value: 0.0,
                        ContributionTier.SILVER.value: 0.0,
                        ContributionTier.COPPER.value: 0.0,
                    }
                }
            
            self.contributors[contributor]["balance"] += allocation_data["reward"]
            self.contributors[contributor]["submissions"].append(submission_hash)
            self.contributors[contributor]["tier_breakdown"][tier.value] += allocation_data["reward"]
        
        return result
    
    def get_submission(self, submission_hash: str) -> Optional[Dict]:
        """Get submission by hash."""
        return self.submissions.get(submission_hash)
    
    def get_contributor_balance(self, contributor: str) -> float:
        """Get contributor SYNTH token balance."""
        return self.synth_token.get_balance(contributor)
    
    def get_contributor_stats(self, contributor: str) -> Dict:
        """Get detailed contributor statistics."""
        contributor_data = self.contributors.get(contributor, {})
        return {
            "address": contributor,
            "balance": self.synth_token.get_balance(contributor),
            "submission_count": len(contributor_data.get("submissions", [])),
            "tier_breakdown": contributor_data.get("tier_breakdown", {}),
            "submissions": contributor_data.get("submissions", []),
        }
    
    def get_tier(self, submission_hash: str) -> Optional[ContributionTier]:
        """Get tier assignment for a submission."""
        return self.tier_assignments.get(submission_hash)
    
    def get_epoch_statistics(self) -> Dict:
        """Get statistics by epoch and tier."""
        stats = {
            epoch.value: {
                tier.value: {
                    "count": 0,
                    "total_rewards": 0.0,
                    "avg_pod_score": 0.0,
                }
                for tier in ContributionTier
            }
            for epoch in Epoch
        }
        
        for submission_hash, submission in self.submissions.items():
            if submission["status"] == "approved" and submission.get("epoch"):
                epoch = submission["epoch"]
                tier = self.tier_assignments.get(submission_hash, ContributionTier.COPPER)
                reward = self.rewards.get(submission_hash, {}).get("tokens", 0.0)
                pod_score = submission.get("pod_score", 0.0)
                
                if epoch in stats:
                    tier_stats = stats[epoch][tier.value]
                    tier_stats["count"] += 1
                    tier_stats["total_rewards"] += reward
                    tier_stats["avg_pod_score"] = (
                        (tier_stats["avg_pod_score"] * (tier_stats["count"] - 1) + pod_score) / tier_stats["count"]
                    )
        
        return stats


if __name__ == "__main__":
    # Example usage
    contract = PODContract()
    
    # Example: Scientific contribution (Gold tier)
    scientific_submission = {
        "title": "Novel Scientific Discovery",
        "description": "A significant scientific finding",
        "category": "scientific",
        "contributor": "researcher-001",
        "evidence": "Research paper and experimental data",
    }
    
    submission_hash = contract.submit_pod(scientific_submission)
    print(f"Submitted POD: {submission_hash}")
    print(f"Tier: {contract.get_tier(submission_hash).value}")
    
    evaluation = {
        "coherence": 8500.0,
        "density": 9000.0,
        "novelty": 8000.0,
        "status": "approved",
    }
    
    contract.record_evaluation(submission_hash, evaluation)
    print(f"Qualified Epoch: {contract.submissions[submission_hash]['epoch']}")
    print(f"PoD Score: {contract.submissions[submission_hash]['pod_score']}")
    
    result = contract.allocate_tokens(submission_hash)
    if result["success"]:
        print(f"Allocated: {result['allocation']['reward']} SYNTH")
        print(f"Epoch: {result['allocation']['epoch']}")
        print(f"Tier: {result['allocation']['tier']}")
    
    balance = contract.get_contributor_balance("researcher-001")
    print(f"Contributor balance: {balance} SYNTH")
    
    # Print statistics
    stats = contract.get_epoch_statistics()
    print("\nEpoch Statistics:")
    print(json.dumps(stats, indent=2))

