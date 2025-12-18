"""
Embedding Analyzer - Comprehensive embedding analysis and statistics.

Provides tools for analyzing embedding quality, computing statistics,
and understanding semantic structure in vectorized text data.
"""

import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
import scipy.stats as stats
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

from .logger import get_logger


class EmbeddingAnalyzer:
    """
    Comprehensive embedding analysis and statistics computation.

    Analyzes embedding quality, distributions, clusters, and semantic relationships.
    """

    def __init__(self, logger=None):
        """
        Initialize the embedding analyzer.

        Args:
            logger: Optional logger instance
        """
        self.logger = logger or get_logger(__name__)

    def load_embeddings(self, embeddings_path: str, max_files: Optional[int] = None,
                       skip_errors: bool = True) -> List[Dict[str, Any]]:
        """
        Load embeddings from JSON files in the specified directory.

        Args:
            embeddings_path: Path to directory containing embedding JSON files
            max_files: Maximum number of files to process (for testing/debugging)
            skip_errors: Whether to skip files with errors or raise exceptions

        Returns:
            List of embedding dictionaries with text, embedding vector, and metadata

        Raises:
            ValueError: If embeddings directory doesn't exist or contains no valid files
            FileNotFoundError: If specific files cannot be read and skip_errors=False
        """
        if not embeddings_path or not isinstance(embeddings_path, str):
            raise ValueError("embeddings_path must be a non-empty string")

        embeddings_dir = Path(embeddings_path).resolve()

        if not embeddings_dir.exists():
            raise ValueError(f"Embeddings directory not found: {embeddings_dir}")

        if not embeddings_dir.is_dir():
            raise ValueError(f"Path is not a directory: {embeddings_dir}")

        self.logger.info(f"Loading embeddings from: {embeddings_dir}")

        # Find all JSON files
        json_files = list(embeddings_dir.glob("*.json"))
        if not json_files:
            raise ValueError(f"No JSON embedding files found in {embeddings_dir}")

        # Limit files if specified
        if max_files and max_files > 0:
            json_files = json_files[:max_files]
            self.logger.info(f"Limited to first {max_files} files")

        all_embeddings: List[Dict[str, Any]] = []
        total_chunks = 0
        loaded_files = 0
        failed_files = 0

        for json_file in json_files:
            try:
                self.logger.debug(f"Processing file: {json_file.name}")

                # Check file size (avoid loading extremely large files)
                file_size = json_file.stat().st_size
                if file_size > 500 * 1024 * 1024:  # 500MB limit
                    self.logger.warning(f"Skipping large file: {json_file.name} ({file_size} bytes)")
                    continue

                with open(json_file, 'r', encoding='utf-8', errors='replace') as f:
                    try:
                        chunks = json.load(f)
                    except json.JSONDecodeError as e:
                        raise ValueError(f"Invalid JSON in {json_file}: {e}")

                if not isinstance(chunks, list):
                    raise ValueError(f"Expected list of chunks in {json_file}, got {type(chunks)}")

                pdf_name = json_file.stem
                file_chunks = 0

                for i, chunk in enumerate(chunks):
                    try:
                        # Validate chunk structure
                        if not isinstance(chunk, dict):
                            self.logger.warning(f"Skipping non-dict chunk {i} in {json_file.name}")
                            continue

                        # Ensure required fields are present
                        if 'text' not in chunk:
                            self.logger.warning(f"Chunk {i} missing 'text' field in {json_file.name}")
                            continue

                        if 'embedding' not in chunk:
                            self.logger.warning(f"Chunk {i} missing 'embedding' field in {json_file.name}")
                            continue

                        # Convert and validate embedding
                        embedding = chunk['embedding']
                        if isinstance(embedding, list):
                            if len(embedding) == 0:
                                self.logger.warning(f"Empty embedding in chunk {i} of {json_file.name}")
                                continue
                            try:
                                embedding = np.array(embedding, dtype=np.float32)
                            except (ValueError, TypeError) as e:
                                self.logger.warning(f"Invalid embedding data in chunk {i} of {json_file.name}: {e}")
                                continue
                        elif isinstance(embedding, np.ndarray):
                            embedding = embedding.astype(np.float32)
                        else:
                            self.logger.warning(f"Invalid embedding type in chunk {i} of {json_file.name}")
                            continue

                        # Validate embedding dimensions
                        if embedding.ndim != 1:
                            self.logger.warning(f"Expected 1D embedding in chunk {i} of {json_file.name}")
                            continue

                        if np.any(~np.isfinite(embedding)):
                            self.logger.warning(f"Non-finite values in embedding chunk {i} of {json_file.name}")
                            continue

                        # Create validated chunk
                        validated_chunk = {
                            'text': str(chunk['text']),
                            'embedding': embedding,
                            'metadata': chunk.get('metadata', {}),
                            'chunk_index': chunk.get('chunk_index', i),
                            'pdf_filename': chunk.get('pdf_filename', pdf_name)
                        }

                        all_embeddings.append(validated_chunk)
                        file_chunks += 1
                        total_chunks += 1

                    except Exception as e:
                        self.logger.warning(f"Error processing chunk {i} in {json_file.name}: {e}")
                        continue

                loaded_files += 1
                self.logger.info(f"Loaded {file_chunks} chunks from {json_file.name}")

            except Exception as e:
                failed_files += 1
                error_msg = f"Error loading {json_file.name}: {e}"
                if skip_errors:
                    self.logger.error(error_msg)
                    continue
                else:
                    raise FileNotFoundError(error_msg) from e

        if not all_embeddings:
            if skip_errors:
                self.logger.warning("No valid embeddings found in any files, returning empty list")
                return []
            else:
                raise ValueError("No valid embeddings found in any files")

        self.logger.info(f"Successfully loaded {len(all_embeddings)} embeddings from {loaded_files} files")
        if failed_files > 0:
            self.logger.warning(f"Failed to load {failed_files} files")

        return all_embeddings

    def compute_statistics(self, embeddings_data: List[Dict[str, Any]],
                         include_clustering: bool = True,
                         clustering_max_k: int = 10) -> Dict[str, Any]:
        """
        Compute comprehensive statistics for the embeddings.

        Args:
            embeddings_data: List of embedding dictionaries
            include_clustering: Whether to perform clustering analysis
            clustering_max_k: Maximum number of clusters to test

        Returns:
            Dictionary containing various statistics

        Raises:
            ValueError: If embeddings_data is empty or malformed
        """
        if not embeddings_data:
            raise ValueError("No embeddings provided for analysis")

        if not isinstance(embeddings_data, list):
            raise ValueError("embeddings_data must be a list")

        self.logger.info(f"Computing statistics for {len(embeddings_data)} embeddings")

        try:
            # Extract embeddings as numpy array with validation
            embeddings_list = []
            for i, chunk in enumerate(embeddings_data):
                if not isinstance(chunk, dict):
                    raise ValueError(f"Chunk {i} is not a dictionary")
                if 'embedding' not in chunk:
                    raise ValueError(f"Chunk {i} missing 'embedding' field")

                embedding = chunk['embedding']
                if isinstance(embedding, list):
                    embedding = np.array(embedding, dtype=np.float32)
                elif isinstance(embedding, np.ndarray):
                    embedding = embedding.astype(np.float32)
                else:
                    raise ValueError(f"Invalid embedding type in chunk {i}")

                embeddings_list.append(embedding)

            embeddings_array = np.array(embeddings_list)

            if embeddings_array.size == 0:
                raise ValueError("No valid embeddings found")

            # Basic dimensions with safety checks
            total_embeddings = len(embeddings_data)
            dimension = embeddings_array.shape[1] if embeddings_array.ndim > 1 else 1

            # Vector norms statistics with numerical stability
            norms = np.linalg.norm(embeddings_array, axis=1)
            norms = np.nan_to_num(norms, nan=0.0, posinf=0.0, neginf=0.0)

            if len(norms) == 0 or np.all(norms == 0):
                self.logger.warning("All embedding norms are zero - embeddings may be improperly normalized")
                norm_mean = norm_std = norm_min = norm_max = 0.0
            else:
                norm_mean = float(np.mean(norms))
                norm_std = float(np.std(norms))
                norm_min = float(np.min(norms))
                norm_max = float(np.max(norms))

            # Value statistics with memory-efficient processing
            if embeddings_array.size > 10_000_000:  # Large arrays
                self.logger.info("Large embedding array detected, using sampling for value statistics")
                # Sample 1% of values for statistics
                flat_size = embeddings_array.size
                sample_indices = np.random.choice(flat_size, size=min(100_000, flat_size), replace=False)
                all_values = embeddings_array.flatten()[sample_indices]
            else:
                all_values = embeddings_array.flatten()

            # Compute value statistics
            value_mean = float(np.mean(all_values))
            value_std = float(np.std(all_values))
            value_min = float(np.min(all_values))
            value_max = float(np.max(all_values))

            # Sparsity calculation with configurable threshold
            sparsity_threshold = max(1e-6, abs(value_mean) * 0.01)  # Adaptive threshold
            sparse_count = np.sum(np.abs(all_values) < sparsity_threshold)
            sparsity = float(sparse_count / len(all_values))

            # Outlier detection using multiple methods
            outliers_iqr = self._detect_outliers_iqr(norms)
            outliers_zscore = self._detect_outliers_zscore(norms)
            outliers = max(outliers_iqr, outliers_zscore)  # Conservative estimate

            # Clustering analysis
            clusters = None
            if include_clustering and total_embeddings >= 10 and dimension > 1:
                clusters = self._compute_optimal_clusters(embeddings_array, clustering_max_k)

            # Source distribution with error handling
            source_counts = {}
            for chunk in embeddings_data:
                source = chunk.get('pdf_filename', 'unknown')
                if not isinstance(source, str):
                    source = str(source)
                source_counts[source] = source_counts.get(source, 0) + 1

            # Metadata analysis
            metadata_fields = set()
            total_metadata_entries = 0
            for chunk in embeddings_data:
                metadata = chunk.get('metadata', {})
                if isinstance(metadata, dict):
                    metadata_fields.update(metadata.keys())
                    total_metadata_entries += len(metadata)

            # Text statistics
            text_lengths = []
            for chunk in embeddings_data:
                text = chunk.get('text', '')
                if isinstance(text, str):
                    text_lengths.append(len(text))

            text_stats = None
            if text_lengths:
                text_lengths = np.array(text_lengths)
                text_stats = {
                    'text_length_mean': float(np.mean(text_lengths)),
                    'text_length_std': float(np.std(text_lengths)),
                    'text_length_min': int(np.min(text_lengths)),
                    'text_length_max': int(np.max(text_lengths))
                }

            # Compile comprehensive statistics
            statistics = {
                'total_embeddings': total_embeddings,
                'dimension': dimension,
                'norm_mean': norm_mean,
                'norm_std': norm_std,
                'norm_min': norm_min,
                'norm_max': norm_max,
                'value_mean': value_mean,
                'value_std': value_std,
                'value_min': value_min,
                'value_max': value_max,
                'sparsity': sparsity,
                'sparsity_threshold': sparsity_threshold,
                'outliers': outliers,
                'outlier_method': 'hybrid_iqr_zscore',
                'clusters': clusters,
                'sources': source_counts,
                'metadata_fields': list(metadata_fields),
                'total_metadata_entries': total_metadata_entries,
                'text_statistics': text_stats,
                'analysis_timestamp': datetime.now().isoformat(),
                'computation_time_seconds': None,  # Will be set by caller
                'quality_score': self._compute_quality_score(
                    norm_std, sparsity, outliers, total_embeddings
                )
            }

            self.logger.info("Statistics computation completed successfully")
            return statistics

        except Exception as e:
            self.logger.error(f"Error computing statistics: {e}")
            raise

    def _detect_outliers_iqr(self, values: np.ndarray, multiplier: float = 1.5) -> int:
        """Detect outliers using IQR method."""
        if len(values) < 4:
            return 0

        q1, q3 = np.percentile(values, [25, 75])
        iqr = q3 - q1
        if iqr == 0:
            return 0

        lower_bound = q1 - multiplier * iqr
        upper_bound = q3 + multiplier * iqr
        return int(np.sum((values < lower_bound) | (values > upper_bound)))

    def _detect_outliers_zscore(self, values: np.ndarray, threshold: float = 3.0) -> int:
        """Detect outliers using Z-score method."""
        if len(values) < 2:
            return 0

        mean_val = np.mean(values)
        std_val = np.std(values)
        if std_val == 0:
            return 0

        z_scores = np.abs((values - mean_val) / std_val)
        return int(np.sum(z_scores > threshold))

    def _compute_optimal_clusters(self, embeddings: np.ndarray, max_k: int) -> Optional[int]:
        """Compute optimal number of clusters using silhouette analysis."""
        try:
            if len(embeddings) < max_k * 2:
                max_k = max(2, len(embeddings) // 2)

            best_score = -1
            best_k = None

            for k in range(2, max_k + 1):
                try:
                    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
                    labels = kmeans.fit_predict(embeddings)
                    score = silhouette_score(embeddings, labels)
                    if score > best_score:
                        best_score = score
                        best_k = k
                except Exception:
                    continue

            return best_k if best_score > 0.1 else None  # Only return if score is reasonable

        except Exception as e:
            self.logger.warning(f"Clustering analysis failed: {e}")
            return None

    def _compute_quality_score(self, norm_std: float, sparsity: float,
                             outliers: int, total_embeddings: int) -> float:
        """Compute an overall quality score for the embeddings."""
        try:
            # Normalize factors to 0-1 scale
            norm_uniformity = min(1.0, 1.0 / (1.0 + norm_std))  # Lower std is better
            sparsity_penalty = min(1.0, sparsity * 10)  # Lower sparsity is better
            outlier_penalty = min(1.0, outliers / max(1, total_embeddings * 0.1))  # Lower outliers better

            # Weighted quality score
            quality = (norm_uniformity * 0.5 + (1 - sparsity_penalty) * 0.3 + (1 - outlier_penalty) * 0.2)
            return round(float(quality), 3)

        except Exception:
            return 0.0

    def validate_embeddings(self, embeddings_data: List[Dict]) -> Dict[str, Any]:
        """
        Basic validation of embedding data structure and quality.

        Args:
            embeddings_data: List of embedding dictionaries

        Returns:
            Validation results dictionary
        """
        if not embeddings_data:
            return {'valid': False, 'errors': ['No embeddings provided']}

        self.logger.info("Validating embeddings")

        errors = []
        warnings = []

        # Check basic structure
        for i, chunk in enumerate(embeddings_data):
            if 'text' not in chunk:
                errors.append(f"Chunk {i}: Missing 'text' field")
            if 'embedding' not in chunk:
                errors.append(f"Chunk {i}: Missing 'embedding' field")
            else:
                embedding = chunk['embedding']
                if not isinstance(embedding, np.ndarray):
                    if isinstance(embedding, list):
                        embedding = np.array(embedding)
                    else:
                        errors.append(f"Chunk {i}: Invalid embedding type")
                        continue

                # Check for NaN or infinite values
                if np.any(np.isnan(embedding)) or np.any(np.isinf(embedding)):
                    warnings.append(f"Chunk {i}: Contains NaN or infinite values")

        # Check dimension consistency
        if embeddings_data:
            first_embedding = embeddings_data[0]['embedding']
            if isinstance(first_embedding, np.ndarray):
                expected_dim = first_embedding.shape[0]
                for i, chunk in enumerate(embeddings_data[1:], 1):
                    embedding = chunk['embedding']
                    if isinstance(embedding, np.ndarray) and embedding.shape[0] != expected_dim:
                        errors.append(f"Chunk {i}: Dimension mismatch ({embedding.shape[0]} vs {expected_dim})")

        # Generate details summary
        details = []
        if len(errors) == 0:
            details.append("All embeddings passed validation")
        else:
            details.extend(errors)

        validation_result = {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'details': details,
            'total_chunks': len(embeddings_data),
            'validation_timestamp': datetime.now().isoformat()
        }

        if validation_result['valid']:
            self.logger.info("Validation passed")
        else:
            self.logger.warning(f"Validation failed with {len(errors)} errors")

        return validation_result

    def compute_similarity_matrix(self, embeddings_data: List[Dict],
                                max_samples: Optional[int] = None) -> np.ndarray:
        """
        Compute pairwise cosine similarity matrix for embeddings.

        Args:
            embeddings_data: List of embedding dictionaries
            max_samples: Maximum number of embeddings to include (for memory efficiency)

        Returns:
            Similarity matrix as numpy array
        """
        if not embeddings_data:
            raise ValueError("No embeddings provided")

        # Extract embeddings
        embeddings_array = np.array([chunk['embedding'] for chunk in embeddings_data])

        # Sample if requested
        if max_samples and len(embeddings_array) > max_samples:
            indices = np.random.choice(len(embeddings_array), max_samples, replace=False)
            embeddings_array = embeddings_array[indices]
            self.logger.info(f"Sampled {max_samples} embeddings from {len(embeddings_data)} total")

        self.logger.info(f"Computing similarity matrix for {len(embeddings_array)} embeddings")

        # Normalize embeddings for cosine similarity
        norms = np.linalg.norm(embeddings_array, axis=1, keepdims=True)
        norms[norms == 0] = 1  # Avoid division by zero
        normalized_embeddings = embeddings_array / norms

        # Compute similarity matrix
        similarity_matrix = np.dot(normalized_embeddings, normalized_embeddings.T)

        # Ensure diagonal is 1.0 (self-similarity)
        np.fill_diagonal(similarity_matrix, 1.0)

        self.logger.info("Similarity matrix computation completed")
        return similarity_matrix

    def analyze_clusters(self, embeddings_data: List[Dict],
                        n_clusters: int = 5) -> Dict[str, Any]:
        """
        Perform clustering analysis on embeddings.

        Args:
            embeddings_data: List of embedding dictionaries
            n_clusters: Number of clusters to find

        Returns:
            Clustering results and analysis
        """
        if not embeddings_data or len(embeddings_data) < n_clusters:
            return {'error': 'Insufficient data for clustering'}

        embeddings_array = np.array([chunk['embedding'] for chunk in embeddings_data])

        self.logger.info(f"Analyzing clusters with {n_clusters} clusters")

        try:
            # Perform clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            labels = kmeans.fit_predict(embeddings_array)

            # Compute silhouette score
            silhouette_avg = silhouette_score(embeddings_array, labels)

            # Cluster sizes
            unique_labels, counts = np.unique(labels, return_counts=True)
            cluster_sizes = dict(zip(unique_labels.tolist(), counts.tolist()))

            # Cluster centers (in reduced space for interpretability)
            centers = kmeans.cluster_centers_

            analysis = {
                'n_clusters': n_clusters,
                'silhouette_score': float(silhouette_avg),
                'cluster_sizes': cluster_sizes,
                'cluster_centers': centers.tolist(),
                'labels': labels.tolist(),
                'analysis_timestamp': datetime.now().isoformat()
            }

            self.logger.info(f"Clustering completed. Silhouette score: {silhouette_avg:.3f}")
            return analysis

        except Exception as e:
            self.logger.error(f"Clustering analysis failed: {e}")
            return {'error': str(e)}

    def export_statistics(self, statistics: Dict[str, Any],
                         output_path: str) -> None:
        """
        Export statistics to JSON file.

        Args:
            statistics: Statistics dictionary
            output_path: Path to save the statistics
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(statistics, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Statistics exported to {output_file.absolute()}")
