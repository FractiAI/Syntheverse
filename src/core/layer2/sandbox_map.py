"""
Syntheverse Sandbox Map
Visualization system for contributions with overlap/redundancy detection.
Aids in maximizing sandbox enrichment while minimizing overlap.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from datetime import datetime
from dataclasses import dataclass, asdict

from .poc_archive import PoCArchive, ContributionStatus, MetalType


@dataclass
class ContributionNode:
    """Node in the sandbox map representing a contribution."""
    submission_hash: str
    title: str
    contributor: str
    status: str
    metals: List[str]
    coherence: Optional[float] = None
    density: Optional[float] = None
    redundancy: Optional[float] = None
    created_at: Optional[str] = None


@dataclass
class OverlapEdge:
    """Edge representing overlap/redundancy between contributions."""
    source_hash: str
    target_hash: str
    similarity_score: float
    overlap_type: str  # "exact_duplicate", "high_redundancy", "moderate_overlap", "related"


class SandboxMap:
    """
    Syntheverse Sandbox Map for visualizing contributions and detecting overlap.
    """
    
    def __init__(self, archive: PoCArchive):
        """
        Initialize sandbox map.
        
        Args:
            archive: PoC archive instance
        """
        self.archive = archive
        self.overlap_threshold_high = 0.85      # 85%+ = high redundancy
        self.overlap_threshold_moderate = 0.65  # 65-85% = moderate overlap
        self.overlap_threshold_related = 0.45   # 45-65% = related
    
    def generate_map(
        self,
        filter_status: Optional[List[ContributionStatus]] = None,
        filter_metals: Optional[List[MetalType]] = None,
        include_overlap: bool = True
    ) -> Dict:
        """
        Generate sandbox map with contributions and overlap edges.
        
        Args:
            filter_status: Only include contributions with these statuses (None = all)
            filter_metals: Only include contributions with these metals (None = all)
            include_overlap: Whether to calculate overlap edges
        
        Returns:
            Map structure with nodes and edges
        """
        # Get all contributions
        all_contributions = self.archive.get_all_contributions()
        
        # Apply filters
        nodes = []
        contribution_dict = {}
        
        for contrib in all_contributions:
            # Status filter
            if filter_status is not None:
                if ContributionStatus(contrib["status"]) not in filter_status:
                    continue
            
            # Metal filter
            if filter_metals is not None:
                contrib_metals = [MetalType(m) for m in contrib.get("metals", [])]
                if not any(m in filter_metals for m in contrib_metals):
                    continue
            
            # Create node
            node = ContributionNode(
                submission_hash=contrib["submission_hash"],
                title=contrib["title"],
                contributor=contrib["contributor"],
                status=contrib["status"],
                metals=contrib.get("metals", []),
                coherence=contrib.get("metadata", {}).get("coherence"),
                density=contrib.get("metadata", {}).get("density"),
                redundancy=contrib.get("metadata", {}).get("redundancy"),
                created_at=contrib.get("created_at"),
            )
            nodes.append(node)
            contribution_dict[contrib["submission_hash"]] = contrib
        
        # Calculate overlap edges
        edges = []
        if include_overlap:
            edges = self._calculate_overlap_edges(list(contribution_dict.values()))
        
        return {
            "nodes": [asdict(node) for node in nodes],
            "edges": [asdict(edge) for edge in edges],
            "metadata": {
                "total_nodes": len(nodes),
                "total_edges": len(edges),
                "generated_at": datetime.now().isoformat(),
            }
        }
    
    def _calculate_overlap_edges(self, contributions: List[Dict]) -> List[OverlapEdge]:
        """
        Calculate overlap/redundancy edges between contributions.
        Archive-first: Compares against ALL contributions in archive.
        
        Args:
            contributions: List of contribution records
        
        Returns:
            List of overlap edges
        """
        edges = []
        
        for i, contrib1 in enumerate(contributions):
            content_hash1 = contrib1.get("content_hash")
            if not content_hash1:
                continue
            
            # Check exact duplicates (same content hash)
            same_content = self.archive.get_content_hash_history(content_hash1)
            for contrib2 in same_content:
                hash2 = contrib2["submission_hash"]
                hash1 = contrib1["submission_hash"]
                
                if hash1 != hash2:
                    # Exact duplicate
                    edges.append(OverlapEdge(
                        source_hash=hash1,
                        target_hash=hash2,
                        similarity_score=1.0,
                        overlap_type="exact_duplicate"
                    ))
            
            # Calculate similarity with other contributions
            # For now, we use a simplified approach based on content hash
            # In production, this would use embedding similarity or more sophisticated methods
            for j, contrib2 in enumerate(contributions[i+1:], start=i+1):
                hash2 = contrib2["submission_hash"]
                hash1 = contrib1["submission_hash"]
                
                # Skip if already marked as exact duplicate
                if any(e.source_hash == hash1 and e.target_hash == hash2 and e.similarity_score == 1.0
                       for e in edges):
                    continue
                
                # Calculate similarity (simplified - based on text similarity)
                similarity = self._calculate_text_similarity(
                    contrib1.get("text_content", ""),
                    contrib2.get("text_content", "")
                )
                
                if similarity >= self.overlap_threshold_high:
                    overlap_type = "high_redundancy"
                    edges.append(OverlapEdge(
                        source_hash=hash1,
                        target_hash=hash2,
                        similarity_score=similarity,
                        overlap_type=overlap_type
                    ))
                elif similarity >= self.overlap_threshold_moderate:
                    overlap_type = "moderate_overlap"
                    edges.append(OverlapEdge(
                        source_hash=hash1,
                        target_hash=hash2,
                        similarity_score=similarity,
                        overlap_type=overlap_type
                    ))
                elif similarity >= self.overlap_threshold_related:
                    overlap_type = "related"
                    edges.append(OverlapEdge(
                        source_hash=hash1,
                        target_hash=hash2,
                        similarity_score=similarity,
                        overlap_type=overlap_type
                    ))
        
        return edges
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate text similarity score (0.0 to 1.0).
        Simplified implementation - in production, use embeddings or advanced NLP.
        
        Args:
            text1: First text
            text2: Second text
        
        Returns:
            Similarity score between 0.0 and 1.0
        """
        if not text1 or not text2:
            return 0.0
        
        # Normalize texts
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        # Jaccard similarity (word overlap)
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    def get_redundancy_report(self, submission_hash: str) -> Dict:
        """
        Get redundancy report for a specific contribution.
        Archive-first: Checks against entire archive.
        
        Args:
            submission_hash: Submission to check
        
        Returns:
            Redundancy report with similar contributions
        """
        contrib = self.archive.get_contribution(submission_hash)
        if not contrib:
            return {"error": "Contribution not found"}
        
        # Get all contributions for comparison
        all_contribs = self.archive.get_all_content_for_redundancy_check()
        
        similarities = []
        for other_contrib in all_contribs:
            if other_contrib["submission_hash"] == submission_hash:
                continue
            
            similarity = self._calculate_text_similarity(
                contrib.get("text_content", ""),
                other_contrib.get("text_content", "")
            )
            
            if similarity > 0.3:  # Only report if > 30% similar
                similarities.append({
                    "submission_hash": other_contrib["submission_hash"],
                    "title": other_contrib["title"],
                    "contributor": other_contrib["contributor"],
                    "status": other_contrib["status"],
                    "similarity_score": similarity,
                    "overlap_type": self._classify_overlap_type(similarity),
                })
        
        # Sort by similarity
        similarities.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        return {
            "submission_hash": submission_hash,
            "title": contrib["title"],
            "total_similar": len(similarities),
            "high_redundancy": len([s for s in similarities if s["similarity_score"] >= self.overlap_threshold_high]),
            "moderate_overlap": len([s for s in similarities 
                                    if self.overlap_threshold_moderate <= s["similarity_score"] < self.overlap_threshold_high]),
            "related": len([s for s in similarities 
                           if self.overlap_threshold_related <= s["similarity_score"] < self.overlap_threshold_moderate]),
            "similar_contributions": similarities[:20],  # Top 20 most similar
        }
    
    def _classify_overlap_type(self, similarity: float) -> str:
        """Classify overlap type based on similarity score."""
        if similarity >= self.overlap_threshold_high:
            return "high_redundancy"
        elif similarity >= self.overlap_threshold_moderate:
            return "moderate_overlap"
        elif similarity >= self.overlap_threshold_related:
            return "related"
        else:
            return "low_overlap"
    
    def get_metal_distribution(self) -> Dict:
        """
        Get distribution of metals across the sandbox.
        
        Returns:
            Metal distribution statistics
        """
        all_contribs = self.archive.get_all_contributions()
        
        metal_counts = {
            MetalType.GOLD.value: 0,
            MetalType.SILVER.value: 0,
            MetalType.COPPER.value: 0,
        }
        
        metal_combinations = {}
        
        for contrib in all_contribs:
            metals = contrib.get("metals", [])
            if not metals:
                continue
            
            # Count individual metals
            for metal in metals:
                if metal in metal_counts:
                    metal_counts[metal] += 1
            
            # Count combinations
            metal_key = "+".join(sorted(metals))
            metal_combinations[metal_key] = metal_combinations.get(metal_key, 0) + 1
        
        return {
            "individual_metals": metal_counts,
            "metal_combinations": metal_combinations,
            "total_contributions_with_metals": sum(metal_counts.values()),
        }
    
    def get_contributor_network(self) -> Dict:
        """
        Get contributor collaboration network.
        
        Returns:
            Network structure showing contributor connections
        """
        all_contribs = self.archive.get_all_contributions()
        
        contributor_contributions = {}
        contributor_metals = {}
        
        for contrib in all_contribs:
            contributor = contrib["contributor"]
            metals = contrib.get("metals", [])
            
            if contributor not in contributor_contributions:
                contributor_contributions[contributor] = []
                contributor_metals[contributor] = set()
            
            contributor_contributions[contributor].append(contrib["submission_hash"])
            contributor_metals[contributor].update(metals)
        
        return {
            "contributors": {
                contrib: {
                    "total_contributions": len(hashes),
                    "metals": list(contributor_metals[contrib]),
                    "contribution_hashes": hashes,
                }
                for contrib, hashes in contributor_contributions.items()
            },
            "total_contributors": len(contributor_contributions),
        }
    
    def export_map_for_visualization(self, output_file: Optional[str] = None) -> Dict:
        """
        Export map in format suitable for web visualization.
        
        Args:
            output_file: Optional file path to save JSON
        
        Returns:
            Map data structure
        """
        map_data = self.generate_map(include_overlap=True)
        
        # Add additional metadata for visualization
        map_data["statistics"] = {
            "archive_stats": self.archive.get_statistics(),
            "metal_distribution": self.get_metal_distribution(),
            "contributor_network": self.get_contributor_network(),
        }
        
        # Save to file if requested
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                json.dump(map_data, f, indent=2)
        
        return map_data
