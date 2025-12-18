"""
RAG Analysis Module - Comprehensive embedding analysis and visualization.

This module provides tools for analyzing, validating, and visualizing
embeddings used in Retrieval-Augmented Generation systems.
"""

from .logger import get_logger, setup_analysis_logging, AnalysisLogger
from .utils import (
    load_embeddings_from_dir,
    extract_embeddings_array,
    normalize_embeddings,
    compute_cosine_similarity_batch,
    compute_pairwise_cosine_similarity,
    get_embedding_statistics,
    sample_embeddings,
    validate_embedding_format,
    create_test_embeddings_file,
    ensure_output_dirs
)
from .pca_reducer import PCAReducer
from .word_analyzer import WordAnalyzer
from .word_visualizer import WordVisualizer

# For backward compatibility and convenience
__all__ = [
    # Core utilities
    'get_logger',
    'setup_analysis_logging',
    'AnalysisLogger',

    # Data utilities
    'load_embeddings_from_dir',
    'extract_embeddings_array',
    'normalize_embeddings',
    'compute_cosine_similarity_batch',
    'compute_pairwise_cosine_similarity',
    'get_embedding_statistics',
    'sample_embeddings',
    'validate_embedding_format',
    'create_test_embeddings_file',
    'ensure_output_dirs',

    # Analysis classes
    'PCAReducer',
    'WordAnalyzer',
    'WordVisualizer'
]

# Version info
__version__ = "1.0.0"
__author__ = "Syntheverse AI"