# RAG Embedding Analysis Agents

## Purpose

Embedding analysis, visualization, validation, and word analysis module for the Syntheverse RAG system. Enables inspection of embedding quality, semantic relationships, retrieval performance, and word usage patterns through analytical tools and visualizations.

## Key Features

### Robustness
- Error handling with detailed validation and recovery mechanisms
- Input sanitization and type checking throughout all methods
- Memory-efficient processing for large-scale embedding analysis
- Graceful degradation when optional dependencies are unavailable

### Analytics
- Quality scoring system that combines multiple embedding metrics
- Hybrid outlier detection using statistical and IQR-based methods
- Adaptive clustering with automatic optimal cluster determination
- Metadata completeness analysis for data quality assessment
- Word analysis integration with frequency analysis and PCA associations

### Word Analysis
- Word frequency extraction and statistical analysis
- PCA-word associations linking words to embedding dimensions
- Word similarity networks for semantic relationship visualization
- Source-based word distribution analysis across documents
- TF-IDF keyword extraction for content summarization

### Performance
- Batch processing for similarity computations on large datasets
- Memory-aware sampling for statistical analysis of large embedding collections
- Optimized numerical operations with proper floating-point handling
- Configurable processing limits to prevent resource exhaustion

### Production
- Structured logging with configurable output and severity levels
- Publication-quality visualizations with customizable styling
- Validation reports with actionable recommendations
- CLI automation tools for batch processing workflows
- Organized output structure with logical directory hierarchies

## Key Modules

### WordAnalyzer (`word_analyzer.py`)

Word analysis agent for extracting and analyzing word usage patterns:

- **`WordAnalyzer`**: Main word analysis class with NLTK integration
- **`extract_words()`**: Tokenize and filter words from embedding text
- **`compute_word_frequencies()`**: Calculate comprehensive word frequency statistics
- **`compute_word_embeddings()`**: Generate average embeddings for words
- **`find_keywords_by_pca()`**: Identify words associated with PCA components
- **`analyze_word_distributions()`**: Distribution analysis by document source
- **`compute_word_similarities()`**: Similarity analysis between word embeddings
- **`export_word_analysis()`**: Save word analysis results to JSON

### WordVisualizer (`word_visualizer.py`)

Visualization agent for word analysis results with publication-quality plots:

- **`WordVisualizer`**: Main word visualization class
- **`plot_word_frequency()`**: Bar charts of most frequent words
- **`plot_word_cloud()`**: Word cloud visualization (optional wordcloud dependency)
- **`plot_words_in_pca_space()`**: Scatter plots of words in PCA-reduced space
- **`plot_word_distribution_by_source()`**: Distribution analysis across sources
- **`plot_keyword_heatmap()`**: Heatmaps of keyword-PCA component associations
- **`plot_word_similarity_network()`**: Network graphs of word relationships
- **`create_word_analysis_dashboard()`**: Comprehensive word analysis dashboard

### EmbeddingAnalyzer (`embedding_analyzer.py`)

Analysis agent for computing embedding statistics and quality metrics:

- **`EmbeddingAnalyzer`**: Main analysis class with word analysis integration
- **`load_embeddings()`**: Load embeddings from JSON files with validation
- **`compute_statistics()`**: Calculate comprehensive statistics (mean, std, norms, distributions)
- **`validate_embeddings()`**: Quality validation and consistency checks
- **`compute_similarity_matrix()`**: Pairwise similarity calculations
- **`analyze_clusters()`**: Basic clustering analysis using embeddings
- **`export_statistics()`**: Export analysis results to JSON
- **`_compute_word_statistics()`**: Integrated word analysis for embeddings

### EmbeddingVisualizer (`embedding_visualizer.py`)

Visualization agent for creating static plots of embedding analysis with word overlays:

- **`EmbeddingVisualizer`**: Main visualization class with word enhancement
- **`plot_pca_scatter()`**: 2D/3D PCA scatterplots with optional word annotations
- **`plot_similarity_heatmap()`**: Heatmap visualization of similarity matrix
- **`plot_embedding_distribution()`**: Distribution plots of embedding norms and values
- **`plot_cluster_visualization()`**: Cluster visualization in reduced space
- **`plot_statistics_dashboard()`**: Combined statistics visualization
- **`plot_words_in_pca_scatter()`**: Word-positioned PCA scatter plots
- **`plot_word_frequency_distribution()`**: Word usage statistics plots

