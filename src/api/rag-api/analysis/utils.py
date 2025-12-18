"""
Utility functions for RAG analysis operations.

Provides helper functions for loading embeddings, data processing,
and common analysis operations.
"""

import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union
import warnings


def load_embeddings_from_dir(embeddings_dir: str, max_files: Optional[int] = None,
                           skip_errors: bool = True) -> List[Dict]:
    """
    Load all embedding files from a directory.

    Args:
        embeddings_dir: Directory containing JSON embedding files
        max_files: Maximum number of files to load (None for all)
        skip_errors: Whether to skip files with errors

    Returns:
        List of embedding dictionaries
    """
    embeddings_dir = Path(embeddings_dir)
    if not embeddings_dir.exists():
        raise FileNotFoundError(f"Embeddings directory not found: {embeddings_dir}")

    all_embeddings = []
    json_files = list(embeddings_dir.glob("*.json"))

    if max_files:
        json_files = json_files[:max_files]

    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                file_embeddings = json.load(f)

            if isinstance(file_embeddings, list):
                all_embeddings.extend(file_embeddings)
            else:
                all_embeddings.append(file_embeddings)

        except Exception as e:
            if skip_errors:
                warnings.warn(f"Skipping file {json_file}: {e}")
            else:
                raise

    return all_embeddings


def extract_embeddings_array(embeddings_data: List[Dict]) -> np.ndarray:
    """
    Extract embeddings as a numpy array from embedding dictionaries.

    Args:
        embeddings_data: List of embedding dictionaries

    Returns:
        Numpy array of shape (n_embeddings, embedding_dim)
    """
    if not embeddings_data:
        return np.array([])

    embeddings = []
    for chunk in embeddings_data:
        embedding = chunk.get('embedding')
        if embedding is not None:
            if isinstance(embedding, list):
                embedding = np.array(embedding)
            embeddings.append(embedding)

    return np.array(embeddings)


def normalize_embeddings(embeddings: np.ndarray,
                        norm_type: str = 'l2') -> np.ndarray:
    """
    Normalize embeddings using specified norm type.

    Args:
        embeddings: Array of embeddings
        norm_type: Normalization type ('l2', 'l1', or None)

    Returns:
        Normalized embeddings array
    """
    if embeddings.size == 0 or norm_type is None:
        return embeddings

    if norm_type == 'l2':
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1  # Avoid division by zero
        return embeddings / norms
    elif norm_type == 'l1':
        norms = np.linalg.norm(embeddings, ord=1, axis=1, keepdims=True)
        norms[norms == 0] = 1  # Avoid division by zero
        return embeddings / norms
    else:
        raise ValueError(f"Unsupported norm type: {norm_type}")


def compute_cosine_similarity_batch(query_embedding: np.ndarray,
                                  target_embeddings: np.ndarray) -> np.ndarray:
    """
    Compute cosine similarities between a query embedding and multiple target embeddings.

    Args:
        query_embedding: Single embedding vector (1D)
        target_embeddings: Array of embeddings (n_embeddings, embedding_dim)

    Returns:
        Array of cosine similarity scores
    """
    if query_embedding.ndim != 1:
        raise ValueError("Query embedding must be 1D")

    if target_embeddings.ndim != 2:
        raise ValueError("Target embeddings must be 2D")

    # Normalize inputs
    query_norm = normalize_embeddings(query_embedding.reshape(1, -1))
    target_norm = normalize_embeddings(target_embeddings)

    # Compute cosine similarity
    similarities = np.dot(target_norm, query_norm.T).flatten()

    # Clamp to [-1, 1] range (numerical stability)
    similarities = np.clip(similarities, -1.0, 1.0)

    return similarities


def compute_pairwise_cosine_similarity(embeddings: np.ndarray) -> np.ndarray:
    """
    Compute pairwise cosine similarities between all embeddings.

    Args:
        embeddings: Array of embeddings (n_embeddings, embedding_dim)

    Returns:
        Symmetric similarity matrix (n_embeddings, n_embeddings)
    """
    if embeddings.ndim != 2:
        raise ValueError("Embeddings must be 2D array")

    # Normalize embeddings
    normalized = normalize_embeddings(embeddings)

    # Compute similarity matrix
    similarity_matrix = np.dot(normalized, normalized.T)

    # Ensure symmetry (numerical stability)
    similarity_matrix = (similarity_matrix + similarity_matrix.T) / 2

    # Clamp to [-1, 1] range
    similarity_matrix = np.clip(similarity_matrix, -1.0, 1.0)

    # Set diagonal to 1.0 (perfect self-similarity)
    np.fill_diagonal(similarity_matrix, 1.0)

    return similarity_matrix


