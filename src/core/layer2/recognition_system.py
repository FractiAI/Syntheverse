"""
"I Was Here First" Recognition System
Implements Blueprint §1.4 early contributor recognition with priority, visibility, and legacy features.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from collections import defaultdict


class RecognitionBadge:
    """
    Represents a recognition badge for early contributors per Blueprint §1.4.
    """

    def __init__(self, badge_type: str, name: str, description: str,
                 criteria: Dict, benefits: List[str], rarity: str = "common"):
        self.badge_type = badge_type
        self.name = name
        self.description = description
        self.criteria = criteria  # Dict with requirements
        self.benefits = benefits  # List of benefits
        self.rarity = rarity  # common, rare, epic, legendary
        self.created_at = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        """Convert badge to dictionary representation."""
        return {
            "badge_type": self.badge_type,
            "name": self.name,
            "description": self.description,
            "criteria": self.criteria,
            "benefits": self.benefits,
            "rarity": self.rarity,
            "created_at": self.created_at
        }

    def check_eligibility(self, contributor_stats: Dict) -> bool:
        """
        Check if a contributor meets the criteria for this badge.

        Args:
            contributor_stats: Contributor statistics

        Returns:
            True if eligible for this badge
        """
        for key, required_value in self.criteria.items():
            if key not in contributor_stats:
                return False

            actual_value = contributor_stats[key]

            if isinstance(required_value, dict):
                # Complex criteria with operators
                if "$gte" in required_value and actual_value < required_value["$gte"]:
                    return False
                if "$lte" in required_value and actual_value > required_value["$lte"]:
                    return False
                if "$eq" in required_value and actual_value != required_value["$eq"]:
                    return False
            else:
                # Simple equality check
                if actual_value < required_value:
                    return False

        return True


class RecognitionSystem:
    """
    "I Was Here First" recognition system per Blueprint §1.4.
    Provides priority, visibility, and legacy recognition for early contributors.
    """

    # Recognition badges for early contributors
    RECOGNITION_BADGES = [
        RecognitionBadge(
            badge_type="pioneer",
            name="Syntheverse Pioneer",
            description="One of the first 10 contributors to submit to Syntheverse",
            criteria={"submission_order": {"$lte": 10}},
            benefits=[
                "Priority display in all listings",
                "Special pioneer badge on profile",
                "Invited to all future announcements",
                "Permanent legacy recognition"
            ],
            rarity="legendary"
        ),
        RecognitionBadge(
            badge_type="founder",
            name="Genesis Contributor",
            description="Contributed within the first month of Syntheverse launch",
            criteria={"days_since_launch": {"$lte": 30}},
            benefits=[
                "Enhanced visibility in search results",
                "Founder badge on all submissions",
                "Priority access to new features",
                "Historical significance recognition"
            ],
            rarity="epic"
        ),
        RecognitionBadge(
            badge_type="trailblazer",
            name="Trailblazer",
            description="First contributor in a new research category",
            criteria={"first_in_category": True},
            benefits=[
                "Category pioneer recognition",
                "Special trailblazer icon",
                "Mentorship opportunities",
                "Category leadership status"
            ],
            rarity="rare"
        ),
        RecognitionBadge(
            badge_type="visionary",
            name="Visionary Contributor",
            description="High-impact contribution recognized by community",
            criteria={"community_score": {"$gte": 95}},
            benefits=[
                "Featured contributor status",
                "Community spotlight opportunities",
                "Enhanced networking access",
                "Thought leadership recognition"
            ],
            rarity="rare"
        ),
        RecognitionBadge(
            badge_type="dedicated",
            name="Dedicated Contributor",
            description="Consistent contributor with 5+ qualified submissions",
            criteria={"qualified_submissions": {"$gte": 5}},
            benefits=[
                "Trusted contributor status",
                "Priority review queue",
                "Community voting rights",
                "Expert status recognition"
            ],
            rarity="common"
        )
    ]

    def __init__(self, state_file: str = "test_outputs/recognition_system.json",
                 launch_date: str = "2025-01-01"):  # Default launch date
        """
        Initialize recognition system.

        Args:
            state_file: Path to recognition state persistence file
            launch_date: System launch date (ISO format)
        """
        self.state_file = Path(state_file)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.launch_date = datetime.fromisoformat(launch_date)

        # Initialize state
        self.state = {
            "contributors": {},  # contributor -> recognition data
            "badges_awarded": defaultdict(list),  # badge_type -> list of contributors
            "submission_order": [],  # Ordered list of first-time contributors
            "category_firsts": {},  # category -> first contributor
            "last_updated": datetime.now().isoformat(),
        }

        # Load existing state
        self.load_state()

    def load_state(self):
        """Load recognition state from file."""
        if self.state_file.exists():
            try:
                with open(self.state_file, "r") as f:
                    loaded = json.load(f)
                    self.state.update(loaded)
                    # Convert defaultdict
                    self.state["badges_awarded"] = defaultdict(list, loaded.get("badges_awarded", {}))
            except Exception as e:
                print(f"Warning: Failed to load recognition state: {e}")

    def save_state(self):
        """Save recognition state to file."""
        self.state["last_updated"] = datetime.now().isoformat()
        try:
            # Convert defaultdict to regular dict for JSON serialization
            state_to_save = dict(self.state)
            state_to_save["badges_awarded"] = dict(self.state["badges_awarded"])
            with open(self.state_file, "w") as f:
                json.dump(state_to_save, f, indent=2)
        except Exception as e:
            print(f"Error saving recognition state: {e}")

    def record_contribution(self, contributor: str, submission_hash: str,
                          category: str, submission_date: str,
                          coherence_score: float) -> Dict:
        """
        Record a contribution for recognition tracking per Blueprint §1.4.

        Args:
            contributor: Contributor identifier
            submission_hash: Unique submission identifier
            category: Contribution category (scientific, tech, alignment)
            submission_date: ISO format submission date
            coherence_score: Contribution coherence score

        Returns:
            Recognition update result
        """
        submission_datetime = datetime.fromisoformat(submission_date)
        days_since_launch = (submission_datetime - self.launch_date).days

        # Track submission order for pioneers
        if contributor not in self.state["submission_order"]:
            self.state["submission_order"].append(contributor)

        # Track first in category
        if category not in self.state["category_firsts"]:
            self.state["category_firsts"][category] = contributor

        # Update contributor stats
        if contributor not in self.state["contributors"]:
            self.state["contributors"][contributor] = {
                "first_contribution": submission_date,
                "total_submissions": 0,
                "qualified_submissions": 0,
                "categories": set(),
                "badges": [],
                "recognition_level": "participant",
                "days_since_launch": days_since_launch,
                "submission_order": len(self.state["submission_order"])
            }

        contributor_data = self.state["contributors"][contributor]
        contributor_data["total_submissions"] += 1
        contributor_data["qualified_submissions"] += 1  # Assuming this is a qualified submission
        contributor_data["categories"].add(category)

        # Convert set to list for JSON serialization
        contributor_data["categories"] = list(contributor_data["categories"])

        # Check for new badges
        new_badges = self._check_badge_eligibility(contributor)

        # Update recognition level based on badges
        recognition_level = self._calculate_recognition_level(contributor_data, new_badges)
        contributor_data["recognition_level"] = recognition_level

        self.save_state()

        return {
            "contributor": contributor,
            "submission_order": contributor_data["submission_order"],
            "recognition_level": recognition_level,
            "new_badges": new_badges,
            "total_badges": len(contributor_data["badges"]),
            "days_since_launch": days_since_launch,
            "priority_score": self._calculate_priority_score(contributor_data)
        }

    def _check_badge_eligibility(self, contributor: str) -> List[Dict]:
        """
        Check if contributor is eligible for new badges.

        Args:
            contributor: Contributor identifier

        Returns:
            List of newly awarded badges
        """
        contributor_data = self.state["contributors"][contributor]
        current_badges = set(b["badge_type"] for b in contributor_data["badges"])
        new_badges = []

        # Prepare stats for badge checking
        stats = dict(contributor_data)
        stats["submission_order"] = contributor_data["submission_order"]
        stats["first_in_category"] = any(
            self.state["category_firsts"].get(cat) == contributor
            for cat in contributor_data["categories"]
        )
        stats["community_score"] = 85  # Placeholder - would be calculated from community feedback

        for badge in self.RECOGNITION_BADGES:
            if badge.badge_type not in current_badges and badge.check_eligibility(stats):
                badge_dict = badge.to_dict()
                contributor_data["badges"].append(badge_dict)
                self.state["badges_awarded"][badge.badge_type].append(contributor)
                new_badges.append(badge_dict)

        return new_badges

    def _calculate_recognition_level(self, contributor_data: Dict, new_badges: List[Dict]) -> str:
        """
        Calculate contributor recognition level based on badges and activity.

        Args:
            contributor_data: Contributor statistics
            new_badges: Newly awarded badges

        Returns:
            Recognition level string
        """
        badge_types = set(b["badge_type"] for b in contributor_data["badges"])

        if "pioneer" in badge_types:
            return "legendary_pioneer"
        elif "founder" in badge_types:
            return "epic_founder"
        elif len(badge_types) >= 2:
            return "master_contributor"
        elif len(badge_types) >= 1:
            return "recognized_contributor"
        elif contributor_data["qualified_submissions"] >= 3:
            return "active_contributor"
        else:
            return "valued_contributor"

    def _calculate_priority_score(self, contributor_data: Dict) -> float:
        """
        Calculate priority score for enhanced visibility per Blueprint §1.4.

        Args:
            contributor_data: Contributor statistics

        Returns:
            Priority score (0-100)
        """
        base_score = 50  # Default priority

        # Early contributor bonus
        if contributor_data["submission_order"] <= 10:
            base_score += 40
        elif contributor_data["submission_order"] <= 50:
            base_score += 20
        elif contributor_data["days_since_launch"] <= 30:
            base_score += 15

        # Badge bonuses
        badge_multiplier = len(contributor_data["badges"]) * 5
        base_score += min(badge_multiplier, 25)

        # Activity bonus
        activity_bonus = min(contributor_data["qualified_submissions"] * 2, 15)
        base_score += activity_bonus

        return min(base_score, 100)

    def get_contributor_recognition(self, contributor: str) -> Optional[Dict]:
        """
        Get complete recognition information for a contributor per Blueprint §1.4.

        Args:
            contributor: Contributor identifier

        Returns:
            Recognition information or None if not found
        """
        if contributor not in self.state["contributors"]:
            return None

        contributor_data = self.state["contributors"][contributor]

        return {
            "contributor": contributor,
            "recognition_level": contributor_data["recognition_level"],
            "submission_order": contributor_data["submission_order"],
            "badges": contributor_data["badges"],
            "priority_score": self._calculate_priority_score(contributor_data),
            "statistics": {
                "total_submissions": contributor_data["total_submissions"],
                "qualified_submissions": contributor_data["qualified_submissions"],
                "categories": contributor_data["categories"],
                "first_contribution": contributor_data["first_contribution"],
                "days_since_launch": contributor_data["days_since_launch"]
            },
            "benefits": self._get_recognition_benefits(contributor_data["recognition_level"])
        }

    def _get_recognition_benefits(self, recognition_level: str) -> List[str]:
        """
        Get benefits for a recognition level per Blueprint §1.4.

        Args:
            recognition_level: Recognition level string

        Returns:
            List of benefits
        """
        benefits_map = {
            "legendary_pioneer": [
                "Maximum priority in all listings",
                "Permanent pioneer recognition badge",
                "Invited to all strategic discussions",
                "Legacy founder status",
                "Enhanced visibility multiplier (5x)",
                "Priority access to all new features"
            ],
            "epic_founder": [
                "High priority in search results",
                "Founder recognition badge",
                "Early access to new features",
                "Enhanced visibility multiplier (3x)",
                "Community leadership opportunities"
            ],
            "master_contributor": [
                "Elevated visibility in listings",
                "Multiple recognition badges",
                "Community spotlight features",
                "Enhanced visibility multiplier (2x)",
                "Mentorship program access"
            ],
            "recognized_contributor": [
                "Standard recognition badge",
                "Enhanced visibility multiplier (1.5x)",
                "Community appreciation features"
            ],
            "active_contributor": [
                "Activity recognition",
                "Minor visibility boost",
                "Community participation benefits"
            ],
            "valued_contributor": [
                "Basic recognition",
                "Standard community benefits"
            ]
        }

        return benefits_map.get(recognition_level, ["Basic community participation"])

    def get_recognition_leaderboard(self, limit: int = 20) -> List[Dict]:
        """
        Get recognition leaderboard showing top contributors by priority score.

        Args:
            limit: Maximum number of contributors to return

        Returns:
            Sorted list of top recognized contributors
        """
        contributors = []

        for contributor, data in self.state["contributors"].items():
            priority_score = self._calculate_priority_score(data)
            contributors.append({
                "contributor": contributor,
                "recognition_level": data["recognition_level"],
                "priority_score": priority_score,
                "submission_order": data["submission_order"],
                "badge_count": len(data["badges"]),
                "qualified_submissions": data["qualified_submissions"]
            })

        # Sort by priority score descending
        contributors.sort(key=lambda x: x["priority_score"], reverse=True)

        return contributors[:limit]

    def get_recognition_statistics(self) -> Dict:
        """
        Get comprehensive recognition system statistics.

        Returns:
            Statistics about the recognition system
        """
        total_contributors = len(self.state["contributors"])
        total_badges = sum(len(data["badges"]) for data in self.state["contributors"].values())

        recognition_levels = defaultdict(int)
        badge_distribution = defaultdict(int)

        for data in self.state["contributors"].values():
            recognition_levels[data["recognition_level"]] += 1
            for badge in data["badges"]:
                badge_distribution[badge["badge_type"]] += 1

        return {
            "total_contributors": total_contributors,
            "total_badges_awarded": total_badges,
            "recognition_level_distribution": dict(recognition_levels),
            "badge_distribution": dict(badge_distribution),
            "pioneer_count": len(self.state["submission_order"][:10]) if len(self.state["submission_order"]) >= 10 else len(self.state["submission_order"]),
            "category_pioneers": len(self.state["category_firsts"]),
            "last_updated": self.state["last_updated"]
        }

    def get_legacy_contributors(self, limit: int = 10) -> List[Dict]:
        """
        Get earliest contributors for legacy recognition per Blueprint §1.4.

        Args:
            limit: Maximum number of legacy contributors

        Returns:
            List of earliest contributors with legacy information
        """
        legacy_contributors = []

        for i, contributor in enumerate(self.state["submission_order"][:limit]):
            if contributor in self.state["contributors"]:
                data = self.state["contributors"][contributor]
                legacy_contributors.append({
                    "contributor": contributor,
                    "submission_order": i + 1,
                    "first_contribution": data["first_contribution"],
                    "recognition_level": data["recognition_level"],
                    "legacy_status": self._get_legacy_status(i + 1),
                    "historical_significance": f"#{i + 1} earliest contributor to Syntheverse"
                })

        return legacy_contributors

    def _get_legacy_status(self, submission_order: int) -> str:
        """
        Get legacy status based on submission order.

        Args:
            submission_order: Position in submission order

        Returns:
            Legacy status string
        """
        if submission_order == 1:
            return "Genesis Contributor - The Very First"
        elif submission_order <= 5:
            return "Foundational Pioneer"
        elif submission_order <= 10:
            return "Early Pioneer"
        elif submission_order <= 25:
            return "Trailblazer"
        elif submission_order <= 50:
            return "Early Adopter"
        else:
            return "Valued Early Contributor"
