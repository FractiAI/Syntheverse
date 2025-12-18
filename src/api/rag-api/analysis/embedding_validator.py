"""
Embedding Validator - Quality assurance and validation for embeddings.

Checks embedding format, consistency, quality, and identifies potential issues.
"""

import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path

from .logger import get_logger


class EmbeddingValidator:
    """
    Comprehensive validation suite for embedding quality assurance.

    Performs format validation, dimension consistency checks, normalization
    verification, outlier detection, and metadata validation.
    """

    def __init__(self, logger=None):
        """
        Initialize validator.

        Args:
            logger: Optional logger instance
        """
        self.logger = logger or get_logger(__name__)

    def generate_validation_report(self, embeddings_data: List[Dict],
                                 norm_threshold: float = 0.1,
                                 similarity_threshold: float = 0.95) -> Dict[str, Any]:
        """
        Generate comprehensive validation report.

        Args:
            embeddings_data: List of embedding dictionaries
            norm_threshold: Threshold for norm validation
            similarity_threshold: Threshold for duplicate detection

        Returns:
            Comprehensive validation report
        """
        self.logger.info(f"Generating validation report for {len(embeddings_data)} embeddings")

        report = {
            'overall_status': 'PASS',
            'checks_run': [],
            'summary': {},
            'details': {}
        }

        # Format validation
        is_valid, errors = self.validate_format(embeddings_data)
        report['checks_run'].append('format')
        report['details']['format'] = {'valid': is_valid, 'errors': errors[:10]}  # Limit errors shown

        if not is_valid:
            report['overall_status'] = 'FAIL'

        # Dimensions check
        dim_report = self.validate_dimensions(embeddings_data)
        report['checks_run'].append('dimensions')
        report['details']['dimensions'] = dim_report

        if not dim_report['consistent']:
            report['overall_status'] = 'FAIL'

        # Norms validation
        norm_report = self.validate_norms(embeddings_data, norm_threshold)
        report['checks_run'].append('norms')
        report['details']['norms'] = norm_report

        if not norm_report['normalized'] and report['overall_status'] == 'PASS':
            report['overall_status'] = 'WARNING'

        # Similarity range check
        sim_report = self.validate_similarity_range(embeddings_data)
        report['checks_run'].append('similarity')
        report['details']['similarity'] = sim_report

        # Metadata validation
        meta_report = self.validate_metadata(embeddings_data)
        report['checks_run'].append('metadata')
        report['details']['metadata'] = meta_report

        if not meta_report['complete'] and report['overall_status'] == 'PASS':
            report['overall_status'] = 'WARNING'

        # Outlier detection
        outlier_report = self.detect_outliers(embeddings_data)
        report['checks_run'].append('outliers')
        report['details']['outliers'] = outlier_report

        if outlier_report['outlier_percentage'] > 0.1 and report['overall_status'] == 'PASS':
            report['overall_status'] = 'WARNING'

        # Generate summary
        report['summary'] = {
            'total_embeddings': len(embeddings_data),
            'status': report['overall_status'],
            'checks_passed': sum(1 for check in report['checks_run']
                               if not report['details'][check].get('issues', True)),
            'total_checks': len(report['checks_run'])
        }

        self.logger.info(f"Validation completed with status: {report['overall_status']}")
        return report

    def validate_format(self, embeddings_data: List[Dict]) -> Tuple[bool, List[str]]:
        """
        Validate basic embedding format and structure.

        Args:
            embeddings_data: List of embedding dictionaries

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        if not embeddings_data:
            errors.append("No embeddings provided")
            return False, errors

        for i, chunk in enumerate(embeddings_data):
            if not isinstance(chunk, dict):
                errors.append(f"Chunk {i} is not a dictionary")
                continue

            # Check required fields
            if 'embedding' not in chunk:
                errors.append(f"Chunk {i} missing 'embedding' field")
                continue

            embedding = chunk['embedding']
            if isinstance(embedding, list):
                if not embedding:
                    errors.append(f"Chunk {i} has empty embedding list")
                elif not all(isinstance(x, (int, float)) for x in embedding):
                    errors.append(f"Chunk {i} contains non-numeric values in embedding")
            elif isinstance(embedding, np.ndarray):
                if embedding.size == 0:
                    errors.append(f"Chunk {i} has empty embedding array")
                elif not np.issubdtype(embedding.dtype, np.number):
                    errors.append(f"Chunk {i} contains non-numeric embedding values")
            else:
                errors.append(f"Chunk {i} embedding is not a list or numpy array")

        return len(errors) == 0, errors

    def validate_dimensions(self, embeddings_data: List[Dict]) -> Dict[str, Any]:
        """
        Check that all embeddings have consistent dimensions.

        Args:
            embeddings_data: List of embedding dictionaries

        Returns:
            Dimension validation report
        """
        dimensions = []

        for chunk in embeddings_data:
            if 'embedding' in chunk:
                embedding = chunk['embedding']
                if isinstance(embedding, list):
                    dimensions.append(len(embedding))
                elif isinstance(embedding, np.ndarray):
                    dimensions.append(embedding.shape[0] if embedding.ndim > 1 else 1)

        if not dimensions:
            return {'consistent': False, 'error': 'No valid embeddings found'}

        unique_dims = set(dimensions)
        expected_dim = dimensions[0]

        return {
            'consistent': len(unique_dims) == 1,
            'expected_dimension': expected_dim,
            'unique_dimensions': sorted(unique_dims),
            'dimension_counts': {dim: dimensions.count(dim) for dim in unique_dims}
        }

    def validate_norms(self, embeddings_data: List[Dict],
                      threshold: float = 0.1) -> Dict[str, Any]:
        """
        Check if embeddings are properly normalized.

        Args:
            embeddings_data: List of embedding dictionaries
            threshold: Maximum allowed deviation from unit norm

        Returns:
            Norm validation report
        """
        norms = []

        for chunk in embeddings_data:
            if 'embedding' in chunk:
                embedding = chunk['embedding']
                if isinstance(embedding, list):
                    embedding = np.array(embedding)
                norm = np.linalg.norm(embedding)
                norms.append(norm)

        if not norms:
            return {'normalized': False, 'error': 'No valid embeddings found'}

        norms_array = np.array(norms)
        mean_norm = np.mean(norms_array)
        std_norm = np.std(norms_array)

        # Check if norms are close to 1.0
        normalized = abs(mean_norm - 1.0) < threshold and std_norm < threshold

        return {
            'normalized': normalized,
            'mean_norm': float(mean_norm),
            'std_norm': float(std_norm),
            'min_norm': float(np.min(norms_array)),
            'max_norm': float(np.max(norms_array)),
            'threshold': threshold
        }

    def validate_similarity_range(self, embeddings_data: List[Dict]) -> Dict[str, Any]:
        """
        Check that similarity values are in valid range.

        Args:
            embeddings_data: List of embedding dictionaries

        Returns:
            Similarity validation report
        """
        # Sample a subset for efficiency
        sample_size = min(1000, len(embeddings_data))
        if len(embeddings_data) > sample_size:
            indices = np.random.choice(len(embeddings_data), sample_size, replace=False)
            sample_data = [embeddings_data[i] for i in indices]
        else:
            sample_data = embeddings_data

        # Compute pairwise similarities for sample
        from .utils import compute_pairwise_cosine_similarity, extract_embeddings_array
        embeddings = extract_embeddings_array(sample_data)

        if embeddings.size == 0:
            return {'valid_range': False, 'error': 'No valid embeddings found'}

        similarities = compute_pairwise_cosine_similarity(embeddings)

        # Check range (-1 to 1 for cosine similarity)
        valid_range = np.all((similarities >= -1.01) & (similarities <= 1.01))

        return {
            'valid_range': bool(valid_range),
            'min_similarity': float(np.min(similarities)),
            'max_similarity': float(np.max(similarities)),
            'mean_similarity': float(np.mean(similarities)),
            'sample_size': sample_size
        }

    def validate_metadata(self, embeddings_data: List[Dict]) -> Dict[str, Any]:
        """
        Validate metadata completeness and consistency.

        Args:
            embeddings_data: List of embedding dictionaries

        Returns:
            Metadata validation report
        """
        total_chunks = len(embeddings_data)
        metadata_fields = {}

        for chunk in embeddings_data:
            if 'metadata' in chunk and isinstance(chunk['metadata'], dict):
                for key, value in chunk['metadata'].items():
                    if key not in metadata_fields:
                        metadata_fields[key] = {'count': 0, 'types': set()}
                    metadata_fields[key]['count'] += 1
                    metadata_fields[key]['types'].add(type(value).__name__)

        # Calculate completeness
        completeness = {}
        for field, info in metadata_fields.items():
            completeness[field] = info['count'] / total_chunks

        complete = all(comp > 0.9 for comp in completeness.values())  # 90% threshold

        return {
            'complete': complete,
            'total_chunks': total_chunks,
            'metadata_fields': list(metadata_fields.keys()),
            'field_completeness': completeness,
            'field_types': {k: list(v['types']) for k, v in metadata_fields.items()}
        }

    def detect_outliers(self, embeddings_data: List[Dict],
                       method: str = 'iqr', threshold: float = 1.5) -> Dict[str, Any]:
        """
        Detect outlier embeddings using statistical methods.

        Args:
            embeddings_data: List of embedding dictionaries
            method: Outlier detection method ('iqr', 'zscore', 'isolation_forest')
            threshold: Threshold for outlier detection

        Returns:
            Outlier detection report
        """
        from .utils import extract_embeddings_array
        embeddings = extract_embeddings_array(embeddings_data)

        if embeddings.size == 0:
            return {'outliers_detected': 0, 'error': 'No valid embeddings found'}

        # Compute norms for outlier detection
        norms = np.linalg.norm(embeddings, axis=1)

        if method == 'iqr':
            # IQR method
            q1, q3 = np.percentile(norms, [25, 75])
            iqr = q3 - q1
            lower_bound = q1 - threshold * iqr
            upper_bound = q3 + threshold * iqr

            outliers = (norms < lower_bound) | (norms > upper_bound)

        elif method == 'zscore':
            # Z-score method
            z_scores = np.abs((norms - np.mean(norms)) / np.std(norms))
            outliers = z_scores > threshold

        else:
            # Default to IQR
            q1, q3 = np.percentile(norms, [25, 75])
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            outliers = (norms < lower_bound) | (norms > upper_bound)

        outlier_count = np.sum(outliers)
        outlier_percentage = outlier_count / len(norms)

        return {
            'outliers_detected': int(outlier_count),
            'outlier_percentage': float(outlier_percentage),
            'method': method,
            'threshold': threshold,
            'total_embeddings': len(embeddings_data)
        }