#!/usr/bin/env python3
"""
Test suite for RAG analysis modules.

Tests embedding analysis, visualization, validation, PCA reduction,
similarity analysis, and search functionality.
"""

import sys
import os
import json
import numpy as np
import unittest
import tempfile
import shutil
from pathlib import Path
# No mocks allowed - using real implementations

# Add src/api to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "api"))

from rag_api.analysis import (
    EmbeddingAnalyzer, EmbeddingVisualizer, PCAReducer,
    EmbeddingValidator, SimilarityAnalyzer, EmbeddingSearch
)
from rag_api.analysis.utils import (
    load_embeddings_from_dir, extract_embeddings_array,
    normalize_embeddings, compute_cosine_similarity_batch
)
from rag_api.analysis.logger import get_logger


class TestEmbeddingAnalyzer(unittest.TestCase):
    """Test EmbeddingAnalyzer functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = EmbeddingAnalyzer()
        self.sample_embeddings = self._create_sample_embeddings()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_sample_embeddings(self, n_chunks=10, dim=384):
        """Create sample embedding data for testing"""
        np.random.seed(42)  # For reproducible tests
        embeddings = []
        for i in range(n_chunks):
            embedding = np.random.normal(0, 1, dim).tolist()
            chunk = {
                'text': f'Sample text chunk {i}',
                'embedding': embedding,
                'metadata': {'source': f'doc_{i % 3}', 'chunk_index': i},
                'chunk_index': i,
                'pdf_filename': f'document_{i % 3}.pdf'
            }
            embeddings.append(chunk)
        return embeddings

    def _create_test_files(self, embeddings_data, filename="test_embeddings.json"):
        """Create test embedding files"""
        import json
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(embeddings_data, f)
        return filepath

    def test_load_embeddings(self):
        """Test loading embeddings from JSON files"""
        # Create test file
        test_file = self._create_test_files(self.sample_embeddings)

        # Test loading from file
        loaded = self.analyzer.load_embeddings(self.temp_dir)
        self.assertEqual(len(loaded), len(self.sample_embeddings))

        # Check structure
        for chunk in loaded:
            self.assertIn('text', chunk)
            self.assertIn('embedding', chunk)
            self.assertIsInstance(chunk['embedding'], np.ndarray)
            self.assertEqual(chunk['embedding'].shape, (384,))

    def test_load_embeddings_edge_cases(self):
        """Test loading embeddings with edge cases"""
        # Test empty directory
        with self.assertRaises(ValueError):
            self.analyzer.load_embeddings("/nonexistent/directory")

        # Test with malformed data
        malformed_data = [
            {"text": "test", "embedding": "not_a_list"},  # Invalid embedding
            {"text": "test"},  # Missing embedding
            {"embedding": [1, 2, 3]},  # Missing text
        ]
        test_file = self._create_test_files(malformed_data, "malformed.json")
        loaded = self.analyzer.load_embeddings(self.temp_dir, skip_errors=True)
        # Should load empty list since all chunks are invalid
        self.assertEqual(len(loaded), 0)

        # Test with max_files limit
        large_data = [self.sample_embeddings[0]] * 5
        test_file = self._create_test_files(large_data, "large.json")
        loaded = self.analyzer.load_embeddings(self.temp_dir, max_files=1)
        self.assertGreater(len(loaded), 0)  # Should load from at least one file

    def test_compute_statistics(self):
        """Test statistics computation"""
        stats = self.analyzer.compute_statistics(self.sample_embeddings)

        # Check required fields
        required_fields = [
            'total_embeddings', 'dimension', 'norm_mean', 'norm_std',
            'value_mean', 'value_std', 'sparsity', 'outliers', 'sources',
            'quality_score', 'analysis_timestamp'
        ]
        for field in required_fields:
            self.assertIn(field, stats)

        # Check values
        self.assertEqual(stats['total_embeddings'], len(self.sample_embeddings))
        self.assertEqual(stats['dimension'], 384)
        self.assertGreaterEqual(stats['norm_mean'], 0)
        self.assertGreaterEqual(stats['quality_score'], 0)
        self.assertLessEqual(stats['quality_score'], 1)

    def test_compute_statistics_edge_cases(self):
        """Test statistics computation with edge cases"""
        # Test with empty embeddings
        with self.assertRaises(ValueError):
            self.analyzer.compute_statistics([])

        # Test with single embedding
        single_embedding = [self.sample_embeddings[0]]
        stats = self.analyzer.compute_statistics(single_embedding)
        self.assertEqual(stats['total_embeddings'], 1)

        # Test with all-zero embeddings
        zero_embeddings = [{
            'text': 'test',
            'embedding': np.zeros(384).tolist(),
            'metadata': {},
            'chunk_index': 0,
            'pdf_filename': 'test.pdf'
        }]
        stats = self.analyzer.compute_statistics(zero_embeddings)
        self.assertEqual(stats['norm_mean'], 0.0)

        # Test with very large embeddings (simulate memory constraints)
        large_dim = 1000
        large_embeddings = [{
            'text': 'test',
            'embedding': np.random.normal(0, 1, large_dim).tolist(),
            'metadata': {},
            'chunk_index': 0,
            'pdf_filename': 'test.pdf'
        }]
        stats = self.analyzer.compute_statistics(large_embeddings)
        self.assertEqual(stats['dimension'], large_dim)

    def test_validate_embeddings(self):
        """Test embedding validation"""
        validation = self.analyzer.validate_embeddings(self.sample_embeddings)

        # Should pass for well-formed data
        self.assertIn('valid', validation)
        self.assertIn('details', validation)

    def test_analyze_clusters(self):
        """Test clustering analysis"""
        clustering = self.analyzer.analyze_clusters(self.sample_embeddings, n_clusters=3)

        # Should work for sufficient data
        if len(self.sample_embeddings) >= 10:
            self.assertIn('silhouette_score', clustering)
            self.assertIn('cluster_sizes', clustering)
        else:
            self.assertIn('error', clustering)


class TestPCAReducer(unittest.TestCase):
    """Test PCAReducer functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.pca = PCAReducer(n_components=5, random_state=42)
        self.sample_embeddings = np.random.normal(0, 1, (20, 50))

    def test_fit_transform(self):
        """Test PCA fit and transform"""
        # Fit and transform
        reduced = self.pca.fit_transform(self.sample_embeddings, n_components=5)

        # Check dimensions
        self.assertEqual(reduced.shape, (20, 5))

        # Check PCA is fitted
        self.assertTrue(self.pca.is_fitted)

    def test_explained_variance(self):
        """Test explained variance computation"""
        self.pca.fit(self.sample_embeddings, n_components=5)

        variance = self.pca.explained_variance_ratio()
        self.assertEqual(len(variance), 5)
        # With 5 components out of higher dimensional space, explained variance won't sum to 1.0
        self.assertGreater(np.sum(variance), 0.0)
        self.assertLessEqual(np.sum(variance), 1.0)

    def test_save_load_model(self):
        """Test PCA model save and load"""
        self.pca.fit(self.sample_embeddings)

        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            try:
                # Save model
                self.pca.save_model(tmp.name)

                # Load model
                new_pca = PCAReducer()
                new_pca.load_model(tmp.name)

                # Check they're equivalent
                self.assertTrue(new_pca.is_fitted)
                np.testing.assert_array_almost_equal(
                    self.pca.explained_variance_ratio(),
                    new_pca.explained_variance_ratio()
                )

            finally:
                Path(tmp.name).unlink(missing_ok=True)


