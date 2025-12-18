#!/usr/bin/env python3
"""
CLI tool for comprehensive embedding analysis.

Performs statistics computation, similarity analysis, clustering,
validation, and generates analysis reports.
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from analysis import (
    EmbeddingAnalyzer, SimilarityAnalyzer, PCAReducer,
    load_embeddings_from_dir, ensure_output_dirs, setup_analysis_logging
)


def main():
    parser = argparse.ArgumentParser(
        description="Comprehensive embedding analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full analysis pipeline
  python analyze_embeddings.py --embeddings-dir ./embeddings --output-dir ./output --analysis all

  # Quick statistics only
  python analyze_embeddings.py --embeddings-dir ./embeddings --output-dir ./output --analysis statistics

  # Similarity analysis with sampling
  python analyze_embeddings.py --embeddings-dir ./embeddings --output-dir ./output --analysis similarity --max-samples 5000

  # Include word analysis
  python analyze_embeddings.py --embeddings-dir ./embeddings --output-dir ./output --analysis all --word-analysis
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
        help='Base output directory for analysis results'
    )

    parser.add_argument(
        '--analysis',
        choices=['statistics', 'similarity', 'clustering', 'validation', 'all'],
        default='all',
        help='Type of analysis to perform'
    )

    parser.add_argument(
        '--max-samples',
        type=int,
        default=None,
        help='Maximum number of embeddings to sample for analysis'
    )

    parser.add_argument(
        '--word-analysis',
        action='store_true',
        help='Include word analysis in comprehensive analysis'
    )

    parser.add_argument(
        '--clustering-max-k',
        type=int,
        default=10,
        help='Maximum number of clusters for clustering analysis'
    )

    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level'
    )

    args = parser.parse_args()

    # Setup logging
    logger = setup_analysis_logging(log_level=args.log_level)
    logger.info("Starting comprehensive embedding analysis")

    # Ensure output directories exist
    output_dirs = ensure_output_dirs(args.output_dir)
    analysis_dir = output_dirs['analysis']
    metadata_dir = output_dirs['metadata']

    try:
        # Load embeddings
        print("Loading embeddings...")
        embeddings_data = load_embeddings_from_dir(args.embeddings_dir)

        if not embeddings_data:
            print("❌ No embeddings found in the specified directory")
            return 1

        print(f"✓ Loaded {len(embeddings_data)} embeddings")

        # Sample if needed
        if args.max_samples and len(embeddings_data) > args.max_samples:
            from analysis.utils import sample_embeddings
            embeddings_data = sample_embeddings(embeddings_data, args.max_samples, random_state=42)
            print(f"✓ Sampled to {len(embeddings_data)} embeddings")

        # Initialize analyzers
        analyzer = EmbeddingAnalyzer(logger=logger)
        similarity_analyzer = SimilarityAnalyzer(logger=logger)

        results = {}

        # Compute statistics
        if args.analysis in ['statistics', 'all']:
            print("\nComputing statistics...")
            statistics = analyzer.compute_statistics(
                embeddings_data, include_clustering=True,
                clustering_max_k=args.clustering_max_k
            )
            results['statistics'] = statistics

            # Save statistics
            stats_file = analysis_dir / "statistics.json"
            analyzer.export_statistics(statistics, str(stats_file))
            print("✓ Statistics computed and saved")

        # Compute similarity analysis
        if args.analysis in ['similarity', 'all']:
            print("\nComputing similarity analysis...")
            similarity_summary = similarity_analyzer.get_similarity_summary(embeddings_data)
            results['similarity'] = similarity_summary

            # Save similarity analysis
            sim_file = analysis_dir / "similarity_analysis.json"
            with open(sim_file, 'w') as f:
                import json
                json.dump(similarity_summary, f, indent=2)
            print("✓ Similarity analysis completed and saved")

        # Perform clustering analysis
        if args.analysis in ['clustering', 'all']:
            print("\nPerforming clustering analysis...")
            if len(embeddings_data) >= 10:  # Need minimum data for clustering
                n_clusters = min(args.clustering_max_k, len(embeddings_data) // 10)
                if n_clusters >= 2:
                    from analysis.utils import extract_embeddings_array
                    embeddings = extract_embeddings_array(embeddings_data)

                    # Use analyzer's clustering method
                    clustering_results = analyzer.analyze_clusters(
                        embeddings_data, n_clusters=n_clusters
                    )
                    results['clustering'] = clustering_results

                    # Save clustering results
                    cluster_file = analysis_dir / "clustering_analysis.json"
                    with open(cluster_file, 'w') as f:
                        import json
                        json.dump(clustering_results, f, indent=2, default=str)
                    print("✓ Clustering analysis completed and saved")
                else:
                    print("⚠️  Not enough data for meaningful clustering")
            else:
                print("⚠️  Not enough data for clustering analysis")

        # Perform validation
        if args.analysis in ['validation', 'all']:
            print("\nPerforming validation...")
            from analysis import EmbeddingValidator
            validator = EmbeddingValidator(logger=logger)
            validation_report = validator.generate_validation_report(embeddings_data)
            results['validation'] = validation_report

            # Save validation report
            validation_file = analysis_dir / "validation_report.json"
            with open(validation_file, 'w') as f:
                import json
                json.dump(validation_report, f, indent=2)
            print("✓ Validation completed and saved")

        # Perform word analysis if requested
        if args.word_analysis and args.analysis == 'all':
            print("\nPerforming word analysis...")
            from analysis import WordAnalyzer
            word_analyzer = WordAnalyzer(logger=logger)

            # Compute word frequencies
            word_freq = word_analyzer.compute_word_frequencies(embeddings_data, top_k=100)
            results['word_frequencies'] = word_freq

            # Compute word distributions
            word_dist = word_analyzer.analyze_word_distributions(embeddings_data)
            results['word_distributions'] = word_dist

            # Save word analysis
            word_file = analysis_dir / "word_analysis.json"
            word_analyzer.export_word_analysis({
                'word_frequencies': word_freq,
                'word_distributions': word_dist
            }, str(word_file))
            print("✓ Word analysis completed and saved")

        # Create analysis summary
        print("\nCreating analysis summary...")
        summary = {
            'total_embeddings': len(embeddings_data),
            'analysis_performed': list(results.keys()),
            'timestamp': str(Path(__file__).stat().st_mtime),
            'output_directories': {
                'analysis': str(analysis_dir),
                'metadata': str(metadata_dir)
            }
        }

        # Add key metrics to summary
        if 'statistics' in results:
            stats = results['statistics']
            summary['key_metrics'] = {
                'total_embeddings': stats.get('total_embeddings', 0),
                'dimension': stats.get('dimension', 0),
                'norm_mean': stats.get('norm_mean', 0),
                'sparsity': stats.get('sparsity', 0)
            }

        # Save summary
        summary_file = metadata_dir / "analysis_summary.json"
        with open(summary_file, 'w') as f:
            import json
            json.dump(summary, f, indent=2)

        # Save processing log
        log_file = metadata_dir / "processing_log.txt"
        with open(log_file, 'w') as f:
            f.write("Embedding Analysis Processing Log\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"Analysis performed: {', '.join(results.keys())}\n")
            f.write(f"Embeddings processed: {len(embeddings_data)}\n")
            f.write(f"Output directory: {args.output_dir}\n")
            f.write(f"Timestamp: {summary['timestamp']}\n")

        print("✓ Analysis summary created")

        print("
✅ Comprehensive analysis completed successfully!"        print(f"📁 Analysis results saved to: {args.output_dir}")
        print(f"📊 Analysis files: {analysis_dir}")
        print(f"📋 Metadata: {metadata_dir}")
        print(f"📈 Analyses performed: {', '.join(results.keys())}")

        return 0

    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())