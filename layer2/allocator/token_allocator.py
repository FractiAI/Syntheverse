"""
Token Allocator
Calculates SYNTH token rewards based on POD evaluations.
Implements tokenomics rules and epoch-based distribution.
"""

from typing import Dict, List, Optional
from datetime import datetime
import json


class TokenAllocator:
    """
    Allocates SYNTH tokens based on POD evaluation scores.
    """
    
    def __init__(self, base_reward: float = 100.0):
        """
        Initialize token allocator.
        
        Args:
            base_reward: Base token reward amount
        """
        self.base_reward = base_reward
        self.tokenomics = {
            "base_multiplier": 1.0,
            "novelty_bonus": 0.5,  # Bonus for high novelty
            "significance_bonus": 0.5,  # Bonus for high significance
            "epoch_bonus": 0.1,  # Bonus for early epoch contributions
        }
    
    def calculate_reward(self, evaluation: Dict, epoch: int = 1) -> Dict:
        """
        Calculate token reward based on evaluation.
        
        Args:
            evaluation: POD evaluation report
            epoch: Current epoch number
        
        Returns:
            Token allocation details
        """
        scores = evaluation.get("scores", {})
        overall_score = evaluation.get("overall_score", 0.0)
        
        # Base reward calculation
        base_tokens = self.base_reward * overall_score
        
        # Apply bonuses
        bonuses = {}
        if scores.get("novelty", 0.0) > 0.8:
            bonuses["novelty"] = base_tokens * self.tokenomics["novelty_bonus"]
        
        if scores.get("significance", 0.0) > 0.8:
            bonuses["significance"] = base_tokens * self.tokenomics["significance_bonus"]
        
        # Epoch bonus (decreases over time)
        epoch_bonus = base_tokens * self.tokenomics["epoch_bonus"] / epoch
        
        total_tokens = base_tokens + sum(bonuses.values()) + epoch_bonus
        
        allocation = {
            "submission_id": evaluation.get("submission_id"),
            "base_tokens": base_tokens,
            "bonuses": bonuses,
            "epoch_bonus": epoch_bonus,
            "total_tokens": total_tokens,
            "epoch": epoch,
            "timestamp": datetime.now().isoformat(),
        }
        
        return allocation
    
    def generate_allocation_batch(self, evaluations: List[Dict], epoch: int = 1) -> List[Dict]:
        """
        Generate token allocations for a batch of evaluations.
        
        Args:
            evaluations: List of evaluation reports
            epoch: Current epoch number
        
        Returns:
            List of token allocations
        """
        allocations = []
        for evaluation in evaluations:
            if evaluation.get("status") == "approved":
                allocation = self.calculate_reward(evaluation, epoch)
                allocations.append(allocation)
        
        return allocations


if __name__ == "__main__":
    # Example usage
    allocator = TokenAllocator(base_reward=100.0)
    
    sample_evaluation = {
        "submission_id": "pod-001",
        "scores": {
            "novelty": 0.9,
            "significance": 0.85,
            "verification": 0.8,
            "documentation": 0.75,
        },
        "overall_score": 0.825,
        "status": "approved",
    }
    
    allocation = allocator.calculate_reward(sample_evaluation, epoch=1)
    print(json.dumps(allocation, indent=2))


