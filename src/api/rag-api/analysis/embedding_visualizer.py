"""
Embedding Visualizer - Static visualization tools for embeddings.

Creates PNG/SVG plots for embedding analysis including PCA scatterplots,
similarity heatmaps, distribution plots, and statistics dashboards.
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

from .pca_reducer import PCAReducer
from .word_analyzer import WordAnalyzer
from .word_visualizer import WordVisualizer
from .logger import get_logger


class EmbeddingVisualizer:
    """
    Static visualization tools for embedding analysis.

    Creates publication-quality plots and saves them as image files.
    Supports both standard embedding visualizations and word-enhanced plots.
    """

    def __init__(self, figsize: Tuple[int, int] = (10, 8),
                 dpi: int = 150, logger=None, style: str = 'default'):
        """
        Initialize visualizer.

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

        # Initialize word visualizer for word-enhanced plots
        self.word_visualizer = WordVisualizer(
            figsize=figsize, dpi=dpi, logger=self.logger, style=style
        )

    def plot_pca_scatter(self, embeddings_data: List[Dict],
                        n_components: int = 2, save_path: Optional[str] = None,
                        color_by: str = 'source', title: str = "PCA Scatter Plot",
                        show_words: bool = False, top_words: int = 20) -> plt.Figure:
        """
        Create 2D or 3D PCA scatterplot with optional word overlays.

        Args:
            embeddings_data: List of embedding dictionaries
            n_components: Number of PCA components (2 or 3)
            save_path: Optional path to save the plot
            color_by: How to color points ('source', 'norm', 'index')
            title: Plot title
            show_words: Whether to overlay word labels
            top_words: Number of top words to show if show_words=True

        Returns:
            Matplotlib figure object
        """
        if n_components not in [2, 3]:
            raise ValueError("n_components must be 2 or 3")

        self.logger.info(f"Creating {n_components}D PCA scatter plot with "
                        f"{len(embeddings_data)} embeddings")

        # Extract embeddings
        from .utils import extract_embeddings_array
        embeddings = extract_embeddings_array(embeddings_data)

        if embeddings.size == 0:
            self.logger.warning("No embeddings found for PCA plot")
            return plt.figure()

        # Fit and transform PCA
        pca_reducer = PCAReducer(n_components=n_components, logger=self.logger)
        reduced_embeddings = pca_reducer.fit_transform(embeddings)

        # Prepare color data
        colors, color_label = self._prepare_color_data(embeddings_data, color_by)

        # Create plot
        if n_components == 2:
            fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)
            scatter = ax.scatter(reduced_embeddings[:, 0], reduced_embeddings[:, 1],
                               c=colors, cmap='viridis', alpha=0.7, s=50, edgecolors='black', linewidth=0.5)

            ax.set_xlabel(f'PC1 ({pca_reducer.explained_variance_ratio()[0]:.1%} variance)')
            ax.set_ylabel(f'PC2 ({pca_reducer.explained_variance_ratio()[1]:.1%} variance)')

            # Add word labels if requested
            if show_words:
                self._add_word_labels_to_pca(ax, embeddings_data, pca_reducer, top_words)

        else:  # 3D
            from mpl_toolkits.mplot3d import Axes3D
            fig = plt.figure(figsize=(self.figsize[0], self.figsize[1]), dpi=self.dpi)
            ax = fig.add_subplot(111, projection='3d')

            scatter = ax.scatter(reduced_embeddings[:, 0], reduced_embeddings[:, 1],
                               reduced_embeddings[:, 2], c=colors, cmap='viridis',
                               alpha=0.7, s=50, edgecolors='black', linewidth=0.5)

            ax.set_xlabel(f'PC1 ({pca_reducer.explained_variance_ratio()[0]:.1%} variance)')
            ax.set_ylabel(f'PC2 ({pca_reducer.explained_variance_ratio()[1]:.1%} variance)')
            ax.set_zlabel(f'PC3 ({pca_reducer.explained_variance_ratio()[2]:.1%} variance)')

        # Add colorbar and title
        if n_components == 2:
            cbar = plt.colorbar(scatter, ax=ax)
        else:
            cbar = plt.colorbar(scatter, ax=ax, shrink=0.8)

        cbar.set_label(color_label)
        plt.title(title)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            self.logger.info(f"PCA scatter plot saved to {save_path}")

        return fig

    def plot_similarity_heatmap(self, embeddings_data: List[Dict],
                              max_samples: int = 100, save_path: Optional[str] = None,
                              title: str = "Embedding Similarity Heatmap") -> plt.Figure:
        """
        Create a heatmap visualization of embedding similarities.

        Args:
            embeddings_data: List of embedding dictionaries
            max_samples: Maximum number of samples to include
            save_path: Optional path to save the plot
            title: Plot title

        Returns:
            Matplotlib figure object
        """
        self.logger.info(f"Creating similarity heatmap with max {max_samples} samples")

        # Extract and sample embeddings
        from .utils import extract_embeddings_array, sample_embeddings
        if len(embeddings_data) > max_samples:
            embeddings_data = sample_embeddings(embeddings_data, max_samples, random_state=42)

        embeddings = extract_embeddings_array(embeddings_data)

        if embeddings.size == 0:
            self.logger.warning("No embeddings found for similarity heatmap")
            return plt.figure()

        # Compute similarity matrix
        from .utils import compute_pairwise_cosine_similarity
        similarity_matrix = compute_pairwise_cosine_similarity(embeddings)

        # Create plot
        fig, ax = plt.subplots(figsize=(self.figsize[0], self.figsize[1]), dpi=self.dpi)

        # Create heatmap
        im = ax.imshow(similarity_matrix, cmap='RdYlBu_r', aspect='auto',
                      vmin=-1, vmax=1)

        # Add labels if we have metadata
        if len(embeddings_data) <= 20:  # Only add labels for small matrices
            labels = [chunk.get('pdf_filename', f'chunk_{i}')
                     for i, chunk in enumerate(embeddings_data)]
            ax.set_xticks(range(len(labels)))
            ax.set_yticks(range(len(labels)))
            ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=8)
            ax.set_yticklabels(labels, fontsize=8)

        ax.set_title(title)

        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Cosine Similarity')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            self.logger.info(f"Similarity heatmap saved to {save_path}")

        return fig

    def plot_embedding_distribution(self, embeddings_data: List[Dict],
                                  save_path: Optional[str] = None,
                                  title: str = "Embedding Value Distributions") -> plt.Figure:
        """
        Plot distributions of embedding norms and values.

        Args:
            embeddings_data: List of embedding dictionaries
            save_path: Optional path to save the plot
            title: Plot title

        Returns:
            Matplotlib figure object
        """
        self.logger.info("Creating embedding distribution plots")

        # Extract embeddings and compute statistics
        from .utils import extract_embeddings_array, get_embedding_statistics
        embeddings = extract_embeddings_array(embeddings_data)

        if embeddings.size == 0:
            self.logger.warning("No embeddings found for distribution plot")
            return plt.figure()

        stats = get_embedding_statistics(embeddings)
        norms = np.linalg.norm(embeddings, axis=1)
        all_values = embeddings.flatten()

        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=(self.figsize[0]*1.5, self.figsize[1]*1.5), dpi=self.dpi)

        # Norm distribution
        axes[0, 0].hist(norms, bins=50, alpha=0.7, color='blue', edgecolor='black')
        axes[0, 0].axvline(np.mean(norms), color='red', linestyle='--', label=f'Mean: {np.mean(norms):.3f}')
        axes[0, 0].set_xlabel('Vector Norm')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].set_title('Embedding Norms Distribution')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)

        # Value distribution
        axes[0, 1].hist(all_values, bins=100, alpha=0.7, color='green', edgecolor='black')
        axes[0, 1].axvline(np.mean(all_values), color='red', linestyle='--', label=f'Mean: {np.mean(all_values):.3f}')
        axes[0, 1].set_xlabel('Embedding Values')
        axes[0, 1].set_ylabel('Frequency')
        axes[0, 1].set_title('Embedding Values Distribution')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)

        # Norm boxplot
        axes[1, 0].boxplot(norms, vert=False)
        axes[1, 0].set_xlabel('Vector Norm')
        axes[1, 0].set_title('Embedding Norms Boxplot')
        axes[1, 0].grid(True, alpha=0.3)

        # Sparsity analysis
        sparsity = np.mean(np.abs(all_values) < 1e-6)
        axes[1, 1].bar(['Non-zero', 'Zero'], [1-sparsity, sparsity],
                      color=['lightblue', 'lightcoral'])
        axes[1, 1].set_ylabel('Proportion')
        axes[1, 1].set_title('Embedding Sparsity')
        axes[1, 1].grid(True, alpha=0.3)

        # Add percentage labels
        for i, v in enumerate([1-sparsity, sparsity]):
            axes[1, 1].text(i, v + 0.01, f'{v:.1%}', ha='center', va='bottom')

        fig.suptitle(title, fontsize=14)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            self.logger.info(f"Embedding distribution plot saved to {save_path}")

        return fig

    def plot_cluster_visualization(self, embeddings_data: List[Dict],
                                 n_clusters: int = 5, save_path: Optional[str] = None,
                                 title: str = "Embedding Clusters") -> plt.Figure:
        """
        Visualize clusters in embedding space using PCA.

        Args:
            embeddings_data: List of embedding dictionaries
            n_clusters: Number of clusters to find
            save_path: Optional path to save the plot
            title: Plot title

        Returns:
            Matplotlib figure object
        """
        try:
            from sklearn.cluster import KMeans
        except ImportError:
            self.logger.warning("scikit-learn not available for clustering")
            return plt.figure()

        self.logger.info(f"Creating cluster visualization with {n_clusters} clusters")

        # Extract embeddings
        from .utils import extract_embeddings_array
        embeddings = extract_embeddings_array(embeddings_data)

        if embeddings.size == 0:
            self.logger.warning("No embeddings found for cluster visualization")
            return plt.figure()

        # Perform clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(embeddings)

        # Reduce to 2D for visualization
        pca_reducer = PCAReducer(n_components=2, logger=self.logger)
        reduced_embeddings = pca_reducer.fit_transform(embeddings)

        # Create plot
        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)

        # Plot clusters
        scatter = ax.scatter(reduced_embeddings[:, 0], reduced_embeddings[:, 1],
                           c=cluster_labels, cmap='tab10', alpha=0.7, s=50,
                           edgecolors='black', linewidth=0.5)

        # Plot cluster centers
        centers_2d = pca_reducer.transform(kmeans.cluster_centers_)
        ax.scatter(centers_2d[:, 0], centers_2d[:, 1], c='red', marker='X', s=200,
                  edgecolors='black', linewidth=2, label='Cluster Centers')

        ax.set_xlabel(f'PC1 ({pca_reducer.explained_variance_ratio()[0]:.1%} variance)')
        ax.set_ylabel(f'PC2 ({pca_reducer.explained_variance_ratio()[1]:.1%} variance)')
        ax.set_title(title)
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Add colorbar
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Cluster')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            self.logger.info(f"Cluster visualization saved to {save_path}")

        return fig

    def plot_statistics_dashboard(self, embeddings_data: List[Dict],
                                save_path: Optional[str] = None,
                                title: str = "Embedding Statistics Dashboard") -> plt.Figure:
        """
        Create a comprehensive statistics dashboard.

        Args:
            embeddings_data: List of embedding dictionaries
            save_path: Optional path to save the plot
            title: Plot title

        Returns:
            Matplotlib figure object
        """
        self.logger.info("Creating statistics dashboard")

        # Extract embeddings and compute statistics
        from .utils import extract_embeddings_array, get_embedding_statistics
        embeddings = extract_embeddings_array(embeddings_data)

        if embeddings.size == 0:
            self.logger.warning("No embeddings found for statistics dashboard")
            return plt.figure()

        stats = get_embedding_statistics(embeddings)

        # Create dashboard
        fig, axes = plt.subplots(2, 3, figsize=(self.figsize[0]*2, self.figsize[1]*1.5), dpi=self.dpi)

        # Basic statistics
        stat_names = ['Dimension', 'Count', 'Norm Mean', 'Norm Std', 'Value Mean', 'Value Std']
        stat_values = [stats['dimension'], stats['count'], stats['norm_mean'],
                      stats['norm_std'], stats['value_mean'], stats['value_std']]

        axes[0, 0].bar(stat_names, stat_values, color=sns.color_palette("pastel"))
        axes[0, 0].set_title('Basic Statistics')
        axes[0, 0].tick_params(axis='x', rotation=45)
        axes[0, 0].grid(True, alpha=0.3)

        # Norm distribution
        norms = np.linalg.norm(embeddings, axis=1)
        axes[0, 1].hist(norms, bins=30, alpha=0.7, color='blue', edgecolor='black')
        axes[0, 1].axvline(stats['norm_mean'], color='red', linestyle='--')
        axes[0, 1].set_title('Norm Distribution')
        axes[0, 1].grid(True, alpha=0.3)

        # Value distribution (sample)
        sample_values = np.random.choice(embeddings.flatten(), size=min(10000, embeddings.size))
        axes[0, 2].hist(sample_values, bins=50, alpha=0.7, color='green', edgecolor='black')
        axes[0, 2].axvline(stats['value_mean'], color='red', linestyle='--')
        axes[0, 2].set_title('Value Distribution (Sample)')
        axes[0, 2].grid(True, alpha=0.3)

        # Sparsity
        sparsity = stats['sparsity']
        axes[1, 0].bar(['Non-zero', 'Zero'], [1-sparsity, sparsity],
                      color=['lightblue', 'lightcoral'])
        axes[1, 0].set_title('Embedding Sparsity')
        axes[1, 0].grid(True, alpha=0.3)

        # Summary text
        axes[1, 1].axis('off')
        summary_text = ".0f"".3f"".1%"
        axes[1, 1].text(0.1, 0.5, summary_text, transform=axes[1, 1].transAxes,
                       fontsize=10, verticalalignment='center',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.5))

        # Data quality indicators
        quality_indicators = ['Norm Range', 'Value Range', 'Sparsity']
        quality_values = [stats['norm_max'] - stats['norm_min'],
                         stats['value_max'] - stats['value_min'],
                         sparsity]

        bars = axes[1, 2].bar(quality_indicators, quality_values, color=sns.color_palette("Set2"))
        axes[1, 2].set_title('Data Quality Indicators')
        axes[1, 2].tick_params(axis='x', rotation=45)
        axes[1, 2].grid(True, alpha=0.3)

        fig.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            self.logger.info(f"Statistics dashboard saved to {save_path}")

        return fig

    def plot_words_in_pca_scatter(self, embeddings_data: List[Dict],
                                save_path: Optional[str] = None,
                                top_words: int = 30, title: str = "Words in PCA Space") -> plt.Figure:
        """
        Plot words positioned in PCA space with their frequency-based colors.

        Args:
            embeddings_data: List of embedding dictionaries
            save_path: Optional path to save the plot
            top_words: Number of top words to plot
            title: Plot title

        Returns:
            Matplotlib figure object
        """
        # Use the word visualizer for this functionality
        pca_reducer = PCAReducer(n_components=2, logger=self.logger)
        fig = self.word_visualizer.plot_words_in_pca_space(
            embeddings_data, pca_reducer, save_path, top_words, title
        )
        return fig

    def plot_word_frequency_distribution(self, embeddings_data: List[Dict],
                                       save_path: Optional[str] = None,
                                       top_k: int = 20,
                                       title: str = "Word Frequency Distribution") -> plt.Figure:
        """
        Plot word frequency distribution from embeddings.

        Args:
            embeddings_data: List of embedding dictionaries
            save_path: Optional path to save the plot
            top_k: Number of top words to show
            title: Plot title

        Returns:
            Matplotlib figure object
        """
        # Analyze words
        word_analyzer = WordAnalyzer(logger=self.logger)
        freq_results = word_analyzer.compute_word_frequencies(embeddings_data, top_k=None)
        word_frequencies = freq_results['word_frequencies']

        # Use word visualizer
        fig = self.word_visualizer.plot_word_frequency(
            word_frequencies, top_k, save_path, title
        )
        return fig

    def _prepare_color_data(self, embeddings_data: List[Dict], color_by: str) -> Tuple[np.ndarray, str]:
        """Prepare color data for plotting based on the specified coloring method."""
        if color_by == 'source':
            # Color by source document
            sources = [chunk.get('pdf_filename', 'unknown') for chunk in embeddings_data]
            unique_sources = list(set(sources))
            colors = np.array([unique_sources.index(s) for s in sources])
            color_label = 'Source Document'
        elif color_by == 'norm':
            # Color by vector norm
            from .utils import extract_embeddings_array
            embeddings = extract_embeddings_array(embeddings_data)
            norms = np.linalg.norm(embeddings, axis=1)
            colors = norms
            color_label = 'Vector Norm'
        elif color_by == 'index':
            # Color by index (for ordering)
            colors = np.arange(len(embeddings_data))
            color_label = 'Index'
        else:
            # Default to index
            colors = np.arange(len(embeddings_data))
            color_label = 'Index'

        return colors, color_label

    def _add_word_labels_to_pca(self, ax, embeddings_data: List[Dict],
                              pca_reducer: PCAReducer, top_words: int) -> None:
        """Add word labels to an existing PCA scatter plot."""
        try:
            # Get word embeddings and reduce to 2D
            word_analyzer = WordAnalyzer(logger=self.logger)
            word_embeddings = word_analyzer.compute_word_embeddings(embeddings_data)

            if not word_embeddings:
                return

            # Get most frequent words
            freq_results = word_analyzer.compute_word_frequencies(embeddings_data, top_k=top_words)
            top_word_list = [word for word, _ in freq_results['top_words']]
            words_to_plot = [w for w in top_word_list if w in word_embeddings][:top_words]

            if not words_to_plot:
                return

            # Get word vectors and reduce
            word_vectors = np.array([word_embeddings[w] for w in words_to_plot])
            word_vectors_2d = pca_reducer.transform(word_vectors)

            # Add word labels
            for i, word in enumerate(words_to_plot):
                ax.annotate(word, (word_vectors_2d[i, 0], word_vectors_2d[i, 1]),
                           xytext=(3, 3), textcoords='offset points',
                           fontsize=8, alpha=0.8, bbox=dict(boxstyle="round,pad=0.1",
                           facecolor="white", alpha=0.8, edgecolor="none"))

        except Exception as e:
            self.logger.warning(f"Could not add word labels to PCA plot: {e}")

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