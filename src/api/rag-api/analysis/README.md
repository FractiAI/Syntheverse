# RAG Embedding Analysis Module

Comprehensive toolkit for analyzing, visualizing, and validating embeddings in Retrieval-Augmented Generation (RAG) systems. Features advanced word analysis, PCA visualizations, similarity analysis, and quality validation.

## 🚀 Quick Start

### Installation

```bash
cd src/api/rag-api
pip install -r requirements_api.txt
```

### Basic Usage

```python
from analysis import EmbeddingAnalyzer, EmbeddingVisualizer

# Analyze embeddings
analyzer = EmbeddingAnalyzer()
stats = analyzer.compute_statistics(embeddings_data, include_word_analysis=True)

# Visualize results
visualizer = EmbeddingVisualizer()
visualizer.plot_pca_scatter(embeddings_data, save_path="pca_plot.png")
```

### CLI Usage

```bash
# Comprehensive analysis
python -m analysis.cli.analyze_embeddings --embeddings-dir ./embeddings --output-dir ./output --analysis all

# Generate visualizations
python -m analysis.cli.visualize_embeddings --embeddings-dir ./embeddings --output-dir ./output --plot-type all

# Word analysis
python -m analysis.cli.analyze_words --embeddings-dir ./embeddings --output-dir ./output --analysis all
```

## 📊 Features

### Core Analysis
- **Statistical Analysis**: Comprehensive embedding statistics and quality metrics
- **Clustering**: K-means clustering with automatic cluster number selection
- **Similarity Analysis**: Pairwise similarity computation and distribution analysis
- **Outlier Detection**: Statistical outlier identification and reporting

### Word Analysis
- **Word Frequency**: Extract and analyze word usage patterns
- **PCA-Word Associations**: Link words to principal components
- **Word Similarity**: Semantic similarity analysis between words
- **TF-IDF Keywords**: Extract important keywords using TF-IDF scoring
- **Source Distribution**: Analyze word usage across different documents

### Visualization
- **PCA Scatter Plots**: 2D/3D scatter plots with optional word overlays
- **Similarity Heatmaps**: Visualize embedding similarity matrices
- **Word Clouds**: Frequency-based word cloud generation
- **Distribution Plots**: Statistical distribution analysis
- **Network Graphs**: Word similarity networks (with NetworkX)

### Validation
- **Format Validation**: Check embedding structure and data types
- **Dimension Consistency**: Verify all embeddings have same dimensions
- **Normalization Checks**: Validate proper vector normalization
- **Metadata Completeness**: Assess metadata quality and completeness

## 🏗️ Architecture

### Key Classes

| Class | Purpose |
|-------|---------|
| `EmbeddingAnalyzer` | Core analysis engine with statistics and clustering |
| `WordAnalyzer` | Word extraction, frequency analysis, and PCA associations |
| `EmbeddingVisualizer` | Static plotting for embeddings and statistics |
| `WordVisualizer` | Word-specific visualizations (clouds, networks, PCA overlays) |
| `PCAReducer` | Dimensionality reduction using PCA |
| `EmbeddingValidator` | Quality validation and consistency checks |
| `SimilarityAnalyzer` | Advanced similarity computation and analysis |
| `EmbeddingSearch` | Semantic search using embeddings |

### Output Structure

All analysis outputs are organized in subfolders:

```
output/
├── visualizations/     # PNG/SVG plots
│   ├── pca/           # PCA scatter plots and variance plots
│   ├── similarity/    # Similarity heatmaps
│   ├── statistics/    # Distribution plots and dashboards
│   ├── clusters/      # Cluster visualizations
│   └── words/         # Word analysis plots
├── analysis/          # JSON analysis results
│   ├── statistics.json
│   ├── similarity_analysis.json
│   ├── validation_report.json
│   └── word_analysis.json
└── metadata/          # Processing logs and summaries
    ├── analysis_summary.json
    └── processing_log.txt
```

## 📈 Analysis Types

### Embedding Analysis

```python
from analysis import EmbeddingAnalyzer

analyzer = EmbeddingAnalyzer()

# Basic statistics
stats = analyzer.compute_statistics(embeddings)

# With clustering
stats = analyzer.compute_statistics(embeddings, include_clustering=True)

# With word analysis
stats = analyzer.compute_statistics(embeddings, include_word_analysis=True)

# Export results
analyzer.export_statistics(stats, "output/analysis/statistics.json")
```

### Word Analysis

```python
from analysis import WordAnalyzer

word_analyzer = WordAnalyzer()

# Word frequencies
frequencies = word_analyzer.compute_word_frequencies(embeddings)

# PCA associations
pca_keywords = word_analyzer.find_keywords_by_pca(embeddings, pca_components)

# Word similarities
similarities = word_analyzer.compute_word_similarities(embeddings)

# Export results
word_analyzer.export_word_analysis({
    'frequencies': frequencies,
    'pca_keywords': pca_keywords,
    'similarities': similarities
}, "output/analysis/word_analysis.json")
```

### Visualization

