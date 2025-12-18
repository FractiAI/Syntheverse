# RAG Embedding Analysis Module

Comprehensive tools for analyzing, visualizing, and validating embeddings in the Syntheverse RAG system.

## 🚀 Recent Improvements

### Enhanced Error Handling & Validation
- **Robust input validation** with detailed error messages and severity levels
- **Graceful error recovery** with skip_errors options for batch processing
- **Comprehensive type checking** and data structure validation
- **Memory-efficient processing** for large embedding datasets

### Performance Optimizations
- **Batch processing** for similarity computations on large datasets
- **Memory-aware sampling** for statistical analysis of huge embedding sets
- **Adaptive thresholds** for sparsity and outlier detection
- **Optimized numerical operations** with proper dtype handling

### Advanced Analytics
- **Quality scoring system** combining multiple metrics (norms, sparsity, outliers)
- **Hybrid outlier detection** using both IQR and Z-score methods
- **Clustering analysis** with automatic optimal cluster detection
- **Comprehensive metadata analysis** with field completeness tracking

### Production-Ready Features
- **Structured logging** with configurable levels and file output
- **Configurable matplotlib styling** for publication-quality plots
- **Comprehensive documentation** with examples and troubleshooting
- **CLI tools** for batch processing and automation

## Quick Start

### Installation

Ensure you have the required dependencies:

```bash
pip install matplotlib>=3.7.0 seaborn>=0.12.0 scikit-learn>=1.3.0 scipy>=1.10.0 sentence-transformers>=2.2.0
```

### Basic Usage

```python
from src.api.rag_api.analysis import EmbeddingAnalyzer, EmbeddingVisualizer

# Load and analyze embeddings
analyzer = EmbeddingAnalyzer()
embeddings_data = analyzer.load_embeddings("./data/vectorized/embeddings")

# Compute statistics
stats = analyzer.compute_statistics(embeddings_data)
print(f"Loaded {stats['total_embeddings']} embeddings")
print(f"Average norm: {stats['norm_mean']:.3f}")

# Generate visualizations
visualizer = EmbeddingVisualizer()
visualizer.plot_pca_scatter(embeddings_data, save_path="pca_visualization.png")
visualizer.plot_embedding_distribution(embeddings_data, save_path="distribution.png")
```

## CLI Tools

### Analyze Embeddings

Run comprehensive analysis on embeddings:

```bash
python -m src.api.rag_api.analysis.cli.analyze_embeddings \
  --embeddings-dir ./data/vectorized/embeddings \
  --output-dir ./analysis_results \
  --generate-plots \
  --pca-components 50
```

### Generate Visualizations

Create visualization plots:

```bash
python -m src.api.rag_api.analysis.cli.visualize_embeddings \
  --embeddings-dir ./data/vectorized/embeddings \
  --output-dir ./plots \
  --plot-type pca \
  --format png
```

Available plot types: `pca`, `heatmap`, `distribution`, `all`

### Validate Embeddings

Run validation checks:

```bash
python -m src.api.rag_api.analysis.cli.validate_embeddings \
  --embeddings-dir ./data/vectorized/embeddings \
  --output-file validation_report.json \
  --strict
```

## Analysis Components

### EmbeddingAnalyzer

Compute comprehensive statistics:

```python
analyzer = EmbeddingAnalyzer()
stats = analyzer.compute_statistics(embeddings_data)

# Available statistics:
# - total_embeddings: Number of embeddings
# - dimension: Vector dimension
# - norm_mean/std: Mean and std of vector norms
# - value_mean/std: Mean and std of all values
# - sparsity: Percentage of near-zero values
# - outliers: Number of statistical outliers
```

### EmbeddingVisualizer

Generate various plots:

```python
visualizer = EmbeddingVisualizer()

# PCA scatterplot (2D/3D)
visualizer.plot_pca_scatter(embeddings_data, n_components=2, save_path="pca.png")

# Similarity heatmap (sample of embeddings)
visualizer.plot_similarity_heatmap(embeddings_data, max_samples=1000, save_path="heatmap.png")

# Distribution plots
visualizer.plot_embedding_distribution(embeddings_data, save_path="distributions.png")

# Statistics dashboard
visualizer.plot_statistics_dashboard(stats, save_path="dashboard.png")
```

### PCAReducer

Dimensionality reduction:

```python
pca = PCAReducer(n_components=50)
reduced_embeddings = pca.fit_transform(embeddings_data)

# Get explained variance
variance_explained = pca.explained_variance_ratio()
print(f"Variance explained by first 5 components: {variance_explained[:5]}")
```

### EmbeddingValidator

Comprehensive validation:

```python
validator = EmbeddingValidator()
is_valid, report = validator.generate_validation_report(embeddings_dir)

# Check specific validations
dimensions_ok = validator.validate_dimensions(embeddings_data)
norms_ok = validator.validate_norms(embeddings_data)
outliers = validator.detect_outliers(embeddings_data)
```

### SimilarityAnalyzer

Analyze semantic relationships:

```python
similarity = SimilarityAnalyzer()
similarity_matrix = similarity.compute_pairwise_similarities(embeddings_data)

# Find most/least similar pairs
most_similar = similarity.find_most_similar(embeddings_data, top_k=10)
least_similar = similarity.find_least_similar(embeddings_data, top_k=10)

# Detect duplicates
duplicates = similarity.detect_duplicates(embeddings_data, threshold=0.95)
```

### EmbeddingSearch

Proper semantic search:

```python
search = EmbeddingSearch(model_name="all-MiniLM-L6-v2")
query_embedding = search.generate_query_embedding("What is hydrogen?")

# Search by embedding
results = search.search_by_embedding(query_embedding, embeddings_data, top_k=5)

# Multi-query search
queries = ["hydrogen", "fractal", "blockchain"]
multi_results = search.search_by_multiple_queries(queries, embeddings_data, top_k=3)
```

## Output Formats

### Statistics JSON

```json
{
  "total_embeddings": 1250,
  "dimension": 384,
  "norm_mean": 1.001,
  "norm_std": 0.023,
  "value_mean": 0.001,
  "value_std": 0.045,
  "sparsity": 0.12,
  "outliers": 23,
  "clusters": 5,
  "analysis_timestamp": "2024-01-15T10:30:00Z"
}
```

### Validation Report

```json
{
  "overall_valid": true,
  "checks": {
    "dimensions": {"valid": true, "details": "All vectors have consistent dimension 384"},
    "norms": {"valid": true, "details": "All vectors properly normalized"},
    "similarity_range": {"valid": true, "details": "Similarity scores in valid range [-1, 1]"},
    "outliers": {"valid": false, "details": "23 outliers detected using IQR method"}
  },
  "recommendations": ["Consider reviewing outlier embeddings for quality"]
}
```

## Integration with RAG System

The analysis module integrates seamlessly with the existing RAG pipeline:

```python
# Enhanced RAG search with proper embeddings
from src.api.rag_api.api.rag_api import RAGEngine

rag_engine = RAGEngine()
results = rag_engine.search("hydrogen fractal blockchain", top_k=5)

# Get embedding statistics
stats = rag_engine.get_embedding_statistics()
```

## Performance Considerations

- **Memory**: Large embedding sets may require batch processing
- **Speed**: PCA and similarity computation scale with O(n²)
- **Storage**: Visualizations are saved as high-quality PNG/SVG files

For large datasets (>10k embeddings), consider:
- Using `--max-samples` parameter for heatmaps
- Reducing PCA components for scatterplots
- Processing in batches for validation

## Troubleshooting

### Common Issues

1. **Memory errors**: Reduce batch sizes or use sampling
2. **Slow performance**: Use fewer PCA components or smaller samples
3. **Missing plots**: Check matplotlib backend and file permissions
4. **Validation failures**: Review embedding generation process

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Examples and Use Cases

### Quality Assessment

```python
# Assess embedding quality after generation
validator = EmbeddingValidator()
analyzer = EmbeddingAnalyzer()

embeddings = analyzer.load_embeddings("./embeddings")
is_valid, report = validator.generate_validation_report_from_data(embeddings)

if not is_valid:
    print("Embedding quality issues detected:")
    for check, result in report['checks'].items():
        if not result['valid']:
            print(f"- {check}: {result['details']}")
```

### Semantic Analysis

```python
# Analyze semantic structure of embeddings
similarity = SimilarityAnalyzer()
visualizer = EmbeddingVisualizer()

# Find clusters in embedding space
embeddings = analyzer.load_embeddings("./embeddings")
clusters = similarity.analyze_clusters(embeddings, n_clusters=5)

# Visualize semantic relationships
visualizer.plot_cluster_visualization(embeddings, clusters, save_path="clusters.png")
```

### Search Optimization

```python
# Optimize search performance
search = EmbeddingSearch()

# Test different queries
test_queries = [
    "hydrogen holographic field",
    "fractal cognitive grammar",
    "blockchain proof of contribution"
]

for query in test_queries:
    embedding = search.generate_query_embedding(query)
    results = search.search_by_embedding(embedding, embeddings_data, top_k=3)
    print(f"Query: {query}")
    print(f"Top result score: {results[0]['score']:.3f}")
```

This analysis module provides the foundation for understanding and improving the quality of embeddings in the Syntheverse RAG system.