class TestEmbeddingVisualizer(unittest.TestCase):
    """Test EmbeddingVisualizer functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.visualizer = EmbeddingVisualizer(figsize=(8, 6), dpi=100)
        self.sample_embeddings = self._create_sample_embeddings()

    def _create_sample_embeddings(self, n_chunks=20, dim=10):
        """Create sample embeddings for visualization testing"""
        embeddings = []
        for i in range(n_chunks):
            embedding = np.random.normal(0, 1, dim).tolist()
            chunk = {
                'text': f'Test chunk {i}',
                'embedding': embedding,
                'pdf_filename': f'doc_{i % 3}.pdf',
                'chunk_index': i
            }
            embeddings.append(chunk)
        return embeddings

    def test_plot_pca_scatter(self):
        """Test PCA scatter plot generation"""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            try:
                fig = self.visualizer.plot_pca_scatter(
                    self.sample_embeddings,
                    n_components=2,
                    save_path=tmp.name
                )

                # Check figure was created
                self.assertIsNotNone(fig)

                # Check file was saved
                self.assertTrue(Path(tmp.name).exists())

            finally:
                Path(tmp.name).unlink(missing_ok=True)

    def test_plot_embedding_distribution(self):
        """Test distribution plot generation"""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            try:
                fig = self.visualizer.plot_embedding_distribution(
                    self.sample_embeddings,
                    save_path=tmp.name
                )

                self.assertIsNotNone(fig)
                self.assertTrue(Path(tmp.name).exists())

            finally:
                Path(tmp.name).unlink(missing_ok=True)

    def test_plot_statistics_dashboard(self):
        """Test statistics dashboard generation"""
        from api.rag_api.analysis import EmbeddingAnalyzer

        analyzer = EmbeddingAnalyzer()
        stats = analyzer.compute_statistics(self.sample_embeddings)

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            try:
                fig = self.visualizer.plot_statistics_dashboard(
                    stats,
                    save_path=tmp.name
                )

                self.assertIsNotNone(fig)
                self.assertTrue(Path(tmp.name).exists())

            finally:
                Path(tmp.name).unlink(missing_ok=True)


class TestEmbeddingValidator(unittest.TestCase):
    """Test EmbeddingValidator functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.validator = EmbeddingValidator()
        self.sample_embeddings = self._create_sample_embeddings()

    def _create_sample_embeddings(self, n_chunks=10, dim=384):
        """Create valid sample embeddings"""
        embeddings = []
        for i in range(n_chunks):
            embedding = np.random.normal(0, 1, dim).tolist()
            chunk = {
                'text': f'Valid text chunk {i}',
                'embedding': embedding,
                'metadata': {'source': 'test'},
                'chunk_index': i,
                'pdf_filename': 'test.pdf'
            }
            embeddings.append(chunk)
        return embeddings

    def test_validate_dimensions(self):
        """Test dimension validation"""
        result = self.validator.validate_dimensions(self.sample_embeddings)

        self.assertTrue(result['valid'])
        self.assertIn('All 10 embeddings have consistent dimension', result['details'])

    def test_validate_norms(self):
        """Test norm validation"""
        result = self.validator.validate_norms(self.sample_embeddings)

        self.assertIn('valid', result)
        self.assertIn('mean_norm', result)

    def test_validate_similarity_range(self):
        """Test similarity range validation"""
        result = self.validator.validate_similarity_range(self.sample_embeddings)

        self.assertIn('valid', result)
        self.assertIn('min_similarity', result)
        self.assertIn('max_similarity', result)

    def test_validate_metadata(self):
        """Test metadata validation"""
        result = self.validator.validate_metadata(self.sample_embeddings)

        self.assertTrue(result['valid'])
        self.assertIn('field_completeness', result)

    def test_generate_validation_report(self):
        """Test comprehensive validation report"""
        report = self.validator.generate_validation_report_from_data(self.sample_embeddings)

        required_keys = ['overall_valid', 'summary', 'checks', 'recommendations', 'validation_timestamp']
        for key in required_keys:
            self.assertIn(key, report)

        self.assertIn('checks', report)
        checks = report['checks']
        expected_checks = ['dimensions', 'norms', 'similarity_range', 'metadata']
        for check in expected_checks:
            self.assertIn(check, checks)

    def test_validate_dimensions_edge_cases(self):
        """Test dimension validation with edge cases"""
        # Test empty input
        result = self.validator.validate_dimensions([])
        self.assertFalse(result['valid'])
        self.assertIn('No embeddings provided', result['details'])

        # Test inconsistent dimensions
        inconsistent_data = [
            {'embedding': [1, 2, 3]},
            {'embedding': [1, 2, 3, 4]},
            {'embedding': [1, 2]},
        ]
        result = self.validator.validate_dimensions(inconsistent_data)
        self.assertFalse(result['valid'])

        # Test invalid embedding types
        invalid_data = [
            {'embedding': "not_an_array"},
            {'embedding': None},
        ]
        result = self.validator.validate_dimensions(invalid_data)
        self.assertFalse(result['valid'])
        self.assertIn('errors', result)

    def test_validate_norms_edge_cases(self):
        """Test norm validation with edge cases"""
        # Test with zero norms
        zero_norm_data = [
            {'embedding': np.zeros(10).tolist()},
            {'embedding': np.zeros(10).tolist()},
        ]
        result = self.validator.validate_norms(zero_norm_data)
        self.assertIn('mean_norm', result)

        # Test with extreme norms
        extreme_data = [
            {'embedding': (np.ones(10) * 100).tolist()},
            {'embedding': (np.ones(10) * 0.001).tolist()},
        ]
        result = self.validator.validate_norms(extreme_data)
        self.assertIn('extreme_norms_count', result)

    def test_strict_mode_validation(self):
        """Test validation in strict mode"""
        strict_validator = EmbeddingValidator(strict_mode=True)

        # Create data with warnings
        warning_data = self._create_sample_embeddings()
        # Add some extreme norms that might trigger warnings
        warning_data[0]['embedding'] = (np.array(warning_data[0]['embedding']) * 10).tolist()

        report = strict_validator.generate_validation_report_from_data(warning_data)
        self.assertTrue(isinstance(report, dict))  # Should still work even if stricter


