# RAG Analysis CLI Agents

## Purpose

Command-line interface tools for automated embedding analysis, validation, and visualization workflows in the Syntheverse RAG system.

## Key Tools

### analyze_embeddings.py

Batch analysis CLI for comprehensive embedding evaluation:

- **`analyze_embeddings`**: Main CLI entry point for embedding analysis
- **`--embeddings-dir`**: Directory containing embedding JSON files
- **`--output-dir`**: Output directory for analysis results
- **`--analysis`**: Analysis types (statistics, similarity, clusters, validation)
- **`--word-analysis`**: Include word frequency and pattern analysis
- **`--batch-size`**: Processing batch size for large datasets

### validate_embeddings.py

Validation CLI for embedding quality assurance:

- **`validate_embeddings`**: Comprehensive validation of embedding files
- **`--embeddings-dir`**: Source directory with embedding files
- **`--output-file`**: JSON report file path
- **`--strict`**: Enable strict validation mode
- **`--detailed`**: Include detailed validation metrics

### visualize_embeddings.py

Visualization CLI for generating analysis plots:

- **`visualize_embeddings`**: Generate publication-quality visualizations
- **`--embeddings-dir`**: Source embedding directory
- **`--output-dir`**: Output directory for plots
- **`--plot-type`**: Visualization types (pca, similarity, statistics, clusters)
- **`--word-analysis`**: Include word-based visualizations

## Integration Points

### Input Sources

- **Analysis Directory**: Receives processed embeddings from analysis modules
- **File System**: Reads JSON embedding files from vectorized directories
- **Configuration**: Accepts command-line parameters for customization

### Output Consumers

- **Analysis Reports**: Generates JSON reports for automated processing
- **Visualization Files**: Creates PNG/SVG plots for documentation and reports
- **Validation Reports**: Produces quality assurance reports
- **CI/CD Pipelines**: Supports automated testing and validation workflows

## Usage Patterns

### Comprehensive Analysis Pipeline

```bash
# Full analysis with word integration
python analyze_embeddings.py \
  --embeddings-dir ../data/vectorized/embeddings \
  --output-dir ../../output \
  --analysis all \
  --word-analysis \
  --batch-size 100
```

### Quality Validation

```bash
# Validate embedding quality
python validate_embeddings.py \
  --embeddings-dir ../data/vectorized/embeddings \
  --output-file ../../output/validation_report.json \
  --strict \
  --detailed
```

### Visualization Generation

```bash
# Generate all visualization types
python visualize_embeddings.py \
  --embeddings-dir ../data/vectorized/embeddings \
  --output-dir ../../output/visualizations \
  --plot-type all \
  --word-analysis
```

## Development Guidelines

- Implement consistent CLI argument patterns
- Provide helpful usage messages and examples
- Support both interactive and automated usage
- Handle errors gracefully with informative messages
- Generate structured output formats for automation

## Dependencies

- **Click**: Command-line interface framework
- **Pathlib**: Cross-platform path handling
- **JSON**: Structured data output
- **Analysis Modules**: Core analysis functionality

## Cross-References

- **Parent**: [analysis/AGENTS.md](../AGENTS.md) - Main analysis suite
- **Related**:
  - [embedding_analyzer.py](../embedding_analyzer.py) - Core analysis engine
  - [embedding_visualizer.py](../embedding_visualizer.py) - Visualization tools
  - [embedding_validator.py](../embedding_validator.py) - Validation logic
  - [word_analyzer.py](../word_analyzer.py) - Word analysis functionality
  - [word_visualizer.py](../word_visualizer.py) - Word visualization tools
