#!/usr/bin/env python3
"""
CLI tool for comprehensive embedding analysis.

Generates statistics, performs clustering analysis, and computes similarity metrics
for embeddings stored in JSON files.
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from analysis import EmbeddingAnalyzer, SimilarityAnalyzer
from analysis.utils import load_embeddings_from_dir
from analysis.logger import setup_analysis_logging


def main():
    parser = argparse.ArgumentParser(
        description="Analyze embeddings with comprehensive statistics and similarity analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic analysis
  python analyze_embeddings.py --embeddings-dir ./data/vectorized/embeddings --output-dir ./analysis

  # Full analysis with PCA components
  python analyze_embeddings.py --embeddings-dir ./embeddings --output-dir ./results --pca-components 50

  # Analysis with custom batch size
  python analyze_embeddings.py --embeddings-dir ./embeddings --output-dir ./results --batch-size 500
        """
    )

    parser.add_argument(
        '--embeddings-dir',
        required=True,
        help='Directory containing embedding JSON files'
    )

    parser.add_argument(
        '--output-dir',
        required=True,
        help='Directory to save analysis results'
    )

    parser.add_argument(
        '--pca-components',
        type=int,
        default=50,
        help='Number of PCA components for analysis (default: 50)'
    )

    parser.add_argument(
        '--batch-size',
        type=int,
        default=1000,
        help='Batch size for similarity computations (default: 1000)'
    )

    parser.add_argument(
        '--max-samples',
        type=int,
        default=5000,
        help='Maximum number of embeddings to sample for analysis (default: 5000)'
    )

    parser.add_argument(
        '--log-file',
        help='Optional log file path'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Setup logging
    log_level = 'DEBUG' if args.verbose else 'INFO'
    setup_analysis_logging(log_file=args.log_file, level=log_level)

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("Embedding Analysis Tool")
    print("=" * 80)
    print(f"Embeddings directory: {args.embeddings_dir}")
    print(f"Output directory: {args.output_dir}")
    print(f"PCA components: {args.pca_components}")
    print(f"Batch size: {args.batch_size}")
    print(f"Max samples: {args.max_samples}")
    print()

    try:
        # Load embeddings
        print("Loading embeddings...")
        embeddings_data = load_embeddings_from_dir(args.embeddings_dir)

        if not embeddings_data:
            print("❌ No embeddings found in the specified directory")
            return 1

        print(f"✓ Loaded {len(embeddings_data)} embeddings")

        # Sample if needed
        if len(embeddings_data) > args.max_samples:
            from analysis.utils import sample_embeddings
            embeddings_data = sample_embeddings(embeddings_data, args.max_samples, random_state=42)
            print(f"✓ Sampled to {len(embeddings_data)} embeddings")

        # Initialize analyzers
        analyzer = EmbeddingAnalyzer()
        similarity_analyzer = SimilarityAnalyzer()

        # Compute statistics
        print("\nComputing statistics...")
        statistics = analyzer.compute_statistics(embeddings_data)
        analyzer.export_statistics(statistics, output_dir / "statistics.json")
        print("✓ Statistics computed and saved")

        # Compute similarity analysis
        print("\nComputing similarity analysis...")
        similarity_summary = similarity_analyzer.get_similarity_summary(embeddings_data)
        with open(output_dir / "similarity_analysis.json", 'w') as f:
            import json
            json.dump(similarity_summary, f, indent=2)
        print("✓ Similarity analysis completed and saved")

        # Clustering analysis
        print("\nPerforming clustering analysis...")
        n_clusters = min(10, len(embeddings_data) // 10)  # Reasonable cluster count
        if n_clusters >= 2:
            clustering_results = analyzer.analyze_clusters(embeddings_data, n_clusters=n_clusters)
            if 'error' not in clustering_results:
                with open(output_dir / "clustering_analysis.json", 'w') as f:
                    json.dump(clustering_results, f, indent=2)
                print("✓ Clustering analysis completed and saved")
            else:
                print(f"⚠️  Clustering analysis skipped: {clustering_results['error']}")
        else:
            print("⚠️  Clustering analysis skipped: insufficient data")

        # Generate summary report
        print("\nGenerating summary report...")
        summary = {
            'analysis_timestamp': statistics.get('analysis_timestamp'),
            'total_embeddings_analyzed': len(embeddings_data),
            'embedding_dimension': statistics.get('dimension'),
            'embedding_norm_stats': {
                'mean': statistics.get('norm_mean'),
                'std': statistics.get('norm_std'),
                'min': statistics.get('norm_min'),
                'max': statistics.get('norm_max')
            },
            'similarity_stats': {
                'mean_similarity': similarity_summary.get('distribution_analysis', {}).get('mean_similarity'),
                'duplicate_groups_found': len(similarity_summary.get('duplicate_groups', [])),
                'clusters_found': statistics.get('clusters')
            },
            'quality_metrics': {
                'sparsity': statistics.get('sparsity'),
                'outliers': statistics.get('outliers')
            },
            'source_distribution': statistics.get('sources', {}),
            'files_analyzed': list(output_dir.glob("*.json"))
        }

        with open(output_dir / "analysis_summary.json", 'w') as f:
            json.dump(summary, f, indent=2, default=str)

        # Print summary
        print("\n" + "=" * 80)
        print("ANALYSIS COMPLETE")
        print("=" * 80)
        print(f"Total embeddings analyzed: {len(embeddings_data)}")
        print(f"Embedding dimension: {statistics.get('dimension', 'N/A')}")
        print(".3f")
        print(f"Sparsity: {statistics.get('sparsity', 0):.3%}")
        print(f"Outliers detected: {statistics.get('outliers', 0)}")
        print(f"Duplicate groups found: {len(similarity_summary.get('duplicate_groups', []))}")
        print(f"Clusters identified: {statistics.get('clusters', 'N/A')}")
        print()
        print("Results saved to:")
        print(f"  Statistics: {output_dir / 'statistics.json'}")
        print(f"  Similarity analysis: {output_dir / 'similarity_analysis.json'}")
        print(f"  Clustering analysis: {output_dir / 'clustering_analysis.json'}")
        print(f"  Summary: {output_dir / 'analysis_summary.json'}")
        print("=" * 80)

        return 0

    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        if args.verbose:
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
