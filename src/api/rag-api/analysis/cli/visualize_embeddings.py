#!/usr/bin/env python3
"""
CLI tool for generating embedding visualizations.

Creates static plots (PNG/SVG) for PCA analysis, similarity heatmaps,
distribution plots, cluster visualizations, and word-enhanced plots.
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from analysis import (
    EmbeddingVisualizer, load_embeddings_from_dir, ensure_output_dirs, setup_analysis_logging
)


def main():
    parser = argparse.ArgumentParser(
        description="Generate visualizations for embedding analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate all visualizations
  python visualize_embeddings.py --embeddings-dir ./embeddings --output-dir ./output --plot-type all

  # Generate only PCA plots
  python visualize_embeddings.py --embeddings-dir ./embeddings --output-dir ./output --plot-type pca

  # Generate heatmaps with sampling
  python visualize_embeddings.py --embeddings-dir ./embeddings --output-dir ./output --plot-type heatmap --max-samples 1000

  # Generate word-enhanced PCA plots
  python visualize_embeddings.py --embeddings-dir ./embeddings --output-dir ./output --plot-type pca --word-analysis --top-words 30

  # Generate SVG plots
  python visualize_embeddings.py --embeddings-dir ./embeddings --output-dir ./output --format svg
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
        help='Base output directory for visualizations'
    )

    parser.add_argument(
        '--plot-type',
        choices=['pca', 'heatmap', 'distribution', 'clusters', 'statistics', 'all'],
        default='all',
        help='Type of plots to generate'
    )

    parser.add_argument(
        '--format',
        choices=['png', 'svg', 'both'],
        default='png',
        help='Output format for plots'
    )

    parser.add_argument(
        '--max-samples',
        type=int,
        default=1000,
        help='Maximum number of embeddings to sample for analysis'
    )

    parser.add_argument(
        '--word-analysis',
        action='store_true',
        help='Include word analysis and overlays in visualizations'
    )

    parser.add_argument(
        '--top-words',
        type=int,
        default=30,
        help='Number of top words to include in word-enhanced plots'
    )

    parser.add_argument(
        '--pca-components',
        type=int,
        choices=[2, 3],
        default=2,
        help='Number of PCA components for scatter plots'
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
    logger.info("Starting embedding visualization")

    # Ensure output directories exist
    output_dirs = ensure_output_dirs(args.output_dir)
    viz_dir = output_dirs['visualizations']
    pca_dir = output_dirs['pca']
    similarity_dir = output_dirs['similarity']
    statistics_dir = output_dirs['statistics']
    clusters_dir = output_dirs['clusters']

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
        visualizer = EmbeddingVisualizer(logger=logger)

        # Generate PCA plots
        if args.plot_type in ['pca', 'all']:
            print(f"\nGenerating {args.pca_components}D PCA plots...")

            color_options = ['source', 'norm', 'index'] if args.plot_type == 'all' else ['source']

            for color_by in color_options:
                # Standard PCA plot
                pca_plot_name = f"pca_{args.pca_components}d_scatter_{color_by}.png"
                pca_plot_path = pca_dir / pca_plot_name

                if args.format in ['png', 'both']:
                    visualizer.plot_pca_scatter(
                        embeddings_data, n_components=args.pca_components,
                        color_by=color_by, save_path=str(pca_plot_path)
                    )
                    print(f"✓ PCA {args.pca_components}D scatter plot ({color_by}) saved (PNG)")

                if args.format in ['svg', 'both']:
                    pca_plot_svg = pca_plot_path.with_suffix('.svg')
                    visualizer.plot_pca_scatter(
                        embeddings_data, n_components=args.pca_components,
                        color_by=color_by, save_path=str(pca_plot_svg)
                    )
                    print(f"✓ PCA {args.pca_components}D scatter plot ({color_by}) saved (SVG)")

                # Word-enhanced PCA plot
                if args.word_analysis:
                    word_pca_plot_name = f"pca_{args.pca_components}d_words_{color_by}.png"
                    word_pca_plot_path = pca_dir / word_pca_plot_name

                    if args.format in ['png', 'both']:
                        visualizer.plot_pca_scatter(
                            embeddings_data, n_components=args.pca_components,
                            color_by=color_by, show_words=True, top_words=args.top_words,
                            save_path=str(word_pca_plot_path)
                        )
                        print(f"✓ Word-enhanced PCA {args.pca_components}D plot ({color_by}) saved (PNG)")

                    if args.format in ['svg', 'both']:
                        word_pca_plot_svg = word_pca_plot_path.with_suffix('.svg')
                        visualizer.plot_pca_scatter(
                            embeddings_data, n_components=args.pca_components,
                            color_by=color_by, show_words=True, top_words=args.top_words,
                            save_path=str(word_pca_plot_svg)
                        )
                        print(f"✓ Word-enhanced PCA {args.pca_components}D plot ({color_by}) saved (SVG)")

        # Generate similarity heatmap
        if args.plot_type in ['heatmap', 'all']:
            print("\nGenerating similarity heatmap...")

            heatmap_samples = min(args.max_samples, 200)  # Limit for heatmap readability
            if len(embeddings_data) > heatmap_samples:
                from analysis.utils import sample_embeddings
                heatmap_data = sample_embeddings(embeddings_data, heatmap_samples, random_state=42)
            else:
                heatmap_data = embeddings_data

            heatmap_path = similarity_dir / "similarity_heatmap.png"

            if args.format in ['png', 'both']:
                visualizer.plot_similarity_heatmap(heatmap_data, save_path=str(heatmap_path))
                print("✓ Similarity heatmap saved (PNG)")

            if args.format in ['svg', 'both']:
                heatmap_svg = heatmap_path.with_suffix('.svg')
                visualizer.plot_similarity_heatmap(heatmap_data, save_path=str(heatmap_svg))
                print("✓ Similarity heatmap saved (SVG)")

        # Generate distribution plots
        if args.plot_type in ['distribution', 'all']:
            print("\nGenerating distribution plots...")

            dist_path = statistics_dir / "embedding_distributions.png"

            if args.format in ['png', 'both']:
                visualizer.plot_embedding_distribution(embeddings_data, save_path=str(dist_path))
                print("✓ Embedding distributions saved (PNG)")

            if args.format in ['svg', 'both']:
                dist_svg = dist_path.with_suffix('.svg')
                visualizer.plot_embedding_distribution(embeddings_data, save_path=str(dist_svg))
                print("✓ Embedding distributions saved (SVG)")

        # Generate cluster visualization
        if args.plot_type in ['clusters', 'all']:
            print("\nGenerating cluster visualization...")

            n_clusters = min(8, len(embeddings_data) // 20)  # Reasonable cluster count
            if n_clusters >= 2:
                cluster_path = clusters_dir / "cluster_visualization.png"

                if args.format in ['png', 'both']:
                    visualizer.plot_cluster_visualization(
                        embeddings_data, n_clusters=n_clusters, save_path=str(cluster_path)
                    )
                    print("✓ Cluster visualization saved (PNG)")

                if args.format in ['svg', 'both']:
                    cluster_svg = cluster_path.with_suffix('.svg')
                    visualizer.plot_cluster_visualization(
                        embeddings_data, n_clusters=n_clusters, save_path=str(cluster_svg)
                    )
                    print("✓ Cluster visualization saved (SVG)")
            else:
                print("⚠️  Not enough data for meaningful clustering")

        # Generate statistics dashboard
        if args.plot_type in ['statistics', 'all']:
            print("\nGenerating statistics dashboard...")

            dashboard_path = statistics_dir / "statistics_dashboard.png"

            if args.format in ['png', 'both']:
                visualizer.plot_statistics_dashboard(embeddings_data, save_path=str(dashboard_path))
                print("✓ Statistics dashboard saved (PNG)")

            if args.format in ['svg', 'both']:
                dashboard_svg = dashboard_path.with_suffix('.svg')
                visualizer.plot_statistics_dashboard(embeddings_data, save_path=str(dashboard_svg))
                print("✓ Statistics dashboard saved (SVG)")

        # Generate word-specific visualizations if requested
        if args.word_analysis and args.plot_type in ['all']:
            print("\nGenerating word-specific visualizations...")

            # Word frequency plot
            word_freq_path = viz_dir / "words" / "word_frequency.png"
            if args.format in ['png', 'both']:
                visualizer.plot_word_frequency_distribution(
                    embeddings_data, save_path=str(word_freq_path), top_k=args.top_words
                )
                print("✓ Word frequency plot saved (PNG)")

            if args.format in ['svg', 'both']:
                word_freq_svg = word_freq_path.with_suffix('.svg')
                visualizer.plot_word_frequency_distribution(
                    embeddings_data, save_path=str(word_freq_svg), top_k=args.top_words
                )
                print("✓ Word frequency plot saved (SVG)")

            # Words in PCA space
            words_pca_path = viz_dir / "words" / "words_in_pca_space.png"
            if args.format in ['png', 'both']:
                visualizer.plot_words_in_pca_scatter(
                    embeddings_data, save_path=str(words_pca_path), top_words=args.top_words
                )
                print("✓ Words in PCA space plot saved (PNG)")

            if args.format in ['svg', 'both']:
                words_pca_svg = words_pca_path.with_suffix('.svg')
                visualizer.plot_words_in_pca_scatter(
                    embeddings_data, save_path=str(words_pca_svg), top_words=args.top_words
                )
                print("✓ Words in PCA space plot saved (SVG)")

        print("
✅ Visualization generation completed successfully!"        print(f"📁 Visualizations saved to: {viz_dir}")
        print(f"   ├── PCA plots: {pca_dir}")
        print(f"   ├── Similarity: {similarity_dir}")
        print(f"   ├── Statistics: {statistics_dir}")
        print(f"   ├── Clusters: {clusters_dir}")
        print(f"   └── Words: {viz_dir / 'words'}")

        return 0

    except Exception as e:
        logger.error(f"❌ Visualization generation failed: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())