```python
from analysis import EmbeddingVisualizer, WordVisualizer

# Embedding visualizations
viz = EmbeddingVisualizer()
viz.plot_pca_scatter(embeddings, save_path="output/visualizations/pca/pca_2d.png")
viz.plot_similarity_heatmap(embeddings, save_path="output/visualizations/similarity/heatmap.png")

# Word visualizations
word_viz = WordVisualizer()
word_viz.plot_word_frequency(frequencies['word_frequencies'],
                           save_path="output/visualizations/words/frequency.png")
word_viz.plot_word_cloud(frequencies['word_frequencies'],
                        save_path="output/visualizations/words/cloud.png")
```

### Validation

```python
from analysis import EmbeddingValidator

validator = EmbeddingValidator()
report = validator.generate_validation_report(embeddings)

# Check specific aspects
dimensions_ok = validator.validate_dimensions(embeddings)
norms_ok = validator.validate_norms(embeddings)
```

## 🔧 CLI Tools

### analyze_embeddings.py

Comprehensive embedding analysis pipeline:

```bash
# Full analysis with word integration
python -m analysis.cli.analyze_embeddings \
    --embeddings-dir ./data/embeddings \
    --output-dir ./output \
    --analysis all \
    --word-analysis

# Statistics only
python -m analysis.cli.analyze_embeddings \
    --embeddings-dir ./data/embeddings \
    --output-dir ./output \
    --analysis statistics
```

### visualize_embeddings.py

Generate visualization plots:

```bash
# All visualizations with word overlays
python -m analysis.cli.visualize_embeddings \
    --embeddings-dir ./data/embeddings \
    --output-dir ./output \
    --plot-type all \
    --word-analysis \
    --format png

# PCA plots only
python -m analysis.cli.visualize_embeddings \
    --embeddings-dir ./data/embeddings \
    --output-dir ./output \
    --plot-type pca \
    --pca-components 3
```

### analyze_words.py

Dedicated word analysis tool:

```bash
# Comprehensive word analysis
python -m analysis.cli.analyze_words \
    --embeddings-dir ./data/embeddings \
    --output-dir ./output \
    --analysis all

# Word frequency only
python -m analysis.cli.analyze_words \
    --embeddings-dir ./data/embeddings \
    --output-dir ./output \
    --analysis frequency
```

### validate_embeddings.py

Quality validation:

```bash
# Full validation
python -m analysis.cli.validate_embeddings \
    --embeddings-dir ./data/embeddings \
    --output-file ./output/analysis/validation.json

# Format check only
python -m analysis.cli.validate_embeddings \
    --embeddings-dir ./data/embeddings \
    --checks format \
    --output-file ./validation.json
```

## 🎨 Visualization Examples

### PCA with Word Overlays

```python
# Create PCA plot with word labels
viz = EmbeddingVisualizer()
fig = viz.plot_pca_scatter(embeddings, show_words=True, top_words=30)
plt.show()
```

### Word Similarity Network

```python
# Generate word similarity network
word_viz = WordVisualizer()
network = word_viz.plot_word_similarity_network(similarities)
plt.show()
```

### Comprehensive Dashboard

```python
# Create analysis dashboard
word_viz.create_word_analysis_dashboard(word_analysis_results)
plt.show()
```

## 🔍 Advanced Usage

### Custom Analysis Pipeline

```python
# Load embeddings
from analysis import load_embeddings_from_dir
embeddings = load_embeddings_from_dir("path/to/embeddings")

# Custom analysis workflow
analyzer = EmbeddingAnalyzer()
word_analyzer = WordAnalyzer()

# Compute statistics
stats = analyzer.compute_statistics(embeddings, include_word_analysis=True)

# Additional word analysis
word_freq = word_analyzer.compute_word_frequencies(embeddings)
word_embeddings = word_analyzer.compute_word_embeddings(embeddings)

# PCA analysis
from analysis import PCAReducer
pca = PCAReducer(n_components=2)
reduced = pca.fit_transform(extract_embeddings_array(embeddings))

# Custom visualizations
viz = EmbeddingVisualizer()
viz.plot_pca_scatter(embeddings, save_path="custom_pca.png")
```

### Semantic Search

```python
from analysis import EmbeddingSearch

search = EmbeddingSearch()

# Text search
results = search.search_by_text("machine learning", embeddings, top_k=5)

# Multiple queries
results = search.search_by_multiple_queries(
    ["AI", "neural networks", "deep learning"],
    embeddings,
    top_k=10
)

# Rerank results
reranked = search.rerank_results(results, ['diversity', 'length'])
```

## 📋 Requirements

### Required
- Python 3.8+
- numpy
- scipy
- scikit-learn
- matplotlib
- seaborn
- sentence-transformers

### Optional
- nltk (for advanced tokenization)
- wordcloud (for word clouds)
- networkx (for similarity networks)

## 🧪 Testing

Run the test suite:

```bash
python -m pytest tests/test_rag_analysis.py -v
```

## 🤝 Contributing

1. Follow the existing code style and patterns
2. Add comprehensive docstrings
3. Include unit tests for new functionality
4. Update documentation for new features
5. Ensure CLI tools are properly documented

## 📄 License

This module is part of the Syntheverse project. See project license for details.

## 🔗 Related

- [Syntheverse RAG API](../api/README.md)
- [Vectorization Pipeline](../vectorizer/README.md)
- [Main Documentation](../../README.md)