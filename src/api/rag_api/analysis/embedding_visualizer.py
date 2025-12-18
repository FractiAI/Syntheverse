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
from .logger import get_logger

# Set style
plt.style.use('default')
sns.set_palette("husl")


class EmbeddingVisualizer:
    """
    Static visualization tools for embedding analysis.

    Creates publication-quality plots and saves them as image files.
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
        try:
            plt.style.use(style)
        except ValueError:
            self.logger.warning(f"Style '{style}' not found, using default")
            plt.style.use('default')

        # Suppress warnings for cleaner output
        warnings.filterwarnings('ignore', category=UserWarning)

    def plot_pca_scatter(self, embeddings_data: List[Dict[str, Any]],
                        n_components: int = 2,
                        color_by: Optional[str] = None,
                        save_path: Optional[str] = None,
                        title: str = "PCA Embedding Visualization",
                        alpha: float = 0.7,
                        s: int = 50) -> plt.Figure:
        """
        Create 2D or 3D PCA scatterplot of embeddings.

        Args:
            embeddings_data: List of embedding dictionaries
            n_components: Number of PCA components (2 or 3)
            color_by: Field to color points by ('pdf_filename', 'chunk_index', or None)
            save_path: Path to save plot (optional)
            title: Plot title
            alpha: Transparency of points (0-1)
            s: Size of points

        Returns:
            Matplotlib figure object

        Raises:
            ValueError: If input validation fails
        """
        if n_components not in [2, 3]:
            raise ValueError("n_components must be 2 or 3")

        if not embeddings_data:
            raise ValueError("No embeddings data provided")

        if not isinstance(embeddings_data, list):
            raise ValueError("embeddings_data must be a list")

        if alpha < 0 or alpha > 1:
            raise ValueError("alpha must be between 0 and 1")

        if s <= 0:
            raise ValueError("s (point size) must be positive")

        # Extract and validate embeddings
        embeddings = []
        for i, chunk in enumerate(embeddings_data):
            if not isinstance(chunk, dict):
                raise ValueError(f"Chunk {i} is not a dictionary")
            if 'embedding' not in chunk:
                raise ValueError(f"Chunk {i} missing 'embedding' field")

            embedding = chunk['embedding']
            if isinstance(embedding, list):
                embedding = np.array(embedding, dtype=np.float32)
            elif isinstance(embedding, np.ndarray):
                embedding = embedding.astype(np.float32)
            else:
                raise ValueError(f"Invalid embedding type in chunk {i}")

            embeddings.append(embedding)

        embeddings = np.array(embeddings)

        if embeddings.size == 0:
            raise ValueError("No valid embeddings found")

        if embeddings.shape[1] < n_components:
            raise ValueError(f"Embeddings have {embeddings.shape[1]} dimensions, need at least {n_components}")

        self.logger.info(f"Creating {n_components}D PCA scatterplot for {len(embeddings)} embeddings")

        try:
            # Fit and transform PCA
            pca = PCAReducer(n_components=n_components)
            reduced_embeddings = pca.fit_transform(embeddings)
        except Exception as e:
            self.logger.error(f"PCA computation failed: {e}")
            raise

        # Create figure
        if n_components == 3:
            fig = plt.figure(figsize=self.figsize)
            ax = fig.add_subplot(111, projection='3d')
        else:
            fig, ax = plt.subplots(figsize=self.figsize)

        # Determine colors
        colors = None
        legend_elements = None

        if color_by == 'pdf_filename':
            pdf_names = [chunk.get('pdf_filename', 'unknown') for chunk in embeddings_data]
            unique_pdfs = list(set(pdf_names))
            color_map = plt.cm.get_cmap('tab10')(np.linspace(0, 1, len(unique_pdfs)))
            color_dict = dict(zip(unique_pdfs, color_map))

            colors = [color_dict[name] for name in pdf_names]

            # Create legend
            legend_elements = [mpatches.Patch(color=color_dict[name], label=name)
                             for name in unique_pdfs]

        elif color_by == 'chunk_index':
            chunk_indices = np.array([chunk.get('chunk_index', 0) for chunk in embeddings_data])
            colors = chunk_indices

        # Plot
        if n_components == 3:
            scatter = ax.scatter(reduced_embeddings[:, 0], reduced_embeddings[:, 1],
                               reduced_embeddings[:, 2], c=colors, alpha=0.7, s=50)
        else:
            scatter = ax.scatter(reduced_embeddings[:, 0], reduced_embeddings[:, 1],
                               c=colors, alpha=0.7, s=50)

        # Labels and title
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel(f'PC1 ({pca.explained_variance_ratio()[0]:.1%} variance)')
        ax.set_ylabel(f'PC2 ({pca.explained_variance_ratio()[1]:.1%} variance)')

        if n_components == 3:
            ax.set_zlabel(f'PC3 ({pca.explained_variance_ratio()[2]:.1%} variance)')

        # Add legend if coloring by category
        if legend_elements:
            ax.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), loc='upper left')

        # Add colorbar if coloring by numeric value
        if color_by == 'chunk_index' and colors is not None:
            plt.colorbar(scatter, ax=ax, label='Chunk Index')

        plt.tight_layout()

        # Save if requested
        if save_path:
            self._save_plot(fig, save_path)

        return fig

    def plot_similarity_heatmap(self, embeddings_data: List[Dict],
                               max_samples: int = 1000,
                               save_path: Optional[str] = None,
                               title: str = "Embedding Similarity Heatmap") -> plt.Figure:
        """
        Create heatmap visualization of embedding similarities.

        Args:
            embeddings_data: List of embedding dictionaries
            max_samples: Maximum number of embeddings to include
            save_path: Path to save plot (optional)
            title: Plot title

        Returns:
            Matplotlib figure object
        """
        if not embeddings_data:
            raise ValueError("No embeddings data provided")

        # Sample embeddings if too many
        if len(embeddings_data) > max_samples:
            indices = np.random.choice(len(embeddings_data), max_samples, replace=False)
            sampled_data = [embeddings_data[i] for i in indices]
            self.logger.info(f"Sampled {max_samples} embeddings from {len(embeddings_data)} for heatmap")
        else:
            sampled_data = embeddings_data

        # Extract embeddings and compute similarities
        from .utils import compute_pairwise_cosine_similarity, extract_embeddings_array
        embeddings_array = extract_embeddings_array(sampled_data)
        similarity_matrix = compute_pairwise_cosine_similarity(embeddings_array)

        self.logger.info(f"Creating similarity heatmap for {len(sampled_data)} embeddings")

        # Create heatmap
        fig, ax = plt.subplots(figsize=(12, 10))

        # Mask diagonal for better visualization
        mask = np.eye(len(similarity_matrix), dtype=bool)

        sns.heatmap(similarity_matrix, mask=mask, square=True, cmap='RdYlBu_r',
                   vmin=-1, vmax=1, center=0, ax=ax,
                   cbar_kws={'label': 'Cosine Similarity'})

        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('Embedding Index')
        ax.set_ylabel('Embedding Index')

        plt.tight_layout()

        # Save if requested
        if save_path:
            self._save_plot(fig, save_path)

        return fig

    def plot_embedding_distribution(self, embeddings_data: List[Dict],
                                   save_path: Optional[str] = None,
                                   title: str = "Embedding Value Distribution") -> plt.Figure:
        """
        Create distribution plots for embedding values and norms.

        Args:
            embeddings_data: List of embedding dictionaries
            save_path: Path to save plot (optional)
            title: Plot title

        Returns:
            Matplotlib figure object
        """
        if not embeddings_data:
            raise ValueError("No embeddings data provided")

        # Extract embeddings and compute statistics
        embeddings_array = np.array([chunk['embedding'] for chunk in embeddings_data])
        norms = np.linalg.norm(embeddings_array, axis=1)
        all_values = embeddings_array.flatten()

        self.logger.info(f"Creating distribution plots for {len(embeddings_data)} embeddings")

        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(title, fontsize=16, fontweight='bold')

        # Norm distribution
        axes[0, 0].hist(norms, bins=50, alpha=0.7, color='blue', edgecolor='black')
        axes[0, 0].set_title('Embedding Norms Distribution')
        axes[0, 0].set_xlabel('Norm Value')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].axvline(np.mean(norms), color='red', linestyle='--', label=f'Mean: {np.mean(norms):.3f}')
        axes[0, 0].legend()

        # Norm boxplot
        axes[0, 1].boxplot(norms, orientation='horizontal')
        axes[0, 1].set_title('Embedding Norms Boxplot')
        axes[0, 1].set_xlabel('Norm Value')

        # Value distribution (sample for large datasets)
        max_values = min(100000, len(all_values))
        sampled_values = np.random.choice(all_values, max_values, replace=False)

        axes[1, 0].hist(sampled_values, bins=100, alpha=0.7, color='green', edgecolor='black')
        axes[1, 0].set_title('Embedding Values Distribution')
        axes[1, 0].set_xlabel('Value')
        axes[1, 0].set_ylabel('Frequency')
        axes[1, 0].axvline(np.mean(sampled_values), color='red', linestyle='--',
                          label=f'Mean: {np.mean(sampled_values):.6f}')
        axes[1, 0].legend()

        # Value boxplot
        axes[1, 1].boxplot(sampled_values, orientation='horizontal')
        axes[1, 1].set_title('Embedding Values Boxplot')
        axes[1, 1].set_xlabel('Value')

        plt.tight_layout()

        # Save if requested
        if save_path:
            self._save_plot(fig, save_path)

        return fig

    def plot_cluster_visualization(self, embeddings_data: List[Dict],
                                  cluster_labels: List[int],
                                  save_path: Optional[str] = None,
                                  title: str = "Embedding Clusters") -> plt.Figure:
        """
        Visualize embedding clusters in reduced dimensional space.

        Args:
            embeddings_data: List of embedding dictionaries
            cluster_labels: Cluster labels for each embedding
            save_path: Path to save plot (optional)
            title: Plot title

        Returns:
            Matplotlib figure object
        """
        if not embeddings_data or not cluster_labels:
            raise ValueError("Embeddings data and cluster labels required")

        if len(embeddings_data) != len(cluster_labels):
            raise ValueError("Number of embeddings must match number of cluster labels")

        # Reduce to 2D for visualization
        embeddings_array = np.array([chunk['embedding'] for chunk in embeddings_data])
        pca = PCAReducer(n_components=2)
        reduced_embeddings = pca.fit_transform(embeddings_array)

        self.logger.info(f"Creating cluster visualization for {len(cluster_labels)} points")

        # Create plot
        fig, ax = plt.subplots(figsize=self.figsize)

        # Get unique clusters
        unique_clusters = sorted(list(set(cluster_labels)))
        colors = plt.cm.get_cmap('tab10')(np.linspace(0, 1, len(unique_clusters)))

        # Plot each cluster
        for i, cluster_id in enumerate(unique_clusters):
            mask = np.array(cluster_labels) == cluster_id
            cluster_points = reduced_embeddings[mask]

            ax.scatter(cluster_points[:, 0], cluster_points[:, 1],
                      c=[colors[i]], alpha=0.7, s=50, label=f'Cluster {cluster_id}')

        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel(f'PC1 ({pca.explained_variance_ratio()[0]:.1%} variance)')
        ax.set_ylabel(f'PC2 ({pca.explained_variance_ratio()[1]:.1%} variance)')

        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()

        # Save if requested
        if save_path:
            self._save_plot(fig, save_path)

        return fig

    def plot_statistics_dashboard(self, statistics: Dict[str, Any],
                                save_path: Optional[str] = None,
                                title: str = "Embedding Statistics Dashboard") -> plt.Figure:
        """
        Create comprehensive statistics dashboard.

        Args:
            statistics: Statistics dictionary from EmbeddingAnalyzer
            save_path: Path to save plot (optional)
            title: Plot title

        Returns:
            Matplotlib figure object
        """
        if not statistics:
            raise ValueError("Statistics data required")

        self.logger.info("Creating statistics dashboard")

        # Create figure with multiple subplots
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle(title, fontsize=16, fontweight='bold')

        # Norm distribution
        if 'norm_mean' in statistics and 'norm_std' in statistics:
            # Simulate norm distribution for plotting
            x = np.linspace(statistics['norm_min'], statistics['norm_max'], 100)
            y = (1 / (statistics['norm_std'] * np.sqrt(2 * np.pi))) * \
                np.exp(-0.5 * ((x - statistics['norm_mean']) / statistics['norm_std']) ** 2)

            axes[0, 0].plot(x, y, 'b-', linewidth=2)
            axes[0, 0].fill_between(x, y, alpha=0.3)
            axes[0, 0].axvline(statistics['norm_mean'], color='red', linestyle='--',
                              label=f'Mean: {statistics["norm_mean"]:.3f}')
            axes[0, 0].set_title('Norm Distribution')
            axes[0, 0].set_xlabel('Norm Value')
            axes[0, 0].set_ylabel('Density')
            axes[0, 0].legend()

        # Source distribution (if available)
        if 'sources' in statistics and statistics['sources']:
            sources = list(statistics['sources'].keys())
            counts = list(statistics['sources'].values())

            axes[0, 1].bar(sources, counts, color='skyblue', edgecolor='black')
            axes[0, 1].set_title('Embeddings by Source')
            axes[0, 1].set_xlabel('Source')
            axes[0, 1].set_ylabel('Count')
            axes[0, 1].tick_params(axis='x', rotation=45)

        # Key metrics table
        axes[0, 2].axis('off')
        metrics_text = ".1f"".1f"".1f"f"""
        Total Embeddings: {statistics.get('total_embeddings', 'N/A')}
        Dimension: {statistics.get('dimension', 'N/A')}
        Norm Mean: {statistics.get('norm_mean', 'N/A'):.3f}
        Norm Std: {statistics.get('norm_std', 'N/A'):.3f}
        Sparsity: {statistics.get('sparsity', 'N/A'):.3%}
        Outliers: {statistics.get('outliers', 'N/A')}
        Clusters: {statistics.get('clusters', 'N/A')}
        """
        axes[0, 2].text(0.1, 0.9, metrics_text, transform=axes[0, 2].transAxes,
                        fontsize=10, verticalalignment='top', fontfamily='monospace')

        # Value distribution (simplified)
        if 'value_mean' in statistics and 'value_std' in statistics:
            x_vals = np.linspace(statistics['value_min'], statistics['value_max'], 100)
            y_vals = (1 / (statistics['value_std'] * np.sqrt(2 * np.pi))) * \
                    np.exp(-0.5 * ((x_vals - statistics['value_mean']) / statistics['value_std']) ** 2)

            axes[1, 0].plot(x_vals, y_vals, 'g-', linewidth=2)
            axes[1, 0].fill_between(x_vals, y_vals, alpha=0.3)
            axes[1, 0].axvline(statistics['value_mean'], color='red', linestyle='--',
                              label=f'Mean: {statistics["value_mean"]:.6f}')
            axes[1, 0].set_title('Value Distribution')
            axes[1, 0].set_xlabel('Value')
            axes[1, 0].set_ylabel('Density')
            axes[1, 0].legend()

        # Placeholder for additional plots
        axes[1, 1].text(0.5, 0.5, 'Additional\nAnalysis\nComing Soon',
                       transform=axes[1, 1].transAxes, ha='center', va='center',
                       fontsize=12, alpha=0.7)
        axes[1, 1].set_title('Future Analysis')
        axes[1, 1].set_xlim(0, 1)
        axes[1, 1].set_ylim(0, 1)
        axes[1, 1].axis('off')

        axes[1, 2].text(0.5, 0.5, 'Metadata\nAnalysis\nComing Soon',
                       transform=axes[1, 2].transAxes, ha='center', va='center',
                       fontsize=12, alpha=0.7)
        axes[1, 2].set_title('Metadata Insights')
        axes[1, 2].set_xlim(0, 1)
        axes[1, 2].set_ylim(0, 1)
        axes[1, 2].axis('off')

        plt.tight_layout()

        # Save if requested
        if save_path:
            self._save_plot(fig, save_path)

        return fig

    def plot_pca_variance_explained(self, pca_reducer: PCAReducer,
                                   save_path: Optional[str] = None,
                                   title: str = "PCA Explained Variance") -> plt.Figure:
        """
        Plot explained variance by PCA components.

        Args:
            pca_reducer: Fitted PCAReducer instance
            save_path: Path to save plot (optional)
            title: Plot title

        Returns:
            Matplotlib figure object
        """
        if not pca_reducer.is_fitted:
            raise ValueError("PCA reducer must be fitted")

        explained_var = pca_reducer.explained_variance_ratio()
        cumulative_var = pca_reducer.cumulative_explained_variance()

        self.logger.info("Creating PCA variance explained plot")

        # Create plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        fig.suptitle(title, fontsize=14, fontweight='bold')

        # Individual explained variance
        components = np.arange(1, len(explained_var) + 1)
        ax1.bar(components, explained_var * 100, color='skyblue', edgecolor='black', alpha=0.7)
        ax1.set_title('Explained Variance by Component')
        ax1.set_xlabel('Principal Component')
        ax1.set_ylabel('Explained Variance (%)')
        ax1.grid(axis='y', alpha=0.3)

        # Cumulative explained variance
        ax2.plot(components, cumulative_var * 100, 'r-', linewidth=2, marker='o')
        ax2.axhline(y=95, color='green', linestyle='--', alpha=0.7, label='95% threshold')
        ax2.axhline(y=90, color='orange', linestyle='--', alpha=0.7, label='90% threshold')
        ax2.set_title('Cumulative Explained Variance')
        ax2.set_xlabel('Number of Components')
        ax2.set_ylabel('Cumulative Explained Variance (%)')
        ax2.grid(axis='both', alpha=0.3)
        ax2.legend()

        # Add text annotations for key thresholds
        for threshold in [0.8, 0.9, 0.95]:
            n_comp = pca_reducer.get_n_components_for_variance(threshold)
            if n_comp <= len(cumulative_var):
                y_pos = cumulative_var[n_comp - 1] * 100
                ax2.annotate('.0f',
                           xy=(n_comp, y_pos),
                           xytext=(5, 5), textcoords='offset points',
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.8))

        plt.tight_layout()

        # Save if requested
        if save_path:
            self._save_plot(fig, save_path)

        return fig

    def _save_plot(self, fig: plt.Figure, save_path: str) -> None:
        """
        Save matplotlib figure to file.

        Args:
            fig: Matplotlib figure
            save_path: Path to save file
        """
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)

        # Determine format from extension
        if save_path.suffix.lower() in ['.png', '.jpg', '.jpeg']:
            format_type = 'png'
        elif save_path.suffix.lower() == '.svg':
            format_type = 'svg'
        elif save_path.suffix.lower() == '.pdf':
            format_type = 'pdf'
        else:
            format_type = 'png'
            save_path = save_path.with_suffix('.png')

        try:
            fig.savefig(save_path, dpi=self.dpi, format=format_type, bbox_inches='tight')
            self.logger.info(f"Plot saved to {save_path.absolute()}")
        except Exception as e:
            self.logger.error(f"Failed to save plot: {e}")
            raise