### PCAReducer (`pca_reducer.py`)

Dimensionality reduction using Principal Component Analysis:

- **`PCAReducer`**: PCA-based dimensionality reduction
- **`fit()`**: Fit PCA model on embeddings
- **`transform()`**: Transform embeddings to reduced dimensions
- **`explained_variance_ratio()`**: Get variance explained by components
- **`get_components()`**: Access principal components
- **`find_optimal_components()`**: Determine optimal number of components
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

Similarity analysis for understanding semantic relationships:

- **`SimilarityAnalyzer`**: Advanced similarity analysis
- **`compute_pairwise_similarities()`**: Calculate all pairwise similarities
- **`find_most_similar()`**: Identify most similar embedding pairs
- **`find_least_similar()`**: Identify least similar embedding pairs
- **`analyze_similarity_distribution()`**: Distribution analysis of similarities
- **`detect_duplicates()`**: Find near-duplicate embeddings with threshold
- **`categorize_similarities()`**: Categorize similarities into meaningful ranges
- **`get_similarity_clusters()`**: Find clusters based on similarity thresholds

### EmbeddingSearch (`embedding_search.py`)

Semantic search for efficient similarity-based retrieval:

- **`EmbeddingSearch`**: Semantic search using embeddings
- **`generate_query_embedding()`**: Generate embeddings for query text
- **`search_by_embedding()`**: Cosine similarity-based search
- **`search_by_text()`**: Text-to-embedding search
- **`search_by_multiple_queries()`**: Multi-query search with aggregation
- **`rerank_results()`**: Result reranking using additional criteria
- **`find_similar_chunks()`**: Find chunks similar to target chunk
- **`batch_search()`**: Efficient batch search for multiple queries

## Integration Points

### Input Sources

- **Vectorizer**: Receives vectorized embeddings from PDF processing
- **RAG API**: Uses embeddings for semantic search queries
- **File System**: Loads embeddings from JSON files in vectorized directory
- **Word Analysis**: Extracts words from embedding text for analysis

### Output Consumers

- **Visualization Files**: Generates PNG/SVG plots in organized subdirectories
- **Statistics Reports**: Produces JSON reports with analysis results
- **Validation Reports**: Creates validation reports for quality assurance
- **Word Analysis Results**: Saves word frequency and association data
- **CLI Tools**: Provides command-line interface for batch analysis
- **RAG API**: Enhanced search functionality with proper embeddings

## Output Directory Structure

All analysis outputs are organized in a structured `output/` directory:

```
output/
├── visualizations/
│   ├── pca/
│   │   ├── pca_2d_scatter.png
│   │   ├── pca_3d_scatter.png
│   │   └── pca_variance_explained.png
│   ├── similarity/
│   │   └── similarity_heatmap.png
│   ├── statistics/
│   │   ├── statistics_dashboard.png
│   │   └── embedding_distributions.png
│   ├── clusters/
│   │   └── cluster_visualization.png
│   └── words/
│       ├── word_frequency.png
│       ├── word_cloud.png
│       ├── words_in_pca_space.png
│       ├── keyword_pca_heatmap.png
│       └── word_similarity_network.png
├── analysis/
│   ├── statistics.json
│   ├── similarity_analysis.json
│   ├── validation_report.json
│   └── word_analysis.json
└── metadata/
    ├── analysis_summary.json
    └── processing_log.txt
```

## Development Guidelines

### Analysis Quality

- Implement robust statistical methods for outlier detection
- Use appropriate normalization and scaling for visualizations
- Provide comprehensive validation with clear error reporting
- Ensure reproducibility of analysis results
- Integrate word analysis with embedding analysis for richer insights

### Word Analysis Best Practices

- Use NLTK for advanced tokenization when available
- Filter stop words and punctuation for meaningful analysis
- Consider lemmatization for better word grouping
- Analyze word distributions across different sources
- Link word usage to semantic embedding space

### Performance Considerations

- Implement batch processing for large embedding sets
- Use efficient similarity computation algorithms
- Optimize memory usage for large embedding matrices
- Provide progress indicators for long-running operations
- Sample large datasets for computationally intensive operations

### Visualization Standards

