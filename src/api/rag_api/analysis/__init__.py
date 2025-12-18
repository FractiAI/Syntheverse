"""
Syntheverse RAG Embedding Analysis Module

This module provides comprehensive tools for analyzing, visualizing, and validating
embeddings in the Syntheverse RAG system. Includes PCA visualization, statistics,
similarity analysis, and proper embedding-based search functionality.

Main Components:
- EmbeddingAnalyzer: Statistics and analysis
- EmbeddingVisualizer: PCA plots and visualizations
- PCAReducer: Dimensionality reduction
- EmbeddingValidator: Quality validation
- SimilarityAnalyzer: Similarity analysis
- EmbeddingSearch: Proper embedding-based search
"""

from .embedding_analyzer import EmbeddingAnalyzer
from .embedding_visualizer import EmbeddingVisualizer
from .pca_reducer import PCAReducer
from .embedding_validator import EmbeddingValidator
from .similarity_analyzer import SimilarityAnalyzer
from .embedding_search import EmbeddingSearch
from .utils import load_embeddings_from_dir, extract_embeddings_array, normalize_embeddings
from .logger import get_logger

__all__ = [
    'EmbeddingAnalyzer',
    'EmbeddingVisualizer',
    'PCAReducer',
    'EmbeddingValidator',
    'SimilarityAnalyzer',
    'EmbeddingSearch',
    'load_embeddings_from_dir',
    'extract_embeddings_array',
    'normalize_embeddings',
    'get_logger'
]
