"""
Embedding Search - Semantic search using embeddings.

Provides efficient similarity-based search capabilities for embedding datasets.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple

from .logger import get_logger
from .utils import compute_cosine_similarity_batch, extract_embeddings_array


class EmbeddingSearch:
    """
    Semantic search engine using embeddings.

    Provides efficient similarity-based search with support for
    query expansion, reranking, and multi-query search.
    """

    def __init__(self, logger=None):
        """
        Initialize embedding search.

        Args:
            logger: Optional logger instance
        """
        self.logger = logger or get_logger(__name__)

    def generate_query_embedding(self, query: str, normalize: bool = True) -> np.ndarray:
        """
        Generate embedding for search query.

        Args:
            query: Search query text

        Returns:
            Query embedding vector
        """
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError("sentence-transformers required for query embedding generation")

        # Initialize model (could be cached in production)
        model = SentenceTransformer('all-MiniLM-L6-v2')
        embedding = model.encode(query, normalize_embeddings=normalize)

        return embedding

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

        self.logger.info(f"Searching {len(embeddings_data)} embeddings with top_k={top_k}")

        # Extract target embeddings
        target_embeddings = extract_embeddings_array(embeddings_data)

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
        Search embeddings using text query.

        Args:
            query: Text query to search for
            embeddings_data: List of embedding dictionaries to search
            top_k: Number of top results to return
            min_score: Minimum similarity score threshold

        Returns:
            List of search results with scores and metadata
        """
        self.logger.info(f"Performing text search for: '{query}'")

        try:
            query_embedding = self.generate_query_embedding(query)
            return self.search_by_embedding(query_embedding, embeddings_data, top_k, min_score)
        except Exception as e:
            self.logger.error(f"Query embedding generation failed: {e}")
            return []

    def search_by_multiple_queries(self, queries: List[str],
                                 embeddings_data: List[Dict],
                                 top_k: int = 10,
                                 aggregation_method: str = 'max') -> List[Dict[str, Any]]:
        """
        Search using multiple queries with result aggregation.

        Args:
            queries: List of query strings
            embeddings_data: List of embedding dictionaries to search
            top_k: Number of top results to return
            aggregation_method: How to aggregate scores ('max', 'mean', 'sum')

        Returns:
            Aggregated search results
        """
        if not queries:
            return []

        self.logger.info(f"Searching with {len(queries)} queries using {aggregation_method} aggregation")

        # Get results for each query
        all_results = []
        for query in queries:
            results = self.search_by_text(query, embeddings_data, top_k=len(embeddings_data))
            all_results.append(results)

        if not all_results or not all_results[0]:
            return []

        # Aggregate scores across queries
        score_aggregation = {}
        result_details = {}

        for results in all_results:
            for result in results:
                idx = result['index']
                score = result['score']

                if idx not in score_aggregation:
                    score_aggregation[idx] = []
                    result_details[idx] = result

                score_aggregation[idx].append(score)

        # Apply aggregation method
        aggregated_scores = {}
        for idx, scores in score_aggregation.items():
            if aggregation_method == 'max':
                aggregated_scores[idx] = max(scores)
            elif aggregation_method == 'mean':
                aggregated_scores[idx] = np.mean(scores)
            elif aggregation_method == 'sum':
                aggregated_scores[idx] = sum(scores)
            else:
                aggregated_scores[idx] = max(scores)  # Default to max

        # Sort and return top results
        sorted_indices = sorted(aggregated_scores.items(),
                              key=lambda x: x[1], reverse=True)[:top_k]

        final_results = []
        for rank, (idx, score) in enumerate(sorted_indices, 1):
            result = result_details[idx].copy()
            result['rank'] = rank
            result['score'] = float(score)
            result['query_count'] = len(score_aggregation[idx])
            final_results.append(result)

        self.logger.info(f"Multi-query search returned {len(final_results)} results")
        return final_results

    def rerank_results(self, results: List[Dict[str, Any]],
                      reranking_criteria: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Rerank search results based on additional criteria.

        Args:
            results: Search results to rerank
            reranking_criteria: Criteria for reranking ('diversity', 'recency', 'length')

        Returns:
            Reranked results
        """
        if not results or not reranking_criteria:
            return results

        reranked = results.copy()

        for criterion in reranking_criteria:
            if criterion == 'diversity':
                # Promote diverse sources
                source_counts = {}
                for result in reranked:
                    source = result.get('pdf_filename', 'unknown')
                    source_counts[source] = source_counts.get(source, 0) + 1

                # Adjust scores based on source diversity
                for result in reranked:
                    source = result.get('pdf_filename', 'unknown')
                    diversity_bonus = 1.0 / (source_counts[source] ** 0.5)  # Diminishing returns
                    result['score'] *= diversity_bonus

            elif criterion == 'recency':
                # Assume higher chunk_index means more recent (customize as needed)
                for result in reranked:
                    chunk_idx = result.get('chunk_index', 0)
                    recency_bonus = 1.0 + (chunk_idx / 1000.0)  # Small bonus
                    result['score'] *= recency_bonus

            elif criterion == 'length':
                # Prefer chunks of moderate length
                for result in reranked:
                    text_len = len(result.get('text', ''))
                    if 100 <= text_len <= 1000:
                        length_bonus = 1.1
                    elif text_len < 50 or text_len > 2000:
                        length_bonus = 0.9
                    else:
                        length_bonus = 1.0
                    result['score'] *= length_bonus

        # Re-sort by adjusted scores
        reranked.sort(key=lambda x: x['score'], reverse=True)

        # Update ranks
        for rank, result in enumerate(reranked, 1):
            result['rank'] = rank

        self.logger.info(f"Applied reranking criteria: {reranking_criteria}")
        return reranked

    def find_similar_chunks(self, target_index: int,
                           embeddings_data: List[Dict],
                           top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Find chunks similar to a target chunk.

        Args:
            target_index: Index of target chunk in embeddings_data
            embeddings_data: List of embedding dictionaries
            top_k: Number of similar chunks to return

        Returns:
            List of similar chunks with similarity scores
        """
        if target_index >= len(embeddings_data):
            raise ValueError(f"Target index {target_index} out of range")

        target_chunk = embeddings_data[target_index]
        if 'embedding' not in target_chunk:
            raise ValueError(f"Target chunk {target_index} has no embedding")

        target_embedding = np.array(target_chunk['embedding'])

        # Remove target from search data
        search_data = embeddings_data[:target_index] + embeddings_data[target_index + 1:]

        results = self.search_by_embedding(target_embedding, search_data, top_k)

        # Adjust indices since we removed the target
        for result in results:
            if result['index'] >= target_index:
                result['index'] += 1

        return results

    def batch_search(self, queries: List[str], embeddings_data: List[Dict],
                    top_k: int = 10, batch_size: int = 10) -> List[List[Dict[str, Any]]]:
        """
        Perform batch search for multiple queries efficiently.

        Args:
            queries: List of query strings
            embeddings_data: List of embedding dictionaries to search
            top_k: Number of top results per query
            batch_size: Number of queries to process at once

        Returns:
            List of result lists, one per query
        """
        self.logger.info(f"Performing batch search for {len(queries)} queries")

        all_results = []

        # Process in batches to manage memory
        for i in range(0, len(queries), batch_size):
            batch_queries = queries[i:i + batch_size]
            self.logger.info(f"Processing batch {i//batch_size + 1}: queries {i} to {i+len(batch_queries)-1}")

            for query in batch_queries:
                results = self.search_by_text(query, embeddings_data, top_k)
                all_results.append(results)

        return all_results