- Use consistent color schemes and styling across plots
- Provide multiple output formats (PNG, SVG) for different use cases
- Include proper axis labels, legends, and titles
- Ensure plots are publication-ready quality
- Add word annotations to embedding visualizations when relevant

## Common Patterns

### Analysis Workflow

1. **Load**: Load embeddings from JSON files with validation
2. **Validate**: Run comprehensive validation checks
3. **Analyze**: Compute statistics, similarities, and clustering
4. **Word Analysis**: Extract and analyze word usage patterns
5. **Visualize**: Generate plots and visualizations
6. **Export**: Save results and reports in organized structure

### Word Processing Pipeline

1. **Extract**: Tokenize words from embedding text
2. **Filter**: Remove stop words and normalize
3. **Count**: Compute frequency statistics
4. **Embed**: Generate word embeddings from context
5. **Associate**: Link words to PCA dimensions
6. **Visualize**: Create word-based plots and networks

### Embedding Processing

- Normalize embeddings before analysis
- Handle missing or corrupted embedding data
- Preserve metadata throughout analysis pipeline
- Use consistent data structures across modules
- Integrate word analysis for enhanced insights

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

- `nltk`: Advanced natural language processing
- `wordcloud`: Word cloud visualizations
- `networkx`: Network graph visualizations
- `plotly`: Interactive visualizations (future enhancement)

## Testing Strategy

### Unit Tests

- Test individual analysis methods with mock data
- Validate statistical computations against known results
- Test visualization generation (file creation)
- Check error handling and edge cases
- Test word extraction and analysis functions

### Integration Tests

- Test full analysis pipeline with real embeddings
- Validate CLI tools with actual data
- Performance testing with large embedding sets
- Cross-platform compatibility testing
- Word analysis integration testing

## Usage Examples

### Basic Analysis with Word Integration

```python
from src.api.rag_api.analysis import EmbeddingAnalyzer, EmbeddingVisualizer

# Load and analyze embeddings with word analysis
analyzer = EmbeddingAnalyzer()
embeddings = analyzer.load_embeddings("path/to/embeddings")
stats = analyzer.compute_statistics(embeddings, include_word_analysis=True)

# Visualize results including word analysis
visualizer = EmbeddingVisualizer()
visualizer.plot_pca_scatter(embeddings, show_words=True)
visualizer.plot_word_frequency_distribution(embeddings)
```

### Word-Focused Analysis

```python
from src.api.rag_api.analysis import WordAnalyzer, WordVisualizer

# Analyze word usage patterns
word_analyzer = WordAnalyzer()
word_freq = word_analyzer.compute_word_frequencies(embeddings)
word_similarities = word_analyzer.compute_word_similarities(embeddings)

# Visualize word analysis
word_visualizer = WordVisualizer()
word_visualizer.plot_word_frequency(word_freq['word_frequencies'])
word_visualizer.plot_word_cloud(word_freq['word_frequencies'])
```

### Validation Pipeline

```python
from src.api.rag_api.analysis import EmbeddingValidator

validator = EmbeddingValidator()
is_valid, report = validator.generate_validation_report("path/to/embeddings")
print(f"Validation: {'PASS' if is_valid else 'FAIL'}")
```

## CLI Usage

### Comprehensive Analysis

```bash
# Full analysis pipeline with word analysis
python -m src.api.rag_api.analysis.cli.analyze_embeddings --embeddings-dir ./data/vectorized/embeddings --output-dir ./output --analysis all --word-analysis

# Generate visualizations with word overlays
python -m src.api.rag_api.analysis.cli.visualize_embeddings --embeddings-dir ./data/vectorized/embeddings --output-dir ./output --plot-type all --word-analysis

# Dedicated word analysis
python -m src.api.rag_api.analysis.cli.analyze_words --embeddings-dir ./data/vectorized/embeddings --output-dir ./output --analysis all
```

### Validation

```bash
# Validate embedding quality
python -m src.api.rag_api.analysis.cli.validate_embeddings --embeddings-dir ./data/vectorized/embeddings --output-file ./output/analysis/validation_report.json
```

## Future Enhancements

- Interactive web-based visualizations
- Real-time embedding monitoring
- Advanced clustering algorithms (HDBSCAN, spectral clustering)
- Embedding quality improvement suggestions
- Integration with embedding model fine-tuning
- Temporal analysis of word usage patterns
- Multi-language word analysis support