# RAG Embedding Analysis Agents

## Purpose

Embedding analysis, visualization, validation, and statistics module for the Syntheverse RAG system.

## Key Modules

## Key Modules

### EmbeddingAnalyzer (`embedding_analyzer.py`)

Core analysis agent for computing embedding statistics and quality metrics:

- **`EmbeddingAnalyzer`**: Main analysis class
- **`load_embeddings()`**: Load embeddings from JSON files with validation
- **`compute_statistics()`**: Calculate comprehensive statistics (mean, std, norms, distributions)
- **`validate_embeddings()`**: Quality validation and consistency checks
- **`compute_similarity_matrix()`**: Pairwise similarity calculations
- **`analyze_clusters()`**: Basic clustering analysis using embeddings
- **`export_statistics()`**: Export analysis results to JSON

### EmbeddingVisualizer (`embedding_visualizer.py`)

Visualization agent for creating static plots of embedding analysis:

- **`EmbeddingVisualizer`**: Main visualization class
- **`plot_pca_scatter()`**: 2D/3D PCA scatterplots with color coding
- **`plot_similarity_heatmap()`**: Heatmap visualization of similarity matrix
- **`plot_embedding_distribution()`**: Distribution plots of embedding norms and values
- **`plot_cluster_visualization()`**: Cluster visualization in reduced space
- **`plot_statistics_dashboard()`**: Combined statistics visualization
- **`save_visualization()`**: Save plots as PNG/SVG files

### PCAReducer (`pca_reducer.py`)

Dimensionality reduction agent using Principal Component Analysis:

- **`PCAReducer`**: PCA-based dimensionality reduction
- **`fit()`**: Fit PCA model on embeddings
- **`transform()`**: Transform embeddings to reduced dimensions
- **`explained_variance_ratio()`**: Get variance explained by components
- **`get_components()`**: Access principal components
- **`save_model()`**: Persist PCA model for reuse

### EmbeddingValidator (`embedding_validator.py`)

Validation agent for ensuring embedding quality and consistency:

- **`EmbeddingValidator`**: Comprehensive validation suite
- **`validate_dimensions()`**: Check consistent vector dimensions
- **`validate_norms()`**: Validate vector normalization
- **`validate_similarity_range()`**: Check similarity score validity
- **`detect_outliers()`**: Identify outlier embeddings using statistical methods
- **`validate_metadata()`**: Check metadata completeness and consistency
- **`generate_validation_report()`**: Comprehensive validation report generation

### SimilarityAnalyzer (`similarity_analyzer.py`)

Similarity analysis agent for understanding semantic relationships:

- **`SimilarityAnalyzer`**: Advanced similarity analysis
- **`compute_pairwise_similarities()`**: Calculate all pairwise similarities
- **`find_most_similar()`**: Identify most similar embedding pairs
- **`find_least_similar()`**: Identify least similar embedding pairs
- **`analyze_similarity_distribution()`**: Distribution analysis of similarities
- **`detect_duplicates()`**: Find near-duplicate embeddings with threshold

### EmbeddingSearch (`embedding_search.py`)

Proper embedding-based search agent for semantic retrieval:

- **`EmbeddingSearch`**: Semantic search using embeddings
- **`generate_query_embedding()`**: Generate embeddings for query text
- **`search_by_embedding()`**: Cosine similarity-based search
- **`search_by_multiple_queries()`**: Multi-query search with aggregation
- **`rerank_results()`**: Result reranking using additional criteria

## Integration Points

### Input Sources

- **Vectorizer**: Receives vectorized embeddings from PDF processing
- **RAG API**: Uses embeddings for semantic search queries
- **File System**: Loads embeddings from JSON files in vectorized directory

### Output Consumers

- **Visualization Files**: Generates PNG/SVG plots for analysis
- **Statistics Reports**: Produces JSON reports with analysis results
- **Validation Reports**: Creates validation reports for quality assurance
- **CLI Tools**: Provides command-line interface for batch analysis
- **RAG API**: Enhanced search functionality with proper embeddings

## Development Guidelines

### Analysis Quality

- Implement robust statistical methods for outlier detection
- Use appropriate normalization and scaling for visualizations
- Provide comprehensive validation with clear error reporting
- Ensure reproducibility of analysis results

### Performance Considerations

- Implement batch processing for large embedding sets
- Use efficient similarity computation algorithms
- Optimize memory usage for large embedding matrices
- Provide progress indicators for long-running operations

### Visualization Standards

- Use consistent color schemes and styling
- Provide multiple output formats (PNG, SVG)
- Include proper axis labels and legends
- Ensure plots are publication-ready quality

## Common Patterns

### Analysis Workflow

1. **Load**: Load embeddings from JSON files
2. **Validate**: Run comprehensive validation checks
3. **Analyze**: Compute statistics and similarity metrics
4. **Visualize**: Generate plots and visualizations
5. **Export**: Save results and reports

### Embedding Processing

- Normalize embeddings before analysis
- Handle missing or corrupted embedding data
- Preserve metadata throughout analysis pipeline
- Use consistent data structures across modules

### Error Handling

- Provide detailed error messages for validation failures
- Log warnings for quality issues without stopping analysis
- Graceful degradation when optional dependencies are missing
- Clear indication of analysis completion status

## Dependencies

### Required Libraries

- `numpy`: Numerical computations and array operations
- `scipy`: Statistical functions and analysis
- `scikit-learn`: Machine learning algorithms (PCA, clustering)
- `matplotlib`: Plotting and visualization
- `seaborn`: Enhanced statistical visualizations
- `sentence-transformers`: Query embedding generation

### Optional Dependencies

- `plotly`: Interactive visualizations (future enhancement)
- `umap-learn`: Alternative dimensionality reduction

## Testing Strategy

### Unit Tests

- Test individual analysis methods with mock data
- Validate statistical computations against known results
- Test visualization generation (file creation)
- Check error handling and edge cases

### Integration Tests

- Test full analysis pipeline with real embeddings
- Validate CLI tools with actual data
- Performance testing with large embedding sets
- Cross-platform compatibility testing

## Usage Examples

### Basic Analysis

```python
from src.api.rag_api.analysis import EmbeddingAnalyzer, EmbeddingVisualizer

# Load and analyze embeddings
analyzer = EmbeddingAnalyzer()
embeddings = analyzer.load_embeddings("path/to/embeddings")
stats = analyzer.compute_statistics(embeddings)

# Visualize results
visualizer = EmbeddingVisualizer()
visualizer.plot_pca_scatter(embeddings, save_path="pca_plot.png")
```

### Validation Pipeline

```python
from src.api.rag_api.analysis import EmbeddingValidator

validator = EmbeddingValidator()
is_valid, report = validator.generate_validation_report("path/to/embeddings")
print(f"Validation: {'PASS' if is_valid else 'FAIL'}")
```

### CLI Usage

```bash
# Analyze embeddings
python -m src.api.rag_api.analysis.cli.analyze_embeddings --embeddings-dir ./data/vectorized/embeddings --output-dir ./analysis_results

# Generate visualizations
python -m src.api.rag_api.analysis.cli.visualize_embeddings --embeddings-dir ./data/vectorized/embeddings --plot-type all --format png

# Validate embeddings
python -m src.api.rag_api.analysis.cli.validate_embeddings --embeddings-dir ./data/vectorized/embeddings --output-file validation_report.json
```

## Future Enhancements

- Interactive web-based visualizations
- Real-time embedding monitoring
- Advanced clustering algorithms
- Embedding quality improvement suggestions
- Integration with embedding model fine-tuning
