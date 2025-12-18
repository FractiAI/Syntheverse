"""
Zenodo Community Integration
Implements Blueprint §1.1 community submission workflow for Syntheverse Zenodo communities.
"""

import requests
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
import hashlib

from .poc_archive import ContributionStatus


class ZenodoCommunity:
    """
    Represents a Syntheverse Zenodo community for Blueprint §1.1 implementation.
    """

    def __init__(self, community_id: str, name: str, description: str, keywords: List[str]):
        self.community_id = community_id
        self.name = name
        self.description = description
        self.keywords = keywords
        self.created_at = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        """Convert community to dictionary representation."""
        return {
            "community_id": self.community_id,
            "name": self.name,
            "description": self.description,
            "keywords": self.keywords,
            "created_at": self.created_at
        }


class ZenodoIntegration:
    """
    Integrates with Zenodo API to support Blueprint §1.1 community submission workflow.

    Blueprint §1.1: "Submit to Syntheverse Zenodo communities, a gathering place for
    independent, outcast contributors"
    """

    ZENODO_API_BASE = "https://zenodo.org/api"
    SYNTHVERSE_COMMUNITIES = [
        {
            "id": "syntheverse-fractal-research",
            "name": "Syntheverse Fractal Research",
            "description": "Research artifacts exploring hydrogen-holographic fractal systems",
            "keywords": ["fractal", "hydrogen", "holographic", "research", "syntheverse"]
        },
        {
            "id": "syntheverse-ai-alignment",
            "name": "AI Alignment & Frontier Research",
            "description": "Contributions to AI alignment and frontier AI research",
            "keywords": ["ai", "alignment", "frontier", "research", "syntheverse"]
        },
        {
            "id": "syntheverse-crypto-ecosystems",
            "name": "Cryptographic Ecosystems",
            "description": "Cryptographic systems, blockchain research, and ecosystem design",
            "keywords": ["crypto", "blockchain", "ecosystem", "syntheverse"]
        },
        {
            "id": "syntheverse-mythic-systems",
            "name": "Mythic & Symbolic Systems",
            "description": "Mythic patterns, symbolic systems, and archetypal research",
            "keywords": ["mythic", "symbolic", "archetypal", "syntheverse"]
        }
    ]

    def __init__(self, cache_file: str = "test_outputs/zenodo_cache.json"):
        """
        Initialize Zenodo integration.

        Args:
            cache_file: Path to cache file for Zenodo data
        """
        self.cache_file = Path(cache_file)
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)

        # Initialize cache
        self.cache = {
            "communities": {},
            "records": {},
            "last_updated": None
        }
        self.load_cache()

        # Initialize Syntheverse communities
        self._initialize_syntheverse_communities()

    def load_cache(self):
        """Load cached Zenodo data."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r") as f:
                    self.cache.update(json.load(f))
            except Exception as e:
                print(f"Warning: Failed to load Zenodo cache: {e}")

    def save_cache(self):
        """Save Zenodo data to cache."""
        self.cache["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.cache_file, "w") as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"Error saving Zenodo cache: {e}")

    def _initialize_syntheverse_communities(self):
        """Initialize Syntheverse-specific Zenodo communities."""
        for community_data in self.SYNTHVERSE_COMMUNITIES:
            community_id = community_data["id"]
            if community_id not in self.cache["communities"]:
                community = ZenodoCommunity(
                    community_id=community_id,
                    name=community_data["name"],
                    description=community_data["description"],
                    keywords=community_data["keywords"]
                )
                self.cache["communities"][community_id] = community.to_dict()

        self.save_cache()

    def get_syntheverse_communities(self) -> List[Dict]:
        """
        Get all Syntheverse Zenodo communities per Blueprint §1.1.

        Returns:
            List of community dictionaries
        """
        return list(self.cache["communities"].values())

    def search_community_records(self, community_id: str, query: str = "",
                               limit: int = 20) -> List[Dict]:
        """
        Search for records in a specific Syntheverse community.

        Args:
            community_id: Community ID to search
            query: Search query (optional)
            limit: Maximum number of results

        Returns:
            List of record dictionaries
        """
        # For now, return mock data since we don't have actual Zenodo API access
        # In production, this would call the Zenodo API

        mock_records = [
            {
                "id": f"mock_record_{i}",
                "title": f"Sample Research Contribution {i}",
                "description": f"Research artifact related to {community_id}",
                "authors": [f"Researcher {i}"],
                "publication_date": "2025-01-01",
                "doi": f"10.5281/zenodo.{1000000 + i}",
                "keywords": ["research", "syntheverse", community_id.split('-')[-1]],
                "files": [{"filename": f"contribution_{i}.pdf", "size": 1024000}],
                "community": community_id
            }
            for i in range(min(limit, 10))
        ]

        # Filter by query if provided
        if query:
            mock_records = [
                record for record in mock_records
                if query.lower() in record["title"].lower() or
                   query.lower() in record["description"].lower()
            ]

        return mock_records[:limit]

    def get_community_statistics(self, community_id: str) -> Dict:
        """
        Get statistics for a specific community.

        Args:
            community_id: Community ID

        Returns:
            Community statistics
        """
        if community_id not in self.cache["communities"]:
            return {"error": "Community not found"}

        # Mock statistics - in production, this would query Zenodo API
        return {
            "community_id": community_id,
            "total_records": 42,
            "recent_uploads": 8,
            "active_contributors": 15,
            "total_downloads": 1250,
            "top_keywords": ["research", "fractal", "ai", "blockchain"],
            "last_updated": datetime.now().isoformat()
        }

    def validate_community_submission(self, community_id: str, title: str,
                                    description: str, keywords: List[str]) -> Dict:
        """
        Validate that a submission fits a Syntheverse community.

        Args:
            community_id: Target community ID
            title: Submission title
            description: Submission description
            keywords: Submission keywords

        Returns:
            Validation result
        """
        if community_id not in self.cache["communities"]:
            return {
                "valid": False,
                "reason": f"Community '{community_id}' not found"
            }

        community = self.cache["communities"][community_id]
        community_keywords = set(community["keywords"])

        # Check if submission keywords match community keywords
        submission_keywords = set(keywords)
        keyword_overlap = len(community_keywords.intersection(submission_keywords))

        # Basic validation - at least one keyword match
        if keyword_overlap == 0:
            return {
                "valid": False,
                "reason": f"Submission keywords don't match community theme. Community keywords: {list(community_keywords)}",
                "community_keywords": list(community_keywords),
                "suggestion": "Consider adding relevant keywords like 'fractal', 'ai', 'research', or 'blockchain'"
            }

        return {
            "valid": True,
            "keyword_overlap": keyword_overlap,
            "community_match_score": min(keyword_overlap * 20, 100),  # Max 100%
            "community": community
        }

    def submit_to_community(self, community_id: str, title: str, description: str,
                           keywords: List[str], file_path: str,
                           contributor: str) -> Dict:
        """
        Submit a contribution to a Syntheverse community (Blueprint §1.1 workflow).

        Args:
            community_id: Target community ID
            title: Submission title
            description: Submission description
            keywords: Submission keywords
            file_path: Path to submission file
            contributor: Contributor identifier

        Returns:
            Submission result
        """
        # Validate community fit
        validation = self.validate_community_submission(
            community_id, title, description, keywords
        )

        if not validation["valid"]:
            return validation

        # Check file exists
        if not Path(file_path).exists():
            return {
                "success": False,
                "reason": f"File not found: {file_path}"
            }

        # Generate submission ID
        submission_id = hashlib.sha256(
            f"{community_id}:{title}:{contributor}:{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]

        # Mock submission - in production, this would upload to Zenodo
        submission_record = {
            "submission_id": submission_id,
            "community_id": community_id,
            "title": title,
            "description": description,
            "keywords": keywords,
            "contributor": contributor,
            "file_path": file_path,
            "submitted_at": datetime.now().isoformat(),
            "status": "submitted",
            "zenodo_url": f"https://zenodo.org/records/{submission_id}",
            "validation_score": validation["community_match_score"]
        }

        # Store in cache (in production, this would be stored in database)
        record_key = f"{community_id}:{submission_id}"
        self.cache["records"][record_key] = submission_record
        self.save_cache()

        return {
            "success": True,
            "submission_id": submission_id,
            "community_id": community_id,
            "zenodo_url": submission_record["zenodo_url"],
            "validation_score": validation["community_match_score"],
            "status": "submitted",
            "message": f"Successfully submitted to {self.cache['communities'][community_id]['name']} community"
        }

    def get_community_feed(self, community_id: str, limit: int = 10) -> List[Dict]:
        """
        Get recent submissions feed for a community.

        Args:
            community_id: Community ID
            limit: Maximum number of items

        Returns:
            List of recent submissions
        """
        community_records = [
            record for key, record in self.cache["records"].items()
            if key.startswith(f"{community_id}:")
        ]

        # Sort by submission date (newest first)
        community_records.sort(key=lambda x: x["submitted_at"], reverse=True)

        return community_records[:limit]

    def get_popular_communities(self, limit: int = 5) -> List[Dict]:
        """
        Get most popular Syntheverse communities by activity.

        Args:
            limit: Maximum number of communities

        Returns:
            List of popular communities with statistics
        """
        communities_with_stats = []

        for community_id, community in self.cache["communities"].items():
            stats = self.get_community_statistics(community_id)
            communities_with_stats.append({
                **community,
                **stats
            })

        # Sort by total records (most active first)
        communities_with_stats.sort(key=lambda x: x.get("total_records", 0), reverse=True)

        return communities_with_stats[:limit]

    def discover_relevant_communities(self, keywords: List[str],
                                     limit: int = 3) -> List[Dict]:
        """
        Discover communities relevant to given keywords.

        Args:
            keywords: List of keywords to match
            limit: Maximum number of communities

        Returns:
            List of relevant communities
        """
        keyword_set = set(keywords)
        relevant_communities = []

        for community_id, community in self.cache["communities"].items():
            community_keywords = set(community["keywords"])
            overlap = len(keyword_set.intersection(community_keywords))

            if overlap > 0:
                relevant_communities.append({
                    **community,
                    "keyword_overlap": overlap,
                    "relevance_score": overlap * 25  # Simple scoring
                })

        # Sort by relevance
        relevant_communities.sort(key=lambda x: x["relevance_score"], reverse=True)

        return relevant_communities[:limit]
