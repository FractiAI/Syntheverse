"""
Embedding Analyzer - Core analysis engine for embedding datasets.

Provides comprehensive statistical analysis, quality metrics, clustering,
and integration with word analysis capabilities.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import json

try:
    from sklearn.cluster import KMeans
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

from .logger import get_logger


class EmbeddingAnalyzer:
    """
    Core analysis engine for embedding datasets.

    Performs statistical analysis, quality assessment, clustering,
    and generates comprehensive reports.
    """

    def __init__(self, logger=None):
        """
        Initialize embedding analyzer.

        Args:
            logger: Optional logger instance
        """
        self.logger = logger or get_logger(__name__)

    def load_embeddings(self, embeddings_path: str, max_files: Optional[int] = None,
                       skip_errors: bool = True) -> List[Dict]:
        """
        Load embeddings from JSON files.

        Args:
            embeddings_path: Path to embeddings directory or file
            max_files: Maximum number of files to load
            skip_errors: Whether to skip files with errors

        Returns:
            List of embedding dictionaries
        """
        from .utils import load_embeddings_from_dir

        embeddings_path = Path(embeddings_path)

        if embeddings_path.is_file():
            # Single file
            try:
                with open(embeddings_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data if isinstance(data, list) else [data]
            except Exception as e:
                if not skip_errors:
                    raise
                self.logger.warning(f"Failed to load {embeddings_path}: {e}")
                return []
        else:
            # Directory
            return load_embeddings_from_dir(str(embeddings_path), max_files, skip_errors)

    def compute_statistics(self, embeddings_data: List[Dict[str, Any]],
                         include_clustering: bool = True,
                         clustering_max_k: int = 10,
                         include_word_analysis: bool = False) -> Dict[str, Any]:
        """
        Compute comprehensive statistics for embeddings.

        Args:
            embeddings_data: List of embedding dictionaries
            include_clustering: Whether to include clustering analysis
            clustering_max_k: Maximum number of clusters for analysis
            include_word_analysis: Whether to include word analysis

        Returns:
            Comprehensive statistics dictionary
        """
        self.logger.info(f"Computing statistics for {len(embeddings_data)} embeddings")

        if not embeddings_data:
            return {'error': 'No embeddings provided'}

        # Extract embeddings array
        from .utils import extract_embeddings_array, get_embedding_statistics
        embeddings = extract_embeddings_array(embeddings_data)

        if embeddings.size == 0:
            return {'error': 'No valid embeddings found'}

        # Basic statistics
        stats = get_embedding_statistics(embeddings)
        stats['total_embeddings'] = len(embeddings_data)

        # Quality metrics
        quality_metrics = self._compute_quality_metrics(embeddings_data, embeddings)
        stats['quality_metrics'] = quality_metrics

        # Distribution analysis
        distribution_stats = self._analyze_distributions(embeddings)
        stats['distribution_analysis'] = distribution_stats

        # Source analysis
        source_stats = self._analyze_sources(embeddings_data)
        stats['source_analysis'] = source_stats

        # Clustering analysis (optional)
        if include_clustering and SKLEARN_AVAILABLE:
            clustering_stats = self.analyze_clusters(embeddings_data, clustering_max_k)
            stats['clustering'] = clustering_stats

        # Outlier analysis
        outlier_stats = self._detect_outliers(embeddings)
        stats['outliers'] = outlier_stats

        # Word analysis (optional)
        if include_word_analysis:
            word_stats = self._compute_word_statistics(embeddings_data)
            stats['word_analysis'] = word_stats

        self.logger.info("Statistics computation completed")
        return stats

    def validate_embeddings(self, embeddings_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate embedding quality and consistency.

        Args:
            embeddings_data: List of embedding dictionaries

        Returns:
            Validation results
        """
        from .embedding_validator import EmbeddingValidator

        validator = EmbeddingValidator(logger=self.logger)
        return validator.generate_validation_report(embeddings_data)

    def analyze_clusters(self, embeddings_data: List[Dict[str, Any]],
                        n_clusters: Optional[int] = None, method: str = 'kmeans') -> Dict[str, Any]:
        """
        Perform clustering analysis on embeddings.

        Args:
            embeddings_data: List of embedding dictionaries
            n_clusters: Number of clusters (auto-determined if None)
            method: Clustering method ('kmeans')

        Returns:
            Clustering analysis results
        """
        if not SKLEARN_AVAILABLE:
            return {'error': 'scikit-learn not available for clustering'}

        from .utils import extract_embeddings_array
        embeddings = extract_embeddings_array(embeddings_data)

        if embeddings.size == 0:
            return {'error': 'No valid embeddings for clustering'}

        # Auto-determine number of clusters if not specified
        if n_clusters is None:
            n_clusters = min(len(embeddings_data) // 20, 10)  # Rough heuristic
            n_clusters = max(2, n_clusters)  # At least 2 clusters

        self.logger.info(f"Performing {method} clustering with {n_clusters} clusters")

        # Perform clustering
        if method == 'kmeans':
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(embeddings)
            centroids = kmeans.cluster_centers_
            inertia = kmeans.inertia_

        # Analyze clusters
        cluster_sizes = []
        cluster_stats = []

        for i in range(n_clusters):
            cluster_mask = cluster_labels == i
            cluster_embeddings = embeddings[cluster_mask]
            cluster_size = np.sum(cluster_mask)

            if cluster_size > 0:
                cluster_sizes.append(cluster_size)

                # Compute cluster statistics
                centroid = centroids[i]
                distances = np.linalg.norm(cluster_embeddings - centroid, axis=1)

                cluster_stat = {
                    'cluster_id': i,
                    'size': int(cluster_size),
                    'percentage': float(cluster_size / len(embeddings_data) * 100),
                    'centroid_norm': float(np.linalg.norm(centroid)),
                    'avg_distance_to_centroid': float(np.mean(distances)),
                    'max_distance_to_centroid': float(np.max(distances))
                }
                cluster_stats.append(cluster_stat)

        return {
            'method': method,
            'n_clusters': n_clusters,
            'total_samples': len(embeddings_data),
            'cluster_sizes': cluster_sizes,
            'cluster_statistics': cluster_stats,
            'overall_inertia': float(inertia) if 'inertia' in locals() else None,
            'silhouette_score': self._compute_silhouette_score(embeddings, cluster_labels)
        }

    def export_statistics(self, statistics: Dict[str, Any], output_path: str) -> None:
        """
        Export statistics to JSON file.

        Args:
            statistics: Statistics dictionary
            output_path: Path to save the statistics
        """
        # Convert numpy types to Python types for JSON serialization
        def convert_for_json(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, dict):
                return {k: convert_for_json(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_for_json(item) for item in obj]
            else:
                return obj

        serializable_stats = convert_for_json(statistics)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_stats, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Statistics exported to {output_path}")

    def _compute_quality_metrics(self, embeddings_data: List[Dict], embeddings: np.ndarray) -> Dict[str, Any]:
        """Compute quality metrics for embeddings."""
        # Norm consistency
        norms = np.linalg.norm(embeddings, axis=1)
        norm_std = np.std(norms)
        norm_mean = np.mean(norms)

        # Value distribution quality
        all_values = embeddings.flatten()
        value_sparsity = np.mean(np.abs(all_values) < 1e-6)

        # Information content (entropy-like measure)
        hist, _ = np.histogram(all_values, bins=50, density=True)
        hist = hist[hist > 0]  # Remove zeros
        entropy = -np.sum(hist * np.log(hist)) if len(hist) > 0 else 0

        return {
            'norm_consistency': 1.0 / (1.0 + norm_std),  # Higher is better
            'value_sparsity': value_sparsity,
            'information_content': entropy,
            'normalization_quality': abs(norm_mean - 1.0)
        }

    def _analyze_distributions(self, embeddings: np.ndarray) -> Dict[str, Any]:
        """Analyze embedding value distributions."""
        all_values = embeddings.flatten()

        # Basic distribution stats
        mean_val = np.mean(all_values)
        std_val = np.std(all_values)
        skew = np.mean(((all_values - mean_val) / std_val) ** 3) if std_val > 0 else 0
        kurtosis = np.mean(((all_values - mean_val) / std_val) ** 4) if std_val > 0 else 0

        # Quantile analysis
        quantiles = np.percentile(all_values, [1, 5, 25, 50, 75, 95, 99])

        return {
            'mean': float(mean_val),
            'std': float(std_val),
            'skewness': float(skew),
            'kurtosis': float(kurtosis),
            'quantiles': quantiles.tolist(),
            'range': float(np.max(all_values) - np.min(all_values))
        }

    def _analyze_sources(self, embeddings_data: List[Dict]) -> Dict[str, Any]:
        """Analyze embeddings by source/document."""
        source_counts = {}
        source_quality = {}

        for chunk in embeddings_data:
            source = chunk.get('pdf_filename', 'unknown')
            if source not in source_counts:
                source_counts[source] = 0
                source_quality[source] = []

            source_counts[source] += 1

            # Track embedding quality by source
            if 'embedding' in chunk:
                embedding = np.array(chunk['embedding'])
                norm = np.linalg.norm(embedding)
                source_quality[source].append(norm)

        # Compute source statistics
        sources_info = {}
        for source in source_counts:
            quality_scores = source_quality[source]
            sources_info[source] = {
                'count': source_counts[source],
                'percentage': source_counts[source] / len(embeddings_data) * 100,
                'avg_norm': float(np.mean(quality_scores)) if quality_scores else 0,
                'norm_std': float(np.std(quality_scores)) if quality_scores else 0
            }

        return {
            'total_sources': len(source_counts),
            'source_distribution': sources_info,
            'most_common_source': max(source_counts.items(), key=lambda x: x[1])[0] if source_counts else None
        }

    def _detect_outliers(self, embeddings: np.ndarray, method: str = 'iqr') -> Dict[str, Any]:
        """Detect outlier embeddings."""
        norms = np.linalg.norm(embeddings, axis=1)

        if method == 'iqr':
            q1, q3 = np.percentile(norms, [25, 75])
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr

            outlier_mask = (norms < lower_bound) | (norms > upper_bound)
        else:
            # Z-score method
            z_scores = np.abs((norms - np.mean(norms)) / np.std(norms))
            outlier_mask = z_scores > 3

        outlier_count = np.sum(outlier_mask)
        outlier_percentage = outlier_count / len(embeddings) * 100

        return {
            'method': method,
            'outlier_count': int(outlier_count),
            'outlier_percentage': float(outlier_percentage),
            'total_embeddings': len(embeddings)
        }

    def _compute_silhouette_score(self, embeddings: np.ndarray, labels: np.ndarray) -> float:
        """Compute silhouette score for clustering quality."""
        try:
            from sklearn.metrics import silhouette_score
            return float(silhouette_score(embeddings, labels))
        except ImportError:
            return 0.0

    def _compute_word_statistics(self, embeddings_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compute word-related statistics for embeddings."""
        from .word_analyzer import WordAnalyzer

        word_analyzer = WordAnalyzer(logger=self.logger)

        # Compute word frequencies
        freq_results = word_analyzer.compute_word_frequencies(embeddings_data, top_k=100)

        # Basic word statistics
        word_stats = {
            'total_unique_words': freq_results['unique_words'],
            'total_word_occurrences': freq_results['total_words'],
            'top_words': freq_results['top_words'][:20],  # Top 20 words
            'vocabulary_richness': freq_results['unique_words'] / max(1, len(embeddings_data)),
            'avg_words_per_chunk': freq_results['total_words'] / max(1, len(embeddings_data))
        }

        # Word frequency distribution statistics
        if freq_results['word_frequencies']:
            frequencies = list(freq_results['word_frequencies'].values())
            word_stats['word_freq_stats'] = {
                'mean_frequency': float(np.mean(frequencies)),
                'std_frequency': float(np.std(frequencies)),
                'max_frequency': max(frequencies),
                'min_frequency': min(frequencies)
            }

        # Source diversity in word usage
        source_diversity = freq_results.get('source_diversity', {})
        if source_diversity:
            source_word_stats = []
            for source, stats in source_diversity.items():
                source_word_stats.append({
                    'source': source,
                    'unique_words': stats['unique_words'],
                    'total_words': stats['total_words'],
                    'lexical_density': stats['unique_words'] / max(1, stats['total_words'])
                })
            word_stats['source_word_diversity'] = source_word_stats

        return word_stats