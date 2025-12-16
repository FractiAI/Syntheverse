"""
SYNTH Token Contract
ERC20-like token contract with epoch-based distribution and tier rewards.
"""

from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum
import json

from ..blockchain import Epoch, ContributionTier


class SYNTHToken:
    """
    SYNTH token contract with epoch-based distribution.
    Total Supply: 90 Trillion SYNTH tokens
    """
    
    # Total supply: 90 Trillion
    TOTAL_SUPPLY = 90_000_000_000_000
    
    # Epoch distribution percentages
    EPOCH_DISTRIBUTION = {
        Epoch.FOUNDER: 0.50,    # 45T (50%)
        Epoch.PIONEER: 0.10,    # 9T (10%)
        Epoch.COMMUNITY: 0.20,  # 18T (20%)
        Epoch.ECOSYSTEM: 0.20,  # 18T (20%)
    }
    
    # Epoch qualification thresholds (density scores)
    EPOCH_THRESHOLDS = {
        Epoch.FOUNDER: 8000,
        Epoch.PIONEER: 6000,
        Epoch.COMMUNITY: 4000,
        Epoch.ECOSYSTEM: 0,  # All others
    }
    
    # Tier multipliers for rewards
    TIER_MULTIPLIERS = {
        ContributionTier.GOLD: 1000.0,   # Scientific: 1000x multiplier
        ContributionTier.SILVER: 100.0,   # Tech: 100x multiplier
        ContributionTier.COPPER: 1.0,    # Alignment: 1x base
    }
    
    # Tier availability by epoch
    # Each tier can only be used in specific epochs
    TIER_EPOCH_AVAILABILITY = {
        ContributionTier.GOLD: [
            Epoch.FOUNDER,
            Epoch.PIONEER,
            Epoch.COMMUNITY,
            Epoch.ECOSYSTEM,
        ],  # Gold available in all epochs
        ContributionTier.SILVER: [
            Epoch.COMMUNITY,
            Epoch.ECOSYSTEM,
        ],  # Silver available in Community and Ecosystem only
        ContributionTier.COPPER: [
            Epoch.PIONEER,
            Epoch.COMMUNITY,
            Epoch.ECOSYSTEM,
        ],  # Copper available in Pioneer, Community, and Ecosystem
    }
    
    def __init__(self):
        """Initialize SYNTH token contract."""
        # Epoch balances
        self.epoch_balances = {
            Epoch.FOUNDER: self.TOTAL_SUPPLY * self.EPOCH_DISTRIBUTION[Epoch.FOUNDER],
            Epoch.PIONEER: self.TOTAL_SUPPLY * self.EPOCH_DISTRIBUTION[Epoch.PIONEER],
            Epoch.COMMUNITY: self.TOTAL_SUPPLY * self.EPOCH_DISTRIBUTION[Epoch.COMMUNITY],
            Epoch.ECOSYSTEM: self.TOTAL_SUPPLY * self.EPOCH_DISTRIBUTION[Epoch.ECOSYSTEM],
        }
        
        # User balances
        self.balances: Dict[str, float] = {}
        
        # Epoch state
        self.current_epoch = Epoch.FOUNDER
        self.epoch_progression = {
            Epoch.FOUNDER: False,
            Epoch.PIONEER: False,
            Epoch.COMMUNITY: False,
            Epoch.ECOSYSTEM: False,
        }
        
        # Halving configuration for Founder epoch
        self.founder_halving_interval = 1_000_000  # Coherence density units
        self.founder_halving_count = 0
        self.total_coherence_density = 0.0
        
        # Reward history
        self.reward_history: List[Dict] = []
    
    def get_epoch_balance(self, epoch: Epoch) -> float:
        """Get available balance for an epoch."""
        return self.epoch_balances.get(epoch, 0.0)
    
    def get_balance(self, address: str) -> float:
        """Get SYNTH token balance for an address."""
        return self.balances.get(address, 0.0)
    
    def qualify_epoch(self, density_score: float) -> Optional[Epoch]:
        """
        Determine which epoch a contribution qualifies for based on density score.
        
        Args:
            density_score: Density score of the contribution
        
        Returns:
            Qualified epoch or None
        """
        if density_score >= self.EPOCH_THRESHOLDS[Epoch.FOUNDER]:
            return Epoch.FOUNDER
        elif density_score >= self.EPOCH_THRESHOLDS[Epoch.PIONEER]:
            return Epoch.PIONEER
        elif density_score >= self.EPOCH_THRESHOLDS[Epoch.COMMUNITY]:
            return Epoch.COMMUNITY
        else:
            return Epoch.ECOSYSTEM
    
    def calculate_pod_score(
        self,
        coherence: float,
        density: float,
        novelty: float
    ) -> float:
        """
        Calculate Proof-of-Discovery score.
        
        Formula: PoD Score = (coherence/10000) × (density/10000) × (novelty/10000) × 10000
        
        Args:
            coherence: Coherence score (0-10000)
            density: Density score (0-10000)
            novelty: Novelty score (0-10000)
        
        Returns:
            PoD Score (0-10000)
        """
        pod_score = (coherence / 10000) * (density / 10000) * (novelty / 10000) * 10000
        return min(pod_score, 10000.0)  # Cap at 10000
    
    def is_tier_available_in_epoch(self, tier: ContributionTier, epoch: Epoch) -> bool:
        """
        Check if a tier is available in the specified epoch.
        
        Args:
            tier: Contribution tier
            epoch: Epoch to check
        
        Returns:
            True if tier is available in epoch
        """
        available_epochs = self.TIER_EPOCH_AVAILABILITY.get(tier, [])
        return epoch in available_epochs
    
    def get_available_tiers_for_epoch(self, epoch: Epoch) -> List[ContributionTier]:
        """
        Get list of tiers available in a specific epoch.
        
        Args:
            epoch: Epoch to check
        
        Returns:
            List of available tiers
        """
        available_tiers = []
        for tier, epochs in self.TIER_EPOCH_AVAILABILITY.items():
            if epoch in epochs:
                available_tiers.append(tier)
        return available_tiers
    
    def get_available_epochs_for_tier(self, tier: ContributionTier) -> List[Epoch]:
        """
        Get list of epochs where a tier is available.
        
        Args:
            tier: Tier to check
        
        Returns:
            List of available epochs
        """
        return self.TIER_EPOCH_AVAILABILITY.get(tier, [])
    
    def calculate_reward(
        self,
        pod_score: float,
        epoch: Epoch,
        tier: ContributionTier
    ) -> float:
        """
        Calculate token reward based on PoD score, epoch, and tier.
        
        Formula: Reward = (PoD Score / 10000) × available epoch balance × tier multiplier
        
        Args:
            pod_score: Proof-of-Discovery score (0-10000)
            epoch: Qualified epoch
            tier: Contribution tier
        
        Returns:
            Token reward amount (0.0 if tier not available in epoch)
        """
        # Check if tier is available in this epoch
        if not self.is_tier_available_in_epoch(tier, epoch):
            return 0.0
        
        epoch_balance = self.get_epoch_balance(epoch)
        if epoch_balance <= 0:
            return 0.0
        
        # Base reward: PoD Score percentage of epoch balance
        base_reward = (pod_score / 10000) * epoch_balance
        
        # Apply tier multiplier
        tier_multiplier = self.TIER_MULTIPLIERS.get(tier, 1.0)
        reward = base_reward * tier_multiplier
        
        # Ensure we don't exceed epoch balance
        reward = min(reward, epoch_balance)
        
        return reward
    
    def allocate_reward(
        self,
        recipient: str,
        pod_score: float,
        epoch: Epoch,
        tier: ContributionTier,
        submission_hash: str
    ) -> Dict:
        """
        Allocate tokens to a recipient based on their contribution.
        
        Args:
            recipient: Address/ID of recipient
            pod_score: Proof-of-Discovery score
            epoch: Qualified epoch
            tier: Contribution tier
            submission_hash: Hash of the POD submission
        
        Returns:
            Allocation details
        """
        # Check if tier is available in epoch
        if not self.is_tier_available_in_epoch(tier, epoch):
            return {
                "success": False,
                "reason": f"Tier {tier.value} is not available in {epoch.value} epoch",
            }
        
        reward = self.calculate_reward(pod_score, epoch, tier)
        
        if reward <= 0:
            return {
                "success": False,
                "reason": "No reward available or invalid parameters",
            }
        
        # Check epoch balance
        if self.epoch_balances[epoch] < reward:
            reward = self.epoch_balances[epoch]  # Allocate remaining balance
        
        # Update balances
        self.epoch_balances[epoch] -= reward
        if recipient not in self.balances:
            self.balances[recipient] = 0.0
        self.balances[recipient] += reward
        
        # Record reward
        allocation = {
            "submission_hash": submission_hash,
            "recipient": recipient,
            "pod_score": pod_score,
            "epoch": epoch.value,
            "tier": tier.value,
            "reward": reward,
            "timestamp": datetime.now().isoformat(),
        }
        self.reward_history.append(allocation)
        
        return {
            "success": True,
            "allocation": allocation,
        }
    
    def update_coherence_density(self, coherence_density: float):
        """
        Update total coherence density and check for Founder epoch halving.
        
        Args:
            coherence_density: Additional coherence density to add
        """
        self.total_coherence_density += coherence_density
        
        # Check for halving
        halvings = int(self.total_coherence_density / self.founder_halving_interval)
        if halvings > self.founder_halving_count:
            # Perform halving
            for _ in range(halvings - self.founder_halving_count):
                self.epoch_balances[Epoch.FOUNDER] /= 2
            self.founder_halving_count = halvings
    
    def can_transition_epoch(self, epoch: Epoch) -> bool:
        """
        Check if epoch can be transitioned to.
        Each epoch opens only after the previous epoch achieves minimum resonance density.
        
        Args:
            epoch: Epoch to check
        
        Returns:
            True if epoch can be activated
        """
        epoch_order = [Epoch.FOUNDER, Epoch.PIONEER, Epoch.COMMUNITY, Epoch.ECOSYSTEM]
        
        try:
            current_index = epoch_order.index(self.current_epoch)
            target_index = epoch_order.index(epoch)
            
            # Can only transition forward
            if target_index <= current_index:
                return True  # Already active or past
            
            # Check if previous epochs are complete
            for i in range(current_index, target_index):
                if not self.epoch_progression.get(epoch_order[i], False):
                    return False
            
            return True
        except ValueError:
            return False
    
    def transition_epoch(self, epoch: Epoch) -> bool:
        """
        Transition to a new epoch.
        
        Args:
            epoch: Target epoch
        
        Returns:
            True if transition successful
        """
        if not self.can_transition_epoch(epoch):
            return False
        
        self.current_epoch = epoch
        self.epoch_progression[epoch] = True
        return True
    
    def get_statistics(self) -> Dict:
        """Get token contract statistics."""
        total_distributed = sum(
            self.TOTAL_SUPPLY * self.EPOCH_DISTRIBUTION[epoch] - balance
            for epoch, balance in self.epoch_balances.items()
        )
        
        return {
            "total_supply": self.TOTAL_SUPPLY,
            "total_distributed": total_distributed,
            "total_remaining": sum(self.epoch_balances.values()),
            "epoch_balances": {
                epoch.value: balance for epoch, balance in self.epoch_balances.items()
            },
            "current_epoch": self.current_epoch.value,
            "founder_halving_count": self.founder_halving_count,
            "total_coherence_density": self.total_coherence_density,
            "total_holders": len(self.balances),
            "total_rewards": len(self.reward_history),
        }
    
    def to_dict(self) -> Dict:
        """Convert contract state to dictionary."""
        return {
            "epoch_balances": {
                epoch.value: balance for epoch, balance in self.epoch_balances.items()
            },
            "balances": self.balances,
            "current_epoch": self.current_epoch.value,
            "epoch_progression": {
                epoch.value: status for epoch, status in self.epoch_progression.items()
            },
            "founder_halving_count": self.founder_halving_count,
            "total_coherence_density": self.total_coherence_density,
            "reward_history": self.reward_history,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "SYNTHToken":
        """Create contract from dictionary."""
        contract = cls()
        contract.epoch_balances = {
            Epoch(epoch): balance for epoch, balance in data["epoch_balances"].items()
        }
        contract.balances = data["balances"]
        contract.current_epoch = Epoch(data["current_epoch"])
        contract.epoch_progression = {
            Epoch(epoch): status for epoch, status in data["epoch_progression"].items()
        }
        contract.founder_halving_count = data["founder_halving_count"]
        contract.total_coherence_density = data["total_coherence_density"]
        contract.reward_history = data["reward_history"]
        return contract

