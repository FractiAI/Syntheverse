# RAG Analysis CLI Tools

Command-line interface utilities for RAG document analysis, visualization, and processing.

## Overview

This directory provides CLI tools for analyzing, processing, and visualizing document embeddings and semantic relationships in the RAG system.

## Available Tools

### Embedding Analysis (`analyze_embeddings.py`)
Statistical analysis of vector embeddings and semantic spaces.

```bash
# Analyze embeddings from a JSON file
python analyze_embeddings.py --input embeddings.json --output analysis.json

# Generate detailed statistics report
python analyze_embeddings.py --input data.json --stats --visualize
```

### Similarity Analysis (`analyze_words.py`)
Semantic similarity analysis between documents and terms.

```bash
# Find similar documents
python analyze_words.py --query "hydrogen fractal" --top-k 10

# Analyze term relationships
python analyze_words.py --terms "quantum,fractal,blockchain" --similarity-matrix
```

### Validation Tools (`validate_embeddings.py`)
Embedding quality assessment and consistency checking.

```bash
# Validate embedding quality
python validate_embeddings.py --embeddings vectors.npy --check-quality

# Detect outliers in embedding space
python validate_embeddings.py --embeddings data.json --outliers --threshold 0.95
```

### Visualization (`visualize_embeddings.py`)
Interactive visualization of embedding spaces and relationships.

```bash
# Create 2D visualization
python visualize_embeddings.py --embeddings vectors.npy --method pca --dimensions 2

# Generate similarity heatmap
python visualize_embeddings.py --embeddings data.json --heatmap --save plot.png
```

## Common Usage Patterns

### Quality Assessment Pipeline
```bash
# 1. Load and validate embeddings
python validate_embeddings.py --embeddings production_vectors.npy --comprehensive

# 2. Analyze statistical properties
python analyze_embeddings.py --input vectors.npy --stats --distribution

# 3. Visualize embedding space
python visualize_embeddings.py --embeddings vectors.npy --method t-sne --interactive
```

### Similarity Search Workflow
```bash
# 1. Analyze query terms
python analyze_words.py --query "machine learning blockchain" --expand

# 2. Find similar documents
python analyze_words.py --query "expanded terms" --documents corpus.json --ranking

# 3. Visualize results
python visualize_embeddings.py --query-results search_results.json --network-graph
```

## Configuration

### CLI Arguments
All tools support common configuration options:

```bash
--input, -i        Input file path (JSON, NPY, or CSV)
--output, -o       Output file path for results
--config, -c       Configuration file path
--verbose, -v      Enable verbose logging
--quiet, -q        Suppress non-error output
--help, -h         Show help message
```

### Configuration File
```json
{
  "embedding": {
    "dimensions": 768,
    "model": "sentence-transformers/all-MiniLM-L6-v2",
    "normalization": true
  },
  "analysis": {
    "similarity_threshold": 0.8,
    "clustering_algorithm": "hdbscan",
    "visualization_method": "pca"
  },
  "output": {
    "format": "json",
    "compression": "gzip",
    "save_intermediates": false
  }
}
```

## Integration

### Pipeline Integration
```bash
# Complete analysis pipeline
python analyze_embeddings.py -i embeddings.npy -o stats.json &&
python validate_embeddings.py -i embeddings.npy -o quality.json &&
python visualize_embeddings.py -i embeddings.npy -o plots/
```

### API Integration
```python
from cli.analyze_embeddings import EmbeddingAnalyzer
from cli.validate_embeddings import EmbeddingValidator

# Programmatic usage
analyzer = EmbeddingAnalyzer(config_path="config.json")
stats = analyzer.analyze("embeddings.npy")

validator = EmbeddingValidator()
quality_report = validator.validate(embeddings, comprehensive=True)
```

## Output Formats

### Analysis Results (JSON)
```json
{
  "statistics": {
    "total_vectors": 10000,
    "dimensions": 768,
    "mean_similarity": 0.234,
    "clusters_found": 15
  },
  "quality_metrics": {
    "isotropy": 0.89,
    "uniformity": 0.76,
    "separation": 0.92
  },
  "visualization_data": {
    "method": "pca",
    "coordinates": [[0.1, 0.2], [0.3, 0.4], ...]
  }
}
```

### Validation Report
```json
{
  "passed": true,
  "score": 0.94,
  "checks": {
    "dimensionality": "passed",
    "normalization": "passed",
    "outlier_detection": "warning"
  },
  "recommendations": [
    "Consider removing 2% outlier vectors",
    "Normalization is optimal"
  ]
}
```

## Performance Considerations

### Memory Usage
- Large embedding files may require chunked processing
- Use `--chunk-size` parameter for memory-constrained environments
- Consider using `--streaming` mode for very large datasets

### Processing Speed
- GPU acceleration available for compatible hardware
- Batch processing for multiple files
- Parallel processing options for multi-core systems

## Error Handling

### Common Issues
- **Memory errors**: Use chunked processing or increase system memory
- **File format errors**: Ensure correct JSON/NPY file formats
- **Dimension mismatches**: Verify all embeddings have consistent dimensions

### Logging
```bash
# Enable debug logging
python analyze_embeddings.py --verbose --log-level DEBUG

# Save logs to file
python validate_embeddings.py --log-file analysis.log
```

## Documentation

- [AGENTS.md](AGENTS.md) - Detailed component documentation
- [FRACTAL.md](FRACTAL.md) - Fractal analysis and patterns
- [Analysis Suite](../../AGENTS.md) - Analysis tools overview