class TestSimilarityAnalyzer(unittest.TestCase):
    """Test SimilarityAnalyzer functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.similarity = SimilarityAnalyzer()
        self.sample_embeddings = self._create_sample_embeddings()

    def _create_sample_embeddings(self, n_chunks=20, dim=10):
        """Create sample embeddings with some duplicates"""
        embeddings = []
        base_vectors = [
            np.random.normal(0, 1, dim),
            np.random.normal(2, 1, dim),
            np.random.normal(-2, 1, dim)
        ]

        for i in range(n_chunks):
            # Create some near-duplicates
            if i < 3:  # First 3 are unique
                vector = base_vectors[i % len(base_vectors)]
            else:  # Others are slight variations
                base = base_vectors[i % len(base_vectors)]
                vector = base + np.random.normal(0, 0.1, dim)

            chunk = {
                'text': f'Chunk {i} with content',
                'embedding': vector.tolist(),
                'chunk_index': i,
                'pdf_filename': f'doc_{i % 3}.pdf'
            }
            embeddings.append(chunk)

        return embeddings

    def test_compute_pairwise_similarities(self):
        """Test pairwise similarity computation"""
        similarity_matrix = self.similarity.compute_pairwise_similarities(self.sample_embeddings[:5])

        self.assertEqual(similarity_matrix.shape, (5, 5))
        # Diagonal should be 1.0
        np.testing.assert_array_almost_equal(np.diag(similarity_matrix), 1.0)

    def test_find_most_similar(self):
        """Test finding most similar pairs"""
        similar_pairs = self.similarity.find_most_similar(self.sample_embeddings, top_k=3)

        self.assertEqual(len(similar_pairs), 3)
        for pair in similar_pairs:
            required_keys = ['index_1', 'index_2', 'similarity', 'chunk_1', 'chunk_2']
            for key in required_keys:
                self.assertIn(key, pair)

    def test_detect_duplicates(self):
        """Test duplicate detection"""
        duplicates = self.similarity.detect_duplicates(
            self.sample_embeddings,
            threshold=0.95
        )

        # Should find some duplicate groups
        self.assertIsInstance(duplicates, list)
        for group in duplicates:
            self.assertIn('group_size', group)
            self.assertIn('indices', group)
            self.assertGreater(group['group_size'], 1)

    def test_analyze_similarity_distribution(self):
        """Test similarity distribution analysis"""
        analysis = self.similarity.analyze_similarity_distribution(self.sample_embeddings)

        required_keys = ['total_similarity_pairs', 'mean_similarity', 'min_similarity', 'max_similarity']
        for key in required_keys:
            self.assertIn(key, analysis)


class TestEmbeddingSearch(unittest.TestCase):
    """Test EmbeddingSearch functionality"""

    def setUp(self):
        """Set up test fixtures"""
        try:
            # Try to create real EmbeddingSearch instance with minimal model
            # Use a very small model for testing if available
            import time
            start_time = time.time()
            self.search = EmbeddingSearch(model_name='all-MiniLM-L6-v2')  # Small, fast model
            load_time = time.time() - start_time

            # If loading takes too long, skip the test
            if load_time > 10:  # 10 seconds max for model loading
                self.skipTest(f"Model loading too slow ({load_time:.1f}s), skipping real model tests")

        except Exception as e:
            # If model loading fails, skip the test
            self.skipTest(f"Cannot load sentence transformer model: {e}")

        self.sample_embeddings = self._create_sample_embeddings()

    def _create_sample_embeddings(self, n_chunks=10, dim=384):
        """Create sample embeddings for search testing"""
        embeddings = []
        for i in range(n_chunks):
            embedding = np.random.normal(0, 1, dim).tolist()
            chunk = {
                'text': f'Test document about topic {i % 3}',
                'embedding': embedding,
                'pdf_filename': f'doc_{i % 3}.pdf',
                'chunk_index': i
            }
            embeddings.append(chunk)
        return embeddings

    def test_generate_query_embedding(self):
        """Test query embedding generation"""
        embedding = self.search.generate_query_embedding("test query")

        self.assertIsInstance(embedding, np.ndarray)
        self.assertEqual(embedding.shape, (384,))  # all-MiniLM-L6-v2 produces 384-dim embeddings
        self.assertTrue(np.all(np.isfinite(embedding)))  # Check for valid values

    def test_search_by_embedding(self):
        """Test search by embedding"""
        query_embedding = np.random.normal(0, 1, 384)

        results = self.search.search_by_embedding(
            query_embedding,
            self.sample_embeddings,
            top_k=3
        )

        self.assertEqual(len(results), 3)
        for result in results:
            required_keys = ['rank', 'score', 'index', 'text', 'pdf_filename']
            for key in required_keys:
                self.assertIn(key, result)

    def test_search_by_text(self):
        """Test search by text query"""
        results = self.search.search_by_text("test query", self.sample_embeddings, top_k=2)

        self.assertEqual(len(results), 2)
        # Verify results have expected structure
        for result in results:
            self.assertIn('score', result)
            self.assertIn('text', result)
            self.assertGreaterEqual(result['score'], 0.0)

    def test_generate_query_embedding_edge_cases(self):
        """Test query embedding generation with edge cases"""
        # Test empty query
        with self.assertRaises(ValueError):
            self.search.generate_query_embedding("")

        with self.assertRaises(ValueError):
            self.search.generate_query_embedding("   ")

        # Test very long query (should be truncated)
        long_query = "word " * 1000
        result = self.search.generate_query_embedding(long_query)
        self.assertIsInstance(result, np.ndarray)
        self.assertEqual(result.shape, (384,))  # Should still produce valid embedding

    def test_search_by_embedding_edge_cases(self):
        """Test search by embedding with edge cases"""
        query_embedding = np.random.normal(0, 1, 384)

        # Test empty embeddings
        results = self.search.search_by_embedding(query_embedding, [])
        self.assertEqual(len(results), 0)

        # Test with min_score
        results = self.search.search_by_embedding(query_embedding, self.sample_embeddings, min_score=0.9)
        # Should return fewer or no results due to high threshold
        self.assertLessEqual(len(results), len(self.sample_embeddings))

    def test_multi_query_search(self):
        """Test multi-query search functionality"""
        queries = ["test query 1", "test query 2"]

        results = self.search.search_by_multiple_queries(queries, self.sample_embeddings, top_k=3)

        self.assertEqual(len(results), 3)
        for result in results:
            self.assertIn('per_query_scores', result)
            self.assertIn('combined_score', result)
            self.assertEqual(len(result['per_query_scores']), len(queries))

    def test_reranking(self):
        """Test result reranking functionality"""
        # Get initial results
        query_embedding = np.random.normal(0, 1, 384)
        initial_results = self.search.search_by_embedding(query_embedding, self.sample_embeddings, top_k=5)

        # Apply reranking
        reranked_results = self.search.rerank_results(initial_results, rerank_criteria=['text_length'])

        self.assertEqual(len(reranked_results), len(initial_results))
        # Check that reranking info was added
        for result in reranked_results:
            self.assertIn('original_rank', result)
            self.assertIn('rerank_score', result)
            self.assertIn('final_score', result)


class TestAnalysisUtils(unittest.TestCase):
    """Test utility functions"""

    def setUp(self):
        """Set up test fixtures"""
        self.sample_embeddings = self._create_sample_embeddings()

    def _create_sample_embeddings(self, n_chunks=5, dim=10):
        """Create sample embeddings"""
        embeddings = []
        for i in range(n_chunks):
            chunk = {
                'text': f'Text {i}',
                'embedding': np.random.normal(0, 1, dim).tolist(),
                'pdf_filename': f'doc_{i}.pdf'
            }
            embeddings.append(chunk)
        return embeddings

    def test_extract_embeddings_array(self):
        """Test embedding array extraction"""
        array = extract_embeddings_array(self.sample_embeddings)

        self.assertEqual(array.shape, (5, 10))
        self.assertIsInstance(array, np.ndarray)

    def test_normalize_embeddings(self):
        """Test embedding normalization"""
        embeddings = np.random.normal(0, 1, (5, 10))
        normalized = normalize_embeddings(embeddings, 'l2')

        # Check norms are approximately 1
        norms = np.linalg.norm(normalized, axis=1)
        np.testing.assert_array_almost_equal(norms, 1.0, decimal=5)

    def test_compute_cosine_similarity_batch(self):
        """Test batch cosine similarity computation"""
        query = np.random.normal(0, 1, 10)
        targets = np.random.normal(0, 1, (5, 10))

        similarities = compute_cosine_similarity_batch(query, targets)

        self.assertEqual(len(similarities), 5)
        self.assertTrue(all(-1 <= s <= 1 for s in similarities))


class TestRAGEngineEnhancements(unittest.TestCase):
    """Test enhanced RAG engine functionality"""

    def test_rag_engine_with_analysis(self):
        """Test that RAG engine can use analysis modules"""
        # This is a basic smoke test - full integration testing would require
        # setting up the complete RAG environment

        # Test import
        try:
            from api.rag_api.api.rag_api import RAGEngine
            # Should not fail to import
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import enhanced RAG engine: {e}")


class TestAnalysisPerformance(unittest.TestCase):
    """Test performance characteristics of analysis modules"""

    def setUp(self):
        """Set up performance test fixtures"""
        self.analyzer = EmbeddingAnalyzer()
        self.validator = EmbeddingValidator()

        # Create larger test dataset
        self.large_embeddings = []
        for i in range(50):  # Smaller for test performance
            embedding = np.random.normal(0, 1, 384).tolist()
            chunk = {
                'text': f'Performance test chunk {i} with some additional text.',
                'embedding': embedding,
                'metadata': {'source': f'doc_{i % 5}', 'chunk_index': i},
                'chunk_index': i,
                'pdf_filename': f'perf_test_{i % 5}.pdf'
            }
            self.large_embeddings.append(chunk)

    def test_large_dataset_performance(self):
        """Test performance with larger datasets"""
        import time

        start_time = time.time()
        stats = self.analyzer.compute_statistics(self.large_embeddings)
        end_time = time.time()

        processing_time = end_time - start_time

        # Should complete in reasonable time (< 2 seconds for 50 embeddings)
        self.assertLess(processing_time, 2.0, f"Processing took too long: {processing_time:.2f}s")

        # Verify results are correct
        self.assertEqual(stats['total_embeddings'], 50)
        self.assertEqual(stats['dimension'], 384)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
