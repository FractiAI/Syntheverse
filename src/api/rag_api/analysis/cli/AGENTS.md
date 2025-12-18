# Embedding Analysis CLI Tools

## Purpose

Command-line interface tools for embedding analysis, visualization, and validation workflows.

## Key Modules

### Analyze Embeddings (`analyze_embeddings.py`)

Comprehensive embedding analysis and statistics:

```bash
python -m src.api.rag_api.analysis.cli.analyze_embeddings \
    --embeddings-dir ./src/data/vectorized/embeddings \
    --output-dir ./analysis_results
```

- Compute embedding statistics (mean, std, norms)
- Similarity matrix calculation
- Cluster analysis
- Export results to JSON

### Visualize Embeddings (`visualize_embeddings.py`)

Static visualization generation:

```bash
python -m src.api.rag_api.analysis.cli.visualize_embeddings \
    --embeddings-dir ./src/data/vectorized/embeddings \
    --plot-type all --format png
```

- PCA scatter plots (2D and 3D)
- Similarity heatmaps
- Distribution histograms
- Statistics dashboards

### Validate Embeddings (`validate_embeddings.py`)

Quality assurance and validation:

```bash
python -m src.api.rag_api.analysis.cli.validate_embeddings \
    --embeddings-dir ./src/data/vectorized/embeddings \
    --output-file ./analysis_results/validation_report.json
```

- Dimension consistency checks
- Norm validation
- Outlier detection
- Metadata completeness verification

## Integration Points

- Uses analysis modules from parent `analysis/` directory
- Reads embeddings from `src/data/vectorized/embeddings/`
- Outputs to `analysis_results/` by default
- Supports batch processing for large datasets

## Common Options

| Option | Description | Default |
|--------|-------------|---------|
| `--embeddings-dir` | Path to embeddings directory | Required |
| `--output-dir` | Output directory for results | `./analysis_results` |
| `--format` | Output format (png, svg) | `png` |
| `--verbose` | Enable verbose logging | False |

## Development Guidelines

- Follow argparse conventions for CLI arguments
- Provide progress indicators for long operations
- Support both file and directory inputs
- Exit with appropriate codes (0=success, 1=failure)

## File Structure

```
cli/
├── __init__.py              # Package initialization
├── analyze_embeddings.py    # Analysis CLI
├── validate_embeddings.py   # Validation CLI
├── visualize_embeddings.py  # Visualization CLI
└── AGENTS.md                # This documentation
```

## Cross-References

- **Parent**: [analysis/AGENTS.md](../AGENTS.md) - Analysis module
- **Output**: [analysis_results/AGENTS.md](../../../../../analysis_results/AGENTS.md) - Results storage
- **Input**: [src/data/vectorized/AGENTS.md](../../../../data/vectorized/AGENTS.md) - Source embeddings

