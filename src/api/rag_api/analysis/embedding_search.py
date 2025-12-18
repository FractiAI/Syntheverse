"""
Embedding Search - Proper embedding-based semantic search.

Provides semantic search capabilities using embeddings with query embedding generation,
cosine similarity search, multi-query support, and result reranking.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

from .logger import get_logger
from .utils import extract_embeddings_array, compute_cosine_similarity_batch


class EmbeddingSearch:
    """
    Semantic search using embeddings with proper query embedding generation.

    Supports single and multi-query search with result reranking and filtering.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2",
                 device: str = "cpu", logger=None):
        """
        Initialize embedding search with sentence transformer model.

        Args:
            model_name: Sentence transformer model name
            device: Device to run model on ('cpu' or 'cuda')
            logger: Optional logger instance
        """
        self.model_name = model_name
        self.device = device
        self.logger = logger or get_logger(__name__)
        self.model = None

        if SentenceTransformer is None:
            raise ImportError("sentence-transformers is required for EmbeddingSearch. Install with: pip install sentence-transformers")

        self._load_model()

    def _load_model(self):
        """Load the sentence transformer model."""
        try:
            self.logger.info(f"Loading sentence transformer model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name, device=self.device)
            self.logger.info("Model loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load model {self.model_name}: {e}")
            raise

    def generate_query_embedding(self, query: str, normalize: bool = True) -> np.ndarray:
        """
        Generate embedding for a search query.

        Args:
            query: Search query text
            normalize: Whether to normalize the embedding

        Returns:
            Query embedding as numpy array

        Raises:
            ValueError: If query is empty or invalid
            RuntimeError: If model is not loaded or generation fails
        """
        if not query or not isinstance(query, str):
            raise ValueError("Query must be a non-empty string")

        query = query.strip()
        if not query:
            raise ValueError("Query cannot be empty after stripping whitespace")

        if len(query) > 10000:  # Reasonable limit
            self.logger.warning(f"Query is very long ({len(query)} chars), truncating")
            query = query[:10000]

        if self.model is None:
            raise RuntimeError("Sentence transformer model not loaded. Call __init__ first.")

        try:
            self.logger.debug(f"Generating embedding for query: {query[:50]}...")

            # Use model's built-in normalization if requested
            embedding = self.model.encode(
                query,
                convert_to_numpy=True,
                normalize_embeddings=normalize,
                show_progress_bar=False  # Disable for cleaner output
            )

            # Additional validation
            if not isinstance(embedding, np.ndarray):
                raise RuntimeError("Model did not return numpy array")

            if embedding.ndim != 1:
                raise RuntimeError(f"Expected 1D embedding, got {embedding.ndim}D")

            if np.any(~np.isfinite(embedding)):
                self.logger.warning("Query embedding contains non-finite values")
                embedding = np.nan_to_num(embedding, nan=0.0, posinf=1.0, neginf=-1.0)

            self.logger.debug(f"Query embedding generated, shape: {embedding.shape}")
            return embedding

        except Exception as e:
            self.logger.error(f"Failed to generate query embedding: {e}")
            raise RuntimeError(f"Query embedding generation failed: {e}") from e

    def search_by_embedding(self, query_embedding: np.ndarray,
                           embeddings_data: List[Dict],
                           top_k: int = 10,
                           min_score: float = 0.0) -> List[Dict[str, Any]]:
        """
        Search embeddings by cosine similarity to query embedding.

        Args:
            query_embedding: Query embedding vector
            embeddings_data: List of embedding dictionaries to search
            top_k: Number of top results to return
            min_score: Minimum similarity score threshold

        Returns:
            List of search results with scores and metadata
        """
        if not embeddings_data:
            return []

        if len(query_embedding.shape) != 1:
            raise ValueError("Query embedding must be 1D")

        # Extract target embeddings
        target_embeddings = extract_embeddings_array(embeddings_data)

        self.logger.info(f"Searching {len(embeddings_data)} embeddings with top_k={top_k}")

        # Compute similarities
        similarities = compute_cosine_similarity_batch(query_embedding, target_embeddings)

        # Get top k results
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for rank, idx in enumerate(top_indices, 1):
            score = float(similarities[idx])

            # Apply minimum score filter
            if score < min_score:
                continue

            chunk = embeddings_data[idx]
            result = {
                'rank': rank,
                'score': score,
                'index': int(idx),
                'text': chunk['text'],
                'metadata': chunk.get('metadata', {}),
                'pdf_filename': chunk.get('pdf_filename', 'unknown'),
                'chunk_index': chunk.get('chunk_index', 0)
            }
            results.append(result)

        self.logger.info(f"Found {len(results)} results above threshold {min_score}")
        return results

    def search_by_text(self, query: str, embeddings_data: List[Dict],
                      top_k: int = 10, min_score: float = 0.0) -> List[Dict[str, Any]]:
        """
        Search embeddings by text query (convenience method).

        Args:
            query: Text query
            embeddings_data: List of embedding dictionaries to search
            top_k: Number of top results to return
            min_score: Minimum similarity score threshold

        Returns:
            List of search results
        """
        query_embedding = self.generate_query_embedding(query)
        return self.search_by_embedding(query_embedding, embeddings_data, top_k, min_score)

    def search_by_multiple_queries(self, queries: List[str],
                                 embeddings_data: List[Dict],
                                 top_k: int = 10,
                                 combination_method: str = "max") -> List[Dict[str, Any]]:
        """
        Search using multiple queries with result combination.

        Args:
            queries: List of query strings
            embeddings_data: List of embedding dictionaries to search
            top_k: Number of top results to return
            combination_method: How to combine scores ('max', 'mean', 'sum')

        Returns:
            Combined search results
        """
        if not queries:
            return []

        if not embeddings_data:
            return []

        self.logger.info(f"Multi-query search with {len(queries)} queries, method: {combination_method}")

        # Generate embeddings for all queries
        query_embeddings = []
        for query in queries:
            embedding = self.generate_query_embedding(query)
            query_embeddings.append(embedding)

        query_embeddings = np.array(query_embeddings)

        # Extract target embeddings
        target_embeddings = extract_embeddings_array(embeddings_data)

        # Compute similarities for all query-target pairs
        all_similarities = []
        for query_emb in query_embeddings:
            similarities = compute_cosine_similarity_batch(query_emb, target_embeddings)
            all_similarities.append(similarities)

        all_similarities = np.array(all_similarities)  # Shape: (n_queries, n_targets)

        # Combine similarities across queries
        if combination_method == "max":
            combined_similarities = np.max(all_similarities, axis=0)
        elif combination_method == "mean":
            combined_similarities = np.mean(all_similarities, axis=0)
        elif combination_method == "sum":
            combined_similarities = np.sum(all_similarities, axis=0)
        else:
            raise ValueError(f"Unknown combination method: {combination_method}")

        # Get top k results
        top_indices = np.argsort(combined_similarities)[::-1][:top_k]

        results = []
        for rank, idx in enumerate(top_indices, 1):
            score = float(combined_similarities[idx])

            chunk = embeddings_data[idx]

            # Include per-query scores
            per_query_scores = [float(all_similarities[q_idx, idx]) for q_idx in range(len(queries))]

            result = {
                'rank': rank,
                'combined_score': score,
                'per_query_scores': per_query_scores,
                'index': int(idx),
                'text': chunk['text'],
                'metadata': chunk.get('metadata', {}),
                'pdf_filename': chunk.get('pdf_filename', 'unknown'),
                'chunk_index': chunk.get('chunk_index', 0)
            }
            results.append(result)

        self.logger.info(f"Multi-query search completed, found {len(results)} results")
        return results

    def rerank_results(self, results: List[Dict[str, Any]],
                      rerank_criteria: List[str] = None) -> List[Dict[str, Any]]:
        """
        Rerank search results based on additional criteria.

        Args:
            results: Search results to rerank
            rerank_criteria: Criteria to use for reranking
                           ('text_length', 'metadata_completeness', 'source_diversity')

        Returns:
            Reranked results
        """
        if not results or not rerank_criteria:
            return results

        self.logger.info(f"Reranking {len(results)} results with criteria: {rerank_criteria}")

        # Calculate reranking scores
        rerank_scores = np.zeros(len(results))

        for i, result in enumerate(results):
            score = 0

            if 'text_length' in rerank_criteria:
                # Prefer chunks with moderate text length (not too short, not too long)
                text_len = len(result['text'])
                if 100 <= text_len <= 1000:
                    score += 1.0
                elif text_len < 50 or text_len > 2000:
                    score -= 0.5

            if 'metadata_completeness' in rerank_criteria:
                # Prefer chunks with complete metadata
                metadata = result.get('metadata', {})
                completeness = len(metadata) / 10.0  # Assume up to 10 metadata fields
                score += completeness

            if 'source_diversity' in rerank_criteria:
                # Prefer diverse sources (this would need global context)
                # For now, just add a small random factor to encourage diversity
                score += np.random.random() * 0.1

            rerank_scores[i] = score

        # Sort by combined score (original similarity + reranking bonus)
        combined_scores = np.array([r['score'] for r in results]) + rerank_scores

        # Sort indices by combined score
        sorted_indices = np.argsort(combined_scores)[::-1]

        # Reorder results
        reranked_results = []
        for new_rank, old_idx in enumerate(sorted_indices, 1):
            result = results[old_idx].copy()
            result['original_rank'] = result['rank']
            result['rank'] = new_rank
            result['rerank_score'] = float(rerank_scores[old_idx])
            result['final_score'] = float(combined_scores[old_idx])
            reranked_results.append(result)

        self.logger.info("Results reranked")
        return reranked_results

    def search_with_reranking(self, query: str, embeddings_data: List[Dict],
                             top_k: int = 10, min_score: float = 0.0,
                             rerank_criteria: List[str] = None) -> List[Dict[str, Any]]:
        """
        Complete search pipeline with optional reranking.

        Args:
            query: Search query
            embeddings_data: Embeddings to search
            top_k: Number of results to return
            min_score: Minimum similarity score
            rerank_criteria: Criteria for reranking results

        Returns:
            Search results (reranked if criteria provided)
        """
        # Initial search
        results = self.search_by_text(query, embeddings_data, top_k=top_k, min_score=min_score)

        # Apply reranking if requested
        if rerank_criteria and results:
            results = self.rerank_results(results, rerank_criteria)

        return results

    def batch_search(self, queries: List[str], embeddings_data: List[Dict],
                    top_k: int = 10, min_score: float = 0.0) -> Dict[str, List[Dict[str, Any]]]:
        """
        Perform batch search for multiple queries.

        Args:
            queries: List of query strings
            embeddings_data: Embeddings to search
            top_k: Number of results per query
            min_score: Minimum similarity score

        Returns:
            Dictionary mapping queries to their search results
        """
        if not queries:
            return {}

        self.logger.info(f"Batch searching {len(queries)} queries")

        results = {}
        for query in queries:
            query_results = self.search_by_text(query, embeddings_data, top_k, min_score)
            results[query] = query_results

        self.logger.info("Batch search completed")
        return results

    def get_search_statistics(self, query: str, embeddings_data: List[Dict]) -> Dict[str, Any]:
        """
        Get comprehensive search statistics for a query.

        Args:
            query: Search query
            embeddings_data: Embeddings to search

        Returns:
            Search performance statistics
        """
        if not embeddings_data:
            return {'error': 'No embeddings provided'}

        start_time = datetime.now()

        # Generate query embedding
        query_embedding = self.generate_query_embedding(query)

        # Search all embeddings (not just top-k)
        target_embeddings = extract_embeddings_array(embeddings_data)
        similarities = compute_cosine_similarity_batch(query_embedding, target_embeddings)

        search_time = (datetime.now() - start_time).total_seconds()

        # Compute statistics
        stats = {
            'query': query,
            'total_embeddings_searched': len(embeddings_data),
            'search_time_seconds': search_time,
            'similarity_stats': {
                'mean': float(np.mean(similarities)),
                'std': float(np.std(similarities)),
                'min': float(np.min(similarities)),
                'max': float(np.max(similarities)),
                'median': float(np.median(similarities))
            },
            'score_distribution': {
                'very_high (>0.8)': int(np.sum(similarities > 0.8)),
                'high (0.6-0.8)': int(np.sum((similarities > 0.6) & (similarities <= 0.8))),
                'moderate (0.4-0.6)': int(np.sum((similarities > 0.4) & (similarities <= 0.6))),
                'low (0.2-0.4)': int(np.sum((similarities > 0.2) & (similarities <= 0.4))),
                'very_low (≤0.2)': int(np.sum(similarities <= 0.2))
            },
            'top_5_scores': similarities[np.argsort(similarities)[::-1][:5]].tolist(),
            'search_timestamp': datetime.now().isoformat()
        }

        return stats

    def find_similar_chunks(self, target_chunk: Dict, embeddings_data: List[Dict],
                           top_k: int = 5, min_score: float = 0.5) -> List[Dict[str, Any]]:
        """
        Find chunks similar to a target chunk.

        Args:
            target_chunk: Target chunk to find similar items for
            embeddings_data: All embeddings to search
            top_k: Number of similar chunks to return
            min_score: Minimum similarity score

        Returns:
            Similar chunks with scores
        """
        if 'embedding' not in target_chunk:
            raise ValueError("Target chunk must have embedding")

        target_embedding = target_chunk['embedding']
        if isinstance(target_embedding, list):
            target_embedding = np.array(target_embedding)

        # Remove target chunk from search space
        search_data = [chunk for chunk in embeddings_data if chunk is not target_chunk]

        return self.search_by_embedding(target_embedding, search_data, top_k, min_score)
