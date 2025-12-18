#!/usr/bin/env python3
"""
CLI tool for comprehensive word analysis on embeddings.

Extracts words, computes frequencies, analyzes PCA associations,
and generates word-based visualizations.
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from analysis import (
    WordAnalyzer, WordVisualizer, PCAReducer,
    load_embeddings_from_dir, ensure_output_dirs, setup_analysis_logging
)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze words in embedding datasets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic word frequency analysis
  python analyze_words.py --embeddings-dir ./embeddings --output-dir ./output --analysis frequency

  # Comprehensive word analysis with PCA associations
  python analyze_words.py --embeddings-dir ./embeddings --output-dir ./output --analysis all

  # Word analysis with custom top-k
  python analyze_words.py --embeddings-dir ./embeddings --output-dir ./output --analysis all --top-words 50

  # Word similarity analysis
  python analyze_words.py --embeddings-dir ./embeddings --output-dir ./output --analysis similarity
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
        help='Base output directory for results'
    )

    parser.add_argument(
        '--analysis',
        choices=['frequency', 'pca', 'similarity', 'distribution', 'all'],
        default='all',
        help='Type of word analysis to perform'
    )

    parser.add_argument(
        '--top-words',
        type=int,
        default=50,
        help='Number of top words to analyze'
    )

    parser.add_argument(
        '--max-samples',
        type=int,
        default=None,
        help='Maximum number of embeddings to sample for analysis'
    )

    parser.add_argument(
        '--format',
        choices=['png', 'svg', 'both'],
        default='png',
        help='Output format for visualizations'
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
    logger.info("Starting word analysis")

    # Ensure output directories exist
    output_dirs = ensure_output_dirs(args.output_dir)
    words_dir = output_dirs['words']
    analysis_dir = output_dirs['analysis']

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
        word_analyzer = WordAnalyzer(logger=logger)
        word_visualizer = WordVisualizer(logger=logger)

        results = {}

        # Perform frequency analysis
        if args.analysis in ['frequency', 'all']:
            print("\nComputing word frequencies...")
            freq_results = word_analyzer.compute_word_frequencies(embeddings_data, top_k=None)
            results['frequencies'] = freq_results

            # Save results
            freq_file = analysis_dir / "word_frequencies.json"
            word_analyzer.export_word_analysis({'word_frequencies': freq_results}, str(freq_file))
            print("✓ Word frequencies saved")

            # Create frequency plot
            if args.format in ['png', 'both']:
                freq_plot = words_dir / "word_frequency.png"
                word_visualizer.plot_word_frequency(freq_results['word_frequencies'], args.top_words, str(freq_plot))
                print("✓ Word frequency plot saved (PNG)")

            if args.format in ['svg', 'both']:
                freq_plot_svg = words_dir / "word_frequency.svg"
                word_visualizer.plot_word_frequency(freq_results['word_frequencies'], args.top_words, str(freq_plot_svg))
                print("✓ Word frequency plot saved (SVG)")

            # Create word cloud if available
            if args.format in ['png', 'both']:
                cloud_plot = words_dir / "word_cloud.png"
                word_visualizer.plot_word_cloud(freq_results['word_frequencies'], str(cloud_plot))
                print("✓ Word cloud saved (PNG)")

        # Perform PCA-word association analysis
        if args.analysis in ['pca', 'all']:
            print("\nAnalyzing PCA-word associations...")

            # Fit PCA on embeddings
            from analysis.utils import extract_embeddings_array
            embeddings = extract_embeddings_array(embeddings_data)
            pca_reducer = PCAReducer(n_components=min(10, embeddings.shape[1]), logger=logger)
            pca_reducer.fit(embeddings)

            # Find keyword associations
            pca_keywords = word_analyzer.find_keywords_by_pca(
                embeddings_data, pca_reducer.pca.components_, top_k=10
            )
            results['pca_keywords'] = pca_keywords

            # Save results
            pca_file = analysis_dir / "word_pca_associations.json"
            word_analyzer.export_word_analysis({'pca_keywords': pca_keywords}, str(pca_file))
            print("✓ PCA-word associations saved")

            # Create keyword heatmap
            if args.format in ['png', 'both']:
                heatmap_plot = words_dir / "keyword_pca_heatmap.png"
                word_visualizer.plot_keyword_heatmap(pca_keywords, str(heatmap_plot))
                print("✓ Keyword-PCA heatmap saved (PNG)")

            if args.format in ['svg', 'both']:
                heatmap_plot_svg = words_dir / "keyword_pca_heatmap.svg"
                word_visualizer.plot_keyword_heatmap(pca_keywords, str(heatmap_plot_svg))
                print("✓ Keyword-PCA heatmap saved (SVG)")

            # Create words in PCA space plot
            if args.format in ['png', 'both']:
                pca_words_plot = words_dir / "words_in_pca_space.png"
                word_visualizer.plot_words_in_pca_space(
                    embeddings_data, pca_reducer, str(pca_words_plot), args.top_words
                )
                print("✓ Words in PCA space plot saved (PNG)")

            if args.format in ['svg', 'both']:
                pca_words_plot_svg = words_dir / "words_in_pca_space.svg"
                word_visualizer.plot_words_in_pca_space(
                    embeddings_data, pca_reducer, str(pca_words_plot_svg), args.top_words
                )
                print("✓ Words in PCA space plot saved (SVG)")

        # Perform word similarity analysis
        if args.analysis in ['similarity', 'all']:
            print("\nComputing word similarities...")
            similarity_results = word_analyzer.compute_word_similarities(
                embeddings_data, top_k_words=args.top_words
            )
            results['similarities'] = similarity_results

            # Save results
            sim_file = analysis_dir / "word_similarities.json"
            word_analyzer.export_word_analysis({'word_similarities': similarity_results}, str(sim_file))
            print("✓ Word similarities saved")

            # Create similarity network if networkx available
            if args.format in ['png', 'both']:
                network_plot = words_dir / "word_similarity_network.png"
                word_visualizer.plot_word_similarity_network(similarity_results, str(network_plot))
                print("✓ Word similarity network saved (PNG)")

            if args.format in ['svg', 'both']:
                network_plot_svg = words_dir / "word_similarity_network.svg"
                word_visualizer.plot_word_similarity_network(similarity_results, str(network_plot_svg))
                print("✓ Word similarity network saved (SVG)")

        # Perform distribution analysis
        if args.analysis in ['distribution', 'all']:
            print("\nAnalyzing word distributions...")
            dist_results = word_analyzer.analyze_word_distributions(embeddings_data)
            results['distributions'] = dist_results

            # Save results
            dist_file = analysis_dir / "word_distributions.json"
            word_analyzer.export_word_analysis({'word_distributions': dist_results}, str(dist_file))
            print("✓ Word distributions saved")

            # Create distribution plots
            if args.format in ['png', 'both']:
                dist_plot = words_dir / "word_distribution_by_source.png"
                word_visualizer.plot_word_distribution_by_source(dist_results, str(dist_plot))
                print("✓ Word distribution plot saved (PNG)")

            if args.format in ['svg', 'both']:
                dist_plot_svg = words_dir / "word_distribution_by_source.svg"
                word_visualizer.plot_word_distribution_by_source(dist_results, str(dist_plot_svg))
                print("✓ Word distribution plot saved (SVG)")

        # Create comprehensive word analysis dashboard
        if args.analysis == 'all':
            print("\nCreating word analysis dashboard...")
            dashboard_data = {
                'word_frequencies': results.get('frequencies', {}),
                'word_distributions': results.get('distributions', {}),
                'pca_keywords': results.get('pca_keywords', {}),
                'word_similarities': results.get('similarities', {})
            }

            dashboard_file = analysis_dir / "word_analysis_summary.json"
            word_analyzer.export_word_analysis(dashboard_data, str(dashboard_file))

            if args.format in ['png', 'both']:
                dashboard_plot = words_dir / "word_analysis_dashboard.png"
                word_visualizer.create_word_analysis_dashboard(dashboard_data, str(dashboard_plot))
                print("✓ Word analysis dashboard saved (PNG)")

            if args.format in ['svg', 'both']:
                dashboard_plot_svg = words_dir / "word_analysis_dashboard.svg"
                word_visualizer.create_word_analysis_dashboard(dashboard_data, str(dashboard_plot_svg))
                print("✓ Word analysis dashboard saved (SVG)")

        print("\n✅ Word analysis completed successfully!")
        print(f"📁 Results saved to: {args.output_dir}")
        print(f"📊 Analysis files: {analysis_dir}")
        print(f"📈 Visualizations: {words_dir}")

        return 0

    except Exception as e:
        logger.error(f"❌ Word analysis failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
