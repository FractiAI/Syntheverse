"""
Similarity Analyzer - Advanced similarity analysis for embeddings.

Provides tools for computing pairwise similarities, finding semantic relationships,
analyzing similarity distributions, and detecting duplicate content.
"""

import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
from collections import defaultdict

from .logger import get_logger
from .utils import extract_embeddings_array, compute_pairwise_cosine_similarity


class SimilarityAnalyzer:
    """
    Advanced similarity analysis for embedding collections.

    Computes pairwise similarities, analyzes distributions, finds semantic relationships,
    and detects duplicate or near-duplicate content.
    """

    def __init__(self, logger=None):
        """
        Initialize similarity analyzer.

        Args:
            logger: Optional logger instance
        """
        self.logger = logger or get_logger(__name__)

    def compute_pairwise_similarities(self, embeddings_data: List[Dict],
                                    batch_size: int = 1000) -> np.ndarray:
        """
        Compute pairwise cosine similarities for all embeddings.

        Args:
            embeddings_data: List of embedding dictionaries
            batch_size: Batch size for memory-efficient computation

        Returns:
            Similarity matrix of shape (n_embeddings, n_embeddings)
        """
        if not embeddings_data:
            raise ValueError("No embeddings provided")

        embeddings_array = extract_embeddings_array(embeddings_data)
        n_embeddings = len(embeddings_array)

        self.logger.info(f"Computing pairwise similarities for {n_embeddings} embeddings")

        if n_embeddings <= batch_size:
            # Compute all at once for smaller datasets
            similarity_matrix = compute_pairwise_cosine_similarity(embeddings_array)
        else:
            # Batch computation for large datasets
            self.logger.info(f"Using batched computation with batch_size={batch_size}")

            similarity_matrix = np.zeros((n_embeddings, n_embeddings))

            for i in range(0, n_embeddings, batch_size):
                end_i = min(i + batch_size, n_embeddings)
                batch_i = embeddings_array[i:end_i]

                # Normalize batch
                norms_i = np.linalg.norm(batch_i, axis=1, keepdims=True)
                norms_i[norms_i == 0] = 1
                normalized_i = batch_i / norms_i

                for j in range(0, n_embeddings, batch_size):
                    end_j = min(j + batch_size, n_embeddings)
                    batch_j = embeddings_array[j:end_j]

                    # Normalize batch_j
                    norms_j = np.linalg.norm(batch_j, axis=1, keepdims=True)
                    norms_j[norms_j == 0] = 1
                    normalized_j = batch_j / norms_j

                    # Compute similarities for this block
                    block_similarities = np.dot(normalized_i, normalized_j.T)
                    similarity_matrix[i:end_i, j:end_j] = block_similarities

                    if j % (batch_size * 10) == 0:
                        progress = (i * n_embeddings + j * batch_size) / (n_embeddings * n_embeddings)
                        self.logger.debug(".1%")

        # Ensure diagonal is 1.0
        np.fill_diagonal(similarity_matrix, 1.0)

        self.logger.info("Pairwise similarity computation completed")
        return similarity_matrix

    def find_most_similar(self, embeddings_data: List[Dict],
                         top_k: int = 10,
                         similarity_matrix: Optional[np.ndarray] = None) -> List[Dict[str, Any]]:
        """
        Find the most similar pairs of embeddings.

        Args:
            embeddings_data: List of embedding dictionaries
            top_k: Number of top similar pairs to return
            similarity_matrix: Pre-computed similarity matrix (optional)

        Returns:
            List of most similar pairs with metadata
        """
        if not embeddings_data or len(embeddings_data) < 2:
            return []

        if similarity_matrix is None:
            similarity_matrix = self.compute_pairwise_similarities(embeddings_data)

        n_embeddings = len(embeddings_data)
        self.logger.info(f"Finding top {top_k} most similar pairs")

        # Get upper triangle (excluding diagonal)
        triu_indices = np.triu_indices(n_embeddings, k=1)
        similarities = similarity_matrix[triu_indices]

        # Find top k similarities
        top_indices = np.argsort(similarities)[::-1][:top_k]
        top_similarities = similarities[top_indices]

        most_similar_pairs = []
        for idx, sim in zip(top_indices, top_similarities):
            i, j = triu_indices[0][idx], triu_indices[1][idx]

            pair_info = {
                'index_1': int(i),
                'index_2': int(j),
                'similarity': float(sim),
                'chunk_1': {
                    'text_preview': embeddings_data[i]['text'][:100] + '...' if len(embeddings_data[i]['text']) > 100 else embeddings_data[i]['text'],
                    'pdf_filename': embeddings_data[i].get('pdf_filename', 'unknown'),
                    'chunk_index': embeddings_data[i].get('chunk_index', 0)
                },
                'chunk_2': {
                    'text_preview': embeddings_data[j]['text'][:100] + '...' if len(embeddings_data[j]['text']) > 100 else embeddings_data[j]['text'],
                    'pdf_filename': embeddings_data[j].get('pdf_filename', 'unknown'),
                    'chunk_index': embeddings_data[j].get('chunk_index', 0)
                }
            }
            most_similar_pairs.append(pair_info)

        self.logger.info(f"Found {len(most_similar_pairs)} most similar pairs")
        return most_similar_pairs

    def find_least_similar(self, embeddings_data: List[Dict],
                          top_k: int = 10,
                          similarity_matrix: Optional[np.ndarray] = None) -> List[Dict[str, Any]]:
        """
        Find the least similar pairs of embeddings.

        Args:
            embeddings_data: List of embedding dictionaries
            top_k: Number of top dissimilar pairs to return
            similarity_matrix: Pre-computed similarity matrix (optional)

        Returns:
            List of least similar pairs with metadata
        """
        if not embeddings_data or len(embeddings_data) < 2:
            return []

        if similarity_matrix is None:
            similarity_matrix = self.compute_pairwise_similarities(embeddings_data)

        n_embeddings = len(embeddings_data)
        self.logger.info(f"Finding top {top_k} least similar pairs")

        # Get upper triangle (excluding diagonal)
        triu_indices = np.triu_indices(n_embeddings, k=1)
        similarities = similarity_matrix[triu_indices]

        # Find bottom k similarities (most dissimilar)
        bottom_indices = np.argsort(similarities)[:top_k]
        bottom_similarities = similarities[bottom_indices]

        least_similar_pairs = []
        for idx, sim in zip(bottom_indices, bottom_similarities):
            i, j = triu_indices[0][idx], triu_indices[1][idx]

            pair_info = {
                'index_1': int(i),
                'index_2': int(j),
                'similarity': float(sim),
                'chunk_1': {
                    'text_preview': embeddings_data[i]['text'][:100] + '...' if len(embeddings_data[i]['text']) > 100 else embeddings_data[i]['text'],
                    'pdf_filename': embeddings_data[i].get('pdf_filename', 'unknown'),
                    'chunk_index': embeddings_data[i].get('chunk_index', 0)
                },
                'chunk_2': {
                    'text_preview': embeddings_data[j]['text'][:100] + '...' if len(embeddings_data[j]['text']) > 100 else embeddings_data[j]['text'],
                    'pdf_filename': embeddings_data[j].get('pdf_filename', 'unknown'),
                    'chunk_index': embeddings_data[j].get('chunk_index', 0)
                }
            }
            least_similar_pairs.append(pair_info)

        self.logger.info(f"Found {len(least_similar_pairs)} least similar pairs")
        return least_similar_pairs

    def analyze_similarity_distribution(self, embeddings_data: List[Dict],
                                     similarity_matrix: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        Analyze the distribution of pairwise similarities.

        Args:
            embeddings_data: List of embedding dictionaries
            similarity_matrix: Pre-computed similarity matrix (optional)

        Returns:
            Statistical analysis of similarity distribution
        """
        if not embeddings_data or len(embeddings_data) < 2:
            return {'error': 'Need at least 2 embeddings for distribution analysis'}

        if similarity_matrix is None:
            similarity_matrix = self.compute_pairwise_similarities(embeddings_data)

        self.logger.info("Analyzing similarity distribution")

        # Get upper triangle values (excluding diagonal)
        n_embeddings = len(embeddings_data)
        triu_indices = np.triu_indices(n_embeddings, k=1)
        similarities = similarity_matrix[triu_indices]

        # Compute statistics
        mean_sim = float(np.mean(similarities))
        std_sim = float(np.std(similarities))
        min_sim = float(np.min(similarities))
        max_sim = float(np.max(similarities))
        median_sim = float(np.median(similarities))

        # Percentiles
        percentiles = [10, 25, 75, 90, 95, 99]
        percentile_values = np.percentile(similarities, percentiles)

        # Distribution shape analysis
        skewness = float(self._compute_skewness(similarities))
        kurtosis = float(self._compute_kurtosis(similarities))

        # Categorize similarities
        very_high_sim = np.sum(similarities > 0.9)
        high_sim = np.sum((similarities > 0.7) & (similarities <= 0.9))
        moderate_sim = np.sum((similarities > 0.5) & (similarities <= 0.7))
        low_sim = np.sum((similarities > 0.3) & (similarities <= 0.5))
        very_low_sim = np.sum(similarities <= 0.3)

        analysis = {
            'total_similarity_pairs': len(similarities),
            'mean_similarity': mean_sim,
            'std_similarity': std_sim,
            'min_similarity': min_sim,
            'max_similarity': max_sim,
            'median_similarity': median_sim,
            'percentiles': dict(zip([f'p{p}' for p in percentiles], percentile_values.tolist())),
            'distribution_shape': {
                'skewness': skewness,
                'kurtosis': kurtosis
            },
            'similarity_categories': {
                'very_high (>0.9)': int(very_high_sim),
                'high (0.7-0.9)': int(high_sim),
                'moderate (0.5-0.7)': int(moderate_sim),
                'low (0.3-0.5)': int(low_sim),
                'very_low (≤0.3)': int(very_low_sim)
            },
            'analysis_timestamp': datetime.now().isoformat()
        }

        self.logger.info(f"Similarity distribution analysis completed. Mean: {mean_sim:.3f}")
        return analysis

    def detect_duplicates(self, embeddings_data: List[Dict],
                         threshold: float = 0.95,
                         similarity_matrix: Optional[np.ndarray] = None) -> List[Dict[str, Any]]:
        """
        Detect duplicate or near-duplicate embeddings.

        Args:
            embeddings_data: List of embedding dictionaries
            threshold: Similarity threshold for duplicate detection
            similarity_matrix: Pre-computed similarity matrix (optional)

        Returns:
            List of duplicate groups with metadata
        """
        if not embeddings_data or len(embeddings_data) < 2:
            return []

        if similarity_matrix is None:
            similarity_matrix = self.compute_pairwise_similarities(embeddings_data)

        n_embeddings = len(embeddings_data)
        self.logger.info(f"Detecting duplicates with threshold {threshold}")

        # Find highly similar pairs
        duplicate_pairs = []
        triu_indices = np.triu_indices(n_embeddings, k=1)
        similarities = similarity_matrix[triu_indices]

        # Get pairs above threshold
        high_sim_mask = similarities >= threshold
        high_sim_indices = np.where(high_sim_mask)[0]

        for idx in high_sim_indices:
            i, j = triu_indices[0][idx], triu_indices[1][idx]
            sim = similarities[idx]

            duplicate_pairs.append({
                'index_1': int(i),
                'index_2': int(j),
                'similarity': float(sim),
                'chunk_1_info': {
                    'pdf_filename': embeddings_data[i].get('pdf_filename', 'unknown'),
                    'chunk_index': embeddings_data[i].get('chunk_index', 0),
                    'text_length': len(embeddings_data[i]['text'])
                },
                'chunk_2_info': {
                    'pdf_filename': embeddings_data[j].get('pdf_filename', 'unknown'),
                    'chunk_index': embeddings_data[j].get('chunk_index', 0),
                    'text_length': len(embeddings_data[j]['text'])
                }
            })

        # Group duplicates into clusters
        duplicate_groups = self._cluster_duplicates(duplicate_pairs, embeddings_data)

        self.logger.info(f"Detected {len(duplicate_groups)} duplicate groups")
        return duplicate_groups

    def _cluster_duplicates(self, duplicate_pairs: List[Dict],
                           embeddings_data: List[Dict]) -> List[Dict[str, Any]]:
        """
        Cluster duplicate pairs into groups.

        Args:
            duplicate_pairs: List of duplicate pairs
            embeddings_data: Original embeddings data

        Returns:
            List of duplicate groups
        """
        if not duplicate_pairs:
            return []

        # Build adjacency list
        from collections import defaultdict
        adjacency = defaultdict(set)

        for pair in duplicate_pairs:
            i, j = pair['index_1'], pair['index_2']
            adjacency[i].add(j)
            adjacency[j].add(i)

        # Find connected components (duplicate groups)
        visited = set()
        duplicate_groups = []

        for i in range(len(embeddings_data)):
            if i not in visited:
                # Start new group
                group = set()
                stack = [i]

                while stack:
                    current = stack.pop()
                    if current not in visited:
                        visited.add(current)
                        group.add(current)

                        # Add all connected nodes
                        for neighbor in adjacency[current]:
                            if neighbor not in visited:
                                stack.append(neighbor)

                # Only keep groups with more than 1 member
                if len(group) > 1:
                    group_indices = sorted(list(group))
                    group_info = {
                        'group_size': len(group_indices),
                        'indices': group_indices,
                        'chunks': []
                    }

                    # Add chunk information
                    for idx in group_indices:
                        chunk_info = {
                            'index': idx,
                            'pdf_filename': embeddings_data[idx].get('pdf_filename', 'unknown'),
                            'chunk_index': embeddings_data[idx].get('chunk_index', 0),
                            'text_preview': embeddings_data[idx]['text'][:200] + '...' if len(embeddings_data[idx]['text']) > 200 else embeddings_data[idx]['text']
                        }
                        group_info['chunks'].append(chunk_info)

                    duplicate_groups.append(group_info)

        return duplicate_groups

    def _compute_skewness(self, data: np.ndarray) -> float:
        """Compute skewness of data distribution."""
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return 0.0
        return float(np.mean(((data - mean) / std) ** 3))

    def _compute_kurtosis(self, data: np.ndarray) -> float:
        """Compute kurtosis of data distribution."""
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return 0.0
        return float(np.mean(((data - mean) / std) ** 4) - 3)

    def get_similarity_summary(self, embeddings_data: List[Dict]) -> Dict[str, Any]:
        """
        Get comprehensive similarity summary for embeddings.

        Args:
            embeddings_data: List of embedding dictionaries

        Returns:
            Comprehensive similarity analysis summary
        """
        if not embeddings_data or len(embeddings_data) < 2:
            return {'error': 'Need at least 2 embeddings for similarity analysis'}

        self.logger.info("Generating comprehensive similarity summary")

        # Compute similarity matrix
        similarity_matrix = self.compute_pairwise_similarities(embeddings_data)

        # Run all analyses
        distribution_analysis = self.analyze_similarity_distribution(embeddings_data, similarity_matrix)
        most_similar = self.find_most_similar(embeddings_data, top_k=5, similarity_matrix=similarity_matrix)
        least_similar = self.find_least_similar(embeddings_data, top_k=5, similarity_matrix=similarity_matrix)
        duplicates = self.detect_duplicates(embeddings_data, threshold=0.95, similarity_matrix=similarity_matrix)

        summary = {
            'total_embeddings': len(embeddings_data),
            'similarity_matrix_shape': similarity_matrix.shape,
            'distribution_analysis': distribution_analysis,
            'most_similar_pairs': most_similar,
            'least_similar_pairs': least_similar,
            'duplicate_groups': duplicates,
            'duplicate_summary': {
                'total_duplicate_groups': len(duplicates),
                'total_embeddings_in_duplicates': sum(group['group_size'] for group in duplicates),
                'largest_duplicate_group': max((group['group_size'] for group in duplicates), default=0)
            },
            'analysis_timestamp': datetime.now().isoformat()
        }

        self.logger.info("Similarity summary generation completed")
        return summary
