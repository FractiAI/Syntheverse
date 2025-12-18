"""
Utility functions for embedding analysis.

Provides helper functions for loading, processing, and manipulating embeddings.
"""

import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple


def load_embeddings_from_dir(embeddings_dir: str) -> List[Dict]:
    """
    Load all embeddings from JSON files in a directory.

    Args:
        embeddings_dir: Path to directory containing embedding JSON files

    Returns:
        List of embedding dictionaries

    Raises:
        ValueError: If directory doesn't exist or contains no valid files
    """
    embeddings_path = Path(embeddings_dir)

    if not embeddings_path.exists():
        raise ValueError(f"Embeddings directory not found: {embeddings_dir}")

    all_embeddings = []

    for json_file in embeddings_path.glob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                chunks = json.load(f)

            for chunk in chunks:
                if 'embedding' in chunk:
                    # Convert embedding to numpy array if needed
                    if isinstance(chunk['embedding'], list):
                        chunk['embedding'] = np.array(chunk['embedding'])
                    all_embeddings.append(chunk)

        except Exception as e:
            print(f"Warning: Error loading {json_file}: {e}")
            continue

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
    Normalize embeddings using specified normalization.

    Args:
        embeddings: Input embeddings array
        norm_type: Type of normalization ('l2', 'l1', or None)

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
        norms[norms == 0] = 1
        return embeddings / norms
    else:
        raise ValueError(f"Unsupported norm type: {norm_type}")


def compute_cosine_similarity_batch(query_embedding: np.ndarray,
                                  target_embeddings: np.ndarray) -> np.ndarray:
    """
    Compute cosine similarity between query and multiple target embeddings.

    Args:
        query_embedding: Single query embedding
        target_embeddings: Array of target embeddings

    Returns:
        Array of similarity scores
    """
    # Normalize query
    query_norm = np.linalg.norm(query_embedding)
    if query_norm == 0:
        return np.zeros(len(target_embeddings))

    query_normalized = query_embedding / query_norm

    # Normalize targets
    target_norms = np.linalg.norm(target_embeddings, axis=1)
    target_norms[target_norms == 0] = 1
    targets_normalized = target_embeddings / target_norms[:, np.newaxis]

    # Compute similarities
    similarities = np.dot(targets_normalized, query_normalized)

    return similarities


def compute_pairwise_cosine_similarity(embeddings: np.ndarray) -> np.ndarray:
    """
    Compute pairwise cosine similarity matrix for all embeddings.

    Args:
        embeddings: Array of embeddings

    Returns:
        Similarity matrix of shape (n_embeddings, n_embeddings)
    """
    # Normalize all embeddings
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1
    normalized_embeddings = embeddings / norms

    # Compute similarity matrix
    similarity_matrix = np.dot(normalized_embeddings, normalized_embeddings.T)

    # Ensure diagonal is 1.0
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


def validate_embedding_format(chunk: Dict) -> Tuple[bool, List[str]]:
    """
    Validate that an embedding chunk has the correct format.

    Args:
        chunk: Embedding chunk dictionary

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    # Check required fields
    if 'text' not in chunk:
        errors.append("Missing 'text' field")
    if 'embedding' not in chunk:
        errors.append("Missing 'embedding' field")
        return False, errors

    # Validate embedding
    embedding = chunk['embedding']
    if isinstance(embedding, list):
        try:
            embedding = np.array(embedding)
        except:
            errors.append("Invalid embedding format")
            return False, errors

    if not isinstance(embedding, np.ndarray):
        errors.append("Embedding must be numpy array or list")
        return False, errors

    if embedding.ndim != 1:
        errors.append(f"Embedding must be 1D array, got {embedding.ndim}D")
        return False, errors

    # Check for invalid values
    if np.any(np.isnan(embedding)) or np.any(np.isinf(embedding)):
        errors.append("Embedding contains NaN or infinite values")

    return len(errors) == 0, errors


def sample_embeddings(embeddings_data: List[Dict],
                     n_samples: int,
                     random_state: Optional[int] = None) -> List[Dict]:
    """
    Sample a subset of embeddings.

    Args:
        embeddings_data: Full list of embeddings
        n_samples: Number of samples to select
        random_state: Random seed for reproducibility

    Returns:
        Sampled embeddings list
    """
    if n_samples >= len(embeddings_data):
        return embeddings_data.copy()

    if random_state is not None:
        np.random.seed(random_state)

    indices = np.random.choice(len(embeddings_data), n_samples, replace=False)
    return [embeddings_data[i] for i in indices]
