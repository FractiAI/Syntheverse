"""
Similarity Analyzer - Advanced similarity analysis for embeddings.

Computes pairwise similarities, finds most/least similar pairs,
analyzes similarity distributions, and detects duplicates.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict

from .logger import get_logger


class SimilarityAnalyzer:
    """
    Advanced similarity analysis for embedding datasets.

    Provides comprehensive similarity computations, distribution analysis,
    duplicate detection, and similarity-based insights.
    """

    def __init__(self, logger=None):
        """
        Initialize similarity analyzer.

        Args:
            logger: Optional logger instance
        """
        self.logger = logger or get_logger(__name__)

    def get_similarity_summary(self, embeddings_data: List[Dict],
                             max_samples: int = 5000) -> Dict[str, Any]:
        """
        Generate comprehensive similarity summary.

        Args:
            embeddings_data: List of embedding dictionaries
            max_samples: Maximum number of samples for analysis

        Returns:
            Comprehensive similarity analysis results
        """
        self.logger.info(f"Computing similarity summary for {len(embeddings_data)} embeddings")

        # Sample if needed
        if len(embeddings_data) > max_samples:
            from .utils import sample_embeddings
            analysis_data = sample_embeddings(embeddings_data, max_samples, random_state=42)
            self.logger.info(f"Sampled to {len(analysis_data)} embeddings for analysis")
        else:
            analysis_data = embeddings_data

        results = {
            'total_embeddings': len(embeddings_data),
            'analyzed_embeddings': len(analysis_data)
        }

        # Compute pairwise similarities
        similarity_matrix = self.compute_pairwise_similarities(analysis_data)
        results['similarity_matrix_shape'] = similarity_matrix.shape

        # Analyze similarity distribution
        dist_analysis = self.analyze_similarity_distribution(similarity_matrix)
        results['distribution'] = dist_analysis

        # Find most and least similar pairs
        most_similar = self.find_most_similar(analysis_data, similarity_matrix, top_k=20)
        least_similar = self.find_least_similar(analysis_data, similarity_matrix, top_k=20)
        results['most_similar_pairs'] = most_similar
        results['least_similar_pairs'] = least_similar

        # Detect duplicates
        duplicates = self.detect_duplicates(analysis_data, similarity_matrix, threshold=0.98)
        results['duplicates'] = duplicates

        # Similarity categories
        categories = self.categorize_similarities(similarity_matrix)
        results['similarity_categories'] = categories

        self.logger.info("Similarity analysis completed")
        return results

    def compute_pairwise_similarities(self, embeddings_data: List[Dict]) -> np.ndarray:
        """
        Compute pairwise cosine similarities between all embeddings.

        Args:
            embeddings_data: List of embedding dictionaries

        Returns:
            Symmetric similarity matrix
        """
        from .utils import compute_pairwise_cosine_similarity, extract_embeddings_array

        embeddings = extract_embeddings_array(embeddings_data)

        if embeddings.size == 0:
            raise ValueError("No valid embeddings found")

        self.logger.info(f"Computing pairwise similarities for {len(embeddings)} embeddings")

        similarity_matrix = compute_pairwise_cosine_similarity(embeddings)

        return similarity_matrix

    def analyze_similarity_distribution(self, similarity_matrix: np.ndarray) -> Dict[str, Any]:
        """
        Analyze the distribution of similarity values.

        Args:
            similarity_matrix: Pairwise similarity matrix

        Returns:
            Distribution analysis results
        """
        # Extract upper triangle (excluding diagonal)
        n = similarity_matrix.shape[0]
        upper_tri = similarity_matrix[np.triu_indices(n, k=1)]

        if len(upper_tri) == 0:
            return {'error': 'No similarity pairs to analyze'}

        # Basic statistics
        analysis = {
            'count': len(upper_tri),
            'mean': float(np.mean(upper_tri)),
            'std': float(np.std(upper_tri)),
            'min': float(np.min(upper_tri)),
            'max': float(np.max(upper_tri)),
            'median': float(np.median(upper_tri))
        }

        # Percentiles
        percentiles = [10, 25, 75, 90, 95, 99]
        analysis['percentiles'] = {
            f'p{int(p)}': float(np.percentile(upper_tri, p)) for p in percentiles
        }

        # Distribution categories
        very_high = np.sum(upper_tri > 0.9)
        high = np.sum((upper_tri > 0.7) & (upper_tri <= 0.9))
        medium = np.sum((upper_tri > 0.3) & (upper_tri <= 0.7))
        low = np.sum((upper_tri > 0.1) & (upper_tri <= 0.3))
        very_low = np.sum(upper_tri <= 0.1)

        analysis['categories'] = {
            'very_high (>0.9)': int(very_high),
            'high (0.7-0.9)': int(high),
            'medium (0.3-0.7)': int(medium),
            'low (0.1-0.3)': int(low),
            'very_low (≤0.1)': int(very_low)
        }

        # Category percentages
        total_pairs = len(upper_tri)
        analysis['category_percentages'] = {
            k: (v / total_pairs) * 100 for k, v in analysis['categories'].items()
        }

        return analysis

    def find_most_similar(self, embeddings_data: List[Dict],
                         similarity_matrix: Optional[np.ndarray] = None,
                         top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Find the most similar pairs of embeddings.

        Args:
            embeddings_data: List of embedding dictionaries
            similarity_matrix: Pre-computed similarity matrix (optional)
            top_k: Number of top pairs to return

        Returns:
            List of most similar pairs with metadata
        """
        if similarity_matrix is None:
            similarity_matrix = self.compute_pairwise_similarities(embeddings_data)

        n = similarity_matrix.shape[0]

        # Get upper triangle indices and similarities
        triu_indices = np.triu_indices(n, k=1)
        similarities = similarity_matrix[triu_indices]

        # Get top k most similar
        top_indices = np.argsort(similarities)[::-1][:top_k]

        most_similar = []
        for idx in top_indices:
            i, j = triu_indices[0][idx], triu_indices[1][idx]
            similarity = float(similarities[idx])

            pair_info = {
                'similarity': similarity,
                'chunk_1': {
                    'index': int(i),
                    'text_preview': embeddings_data[i].get('text', '')[:100] + '...',
                    'pdf_filename': embeddings_data[i].get('pdf_filename', 'unknown'),
                    'chunk_index': embeddings_data[i].get('chunk_index', 0)
                },
                'chunk_2': {
                    'index': int(j),
                    'text_preview': embeddings_data[j].get('text', '')[:100] + '...',
                    'pdf_filename': embeddings_data[j].get('pdf_filename', 'unknown'),
                    'chunk_index': embeddings_data[j].get('chunk_index', 0)
                }
            }
            most_similar.append(pair_info)

        return most_similar

    def find_least_similar(self, embeddings_data: List[Dict],
                          similarity_matrix: Optional[np.ndarray] = None,
                          top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Find the least similar pairs of embeddings.

        Args:
            embeddings_data: List of embedding dictionaries
            similarity_matrix: Pre-computed similarity matrix (optional)
            top_k: Number of top pairs to return

        Returns:
            List of least similar pairs with metadata
        """
        if similarity_matrix is None:
            similarity_matrix = self.compute_pairwise_similarities(embeddings_data)

        n = similarity_matrix.shape[0]

        # Get upper triangle indices and similarities
        triu_indices = np.triu_indices(n, k=1)
        similarities = similarity_matrix[triu_indices]

        # Get top k least similar
        bottom_indices = np.argsort(similarities)[:top_k]

        least_similar = []
        for idx in bottom_indices:
            i, j = triu_indices[0][idx], triu_indices[1][idx]
            similarity = float(similarities[idx])

            pair_info = {
                'similarity': similarity,
                'chunk_1': {
                    'index': int(i),
                    'text_preview': embeddings_data[i].get('text', '')[:100] + '...',
                    'pdf_filename': embeddings_data[i].get('pdf_filename', 'unknown'),
                    'chunk_index': embeddings_data[i].get('chunk_index', 0)
                },
                'chunk_2': {
                    'index': int(j),
                    'text_preview': embeddings_data[j].get('text', '')[:100] + '...',
                    'pdf_filename': embeddings_data[j].get('pdf_filename', 'unknown'),
                    'chunk_index': embeddings_data[j].get('chunk_index', 0)
                }
            }
            least_similar.append(pair_info)

        return least_similar

    def detect_duplicates(self, embeddings_data: List[Dict],
                         similarity_matrix: Optional[np.ndarray] = None,
                         threshold: float = 0.98) -> Dict[str, Any]:
        """
        Detect near-duplicate embeddings based on similarity threshold.

        Args:
            embeddings_data: List of embedding dictionaries
            similarity_matrix: Pre-computed similarity matrix (optional)
            threshold: Similarity threshold for duplicate detection

        Returns:
            Duplicate detection results
        """
        if similarity_matrix is None:
            similarity_matrix = self.compute_pairwise_similarities(embeddings_data)

        n = similarity_matrix.shape[0]

        # Find pairs above threshold
        triu_indices = np.triu_indices(n, k=1)
        similarities = similarity_matrix[triu_indices]

        duplicate_mask = similarities >= threshold
        duplicate_pairs = np.where(duplicate_mask)[0]

        duplicates = []
        for pair_idx in duplicate_pairs:
            i, j = triu_indices[0][pair_idx], triu_indices[1][pair_idx]
            similarity = float(similarities[pair_idx])

            duplicate_info = {
                'similarity': similarity,
                'chunk_1': {
                    'index': int(i),
                    'text_length': len(embeddings_data[i].get('text', '')),
                    'pdf_filename': embeddings_data[i].get('pdf_filename', 'unknown')
                },
                'chunk_2': {
                    'index': int(j),
                    'text_length': len(embeddings_data[j].get('text', '')),
                    'pdf_filename': embeddings_data[j].get('pdf_filename', 'unknown')
                }
            }
            duplicates.append(duplicate_info)

        return {
            'duplicate_pairs': duplicates,
            'total_duplicates': len(duplicates),
            'threshold': threshold,
            'duplicate_percentage': (len(duplicates) / max(1, n * (n-1) / 2)) * 100
        }

    def categorize_similarities(self, similarity_matrix: np.ndarray) -> Dict[str, Any]:
        """
        Categorize similarities into meaningful ranges.

        Args:
            similarity_matrix: Pairwise similarity matrix

        Returns:
            Similarity categorization results
        """
        # Extract upper triangle
        n = similarity_matrix.shape[0]
        upper_tri = similarity_matrix[np.triu_indices(n, k=1)]

        if len(upper_tri) == 0:
            return {'error': 'No similarities to categorize'}

        # Define categories
        categories = {
            'very_high': (0.9, 1.0),
            'high': (0.7, 0.9),
            'medium': (0.3, 0.7),
            'low': (0.1, 0.3),
            'very_low': (-1.0, 0.1)
        }

        results = {}
        for cat_name, (min_val, max_val) in categories.items():
            count = np.sum((upper_tri > min_val) & (upper_tri <= max_val))
            percentage = (count / len(upper_tri)) * 100

            results[cat_name] = {
                'count': int(count),
                'percentage': float(percentage),
                'range': f'{min_val:.1f} to {max_val:.1f}'
            }

        return results

    def get_similarity_clusters(self, embeddings_data: List[Dict],
                              similarity_matrix: Optional[np.ndarray] = None,
                              threshold: float = 0.8) -> Dict[str, Any]:
        """
        Find clusters of similar embeddings.

        Args:
            embeddings_data: List of embedding dictionaries
            similarity_matrix: Pre-computed similarity matrix (optional)
            threshold: Similarity threshold for clustering

        Returns:
            Similarity-based clustering results
        """
        if similarity_matrix is None:
            similarity_matrix = self.compute_pairwise_similarities(embeddings_data)

        n = similarity_matrix.shape[0]

        # Simple connected components clustering based on similarity threshold
        clusters = []
        visited = set()

        for i in range(n):
            if i in visited:
                continue

            # Find all embeddings similar to this one
            cluster = {i}
            stack = [i]

            while stack:
                current = stack.pop()
                if current in visited:
                    continue

                visited.add(current)

                # Find neighbors above threshold
                neighbors = np.where(similarity_matrix[current] >= threshold)[0]
                for neighbor in neighbors:
                    if neighbor not in visited and neighbor not in cluster:
                        cluster.add(neighbor)
                        stack.append(neighbor)

            if len(cluster) > 1:  # Only include clusters with multiple items
                clusters.append(cluster)

        # Convert to more readable format
        cluster_info = []
        for i, cluster in enumerate(clusters):
            cluster_items = []
            for idx in cluster:
                item_info = {
                    'index': int(idx),
                    'pdf_filename': embeddings_data[idx].get('pdf_filename', 'unknown'),
                    'chunk_index': embeddings_data[idx].get('chunk_index', 0),
                    'text_length': len(embeddings_data[idx].get('text', ''))
                }
                cluster_items.append(item_info)

            cluster_info.append({
                'cluster_id': i,
                'size': len(cluster),
                'items': cluster_items
            })

        return {
            'total_clusters': len(clusters),
            'clusters': cluster_info,
            'threshold': threshold,
            'singletons': n - sum(len(c) for c in clusters)
        }