def get_embedding_statistics(embeddings: np.ndarray) -> Dict[str, Any]:
    """
    Compute basic statistics for embeddings.

    Args:
        embeddings: Array of embeddings

    Returns:
        Dictionary with statistics
    """
    if embeddings.size == 0:
        return {}

    norms = np.linalg.norm(embeddings, axis=1)
    all_values = embeddings.flatten()

    stats = {
        'count': len(embeddings),
        'dimension': embeddings.shape[1] if len(embeddings.shape) > 1 else 0,
        'norm_mean': float(np.mean(norms)),
        'norm_std': float(np.std(norms)),
        'norm_min': float(np.min(norms)),
        'norm_max': float(np.max(norms)),
        'value_mean': float(np.mean(all_values)),
        'value_std': float(np.std(all_values)),
        'value_min': float(np.min(all_values)),
        'value_max': float(np.max(all_values)),
        'sparsity': float(np.sum(np.abs(all_values) < 1e-6) / len(all_values))
    }

    return stats


def sample_embeddings(embeddings_data: List[Dict], n_samples: int,
                     random_state: Optional[int] = None) -> List[Dict]:
    """
    Sample a subset of embeddings for analysis.

    Args:
        embeddings_data: List of embedding dictionaries
        n_samples: Number of samples to return
        random_state: Random seed for reproducibility

    Returns:
        Sampled embeddings list
    """
    if n_samples >= len(embeddings_data):
        return embeddings_data

    rng = np.random.RandomState(random_state)
    indices = rng.choice(len(embeddings_data), size=n_samples, replace=False)

    return [embeddings_data[i] for i in indices]


def validate_embedding_format(chunk: Dict) -> Tuple[bool, List[str]]:
    """
    Validate the format of an embedding chunk.

    Args:
        chunk: Embedding dictionary to validate

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    if not isinstance(chunk, dict):
        errors.append("Chunk must be a dictionary")
        return False, errors

    if 'embedding' not in chunk:
        errors.append("Missing 'embedding' field")
    else:
        embedding = chunk['embedding']
        if not isinstance(embedding, (list, np.ndarray)):
            errors.append("'embedding' must be a list or numpy array")
        elif isinstance(embedding, list) and not embedding:
            errors.append("'embedding' list cannot be empty")
        elif isinstance(embedding, np.ndarray) and embedding.size == 0:
            errors.append("'embedding' array cannot be empty")

    # Optional field validations
    if 'text' in chunk and not isinstance(chunk['text'], str):
        errors.append("'text' field must be a string")

    if 'metadata' in chunk and not isinstance(chunk['metadata'], dict):
        errors.append("'metadata' field must be a dictionary")

    return len(errors) == 0, errors


def create_test_embeddings_file(file_path: str, num_chunks: int = 10,
                              dim: int = 384, random_state: Optional[int] = 42) -> List[Dict]:
    """
    Create a test embeddings file for development and testing.

    Args:
        file_path: Path to save the test file
        num_chunks: Number of embedding chunks to create
        dim: Embedding dimension
        random_state: Random seed

    Returns:
        The created embeddings data
    """
    rng = np.random.RandomState(random_state)

    test_data = []
    sample_texts = [
        "This is a sample text for testing embeddings.",
        "Machine learning models use vector representations.",
        "Natural language processing involves text analysis.",
        "Semantic search finds meaning-based results.",
        "Vector databases store high-dimensional data.",
        "Word embeddings capture semantic relationships.",
        "Transformers revolutionized NLP architectures.",
        "Contextual embeddings adapt to word usage.",
        "Retrieval-augmented generation combines search and synthesis.",
        "Large language models understand complex patterns."
    ]

    for i in range(num_chunks):
        # Create random embedding
        embedding = rng.normal(0, 1, dim).astype(np.float32)
        # Normalize
        embedding = embedding / np.linalg.norm(embedding)

        chunk = {
            'text': sample_texts[i % len(sample_texts)] + f" Chunk {i}.",
            'embedding': embedding.tolist(),
            'metadata': {
                'chunk_index': i,
                'pdf_filename': f'document_{i % 3}.pdf',
                'page': i % 10 + 1
            }
        }
        test_data.append(chunk)

    # Save to file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, indent=2, ensure_ascii=False)

    return test_data


def ensure_output_dirs(output_base: str) -> Dict[str, Path]:
    """
    Ensure all output directories exist and return their paths.

    Args:
        output_base: Base output directory path

    Returns:
        Dictionary mapping directory names to Path objects
    """
    base_path = Path(output_base)

    dirs = {
        'visualizations': base_path / 'visualizations',
        'analysis': base_path / 'analysis',
        'metadata': base_path / 'metadata',
        'pca': base_path / 'visualizations' / 'pca',
        'similarity': base_path / 'visualizations' / 'similarity',
        'statistics': base_path / 'visualizations' / 'statistics',
        'clusters': base_path / 'visualizations' / 'clusters',
        'words': base_path / 'visualizations' / 'words'
    }

    for dir_path in dirs.values():
        dir_path.mkdir(parents=True, exist_ok=True)

    return dirs