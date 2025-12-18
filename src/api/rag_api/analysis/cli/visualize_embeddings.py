#!/usr/bin/env python3
"""
CLI tool for generating embedding visualizations.

Creates static plots (PNG/SVG) for PCA analysis, similarity heatmaps,
distribution plots, and cluster visualizations.
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from analysis import EmbeddingVisualizer, EmbeddingAnalyzer
from analysis.utils import load_embeddings_from_dir
from analysis.logger import setup_analysis_logging


def main():
    parser = argparse.ArgumentParser(
        description="Generate visualizations for embedding analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate all visualizations
  python visualize_embeddings.py --embeddings-dir ./embeddings --output-dir ./plots --plot-type all

  # Generate only PCA plots
  python visualize_embeddings.py --embeddings-dir ./embeddings --output-dir ./plots --plot-type pca

  # Generate heatmaps with sampling
  python visualize_embeddings.py --embeddings-dir ./embeddings --output-dir ./plots --plot-type heatmap --max-samples 1000

  # Generate SVG plots
  python visualize_embeddings.py --embeddings-dir ./embeddings --output-dir ./plots --format svg
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
        help='Directory to save visualization plots'
    )

    parser.add_argument(
        '--plot-type',
        choices=['pca', 'heatmap', 'distribution', 'cluster', 'statistics', 'all'],
        default='all',
        help='Type of plot to generate (default: all)'
    )

    parser.add_argument(
        '--format',
        choices=['png', 'svg', 'both'],
        default='png',
        help='Output format for plots (default: png)'
    )

    parser.add_argument(
        '--max-samples',
        type=int,
        default=5000,
        help='Maximum number of embeddings to sample for visualization (default: 5000)'
    )

    parser.add_argument(
        '--pca-components',
        type=int,
        default=2,
        help='Number of PCA components for scatter plots (2 or 3, default: 2)'
    )

    parser.add_argument(
        '--cluster-by',
        choices=['pdf_filename', 'chunk_index', 'none'],
        default='pdf_filename',
        help='How to color clusters in PCA plots (default: pdf_filename)'
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
    print("Embedding Visualization Tool")
    print("=" * 80)
    print(f"Embeddings directory: {args.embeddings_dir}")
    print(f"Output directory: {args.output_dir}")
    print(f"Plot type: {args.plot_type}")
    print(f"Format: {args.format}")
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

        # Initialize visualizer
        visualizer = EmbeddingVisualizer()

        # Determine formats to generate
        formats = []
        if args.format == 'both':
            formats = ['png', 'svg']
        else:
            formats = [args.format]

        # Generate plots based on type
        plot_types = [args.plot_type] if args.plot_type != 'all' else ['pca', 'heatmap', 'distribution', 'statistics']

        generated_plots = []

        for plot_type in plot_types:
            print(f"\nGenerating {plot_type} plots...")

            try:
                if plot_type == 'pca':
                    # Generate PCA scatter plots
                    for fmt in formats:
                        # 2D PCA
                        fig_2d = visualizer.plot_pca_scatter(
                            embeddings_data,
                            n_components=2,
                            color_by=args.cluster_by if args.cluster_by != 'none' else None,
                            save_path=output_dir / f"pca_2d.{fmt}",
                            title="2D PCA Embedding Visualization"
                        )
                        generated_plots.append(f"pca_2d.{fmt}")

                        # 3D PCA (if requested)
                        if args.pca_components == 3:
                            fig_3d = visualizer.plot_pca_scatter(
                                embeddings_data,
                                n_components=3,
                                color_by=args.cluster_by if args.cluster_by != 'none' else None,
                                save_path=output_dir / f"pca_3d.{fmt}",
                                title="3D PCA Embedding Visualization"
                            )
                            generated_plots.append(f"pca_3d.{fmt}")

                    print("✓ PCA scatter plots generated")

                elif plot_type == 'heatmap':
                    # Generate similarity heatmap
                    max_heatmap_samples = min(1000, len(embeddings_data))  # Heatmaps get slow with too many points
                    heatmap_data = embeddings_data
                    if len(embeddings_data) > max_heatmap_samples:
                        from analysis.utils import sample_embeddings
                        heatmap_data = sample_embeddings(embeddings_data, max_heatmap_samples, random_state=42)

                    for fmt in formats:
                        fig_heatmap = visualizer.plot_similarity_heatmap(
                            heatmap_data,
                            max_samples=max_heatmap_samples,
                            save_path=output_dir / f"similarity_heatmap.{fmt}",
                            title=f"Similarity Heatmap ({len(heatmap_data)} samples)"
                        )
                        generated_plots.append(f"similarity_heatmap.{fmt}")

                    print("✓ Similarity heatmap generated")

                elif plot_type == 'distribution':
                    # Generate distribution plots
                    for fmt in formats:
                        fig_dist = visualizer.plot_embedding_distribution(
                            embeddings_data,
                            save_path=output_dir / f"embedding_distributions.{fmt}",
                            title="Embedding Value Distributions"
                        )
                        generated_plots.append(f"embedding_distributions.{fmt}")

                    print("✓ Distribution plots generated")

                elif plot_type == 'statistics':
                    # Generate statistics dashboard
                    analyzer = EmbeddingAnalyzer()
                    statistics = analyzer.compute_statistics(embeddings_data)

                    for fmt in formats:
                        fig_stats = visualizer.plot_statistics_dashboard(
                            statistics,
                            save_path=output_dir / f"statistics_dashboard.{fmt}",
                            title="Embedding Statistics Dashboard"
                        )
                        generated_plots.append(f"statistics_dashboard.{fmt}")

                    print("✓ Statistics dashboard generated")

                elif plot_type == 'cluster':
                    # Generate cluster visualization (requires clustering analysis)
                    analyzer = EmbeddingAnalyzer()
                    n_clusters = min(8, len(embeddings_data) // 20)  # Reasonable cluster count

                    if n_clusters >= 2:
                        clustering_results = analyzer.analyze_clusters(embeddings_data, n_clusters=n_clusters)

                        if 'error' not in clustering_results:
                            cluster_labels = clustering_results['labels']

                            for fmt in formats:
                                fig_cluster = visualizer.plot_cluster_visualization(
                                    embeddings_data,
                                    cluster_labels,
                                    save_path=output_dir / f"cluster_visualization.{fmt}",
                                    title=f"Embedding Clusters (k={n_clusters})"
                                )
                                generated_plots.append(f"cluster_visualization.{fmt}")

                            print("✓ Cluster visualization generated")
                        else:
                            print(f"⚠️  Cluster visualization skipped: {clustering_results['error']}")
                    else:
                        print("⚠️  Cluster visualization skipped: insufficient data for clustering")

            except Exception as e:
                print(f"⚠️  Failed to generate {plot_type} plots: {e}")
                if args.verbose:
                    import traceback
                    traceback.print_exc()
                continue

        # Print summary
        print("\n" + "=" * 80)
        print("VISUALIZATION COMPLETE")
        print("=" * 80)
        print(f"Total plots generated: {len(generated_plots)}")
        print("\nGenerated files:")
        for plot_file in generated_plots:
            print(f"  {output_dir / plot_file}")
        print("=" * 80)

        return 0

    except Exception as e:
        print(f"❌ Visualization failed: {e}")
        import traceback
        if args.verbose:
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
