"""
Contributor Tier Management System
Manages Copper/Silver/Gold tier contributions and benefits as per Blueprint §4.2.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum


class ContributorTier(Enum):
    """Blueprint-defined contributor tiers."""
    COPPER = "copper"  # $10K-$25K → 0.05-0.25% SYNTH
    SILVER = "silver"  # $50K-$100K → 0.25-1% SYNTH
    GOLD = "gold"      # $250K-$500K → 1-3% SYNTH


class TierManager:
    """
    Manages contributor tiers and allocations according to Blueprint §4.2.

    Tier Structure (Blueprint §4.2):
    - Copper: $10K-$25K contribution → 0.05-0.25% SYNTH allocation
    - Silver: $50K-$100K contribution → 0.25-1% SYNTH allocation
    - Gold: $250K-$500K contribution → 1-3% SYNTH allocation

    Founders' 5% offering supports FractiAI Research Team operations.
    """

    # Blueprint §4.2 tier contribution ranges
    TIER_CONTRIBUTION_RANGES = {
        ContributorTier.COPPER: (10000, 25000),    # $10K-$25K
        ContributorTier.SILVER: (50000, 100000),   # $50K-$100K
        ContributorTier.GOLD: (250000, 500000),    # $250K-$500K
    }

    # Blueprint §4.2 SYNTH allocation percentages (of Founders' 5%)
    TIER_SYNTH_ALLOCATIONS = {
        ContributorTier.COPPER: (0.0005, 0.0025),  # 0.05-0.25%
        ContributorTier.SILVER: (0.0025, 0.01),     # 0.25-1%
        ContributorTier.GOLD: (0.01, 0.03),         # 1-3%
    }

    # Founders' 5% total allocation for tier system
    FOUNDERS_TIER_ALLOCATION_PERCENTAGE = 0.05  # 5%

    def __init__(self, state_file: str = "test_outputs/contributor_tiers.json"):
        """
        Initialize tier manager.

        Args:
            state_file: Path to tier state persistence file
        """
        self.state_file = Path(state_file)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        # Initialize state
        self.state = {
            "contributors": {},  # contributor_address -> tier_info
            "total_contributions": 0.0,
            "tier_totals": {
                tier.value: 0.0 for tier in ContributorTier
            },
            "tier_counts": {
                tier.value: 0 for tier in ContributorTier
            },
            "founders_allocation_used": 0.0,
            "last_updated": datetime.now().isoformat(),
        }

        # Load existing state
        self.load_state()

    @property
    def total_founders_allocation(self) -> float:
        """Total SYNTH available for tier system (Founders' 5%)."""
        # This would need to be connected to the main tokenomics system
        # For now, using a placeholder - should be 5% of 90T = 4.5T
        return 90_000_000_000_000 * self.FOUNDERS_TIER_ALLOCATION_PERCENTAGE

    def load_state(self):
        """Load tier state from file."""
        if self.state_file.exists():
            try:
                with open(self.state_file, "r") as f:
                    loaded = json.load(f)
                    self.state.update(loaded)
            except Exception as e:
                print(f"Warning: Failed to load tier state: {e}")

    def save_state(self):
        """Save tier state to file."""
        self.state["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.state_file, "w") as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            print(f"Error saving tier state: {e}")

    def get_tier_for_contribution(self, contribution_amount: float) -> Optional[ContributorTier]:
        """
        Determine tier based on contribution amount per Blueprint §4.2.

        Args:
            contribution_amount: Contribution in USD

        Returns:
            ContributorTier if eligible, None otherwise
        """
        for tier, (min_amount, max_amount) in self.TIER_CONTRIBUTION_RANGES.items():
            if min_amount <= contribution_amount <= max_amount:
                return tier
        return None

    def calculate_synth_allocation(self, tier: ContributorTier, contribution_amount: float) -> float:
        """
        Calculate SYNTH allocation for tier contribution per Blueprint §4.2.

        Args:
            tier: Contributor tier
            contribution_amount: Contribution amount in USD

        Returns:
            SYNTH tokens to allocate
        """
        if tier not in self.TIER_SYNTH_ALLOCATIONS:
            return 0.0

        min_pct, max_pct = self.TIER_SYNTH_ALLOCATIONS[tier]
        min_contrib, max_contrib = self.TIER_CONTRIBUTION_RANGES[tier]

        # Calculate percentage within tier range
        if max_contrib == min_contrib:
            allocation_pct = min_pct
        else:
            # Linear interpolation within tier range
            pct_within_range = (contribution_amount - min_contrib) / (max_contrib - min_contrib)
            allocation_pct = min_pct + (max_pct - min_pct) * pct_within_range

        # Calculate actual SYNTH allocation
        total_founders_allocation = self.total_founders_allocation
        synth_allocation = total_founders_allocation * allocation_pct

        return synth_allocation

    def register_contribution(self, contributor_address: str, contribution_amount: float,
                            transaction_hash: str = None) -> Dict:
        """
        Register a tier contribution per Blueprint §4.2.

        Args:
            contributor_address: Contributor's address
            contribution_amount: Contribution amount in USD
            transaction_hash: Optional blockchain transaction hash

        Returns:
            Registration result with tier info and SYNTH allocation
        """
        # Determine tier eligibility
        tier = self.get_tier_for_contribution(contribution_amount)
        if not tier:
            return {
                "success": False,
                "reason": f"Contribution ${contribution_amount:,.0f} does not qualify for any tier",
                "eligible_tiers": {
                    t.value: f"${min_amt:,.0f}-${max_amt:,.0f}"
                    for t, (min_amt, max_amt) in self.TIER_CONTRIBUTION_RANGES.items()
                }
            }

        # Calculate SYNTH allocation
        synth_allocation = self.calculate_synth_allocation(tier, contribution_amount)

        # Check if we have remaining allocation
        remaining_allocation = self.total_founders_allocation - self.state["founders_allocation_used"]
        if synth_allocation > remaining_allocation:
            return {
                "success": False,
                "reason": f"Insufficient Founders' allocation remaining. Requested: {synth_allocation:,.0f}, Available: {remaining_allocation:,.0f}",
                "tier": tier.value,
                "requested_allocation": synth_allocation,
                "available_allocation": remaining_allocation
            }

        # Register the contribution
        contributor_info = {
            "tier": tier.value,
            "contribution_amount": contribution_amount,
            "synth_allocation": synth_allocation,
            "transaction_hash": transaction_hash,
            "registered_at": datetime.now().isoformat(),
        }

        self.state["contributors"][contributor_address] = contributor_info
        self.state["total_contributions"] += contribution_amount
        self.state["tier_totals"][tier.value] += contribution_amount
        self.state["tier_counts"][tier.value] += 1
        self.state["founders_allocation_used"] += synth_allocation

        self.save_state()

        return {
            "success": True,
            "tier": tier.value,
            "contribution_amount": contribution_amount,
            "synth_allocation": synth_allocation,
            "benefits": self.get_tier_benefits(tier),
            "contributor_address": contributor_address,
            "transaction_hash": transaction_hash,
            "registered_at": contributor_info["registered_at"]
        }

    def get_tier_benefits(self, tier: ContributorTier) -> Dict:
        """
        Get benefits for a specific tier per Blueprint §4.2.

        Args:
            tier: Contributor tier

        Returns:
            Dictionary of tier benefits
        """
        base_benefits = {
            ContributorTier.COPPER: {
                "dashboard_access": True,
                "early_insight": True,
                "voting_rights": False,
                "advisory_access": False,
                "strategic_influence": False,
                "reserved_slots": False
            },
            ContributorTier.SILVER: {
                "dashboard_access": True,
                "early_insight": True,
                "voting_rights": True,
                "advisory_access": True,
                "strategic_influence": False,
                "reserved_slots": False
            },
            ContributorTier.GOLD: {
                "dashboard_access": True,
                "early_insight": True,
                "voting_rights": True,
                "advisory_access": True,
                "strategic_influence": True,
                "reserved_slots": True
            }
        }

        return base_benefits.get(tier, {})

    def get_contributor_info(self, contributor_address: str) -> Optional[Dict]:
        """
        Get information about a contributor's tier status.

        Args:
            contributor_address: Contributor's address

        Returns:
            Contributor info if registered, None otherwise
        """
        return self.state["contributors"].get(contributor_address)

    def get_tier_statistics(self) -> Dict:
        """
        Get comprehensive tier statistics.

        Returns:
            Statistics about tier system usage
        """
        return {
            "total_contributions": self.state["total_contributions"],
            "total_contributors": len(self.state["contributors"]),
            "tier_breakdown": {
                tier.value: {
                    "count": self.state["tier_counts"][tier.value],
                    "total_contributed": self.state["tier_totals"][tier.value],
                    "benefits": self.get_tier_benefits(tier)
                }
                for tier in ContributorTier
            },
            "founders_allocation": {
                "total": self.total_founders_allocation,
                "used": self.state["founders_allocation_used"],
                "remaining": self.total_founders_allocation - self.state["founders_allocation_used"],
                "utilization_percentage": (self.state["founders_allocation_used"] / self.total_founders_allocation) * 100
            },
            "last_updated": self.state["last_updated"]
        }

    def get_eligible_tiers(self, contribution_amount: float) -> List[Dict]:
        """
        Get all tiers eligible for a given contribution amount.

        Args:
            contribution_amount: Contribution amount in USD

        Returns:
            List of eligible tiers with details
        """
        eligible_tiers = []

        for tier in ContributorTier:
            min_amt, max_amt = self.TIER_CONTRIBUTION_RANGES[tier]
            if min_amt <= contribution_amount <= max_amt:
                synth_allocation = self.calculate_synth_allocation(tier, contribution_amount)
                eligible_tiers.append({
                    "tier": tier.value,
                    "contribution_range": f"${min_amt:,.0f}-${max_amt:,.0f}",
                    "contribution_amount": contribution_amount,
                    "synth_allocation": synth_allocation,
                    "benefits": self.get_tier_benefits(tier)
                })

        return eligible_tiers

    def validate_contribution_amount(self, contribution_amount: float) -> Dict:
        """
        Validate a contribution amount against tier requirements.

        Args:
            contribution_amount: Contribution amount in USD

        Returns:
            Validation result with tier eligibility
        """
        eligible_tiers = self.get_eligible_tiers(contribution_amount)

        if not eligible_tiers:
            return {
                "valid": False,
                "reason": f"Contribution ${contribution_amount:,.0f} does not qualify for any tier",
                "minimum_required": min(min_amt for min_amt, _ in self.TIER_CONTRIBUTION_RANGES.values()),
                "available_tiers": [
                    {
                        "tier": tier.value,
                        "range": f"${min_amt:,.0f}-${max_amt:,.0f}",
                        "benefits": self.get_tier_benefits(tier)
                    }
                    for tier, (min_amt, max_amt) in self.TIER_CONTRIBUTION_RANGES.items()
                ]
            }

        best_tier = max(eligible_tiers, key=lambda x: x["synth_allocation"])

        return {
            "valid": True,
            "eligible_tiers": eligible_tiers,
            "recommended_tier": best_tier["tier"],
            "maximum_allocation": best_tier["synth_allocation"]
        }
