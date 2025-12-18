"""
Word Analyzer - Extract and analyze word usage patterns from embeddings.

Provides comprehensive word analysis including frequency analysis, PCA associations,
and semantic relationships between words in embedding space.
"""

import re
import string
from collections import Counter, defaultdict
from typing import List, Dict, Any, Optional, Tuple, Set
import numpy as np
from pathlib import Path

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    from sklearn.feature_extraction.text import TfidfVectorizer
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

from .logger import get_logger


class WordAnalyzer:
    """
    Comprehensive word analysis for embedding datasets.

    Extracts words from embedding text, computes frequencies, identifies keywords,
    and analyzes relationships with PCA dimensions and embedding space.
    """

    def __init__(self, logger=None, use_nltk: bool = True):
        """
        Initialize word analyzer.

        Args:
            logger: Optional logger instance
            use_nltk: Whether to use NLTK for advanced tokenization
        """
        self.logger = logger or get_logger(__name__)
        self.use_nltk = use_nltk and NLTK_AVAILABLE

        if self.use_nltk:
            try:
                # Download required NLTK data
                nltk.data.find('corpora/stopwords')
                nltk.data.find('corpora/wordnet')
            except LookupError:
                self.logger.info("Downloading NLTK data...")
                nltk.download('stopwords', quiet=True)
                nltk.download('wordnet', quiet=True)

            self.stop_words = set(stopwords.words('english'))
            self.lemmatizer = WordNetLemmatizer()
        else:
            # Basic English stop words
            self.stop_words = {
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                'should', 'may', 'might', 'must', 'can', 'shall', 'this', 'that',
                'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me',
                'him', 'her', 'us', 'them', 'my', 'your', 'his', 'its', 'our', 'their'
            }
            self.lemmatizer = None

        # Common punctuation and special characters to filter
        self.punctuation = string.punctuation + '—–""''•·'

    def extract_words(self, text: str, normalize: bool = True,
                     remove_stopwords: bool = True) -> List[str]:
        """
        Extract and tokenize words from text.

        Args:
            text: Input text to tokenize
            normalize: Whether to lowercase and lemmatize
            remove_stopwords: Whether to filter stop words

        Returns:
            List of extracted words
        """
        if not text or not isinstance(text, str):
            return []

        # Basic tokenization
        words = re.findall(r'\b\w+\b', text.lower() if normalize else text)

        # Filter short words and pure numbers
        words = [w for w in words if len(w) > 2 and not w.isdigit()]

        # Remove punctuation
        words = [w.strip(self.punctuation) for w in words]
        words = [w for w in words if w]

        # Remove stop words
        if remove_stopwords:
            words = [w for w in words if w not in self.stop_words]

        # Lemmatization
        if normalize and self.lemmatizer:
            words = [self.lemmatizer.lemmatize(w) for w in words]

        return words

    def compute_word_frequencies(self, embeddings_data: List[Dict],
                                top_k: Optional[int] = None) -> Dict[str, Any]:
        """
        Compute word frequency statistics across all embeddings.

        Args:
            embeddings_data: List of embedding dictionaries
            top_k: Number of top words to return (None for all)

        Returns:
            Dictionary with frequency statistics
        """
        self.logger.info(f"Computing word frequencies for {len(embeddings_data)} embeddings")

        all_words = []
        word_by_source = defaultdict(Counter)
        word_positions = defaultdict(list)  # Track which chunks contain each word

        for i, chunk in enumerate(embeddings_data):
            if 'text' not in chunk:
                continue

            words = self.extract_words(chunk['text'])
            all_words.extend(words)

            # Track by source
            source = chunk.get('pdf_filename', 'unknown')
            word_by_source[source].update(words)

            # Track word positions
            for word in set(words):  # Use set to avoid duplicates per chunk
                word_positions[word].append(i)

        # Overall frequencies
        word_freq = Counter(all_words)
        total_words = sum(word_freq.values())
        unique_words = len(word_freq)

        # Get top words
        if top_k:
            top_words = word_freq.most_common(top_k)
        else:
            top_words = word_freq.most_common()

        # Compute statistics
        frequencies = list(word_freq.values())
        if frequencies:
            freq_mean = np.mean(frequencies)
            freq_std = np.std(frequencies)
            freq_median = np.median(frequencies)
        else:
            freq_mean = freq_std = freq_median = 0.0

        # Word diversity by source
        source_diversity = {}
        for source, counter in word_by_source.items():
            source_diversity[source] = {
                'unique_words': len(counter),
                'total_words': sum(counter.values()),
                'top_words': counter.most_common(10)
            }

        return {
            'total_words': total_words,
            'unique_words': unique_words,
            'word_frequencies': dict(word_freq),
            'top_words': top_words,
            'frequency_stats': {
                'mean': freq_mean,
                'std': freq_std,
                'median': freq_median
            },
            'source_diversity': source_diversity,
            'word_positions': dict(word_positions)
        }

    def compute_word_embeddings(self, embeddings_data: List[Dict]) -> Dict[str, np.ndarray]:
        """
        Compute average embedding vectors for each word.

        Args:
            embeddings_data: List of embedding dictionaries

        Returns:
            Dictionary mapping words to their average embedding vectors
        """
        self.logger.info("Computing word embeddings")

        word_vectors = defaultdict(list)
        word_counts = defaultdict(int)

        for chunk in embeddings_data:
            if 'text' not in chunk or 'embedding' not in chunk:
                continue

            words = self.extract_words(chunk['text'])
            embedding = np.array(chunk['embedding'])

            # Add this chunk's embedding to each word that appears in it
            for word in set(words):  # Use set to avoid duplicates
                word_vectors[word].append(embedding)
                word_counts[word] += 1

        # Compute averages
        word_embeddings = {}
        for word, vectors in word_vectors.items():
            if vectors:
                avg_embedding = np.mean(vectors, axis=0)
                # Re-normalize
                norm = np.linalg.norm(avg_embedding)
                if norm > 0:
                    avg_embedding = avg_embedding / norm
                word_embeddings[word] = avg_embedding

        self.logger.info(f"Computed embeddings for {len(word_embeddings)} words")
        return word_embeddings

    def find_keywords_by_pca(self, embeddings_data: List[Dict],
                           pca_components: np.ndarray,
                           top_k: int = 10) -> Dict[str, Any]:
        """
        Find keywords associated with each PCA component.

        Args:
            embeddings_data: List of embedding dictionaries
            pca_components: PCA components matrix (n_components x n_features)
            top_k: Number of top keywords per component

        Returns:
            Dictionary with keyword associations for each PCA component
        """
        self.logger.info(f"Finding keywords for {pca_components.shape[0]} PCA components")

        # Get word embeddings
        word_embeddings = self.compute_word_embeddings(embeddings_data)

        if not word_embeddings:
            return {}

        # Convert word embeddings to array for matrix operations
        words = list(word_embeddings.keys())
        word_embedding_matrix = np.array([word_embeddings[w] for w in words])

        # Project word embeddings onto PCA components
        # This gives us the association strength of each word with each component
        word_component_scores = word_embedding_matrix @ pca_components.T

        # For each component, find the most associated words
        component_keywords = {}
        for i in range(pca_components.shape[0]):
            component_scores = word_component_scores[:, i]

            # Get absolute values for importance (direction doesn't matter for keywords)
            abs_scores = np.abs(component_scores)

            # Get top words by absolute score
            top_indices = np.argsort(abs_scores)[::-1][:top_k]
            top_words = [(words[idx], float(component_scores[idx])) for idx in top_indices]

            component_keywords[f'component_{i}'] = {
                'top_keywords': top_words,
                'explained_variance': float(np.var(component_scores))  # Rough importance measure
            }

        return {
            'component_keywords': component_keywords,
            'words_analyzed': len(words),
            'components_analyzed': pca_components.shape[0]
        }

    def analyze_word_distributions(self, embeddings_data: List[Dict]) -> Dict[str, Any]:
        """
        Analyze word distribution patterns across documents/sources.

        Args:
            embeddings_data: List of embedding dictionaries

        Returns:
            Distribution analysis results
        """
        self.logger.info("Analyzing word distributions by source")

        # Get word frequencies by source
        freq_results = self.compute_word_frequencies(embeddings_data, top_k=None)

        # Compute TF-IDF like scores
        tfidf_scores = {}
        total_docs = len(freq_results['source_diversity'])

        for word in freq_results['word_frequencies'].keys():
            # Document frequency (how many sources contain this word)
            df = sum(1 for source_stats in freq_results['source_diversity'].values()
                    if word in dict(source_stats['top_words']))

            if df > 0:
                idf = np.log(total_docs / df)
                tfidf_scores[word] = freq_results['word_frequencies'][word] * idf

        # Sort by TF-IDF
        top_tfidf = sorted(tfidf_scores.items(), key=lambda x: x[1], reverse=True)[:50]

        # Analyze word exclusivity (words unique to specific sources)
        exclusive_words = {}
        for source, stats in freq_results['source_diversity'].items():
            source_words = set(dict(stats['top_words']).keys())
            other_words = set()
            for other_source, other_stats in freq_results['source_diversity'].items():
                if other_source != source:
                    other_words.update(dict(other_stats['top_words']).keys())

            exclusive = source_words - other_words
            exclusive_words[source] = list(exclusive)

        return {
            'tfidf_keywords': top_tfidf,
            'exclusive_words': exclusive_words,
            'source_comparison': freq_results['source_diversity']
        }

    def compute_word_similarities(self, embeddings_data: List[Dict],
                                word_embeddings: Optional[Dict[str, np.ndarray]] = None,
                                top_k_words: int = 100) -> Dict[str, Any]:
        """
        Compute similarities between word embeddings.

        Args:
            embeddings_data: List of embedding dictionaries
            word_embeddings: Pre-computed word embeddings (optional)
            top_k_words: Number of most frequent words to analyze

        Returns:
            Word similarity analysis results
        """
        self.logger.info("Computing word similarities")

        if word_embeddings is None:
            word_embeddings = self.compute_word_embeddings(embeddings_data)

        if not word_embeddings:
            return {}

        # Get most frequent words
        freq_results = self.compute_word_frequencies(embeddings_data, top_k=top_k_words)
        top_words = [word for word, _ in freq_results['top_words']]

        # Filter to words we have embeddings for
        words_with_embeddings = [w for w in top_words if w in word_embeddings]

        if len(words_with_embeddings) < 2:
            return {}

        # Compute pairwise similarities
        word_vectors = np.array([word_embeddings[w] for w in words_with_embeddings])
        similarity_matrix = word_vectors @ word_vectors.T

        # Find most similar pairs
        most_similar = []
        least_similar = []

        # Get upper triangle indices (avoiding diagonal)
        n = len(words_with_embeddings)
        for i in range(n):
            for j in range(i + 1, n):
                sim = float(similarity_matrix[i, j])
                pair = (words_with_embeddings[i], words_with_embeddings[j], sim)

                # Track most similar
                if len(most_similar) < 20:
                    most_similar.append(pair)
                else:
                    min_sim_idx = np.argmin([p[2] for p in most_similar])
                    if sim > most_similar[min_sim_idx][2]:
                        most_similar[min_sim_idx] = pair

                # Track least similar
                if len(least_similar) < 20:
                    least_similar.append(pair)
                else:
                    max_sim_idx = np.argmax([p[2] for p in least_similar])
                    if sim < least_similar[max_sim_idx][2]:
                        least_similar[max_sim_idx] = pair

        most_similar.sort(key=lambda x: x[2], reverse=True)
        least_similar.sort(key=lambda x: x[2])

        return {
            'words_analyzed': words_with_embeddings,
            'most_similar_pairs': most_similar,
            'least_similar_pairs': least_similar,
            'similarity_matrix': similarity_matrix.tolist(),
            'word_embeddings_count': len(word_embeddings)
        }

    def export_word_analysis(self, analysis_results: Dict[str, Any],
                           output_path: str) -> None:
        """
        Export word analysis results to JSON file.

        Args:
            analysis_results: Analysis results dictionary
            output_path: Path to save results
        """
        import json

        # Convert numpy arrays to lists for JSON serialization
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

        serializable_results = convert_for_json(analysis_results)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Word analysis exported to {output_path}")





