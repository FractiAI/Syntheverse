"""
Proof of Contribution (PoC) Archive System
Archive-first evaluation: Stores ALL contributions regardless of status.
This is the system's cognitive memory for redundancy detection.
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime
from enum import Enum


class ContributionStatus(Enum):
    """Contribution lifecycle status."""
    DRAFT = "draft"                    # Initial submission, not yet evaluated
    PENDING = "pending"                # Submitted for evaluation, waiting to be processed
    EVALUATING = "evaluating"          # Currently being evaluated
    QUALIFIED = "qualified"            # Passed evaluation, eligible for allocation
    UNQUALIFIED = "unqualified"        # Failed evaluation thresholds
    ARCHIVED = "archived"              # Archived/superseded
    SUPERSEDED = "superseded"          # Superseded by newer version


class MetalType(Enum):
    """Contribution metal types (can be multiple per contribution)."""
    GOLD = "gold"          # Discovery/Scientific
    SILVER = "silver"      # Technology
    COPPER = "copper"      # Alignment


class PoCArchive:
    """
    Persistent archive of ALL contributions.
    Archive-first rule: All redundancy checks operate over entire archive.
    """
    
    def __init__(self, archive_file: str = "test_outputs/poc_archive.json"):
        """
        Initialize PoC archive.
        
        Args:
            archive_file: Path to archive JSON file
        """
        self.archive_file = Path(archive_file)
        self.archive_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Archive structure
        self.archive = {
            "contributions": {},        # submission_hash -> contribution record
            "content_hashes": {},       # content_hash -> list of submission_hashes
            "by_status": {},            # status -> list of submission_hashes
            "by_contributor": {},       # contributor -> list of submission_hashes
            "by_metal": {               # metal -> list of submission_hashes
                MetalType.GOLD.value: [],
                MetalType.SILVER.value: [],
                MetalType.COPPER.value: [],
            },
            "metadata": {
                "total_contributions": 0,
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
            }
        }
        
        # Load existing archive
        self.load_archive()
    
    def load_archive(self):
        """Load archive from file."""
        if self.archive_file.exists():
            try:
                with open(self.archive_file, "r") as f:
                    loaded = json.load(f)
                    self.archive.update(loaded)
                    # Ensure all required fields exist
                    if "contributions" not in self.archive:
                        self.archive["contributions"] = {}
                    if "content_hashes" not in self.archive:
                        self.archive["content_hashes"] = {}
                    if "by_status" not in self.archive:
                        self.archive["by_status"] = {}
                    if "by_contributor" not in self.archive:
                        self.archive["by_contributor"] = {}
                    if "by_metal" not in self.archive:
                        self.archive["by_metal"] = {
                            MetalType.GOLD.value: [],
                            MetalType.SILVER.value: [],
                            MetalType.COPPER.value: [],
                        }
            except Exception as e:
                print(f"Warning: Failed to load archive: {e}")

    @property
    def contributions(self):
        """Convenience property for accessing contributions."""
        return self.archive["contributions"]
    
    def save_archive(self):
        """Save archive to file."""
        self.archive["metadata"]["last_updated"] = datetime.now().isoformat()
        self.archive["metadata"]["total_contributions"] = len(self.archive["contributions"])

        # Custom JSON encoder to handle enums
        def json_encoder(obj):
            if hasattr(obj, 'value'):  # Enum with value attribute
                return obj.value
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

        try:
            with open(self.archive_file, "w") as f:
                json.dump(self.archive, f, indent=2, default=json_encoder)
        except Exception as e:
            print(f"Error saving archive: {e}")
    
    def calculate_content_hash(self, text: str) -> str:
        """Calculate normalized content hash."""
        # Normalize: lowercase, remove extra whitespace
        normalized = " ".join(text.lower().split())
        return hashlib.sha256(normalized.encode()).hexdigest()
    
    def add_contribution(
        self,
        submission_hash: str,
        title: str,
        contributor: str,
        text_content: str,
        status: ContributionStatus = ContributionStatus.DRAFT,
        category: Optional[str] = None,
        metals: Optional[List[MetalType]] = None,
        metadata: Optional[Dict] = None,
        is_test: bool = False
    ) -> Dict:
        """
        Add a contribution to the archive.
        Archive-first rule: ALL contributions are stored regardless of status.

        Args:
            submission_hash: Unique submission identifier
            title: Contribution title
            contributor: Contributor identifier
            text_content: Full text content for redundancy checking
            status: Current lifecycle status
            category: Category (scientific/tech/alignment)
            metals: List of metal types this contribution contains
            metadata: Additional metadata (evaluation results, scores, etc.)
            is_test: Whether this is a test submission (marked for cleanup)

        Returns:
            Contribution record
        """
        # Calculate content hash
        content_hash = self.calculate_content_hash(text_content)
        
        # Initialize metals if not provided (infer from category)
        if metals is None:
            metals = self._infer_metals_from_category(category)
        
        # Create contribution record
        contribution = {
            "submission_hash": submission_hash,
            "title": title,
            "contributor": contributor,
            "content_hash": content_hash,
            "text_content": text_content,  # Store full content for redundancy checks
            "status": status.value,
            "category": category,
            "metals": [m.value for m in metals],
            "metadata": metadata or {},
            "is_test": is_test,  # Mark for automatic cleanup
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        
        # Add to archive
        self.archive["contributions"][submission_hash] = contribution
        
        # Update indexes
        self._update_content_hash_index(content_hash, submission_hash)
        self._update_status_index(status.value, submission_hash)
        self._update_contributor_index(contributor, submission_hash)
        self._update_metal_index(metals, submission_hash)
        
        # Save archive
        self.save_archive()
        
        return contribution
    
    def update_contribution(
        self,
        submission_hash: str,
        status: Optional[ContributionStatus] = None,
        metals: Optional[List[MetalType]] = None,
        metadata: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Update an existing contribution.
        
        Args:
            submission_hash: Submission identifier
            status: New status (if updating)
            metals: New metals (if updating)
            metadata: Metadata to merge (if updating)
        
        Returns:
            Updated contribution or None if not found
        """
        if submission_hash not in self.archive["contributions"]:
            return None
        
        contribution = self.archive["contributions"][submission_hash]
        old_status = contribution["status"]
        
        # Update status if provided
        if status is not None:
            # Remove from old status index
            if old_status in self.archive["by_status"]:
                if submission_hash in self.archive["by_status"][old_status]:
                    self.archive["by_status"][old_status].remove(submission_hash)
            
            # Update status
            contribution["status"] = status.value
            self._update_status_index(status.value, submission_hash)
        
        # Update metals if provided
        if metals is not None:
            # Remove from old metal indexes
            old_metals = contribution["metals"]
            for metal in old_metals:
                if metal in self.archive["by_metal"] and submission_hash in self.archive["by_metal"][metal]:
                    self.archive["by_metal"][metal].remove(submission_hash)
            
            # Update metals
            contribution["metals"] = [m.value for m in metals]
            self._update_metal_index(metals, submission_hash)
        
        # Update metadata if provided
        if metadata is not None:
            contribution["metadata"].update(metadata)
        
        contribution["updated_at"] = datetime.now().isoformat()
        
        # Save archive
        self.save_archive()
        
        return contribution
    
    def get_contribution(self, submission_hash: str) -> Optional[Dict]:
        """Get a contribution by submission hash."""
        return self.archive["contributions"].get(submission_hash)
    
    def get_all_contributions(
        self,
        status: Optional[ContributionStatus] = None,
        contributor: Optional[str] = None,
        metal: Optional[MetalType] = None
    ) -> List[Dict]:
        """
        Get all contributions with optional filters.
        Archive-first: Returns ALL contributions matching criteria, regardless of registration status.
        
        Args:
            status: Filter by status
            contributor: Filter by contributor
            metal: Filter by metal type
        
        Returns:
            List of contribution records
        """
        hashes = set(self.archive["contributions"].keys())
        
        # Apply filters
        if status is not None:
            status_hashes = set(self.archive["by_status"].get(status.value, []))
            hashes &= status_hashes
        
        if contributor is not None:
            contributor_hashes = set(self.archive["by_contributor"].get(contributor, []))
            hashes &= contributor_hashes
        
        if metal is not None:
            metal_hashes = set(self.archive["by_metal"].get(metal.value, []))
            hashes &= metal_hashes
        
        return [self.archive["contributions"][h] for h in hashes]

    def get_contributor_submission_count(self, contributor: str) -> int:
        """
        Get the number of submissions by a contributor.

        Args:
            contributor: Contributor address/hash

        Returns:
            Number of submissions by this contributor
        """
        return len(self.archive["by_contributor"].get(contributor, []))

    def get_content_hash_history(self, content_hash: str) -> List[Dict]:
        """
        Get all contributions with the same content hash.
        Used for duplicate detection across entire archive.
        
        Args:
            content_hash: Content hash to search for
        
        Returns:
            List of contributions with matching content hash
        """
        submission_hashes = self.archive["content_hashes"].get(content_hash, [])
        return [self.archive["contributions"][h] for h in submission_hashes if h in self.archive["contributions"]]
    
    def get_all_content_for_redundancy_check(self) -> List[Dict]:
        """
        Get ALL contributions for redundancy checking.
        Archive-first rule: Includes drafts, unqualified, archived, historical.
        
        Returns:
            List of all contributions with their content
        """
        return list(self.archive["contributions"].values())
    
    def _infer_metals_from_category(self, category: Optional[str]) -> List[MetalType]:
        """Infer metal types from category."""
        if not category:
            return []
        
        category_lower = category.lower()
        metals = []
        
        if category_lower in ["scientific", "science", "research", "discovery"]:
            metals.append(MetalType.GOLD)
        if category_lower in ["tech", "technology", "technical", "engineering"]:
            metals.append(MetalType.SILVER)
        if category_lower in ["alignment", "ai-alignment", "safety"]:
            metals.append(MetalType.COPPER)
        
        return metals if metals else [MetalType.GOLD]  # Default to Gold if no match
    
    def _update_content_hash_index(self, content_hash: str, submission_hash: str):
        """Update content hash index."""
        if content_hash not in self.archive["content_hashes"]:
            self.archive["content_hashes"][content_hash] = []
        if submission_hash not in self.archive["content_hashes"][content_hash]:
            self.archive["content_hashes"][content_hash].append(submission_hash)
    
    def _update_status_index(self, status: str, submission_hash: str):
        """Update status index."""
        if status not in self.archive["by_status"]:
            self.archive["by_status"][status] = []
        if submission_hash not in self.archive["by_status"][status]:
            self.archive["by_status"][status].append(submission_hash)
    
    def _update_contributor_index(self, contributor: str, submission_hash: str):
        """Update contributor index."""
        if contributor not in self.archive["by_contributor"]:
            self.archive["by_contributor"][contributor] = []
        if submission_hash not in self.archive["by_contributor"][contributor]:
            self.archive["by_contributor"][contributor].append(submission_hash)
    
    def _update_metal_index(self, metals: List[MetalType], submission_hash: str):
        """Update metal index."""
        for metal in metals:
            metal_key = metal.value
            if metal_key not in self.archive["by_metal"]:
                self.archive["by_metal"][metal_key] = []
            if submission_hash not in self.archive["by_metal"][metal_key]:
                self.archive["by_metal"][metal_key].append(submission_hash)
    
    def get_statistics(self) -> Dict:
        """Get archive statistics."""
        status_counts = {
            status.value: len(self.archive["by_status"].get(status.value, []))
            for status in ContributionStatus
        }
        
        metal_counts = {
            metal.value: len(self.archive["by_metal"].get(metal.value, []))
            for metal in MetalType
        }
        
        return {
            "total_contributions": len(self.archive["contributions"]),
            "status_counts": status_counts,
            "metal_counts": metal_counts,
            "unique_contributors": len(self.archive["by_contributor"]),
            "unique_content_hashes": len(self.archive["content_hashes"]),
            "last_updated": self.archive["metadata"]["last_updated"],
        }
