"""
Tokenomics State Manager for Layer 2
Maintains persistent memory of tokenomics, coherence density, and allocation state.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class Epoch(Enum):
    """Epoch types."""
    FOUNDER = "founder"
    PIONEER = "pioneer"
    COMMUNITY = "community"
    ECOSYSTEM = "ecosystem"


class ContributionTier(Enum):
    """Contribution tiers."""
    GOLD = "gold"  # Scientific
    SILVER = "silver"  # Tech
    COPPER = "copper"  # Alignment


class TokenomicsState:
    """
    Persistent tokenomics state manager for L2.
    Tracks epoch balances, coherence density, and allocation history.
    """
    
    # Total supply: 90 Trillion
    TOTAL_SUPPLY = 90_000_000_000_000
    
    # Epoch distribution percentages
    EPOCH_DISTRIBUTION = {
        Epoch.FOUNDER: 0.50,      # 45T (50%)
        Epoch.PIONEER: 0.25,      # 22.5T (25%)
        Epoch.COMMUNITY: 0.125,   # 11.25T (12.5%)
        Epoch.ECOSYSTEM: 0.125,   # 11.25T (12.5%)
    }
    
    # Epoch qualification thresholds (density scores)
    EPOCH_THRESHOLDS = {
        Epoch.FOUNDER: 8000,
        Epoch.PIONEER: 6000,
        Epoch.COMMUNITY: 4000,
        Epoch.ECOSYSTEM: 0,
    }
    
    # Tier multipliers
    TIER_MULTIPLIERS = {
        ContributionTier.GOLD: 1000.0,
        ContributionTier.SILVER: 100.0,
        ContributionTier.COPPER: 1.0,
    }
    
    # Tier availability by epoch
    TIER_EPOCH_AVAILABILITY = {
        ContributionTier.GOLD: [
            Epoch.FOUNDER,
            Epoch.PIONEER,
            Epoch.COMMUNITY,
            Epoch.ECOSYSTEM,
        ],
        ContributionTier.SILVER: [
            Epoch.COMMUNITY,
            Epoch.ECOSYSTEM,
        ],
        ContributionTier.COPPER: [
            Epoch.PIONEER,
            Epoch.COMMUNITY,
            Epoch.ECOSYSTEM,
        ],
    }
    
    # Founder epoch halving interval
    FOUNDER_HALVING_INTERVAL = 1_000_000  # Coherence density units
    
    def __init__(self, state_file: str = "test_outputs/l2_tokenomics_state.json"):
        """
        Initialize tokenomics state.
        
        Args:
            state_file: Path to state file
        """
        self.state_file = Path(state_file)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize state
        self.state = {
            "epoch_balances": {
                epoch.value: self.TOTAL_SUPPLY * self.EPOCH_DISTRIBUTION[epoch]
                for epoch in Epoch
            },
            "total_coherence_density": 0.0,
            "founder_halving_count": 0,
            "current_epoch": Epoch.FOUNDER.value,
            "epoch_progression": {
                epoch.value: False for epoch in Epoch
            },
            "allocation_history": [],
            "contributor_balances": {},
            "last_updated": datetime.now().isoformat(),
        }
        
        # Load existing state if available
        self.load_state()

    @property
    def total_supply(self):
        """Convenience property for accessing total supply."""
        return self.TOTAL_SUPPLY

    @property
    def current_epoch(self):
        """Convenience property for accessing current epoch."""
        return self.state["current_epoch"]
    
    def load_state(self):
        """Load state from file."""
        if self.state_file.exists():
            try:
                with open(self.state_file, "r") as f:
                    loaded = json.load(f)
                    # Merge with defaults to handle new fields
                    self.state.update(loaded)
                    # Ensure all required fields exist
                    for epoch in Epoch:
                        if epoch.value not in self.state["epoch_balances"]:
                            self.state["epoch_balances"][epoch.value] = (
                                self.TOTAL_SUPPLY * self.EPOCH_DISTRIBUTION[epoch]
                            )
            except Exception as e:
                print(f"Warning: Failed to load state: {e}")
    
    def save_state(self):
        """Save state to file."""
        self.state["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.state_file, "w") as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            print(f"Error saving state: {e}")
    
    def get_epoch_balance(self, epoch: Epoch) -> float:
        """Get available balance for an epoch."""
        return self.state["epoch_balances"].get(epoch.value, 0.0)
    
    def qualify_epoch(self, density_score: float) -> Optional[Epoch]:
        """
        Determine which epoch a contribution qualifies for.
        
        Args:
            density_score: Density score
        
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
        """
        pod_score = (coherence / 10000) * (density / 10000) * (novelty / 10000) * 10000
        return min(pod_score, 10000.0)
    
    def is_tier_available_in_epoch(self, tier: ContributionTier, epoch: Epoch) -> bool:
        """Check if tier is available in epoch."""
        available_epochs = self.TIER_EPOCH_AVAILABILITY.get(tier, [])
        return epoch in available_epochs
    
    def update_coherence_density(self, coherence: float):
        """
        Update total coherence density and check for halving.
        
        Args:
            coherence: Coherence score to add
        """
        self.state["total_coherence_density"] += coherence
        
        # Check for Founder epoch halving
        halvings = int(self.state["total_coherence_density"] / self.FOUNDER_HALVING_INTERVAL)
        if halvings > self.state["founder_halving_count"]:
            # Perform halving
            for _ in range(halvings - self.state["founder_halving_count"]):
                self.state["epoch_balances"][Epoch.FOUNDER.value] /= 2
            self.state["founder_halving_count"] = halvings
        
        self.save_state()
    
    def calculate_allocation(
        self,
        pod_score: float,
        epoch: Epoch,
        tier: ContributionTier
    ) -> Dict:
        """
        Calculate token allocation based on PoC score as percentage of available tokens.

        The PoC score (0-10000) represents the percentage allocation of available tokens
        in the epoch, accounting for halvings and tier multipliers.

        Args:
            pod_score: PoC score (0-10000) representing allocation percentage
            epoch: Qualified epoch (with current balance accounting for halvings)
            tier: Contribution tier with multiplier

        Returns:
            Allocation details with availability check
        """
        # Check tier availability
        if not self.is_tier_available_in_epoch(tier, epoch):
            return {
                "success": False,
                "reason": f"Tier {tier.value} not available in {epoch.value} epoch",
                "available": False,
            }
        
        epoch_balance = self.get_epoch_balance(epoch)
        
        if epoch_balance <= 0:
            return {
                "success": False,
                "reason": f"No tokens available in {epoch.value} epoch",
                "available": False,
            }
        
        # PoC score represents percentage of available tokens allocated (0-100%)
        # Convert PoC score (0-10000) to decimal percentage (0-1)
        allocation_percentage = pod_score / 10000.0  # PoC score of 10000 = 100% allocation

        # Calculate base reward as percentage of available epoch balance
        base_reward = allocation_percentage * epoch_balance

        # Check how many tiers are available in this epoch
        available_tiers_in_epoch = [
            t for t in self.TIER_EPOCH_AVAILABILITY.keys()
            if epoch in self.TIER_EPOCH_AVAILABILITY[t]
        ]

        if len(available_tiers_in_epoch) == 1:
            # Single tier epoch (like Founders with only Gold) - use full allocation
            reward = base_reward
        else:
            # Multi-tier epoch - apply proportional sharing
            tier_multiplier = self.TIER_MULTIPLIERS.get(tier, 1.0)
            # Calculate total weight of available tiers only
            total_tier_weight = sum(self.TIER_MULTIPLIERS.get(available_tier, 1.0)
                                  for available_tier in available_tiers_in_epoch)
            tier_share = tier_multiplier / total_tier_weight
            reward = base_reward * tier_share

        # Ensure we don't exceed epoch balance (accounting for halvings)
        reward = min(reward, epoch_balance)
        
        return {
            "success": True,
            "available": True,
            "epoch": epoch.value,
            "tier": tier.value,
            "pod_score": pod_score,
            "allocation_percentage": allocation_percentage,  # PoC score as percentage (0-100%)
            "base_reward": base_reward,
            "tier_multiplier": tier_multiplier,
            "reward": reward,
            "epoch_balance_before": epoch_balance,
            "epoch_balance_after": epoch_balance - reward,
        }
    
    def record_allocation(
        self,
        submission_hash: str,
        contributor: str,
        allocation: Dict,
        coherence: float
    ):
        """
        Record an allocation and update state.
        
        Args:
            submission_hash: Submission hash
            contributor: Contributor address
            allocation: Allocation details from calculate_allocation
            coherence: Coherence score for density tracking
        """
        if not allocation.get("success"):
            return
        
        # Update epoch balance
        epoch = Epoch(allocation["epoch"])
        self.state["epoch_balances"][epoch.value] -= allocation["reward"]
        
        # Update contributor balance
        if contributor not in self.state["contributor_balances"]:
            self.state["contributor_balances"][contributor] = 0.0
        self.state["contributor_balances"][contributor] += allocation["reward"]
        
        # Update coherence density
        self.update_coherence_density(coherence)
        
        # Record in history
        allocation_record = {
            "submission_hash": submission_hash,
            "contributor": contributor,
            "timestamp": datetime.now().isoformat(),
            "allocation": allocation,
            "coherence": coherence,
        }
        self.state["allocation_history"].append(allocation_record)
        
        # Keep only last 1000 allocations in memory
        if len(self.state["allocation_history"]) > 1000:
            self.state["allocation_history"] = self.state["allocation_history"][-1000:]
        
        self.save_state()
    
    def get_statistics(self) -> Dict:
        """Get tokenomics statistics."""
        total_distributed = sum(
            self.TOTAL_SUPPLY * self.EPOCH_DISTRIBUTION[Epoch(epoch_name)] - balance
            for epoch_name, balance in self.state["epoch_balances"].items()
        )
        
        return {
            "total_supply": self.TOTAL_SUPPLY,
            "total_distributed": total_distributed,
            "total_remaining": sum(self.state["epoch_balances"].values()),
            "epoch_balances": self.state["epoch_balances"].copy(),
            "current_epoch": self.state["current_epoch"],
            "founder_halving_count": self.state["founder_halving_count"],
            "total_coherence_density": self.state["total_coherence_density"],
            "total_holders": len(self.state["contributor_balances"]),
            "total_allocations": len(self.state["allocation_history"]),
        }
    
    def get_epoch_info(self) -> Dict:
        """Get epoch information."""
        return {
            "current_epoch": self.state["current_epoch"],
            "epochs": {
                epoch.value: {
                    "balance": self.get_epoch_balance(epoch),
                    "threshold": self.EPOCH_THRESHOLDS[epoch],
                    "distribution_percent": self.EPOCH_DISTRIBUTION[epoch] * 100,
                    "available_tiers": [
                        tier.value for tier, epochs in self.TIER_EPOCH_AVAILABILITY.items()
                        if epoch in epochs
                    ],
                }
                for epoch in Epoch
            },
        }
    
    def sync_from_l1(self, l1_state: Dict):
        """
        Sync state from L1 blockchain.
        
        Args:
            l1_state: State from L1 node
        """
        # Update epoch balances from L1
        if "epoch_balances" in l1_state:
            self.state["epoch_balances"].update(l1_state["epoch_balances"])
        
        # Update coherence density
        if "total_coherence_density" in l1_state:
            self.state["total_coherence_density"] = l1_state["total_coherence_density"]
        
        # Update halving count
        if "founder_halving_count" in l1_state:
            self.state["founder_halving_count"] = l1_state["founder_halving_count"]
        
        # Update current epoch
        if "current_epoch" in l1_state:
            self.state["current_epoch"] = l1_state["current_epoch"]
        
        self.save_state()

