"""
Token Allocator
Calculates SYNTH token rewards based on POD evaluations.
Implements tokenomics rules and epoch-based distribution.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import logging


class TokenAllocator:
    """
    Allocates SYNTH tokens based on POD evaluation scores.
    Implements comprehensive tokenomics rules and validation.
    """

    def __init__(self, base_reward: float = 100.0):
        """
        Initialize token allocator.

        Args:
            base_reward: Base token reward amount

        Raises:
            ValueError: If base_reward is invalid
        """
        if not isinstance(base_reward, (int, float)) or base_reward <= 0:
            raise ValueError("Base reward must be a positive number")

        self.base_reward = float(base_reward)
        self.tokenomics = {
            "base_multiplier": 1.0,
            "novelty_bonus": 0.5,  # Bonus for high novelty
            "significance_bonus": 0.5,  # Bonus for high significance
            "epoch_bonus": 0.1,  # Bonus for early epoch contributions
        }

        # Initialize logger
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def calculate_reward(self, evaluation: Dict, epoch: int = 1) -> Dict:
        """
        Calculate token reward based on evaluation.

        Args:
            evaluation: POD evaluation report
            epoch: Current epoch number

        Returns:
            Token allocation details

        Raises:
            ValueError: If evaluation data is invalid
            TypeError: If input types are incorrect
        """
        try:
            # Validate inputs
            self._validate_evaluation_input(evaluation, epoch)

            submission_id = evaluation.get("submission_id", "unknown")
            self.logger.info(f"Calculating reward for submission: {submission_id}")

            scores = evaluation.get("scores", {})
            overall_score = evaluation.get("overall_score", 0.0)

            # Base reward calculation with bounds checking
            base_tokens = max(0.0, self.base_reward * overall_score)

            # Apply bonuses with validation
            bonuses = self._calculate_bonuses(scores, base_tokens)

            # Epoch bonus (decreases over time, minimum 0)
            epoch_bonus = max(0.0, base_tokens * self.tokenomics["epoch_bonus"] / max(1, epoch))

            total_tokens = base_tokens + sum(bonuses.values()) + epoch_bonus

            # Ensure total is non-negative
            total_tokens = max(0.0, total_tokens)

            allocation = {
                "submission_id": submission_id,
                "base_tokens": round(base_tokens, 2),
                "bonuses": {k: round(v, 2) for k, v in bonuses.items()},
                "epoch_bonus": round(epoch_bonus, 2),
                "total_tokens": round(total_tokens, 2),
                "epoch": epoch,
                "timestamp": datetime.now().isoformat(),
                "allocation_version": "1.0"
            }

            self.logger.info(f"Reward calculated for {submission_id}: {total_tokens:.2f} tokens")

            return allocation

        except Exception as e:
            submission_id = evaluation.get("submission_id", "unknown") if isinstance(evaluation, dict) else "unknown"
            self.logger.error(f"Reward calculation failed for {submission_id}: {e}")
            raise

    def _validate_evaluation_input(self, evaluation: Dict, epoch: int) -> None:
        """Validate evaluation input parameters."""
        if not isinstance(evaluation, dict):
            raise TypeError("Evaluation must be a dictionary")

        if not isinstance(epoch, int) or epoch < 1:
            raise ValueError("Epoch must be a positive integer")

        # Check for required fields
        if "scores" in evaluation and not isinstance(evaluation["scores"], dict):
            raise TypeError("Evaluation scores must be a dictionary")

        if "overall_score" in evaluation:
            score = evaluation["overall_score"]
            if not isinstance(score, (int, float)) or not (0.0 <= score <= 1.0):
                raise ValueError("Overall score must be a number between 0.0 and 1.0")

    def _calculate_bonuses(self, scores: Dict, base_tokens: float) -> Dict[str, float]:
        """Calculate bonus tokens based on evaluation scores."""
        bonuses = {}

        # Novelty bonus
        if scores.get("novelty", 0.0) > 0.8:
            bonuses["novelty"] = base_tokens * self.tokenomics["novelty_bonus"]

        # Significance bonus
        if scores.get("significance", 0.0) > 0.8:
            bonuses["significance"] = base_tokens * self.tokenomics["significance_bonus"]

        # Verification bonus (additional criterion)
        if scores.get("verification", 0.0) > 0.9:
            bonuses["verification"] = base_tokens * 0.2

        # Documentation bonus (additional criterion)
        if scores.get("documentation", 0.0) > 0.9:
            bonuses["documentation"] = base_tokens * 0.1

        return bonuses
    
    def generate_allocation_batch(self, evaluations: List[Dict], epoch: int = 1) -> Dict[str, Any]:
        """
        Generate token allocations for a batch of evaluations.

        Args:
            evaluations: List of evaluation reports
            epoch: Current epoch number

        Returns:
            Dict containing allocations, summary statistics, and any errors

        Raises:
            TypeError: If evaluations is not a list
            ValueError: If epoch is invalid
        """
        if not isinstance(evaluations, list):
            raise TypeError("Evaluations must be a list")

        if not isinstance(epoch, int) or epoch < 1:
            raise ValueError("Epoch must be a positive integer")

        self.logger.info(f"Generating allocation batch for {len(evaluations)} evaluations in epoch {epoch}")

        allocations = []
        errors = []
        total_tokens_allocated = 0.0
        successful_allocations = 0

        for i, evaluation in enumerate(evaluations):
            try:
                if not isinstance(evaluation, dict):
                    errors.append({
                        "index": i,
                        "error": "Evaluation must be a dictionary",
                        "evaluation": str(evaluation)[:100]
                    })
                    continue

                # Check if evaluation is approved/qualified for allocation
                status = evaluation.get("status", "").lower()
                if status in ["approved", "qualified", "excellent", "good"]:
                    allocation = self.calculate_reward(evaluation, epoch)
                    allocations.append(allocation)
                    total_tokens_allocated += allocation["total_tokens"]
                    successful_allocations += 1
                else:
                    self.logger.debug(f"Skipping evaluation {evaluation.get('submission_id', f'#{i}')} with status: {status}")

            except Exception as e:
                submission_id = evaluation.get("submission_id", f"#{i}") if isinstance(evaluation, dict) else f"#{i}"
                error_info = {
                    "index": i,
                    "submission_id": submission_id,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
                errors.append(error_info)
                self.logger.warning(f"Failed to allocate for evaluation {submission_id}: {e}")

        # Calculate summary statistics
        summary = {
            "total_evaluations": len(evaluations),
            "successful_allocations": successful_allocations,
            "failed_allocations": len(errors),
            "total_tokens_allocated": round(total_tokens_allocated, 2),
            "average_tokens_per_allocation": round(total_tokens_allocated / max(1, successful_allocations), 2),
            "epoch": epoch,
            "timestamp": datetime.now().isoformat()
        }

        result = {
            "allocations": allocations,
            "summary": summary,
            "errors": errors
        }

        self.logger.info(f"Batch allocation completed: {successful_allocations}/{len(evaluations)} successful, {total_tokens_allocated:.2f} tokens allocated")

        return result


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


