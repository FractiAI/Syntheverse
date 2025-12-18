"""
Word Visualizer - Create visualizations for word analysis.

Generates plots for word frequencies, word clouds, PCA-word associations,
and word similarity networks.
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import warnings

try:
    from wordcloud import WordCloud
    WORDCLOUD_AVAILABLE = True
except ImportError:
    WORDCLOUD_AVAILABLE = False

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False

from .logger import get_logger
from .word_analyzer import WordAnalyzer


class WordVisualizer:
    """
    Visualization tools for word analysis results.

    Creates publication-quality plots for word frequencies, distributions,
    PCA associations, and semantic networks.
    """

    def __init__(self, figsize: Tuple[int, int] = (12, 8),
                 dpi: int = 150, logger=None, style: str = 'default'):
        """
        Initialize word visualizer.

        Args:
            figsize: Default figure size (width, height) in inches
            dpi: Resolution for saved images
            logger: Optional logger instance
            style: Matplotlib style to use
        """
        if figsize[0] <= 0 or figsize[1] <= 0:
            raise ValueError("Figure size dimensions must be positive")

        if dpi <= 0:
            raise ValueError("DPI must be positive")

        self.figsize = figsize
        self.dpi = dpi
        self.logger = logger or get_logger(__name__)

        # Set style
        plt.style.use(style)
        sns.set_palette("husl")

        # Initialize word analyzer for reuse
        self.word_analyzer = WordAnalyzer(logger=self.logger)

    def plot_word_frequency(self, word_frequencies: Dict[str, int],
                          top_k: int = 20, save_path: Optional[str] = None,
                          title: str = "Word Frequency Distribution") -> plt.Figure:
        """
        Create a bar plot of word frequencies.

        Args:
            word_frequencies: Dictionary mapping words to frequencies
            top_k: Number of top words to show
            save_path: Optional path to save the plot
            title: Plot title

        Returns:
            Matplotlib figure object
        """
        self.logger.info(f"Creating word frequency plot for top {top_k} words")

        # Get top words
        sorted_words = sorted(word_frequencies.items(), key=lambda x: x[1], reverse=True)
        top_words = sorted_words[:top_k]

        if not top_words:
            self.logger.warning("No words found for frequency plot")
            return plt.figure()

        words, frequencies = zip(*top_words)

        # Create plot
        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)

        bars = ax.bar(range(len(words)), frequencies, color=sns.color_palette("husl", len(words)))

        # Add value labels on bars
        for bar, freq in zip(bars, frequencies):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + max(frequencies) * 0.01,
                   f'{freq}', ha='center', va='bottom', fontsize=10)

        ax.set_xticks(range(len(words)))
        ax.set_xticklabels(words, rotation=45, ha='right')
        ax.set_xlabel('Words')
        ax.set_ylabel('Frequency')
        ax.set_title(title)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            self.logger.info(f"Word frequency plot saved to {save_path}")

        return fig

    def plot_word_cloud(self, word_frequencies: Dict[str, int],
                       save_path: Optional[str] = None,
                       title: str = "Word Cloud",
                       max_words: int = 100,
                       width: int = 800, height: int = 600) -> Optional[plt.Figure]:
        """
        Create a word cloud visualization.

        Args:
            word_frequencies: Dictionary mapping words to frequencies
            save_path: Optional path to save the plot
            title: Plot title
            max_words: Maximum number of words to include
            width: Word cloud width
            height: Word cloud height

        Returns:
            Matplotlib figure object or None if wordcloud not available
        """
        if not WORDCLOUD_AVAILABLE:
            self.logger.warning("wordcloud package not available. Skipping word cloud generation.")
            return None

        self.logger.info(f"Creating word cloud with max {max_words} words")

        # Create word cloud
        wordcloud = WordCloud(
            width=width,
            height=height,
            background_color='white',
            max_words=max_words,
            colormap='viridis',
            contour_width=1,
            contour_color='steelblue'
        ).generate_from_frequencies(word_frequencies)

        # Create plot
        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        ax.set_title(title)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            self.logger.info(f"Word cloud saved to {save_path}")

        return fig

    def plot_words_in_pca_space(self, embeddings_data: List[Dict],
                              pca_reducer, save_path: Optional[str] = None,
                              top_words: int = 50, title: str = "Words in PCA Space") -> plt.Figure:
        """
        Plot word positions in PCA-reduced space.

        Args:
            embeddings_data: List of embedding dictionaries
            pca_reducer: Trained PCAReducer instance
            save_path: Optional path to save the plot
            top_words: Number of most frequent words to plot
            title: Plot title

        Returns:
            Matplotlib figure object
        """
        self.logger.info(f"Plotting top {top_words} words in PCA space")

        # Get word embeddings
        word_embeddings = self.word_analyzer.compute_word_embeddings(embeddings_data)

        if not word_embeddings:
            self.logger.warning("No word embeddings available for PCA plot")
            return plt.figure()

        # Get most frequent words
        freq_results = self.word_analyzer.compute_word_frequencies(embeddings_data, top_k=top_words)
        top_word_list = [word for word, _ in freq_results['top_words']]
        words_to_plot = [w for w in top_word_list if w in word_embeddings][:top_words]

        if len(words_to_plot) < 2:
            self.logger.warning("Not enough words with embeddings for PCA plot")
            return plt.figure()

        # Get word vectors and reduce to 2D
        word_vectors = np.array([word_embeddings[w] for w in words_to_plot])
        word_vectors_2d = pca_reducer.transform(word_vectors)

        # Create plot
        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)

        scatter = ax.scatter(word_vectors_2d[:, 0], word_vectors_2d[:, 1],
                           alpha=0.7, s=50, c=range(len(words_to_plot)),
                           cmap='viridis')

        # Add word labels
        for i, word in enumerate(words_to_plot):
            ax.annotate(word, (word_vectors_2d[i, 0], word_vectors_2d[i, 1]),
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=8, alpha=0.8)

        ax.set_xlabel('PCA Component 1')
        ax.set_ylabel('PCA Component 2')
        ax.set_title(title)
        ax.grid(True, alpha=0.3)

        # Add colorbar
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Word Rank (by frequency)')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            self.logger.info(f"Words in PCA space plot saved to {save_path}")

        return fig

    def plot_word_distribution_by_source(self, word_analysis_results: Dict[str, Any],
                                       save_path: Optional[str] = None,
                                       title: str = "Word Distribution by Source") -> plt.Figure:
        """
        Plot word distribution across different sources/documents.

        Args:
            word_analysis_results: Results from WordAnalyzer.analyze_word_distributions()
            save_path: Optional path to save the plot
            title: Plot title

        Returns:
            Matplotlib figure object
        """
        self.logger.info("Creating word distribution by source plot")

        source_diversity = word_analysis_results.get('source_diversity', {})

        if not source_diversity:
            self.logger.warning("No source diversity data available")
            return plt.figure()

        # Prepare data
        sources = list(source_diversity.keys())
        unique_words = [stats['unique_words'] for stats in source_diversity.values()]
        total_words = [stats['total_words'] for stats in source_diversity.values()]

        # Create plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(self.figsize[0]*1.5, self.figsize[1]), dpi=self.dpi)

        # Unique words
        bars1 = ax1.bar(range(len(sources)), unique_words, color=sns.color_palette("husl", len(sources)))
        ax1.set_xticks(range(len(sources)))
        ax1.set_xticklabels(sources, rotation=45, ha='right')
        ax1.set_ylabel('Unique Words')
        ax1.set_title('Unique Words by Source')
        ax1.grid(True, alpha=0.3)

        # Total words
        bars2 = ax2.bar(range(len(sources)), total_words, color=sns.color_palette("husl", len(sources)))
        ax2.set_xticks(range(len(sources)))
        ax2.set_xticklabels(sources, rotation=45, ha='right')
        ax2.set_ylabel('Total Words')
        ax2.set_title('Total Words by Source')
        ax2.grid(True, alpha=0.3)

        # Add value labels
        for bars, values in [(bars1, unique_words), (bars2, total_words)]:
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax = bar.axes
                ax.text(bar.get_x() + bar.get_width()/2., height + max(values) * 0.01,
                       f'{value}', ha='center', va='bottom', fontsize=9)

        fig.suptitle(title)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            self.logger.info(f"Word distribution plot saved to {save_path}")

        return fig

    def plot_keyword_heatmap(self, pca_keywords_results: Dict[str, Any],
                           save_path: Optional[str] = None,
                           title: str = "Keyword-PCA Component Associations") -> plt.Figure:
        """
        Create a heatmap showing keyword associations with PCA components.

        Args:
            pca_keywords_results: Results from WordAnalyzer.find_keywords_by_pca()
            save_path: Optional path to save the plot
            title: Plot title

        Returns:
            Matplotlib figure object
        """
        self.logger.info("Creating keyword-PCA heatmap")

        component_keywords = pca_keywords_results.get('component_keywords', {})

        if not component_keywords:
            self.logger.warning("No PCA keyword data available")
            return plt.figure()

        # Prepare data for heatmap
        components = list(component_keywords.keys())
        all_words = set()

        for comp_data in component_keywords.values():
            for word, _ in comp_data['top_keywords']:
                all_words.add(word)

        all_words = sorted(list(all_words))

        # Create matrix
        heatmap_data = np.zeros((len(components), len(all_words)))

        for i, comp in enumerate(components):
            comp_words = dict(component_keywords[comp]['top_keywords'])
            for j, word in enumerate(all_words):
                heatmap_data[i, j] = comp_words.get(word, 0)

        # Create plot
        fig, ax = plt.subplots(figsize=(self.figsize[0]*1.5, self.figsize[1]), dpi=self.dpi)

        # Create heatmap
        im = ax.imshow(heatmap_data, cmap='RdYlBu_r', aspect='auto')

        # Add labels
        ax.set_xticks(range(len(all_words)))
        ax.set_xticklabels(all_words, rotation=45, ha='right', fontsize=8)
        ax.set_yticks(range(len(components)))
        ax.set_yticklabels([comp.replace('_', ' ').title() for comp in components])

        ax.set_title(title)
        ax.set_xlabel('Keywords')
        ax.set_ylabel('PCA Components')

        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Association Strength')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            self.logger.info(f"Keyword-PCA heatmap saved to {save_path}")

        return fig

    def plot_word_similarity_network(self, word_similarity_results: Dict[str, Any],
                                  save_path: Optional[str] = None,
                                  min_similarity: float = 0.5,
                                  title: str = "Word Similarity Network") -> Optional[plt.Figure]:
        """
        Create a network visualization of word similarities.

        Args:
            word_similarity_results: Results from WordAnalyzer.compute_word_similarities()
            save_path: Optional path to save the plot
            min_similarity: Minimum similarity threshold for edges
            title: Plot title

        Returns:
            Matplotlib figure object or None if networkx not available
        """
        if not NETWORKX_AVAILABLE:
            self.logger.warning("networkx package not available. Skipping similarity network.")
            return None

        self.logger.info(f"Creating word similarity network with min similarity {min_similarity}")

        similarity_matrix = word_similarity_results.get('similarity_matrix')
        words = word_similarity_results.get('words_analyzed', [])

        if not similarity_matrix or not words:
            self.logger.warning("No similarity data available for network plot")
            return plt.figure()

        similarity_matrix = np.array(similarity_matrix)

        # Create graph
        G = nx.Graph()

        # Add nodes
        for word in words:
            G.add_node(word)

        # Add edges for similar words
        n = len(words)
        for i in range(n):
            for j in range(i + 1, n):
                sim = similarity_matrix[i, j]
                if sim >= min_similarity:
                    G.add_edge(words[i], words[j], weight=sim)

        if len(G.edges()) == 0:
            self.logger.warning("No edges found above similarity threshold")
            return plt.figure()

        # Create plot
        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)

        # Use spring layout
        pos = nx.spring_layout(G, k=1, iterations=50, seed=42)

        # Draw edges with varying thickness
        edges = G.edges()
        weights = [G[u][v]['weight'] for u, v in edges]

        nx.draw_networkx_edges(G, pos, ax=ax, width=[w*3 for w in weights],
                             alpha=0.6, edge_color='gray')

        # Draw nodes
        node_sizes = [G.degree(node) * 100 + 300 for node in G.nodes()]
        nx.draw_networkx_nodes(G, pos, ax=ax, node_size=node_sizes,
                             node_color='lightblue', alpha=0.8)

        # Draw labels
        nx.draw_networkx_labels(G, pos, ax=ax, font_size=8, font_weight='bold')

        ax.set_title(title)
        ax.axis('off')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            self.logger.info(f"Word similarity network saved to {save_path}")

        return fig

    def create_word_analysis_dashboard(self, word_analysis_results: Dict[str, Any],
                                     save_path: Optional[str] = None) -> plt.Figure:
        """
        Create a comprehensive dashboard of word analysis results.

        Args:
            word_analysis_results: Complete word analysis results
            save_path: Optional path to save the plot

        Returns:
            Matplotlib figure object
        """
        self.logger.info("Creating word analysis dashboard")

        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=(self.figsize[0]*2, self.figsize[1]*2), dpi=self.dpi)

        # 1. Word frequency distribution
        freq_data = word_analysis_results.get('word_frequencies', {}).get('word_frequencies', {})
        if freq_data:
            sorted_freq = sorted(freq_data.items(), key=lambda x: x[1], reverse=True)[:15]
            words, freqs = zip(*sorted_freq)
            axes[0, 0].bar(range(len(words)), freqs, color=sns.color_palette("husl", len(words)))
            axes[0, 0].set_xticks(range(len(words)))
            axes[0, 0].set_xticklabels(words, rotation=45, ha='right', fontsize=8)
            axes[0, 0].set_title('Top 15 Word Frequencies')
            axes[0, 0].grid(True, alpha=0.3)

        # 2. Source diversity
        source_data = word_analysis_results.get('source_diversity', {})
        if source_data:
            sources = list(source_data.keys())
            unique_counts = [data['unique_words'] for data in source_data.values()]
            axes[0, 1].bar(range(len(sources)), unique_counts, color=sns.color_palette("Set2", len(sources)))
            axes[0, 1].set_xticks(range(len(sources)))
            axes[0, 1].set_xticklabels(sources, rotation=45, ha='right', fontsize=8)
            axes[0, 1].set_title('Unique Words by Source')
            axes[0, 1].grid(True, alpha=0.3)

        # 3. Frequency statistics
        freq_stats = word_analysis_results.get('frequency_stats', {})
        if freq_stats:
            stats_names = list(freq_stats.keys())
            stats_values = list(freq_stats.values())
            axes[1, 0].bar(stats_names, stats_values, color=sns.color_palette("pastel"))
            axes[1, 0].set_title('Word Frequency Statistics')
            axes[1, 0].grid(True, alpha=0.3)

            # Add value labels
            for i, v in enumerate(stats_values):
                axes[1, 0].text(i, v + max(stats_values) * 0.01, '.2f',
                               ha='center', va='bottom', fontsize=9)

        # 4. Summary statistics text
        axes[1, 1].axis('off')
        summary_text = f"""
        Word Analysis Summary

        Total Words: {word_analysis_results.get('total_words', 0):,}
        Unique Words: {word_analysis_results.get('unique_words', 0):,}
        Sources: {len(source_data)}

        Most Frequent Word:
        {word_analysis_results.get('top_words', [('', 0)])[0][0] if word_analysis_results.get('top_words') else 'N/A'}
        ({word_analysis_results.get('top_words', [('', 0)])[0][1] if word_analysis_results.get('top_words') else 0} occurrences)
        """

        axes[1, 1].text(0.1, 0.5, summary_text, transform=axes[1, 1].transAxes,
                       fontsize=10, verticalalignment='center',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.5))

        fig.suptitle('Word Analysis Dashboard', fontsize=14, fontweight='bold')
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            self.logger.info(f"Word analysis dashboard saved to {save_path}")

        return fig

    def save_visualization(self, fig: plt.Figure, save_path: str) -> None:
        """
        Save a matplotlib figure to file.

        Args:
            fig: Matplotlib figure to save
            save_path: Path to save the figure
        """
        fig.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        self.logger.info(f"Visualization saved to {save_path}")
        plt.close(fig)  # Clean up memory
