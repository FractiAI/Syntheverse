"""
Embedding Validator - Comprehensive validation for embeddings.

Provides detailed validation checks for embedding quality, consistency,
and structural integrity with comprehensive reporting.
"""

import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
from scipy import stats

from .logger import get_logger


class EmbeddingValidator:
    """
    Comprehensive validation suite for embeddings.

    Validates embedding quality, consistency, and structural integrity
    with detailed reporting and recommendations.
    """

    def __init__(self, strict_mode: bool = False, logger=None):
        """
        Initialize validator.

        Args:
            strict_mode: If True, treat warnings as errors
            logger: Optional logger instance
        """
        self.strict_mode = strict_mode
        self.logger = logger or get_logger(__name__)

    def validate_dimensions(self, embeddings_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate that all embeddings have consistent dimensions.

        Args:
            embeddings_data: List of embedding dictionaries

        Returns:
            Validation result dictionary
        """
        if not embeddings_data:
            return {'valid': False, 'details': 'No embeddings provided'}

        dimensions = []
        errors = []

        for i, chunk in enumerate(embeddings_data):
            embedding = chunk.get('embedding')
            if embedding is None:
                errors.append(f"Chunk {i}: Missing embedding")
                continue

            # Convert to numpy array if needed
            if isinstance(embedding, list):
                embedding = np.array(embedding)
            elif not isinstance(embedding, np.ndarray):
                errors.append(f"Chunk {i}: Invalid embedding type {type(embedding)}")
                continue

            if embedding.ndim != 1:
                errors.append(f"Chunk {i}: Expected 1D array, got {embedding.ndim}D")
                continue

            dimensions.append(embedding.shape[0])

        if errors:
            return {
                'valid': False,
                'details': f'Found {len(errors)} dimension errors',
                'errors': errors[:10],  # Limit error output
                'error_count': len(errors)
            }

        # Check dimension consistency
        unique_dims = set(dimensions)
        if len(unique_dims) > 1:
            dim_counts = {}
            for dim in dimensions:
                dim_counts[dim] = dim_counts.get(dim, 0) + 1

            return {
                'valid': False,
                'details': f'Inconsistent dimensions: {dim_counts}',
                'dimension_counts': dim_counts
            }

        expected_dim = list(unique_dims)[0]
        return {
            'valid': True,
            'details': f'All {len(embeddings_data)} embeddings have consistent dimension {expected_dim}',
            'dimension': expected_dim
        }

    def validate_norms(self, embeddings_data: List[Dict],
                      tolerance: float = 0.1) -> Dict[str, Any]:
        """
        Validate embedding vector norms.

        Args:
            embeddings_data: List of embedding dictionaries
            tolerance: Maximum allowed deviation from unit norm

        Returns:
            Validation result dictionary
        """
        if not embeddings_data:
            return {'valid': False, 'details': 'No embeddings provided'}

        norms = []
        outliers = []

        for i, chunk in enumerate(embeddings_data):
            embedding = chunk.get('embedding')
            if embedding is None:
                continue

            if isinstance(embedding, list):
                embedding = np.array(embedding)

            norm = np.linalg.norm(embedding)
            norms.append(norm)

            # Check for extreme norms
            if norm < 0.1 or norm > 10.0:
                outliers.append((i, norm))

        if not norms:
            return {'valid': False, 'details': 'No valid norms calculated'}

        norms_array = np.array(norms)
        mean_norm = np.mean(norms_array)
        std_norm = np.std(norms_array)

        # Check if norms are reasonably close to 1.0 (normalized)
        norm_range = mean_norm - tolerance, mean_norm + tolerance
        in_range = np.sum((norms_array >= norm_range[0]) & (norms_array <= norm_range[1]))
        in_range_percent = in_range / len(norms_array)

        details = ".3f"
        if outliers:
            details += f", {len(outliers)} extreme norms detected"

        # Consider valid if most norms are reasonable
        is_valid = in_range_percent > 0.8 and len(outliers) < len(norms_array) * 0.05

        result = {
            'valid': is_valid,
            'details': details,
            'mean_norm': float(mean_norm),
            'std_norm': float(std_norm),
            'min_norm': float(np.min(norms_array)),
            'max_norm': float(np.max(norms_array)),
            'in_range_percentage': float(in_range_percent),
            'extreme_norms_count': len(outliers)
        }

        if outliers:
            result['extreme_norms'] = outliers[:5]  # Show first 5

        return result

    def validate_similarity_range(self, embeddings_data: List[Dict],
                                sample_size: int = 1000) -> Dict[str, Any]:
        """
        Validate that similarity scores are in valid range [-1, 1].

        Args:
            embeddings_data: List of embedding dictionaries
            sample_size: Number of embeddings to sample for similarity computation

        Returns:
            Validation result dictionary
        """
        if not embeddings_data or len(embeddings_data) < 2:
            return {'valid': False, 'details': 'Need at least 2 embeddings for similarity validation'}

        # Sample embeddings for efficiency
        if len(embeddings_data) > sample_size:
            indices = np.random.choice(len(embeddings_data), sample_size, replace=False)
            sampled_data = [embeddings_data[i] for i in indices]
        else:
            sampled_data = embeddings_data

        # Extract embeddings
        embeddings = []
        for chunk in sampled_data:
            embedding = chunk.get('embedding')
            if embedding is not None:
                if isinstance(embedding, list):
                    embedding = np.array(embedding)
                embeddings.append(embedding)

        if len(embeddings) < 2:
            return {'valid': False, 'details': 'Need at least 2 valid embeddings'}

        embeddings_array = np.array(embeddings)

        # Normalize for cosine similarity
        norms = np.linalg.norm(embeddings_array, axis=1, keepdims=True)
        norms[norms == 0] = 1
        normalized = embeddings_array / norms

        # Compute sample similarities
        similarity_matrix = np.dot(normalized, normalized.T)

        # Remove diagonal (self-similarity should be 1.0)
        similarity_matrix_no_diag = similarity_matrix[~np.eye(similarity_matrix.shape[0], dtype=bool)]

        min_sim = float(np.min(similarity_matrix_no_diag))
        max_sim = float(np.max(similarity_matrix_no_diag))
        mean_sim = float(np.mean(similarity_matrix_no_diag))

        # Check range validity
        valid_range = -1.01 <= min_sim <= max_sim <= 1.01  # Small tolerance for floating point

        # Check for suspicious values
        suspicious_count = np.sum((similarity_matrix_no_diag < -1.1) | (similarity_matrix_no_diag > 1.1))

        details = ".3f"
        if suspicious_count > 0:
            details += f", {suspicious_count} suspicious similarity values"

        return {
            'valid': valid_range and suspicious_count == 0,
            'details': details,
            'min_similarity': min_sim,
            'max_similarity': max_sim,
            'mean_similarity': mean_sim,
            'suspicious_count': int(suspicious_count),
            'sample_size': len(embeddings)
        }

    def detect_outliers(self, embeddings_data: List[Dict],
                       method: str = 'iqr',
                       threshold: float = 1.5) -> Dict[str, Any]:
        """
        Detect outlier embeddings using statistical methods.

        Args:
            embeddings_data: List of embedding dictionaries
            method: Outlier detection method ('iqr', 'zscore', 'isolation_forest')
            threshold: Threshold for outlier detection

        Returns:
            Outlier detection results
        """
        if not embeddings_data:
            return {'outliers': [], 'details': 'No embeddings provided'}

        # Extract embeddings
        embeddings = []
        valid_indices = []

        for i, chunk in enumerate(embeddings_data):
            embedding = chunk.get('embedding')
            if embedding is not None:
                if isinstance(embedding, list):
                    embedding = np.array(embedding)
                embeddings.append(embedding)
                valid_indices.append(i)

        if not embeddings:
            return {'outliers': [], 'details': 'No valid embeddings found'}

        embeddings_array = np.array(embeddings)

        if method == 'iqr':
            # IQR method on norms
            norms = np.linalg.norm(embeddings_array, axis=1)
            q1, q3 = np.percentile(norms, [25, 75])
            iqr = q3 - q1
            lower_bound = q1 - threshold * iqr
            upper_bound = q3 + threshold * iqr

            outlier_mask = (norms < lower_bound) | (norms > upper_bound)
            outlier_indices = np.where(outlier_mask)[0]

        elif method == 'zscore':
            # Z-score method on norms
            norms = np.linalg.norm(embeddings_array, axis=1)
            z_scores = np.abs(stats.zscore(norms))
            outlier_indices = np.where(z_scores > threshold)[0]

        elif method == 'isolation_forest':
            try:
                from sklearn.ensemble import IsolationForest
                iso_forest = IsolationForest(contamination=0.1, random_state=42)
                outlier_predictions = iso_forest.fit_predict(embeddings_array)
                outlier_indices = np.where(outlier_predictions == -1)[0]
            except ImportError:
                return {'error': 'scikit-learn not available for isolation forest'}

        else:
            return {'error': f'Unknown outlier detection method: {method}'}

        # Map back to original indices
        outlier_original_indices = [valid_indices[i] for i in outlier_indices]

        details = f"Detected {len(outlier_original_indices)} outliers using {method} method"
        if outlier_original_indices:
            details += f" at indices: {outlier_original_indices[:5]}"
            if len(outlier_original_indices) > 5:
                details += f" (+{len(outlier_original_indices) - 5} more)"

        return {
            'outliers': outlier_original_indices,
            'outlier_count': len(outlier_original_indices),
            'details': details,
            'method': method,
            'threshold': threshold,
            'total_embeddings': len(embeddings_data)
        }

    def validate_metadata(self, embeddings_data: List[Dict]) -> Dict[str, Any]:
        """
        Validate metadata completeness and consistency.

        Args:
            embeddings_data: List of embedding dictionaries

        Returns:
            Metadata validation results
        """
        if not embeddings_data:
            return {'valid': False, 'details': 'No embeddings provided'}

        required_fields = ['text']
        recommended_fields = ['metadata', 'chunk_index', 'pdf_filename']

        field_presence = {field: 0 for field in required_fields + recommended_fields}
        field_presence['embedding'] = 0  # Add embedding presence check

        metadata_field_counts = {}
        empty_texts = 0
        empty_metadata = 0

        for chunk in embeddings_data:
            # Check required fields
            for field in required_fields:
                if field in chunk and chunk[field]:
                    field_presence[field] += 1

            # Check embedding
            if 'embedding' in chunk and chunk['embedding'] is not None:
                field_presence['embedding'] += 1

            # Check recommended fields
            for field in recommended_fields:
                if field in chunk:
                    field_presence[field] += 1

            # Analyze metadata content
            if 'metadata' in chunk:
                metadata = chunk['metadata']
                if isinstance(metadata, dict):
                    for key in metadata.keys():
                        metadata_field_counts[key] = metadata_field_counts.get(key, 0) + 1

                    if not metadata:  # Empty metadata dict
                        empty_metadata += 1
                else:
                    empty_metadata += 1
            else:
                empty_metadata += 1

            # Check for empty text
            if 'text' in chunk and not chunk['text'].strip():
                empty_texts += 1

        # Calculate completeness percentages
        total_chunks = len(embeddings_data)
        completeness = {}
        for field, count in field_presence.items():
            completeness[field] = count / total_chunks

        # Identify issues
        issues = []
        if completeness['text'] < 1.0:
            issues.append(f"Missing text in {total_chunks - field_presence['text']} chunks")
        if completeness['embedding'] < 1.0:
            issues.append(f"Missing embeddings in {total_chunks - field_presence['embedding']} chunks")
        if empty_texts > 0:
            issues.append(f"{empty_texts} chunks have empty text")
        if completeness['metadata'] < 0.8:
            issues.append("Metadata missing in many chunks")

        # Overall validity
        is_valid = (completeness['text'] == 1.0 and
                   completeness['embedding'] == 1.0 and
                   empty_texts == 0)

        details = f"Metadata validation: {len(issues)} issues found"
        if not issues:
            details = "Metadata validation: All required fields present"

        return {
            'valid': is_valid,
            'details': details,
            'issues': issues,
            'field_completeness': completeness,
            'metadata_fields': list(metadata_field_counts.keys()),
            'metadata_field_counts': metadata_field_counts,
            'empty_texts': empty_texts,
            'empty_metadata': empty_metadata,
            'total_chunks': total_chunks
        }

    def generate_validation_report(self, embeddings_path: Optional[str] = None,
                                 embeddings_data: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Generate comprehensive validation report.

        Args:
            embeddings_path: Path to embeddings directory (alternative to embeddings_data)
            embeddings_data: Direct embeddings data (alternative to embeddings_path)

        Returns:
            Comprehensive validation report
        """
        start_time = datetime.now()

        # Load data if path provided
        if embeddings_path and not embeddings_data:
            from .utils import load_embeddings_from_dir
            embeddings_data = load_embeddings_from_dir(embeddings_path)
        elif not embeddings_data:
            return {'error': 'Either embeddings_path or embeddings_data must be provided'}

        if not embeddings_data:
            return {'error': 'No embeddings data available'}

        self.logger.info(f"Generating validation report for {len(embeddings_data)} embeddings")

        # Run all validations
        checks = {}

        # Dimensions check
        checks['dimensions'] = self.validate_dimensions(embeddings_data)

        # Norms check
        checks['norms'] = self.validate_norms(embeddings_data)

        # Similarity range check
        checks['similarity_range'] = self.validate_similarity_range(embeddings_data)

        # Outlier detection
        checks['outliers'] = self.detect_outliers(embeddings_data)

        # Metadata validation
        checks['metadata'] = self.validate_metadata(embeddings_data)

        # Overall assessment
        failed_checks = [name for name, result in checks.items()
                        if isinstance(result, dict) and not result.get('valid', True)]

        # Treat warnings as failures in strict mode
        warnings_as_errors = []
        if self.strict_mode:
            for name, result in checks.items():
                if isinstance(result, dict) and 'warnings' in result and result['warnings']:
                    warnings_as_errors.append(name)

        overall_valid = len(failed_checks) == 0 and len(warnings_as_errors) == 0

        # Generate recommendations
        recommendations = []
        if failed_checks:
            recommendations.append(f"Address issues in: {', '.join(failed_checks)}")

        if warnings_as_errors:
            recommendations.append(f"Address warnings in: {', '.join(warnings_as_errors)}")

        if not overall_valid:
            recommendations.append("Consider re-generating embeddings if issues persist")
            recommendations.append("Check embedding model and preprocessing pipeline")

        # Summary statistics
        summary = {
            'total_embeddings': len(embeddings_data),
            'checks_run': len(checks),
            'failed_checks': len(failed_checks),
            'warnings_as_errors': len(warnings_as_errors),
            'overall_valid': overall_valid
        }

        report = {
            'overall_valid': overall_valid,
            'summary': summary,
            'checks': checks,
            'recommendations': recommendations,
            'validation_timestamp': datetime.now().isoformat(),
            'processing_time_seconds': (datetime.now() - start_time).total_seconds(),
            'strict_mode': self.strict_mode
        }

        self.logger.info(f"Validation report generated: {'PASS' if overall_valid else 'FAIL'}")
        return report

    def generate_validation_report_from_data(self, embeddings_data: List[Dict]) -> Dict[str, Any]:
        """
        Generate validation report from embeddings data directly.

        Args:
            embeddings_data: Embeddings data

        Returns:
            Validation report
        """
        return self.generate_validation_report(embeddings_data=embeddings_data)
