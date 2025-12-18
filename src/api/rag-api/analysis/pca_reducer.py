"""
PCA Reducer - Dimensionality reduction using Principal Component Analysis.

Provides PCA-based dimensionality reduction for embedding visualization
and analysis.
"""

import numpy as np
from typing import Optional, Tuple, Dict, Any
from pathlib import Path
import pickle

try:
    from sklearn.decomposition import PCA
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

from .logger import get_logger


class PCAReducer:
    """
    PCA-based dimensionality reduction for embeddings.

    Reduces high-dimensional embeddings to 2D or 3D for visualization
    while preserving maximum variance.
    """

    def __init__(self, n_components: Optional[int] = None,
                 random_state: int = 42, logger=None):
        """
        Initialize PCA reducer.

        Args:
            n_components: Number of components to keep (None for all)
            random_state: Random seed for reproducibility
            logger: Optional logger instance
        """
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn is required for PCA functionality")

        self.n_components = n_components
        self.random_state = random_state
        self.logger = logger or get_logger(__name__)
        self.pca = None
        self.is_fitted = False

    def fit(self, embeddings: np.ndarray) -> 'PCAReducer':
        """
        Fit PCA on the embeddings.

        Args:
            embeddings: Array of embeddings (n_samples, n_features)

        Returns:
            Self for method chaining
        """
        if embeddings.ndim != 2:
            raise ValueError("Embeddings must be a 2D array")

        if embeddings.shape[0] < 2:
            raise ValueError("Need at least 2 embeddings to fit PCA")

        self.logger.info(f"Fitting PCA on {embeddings.shape[0]} embeddings "
                        f"with {embeddings.shape[1]} dimensions")

        # Determine number of components
        n_components = self.n_components
        if n_components is None:
            n_components = min(embeddings.shape[0], embeddings.shape[1])
        else:
            n_components = min(n_components, embeddings.shape[0], embeddings.shape[1])

        self.pca = PCA(n_components=n_components, random_state=self.random_state)
        self.pca.fit(embeddings)
        self.is_fitted = True

        explained_var = np.sum(self.pca.explained_variance_ratio_)
        self.logger.info(f"PCA fitted. Explained variance: {explained_var:.3f}")

        return self

    def transform(self, embeddings: np.ndarray) -> np.ndarray:
        """
        Transform embeddings to reduced dimensionality.

        Args:
            embeddings: Array of embeddings to transform

        Returns:
            Reduced dimensionality embeddings
        """
        if not self.is_fitted:
            raise RuntimeError("PCA must be fitted before transform")

        if embeddings.ndim != 2:
            raise ValueError("Embeddings must be a 2D array")

        self.logger.info(f"Transforming {embeddings.shape[0]} embeddings to "
                        f"{self.pca.n_components_} dimensions")

        return self.pca.transform(embeddings)

    def fit_transform(self, embeddings: np.ndarray) -> np.ndarray:
        """
        Fit PCA and transform embeddings in one step.

        Args:
            embeddings: Array of embeddings

        Returns:
            Reduced dimensionality embeddings
        """
        return self.fit(embeddings).transform(embeddings)

    def explained_variance_ratio(self) -> np.ndarray:
        """
        Get the explained variance ratio for each component.

        Returns:
            Array of explained variance ratios
        """
        if not self.is_fitted:
            raise RuntimeError("PCA must be fitted to get explained variance")

        return self.pca.explained_variance_ratio_

    def get_components(self) -> np.ndarray:
        """
        Get the principal components (eigenvectors).

        Returns:
            Principal components array
        """
        if not self.is_fitted:
            raise RuntimeError("PCA must be fitted to get components")

        return self.pca.components_

    def get_cumulative_variance(self) -> np.ndarray:
        """
        Get cumulative explained variance ratio.

        Returns:
            Cumulative variance array
        """
        return np.cumsum(self.explained_variance_ratio())

    def find_optimal_components(self, embeddings: np.ndarray,
                              variance_threshold: float = 0.95) -> int:
        """
        Find the optimal number of components to explain the target variance.

        Args:
            embeddings: Array of embeddings to analyze
            variance_threshold: Target explained variance (0-1)

        Returns:
            Optimal number of components
        """
        if not 0 < variance_threshold <= 1:
            raise ValueError("Variance threshold must be between 0 and 1")

        # Fit PCA with all components
        temp_pca = PCA(random_state=self.random_state)
        temp_pca.fit(embeddings)

        cumulative_var = np.cumsum(temp_pca.explained_variance_ratio_)
        optimal_components = np.where(cumulative_var >= variance_threshold)[0]

        if len(optimal_components) == 0:
            return len(cumulative_var)  # Use all components

        return optimal_components[0] + 1  # +1 because indices start at 0

    def save_model(self, filepath: str) -> None:
        """
        Save the fitted PCA model to disk.

        Args:
            filepath: Path to save the model
        """
        if not self.is_fitted:
            raise RuntimeError("Cannot save unfitted PCA model")

        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        model_data = {
            'pca': self.pca,
            'n_components': self.n_components,
            'random_state': self.random_state,
            'is_fitted': self.is_fitted
        }

        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)

        self.logger.info(f"PCA model saved to {filepath}")

    def load_model(self, filepath: str) -> 'PCAReducer':
        """
        Load a fitted PCA model from disk.

        Args:
            filepath: Path to load the model from

        Returns:
            Self with loaded model
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"Model file not found: {filepath}")

        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)

        self.pca = model_data['pca']
        self.n_components = model_data['n_components']
        self.random_state = model_data['random_state']
        self.is_fitted = model_data['is_fitted']

        self.logger.info(f"PCA model loaded from {filepath}")
        return self

    def get_pca_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about the fitted PCA.

        Returns:
            Dictionary with PCA statistics
        """
        if not self.is_fitted:
            raise RuntimeError("PCA must be fitted to get statistics")

        explained_var = self.explained_variance_ratio()
        cumulative_var = self.get_cumulative_variance()

        return {
            'n_components': self.pca.n_components_,
            'explained_variance_ratio': explained_var.tolist(),
            'cumulative_variance': cumulative_var.tolist(),
            'singular_values': self.pca.singular_values_.tolist(),
            'total_explained_variance': float(np.sum(explained_var)),
            'components_shape': self.pca.components_.shape
        }

    def plot_variance_explained(self, save_path: Optional[str] = None) -> Optional[object]:
        """
        Plot the explained variance for each component.

        Args:
            save_path: Optional path to save the plot

        Returns:
            Matplotlib figure if matplotlib available
        """
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns

            if not self.is_fitted:
                raise RuntimeError("PCA must be fitted to plot variance")

            explained_var = self.explained_variance_ratio()
            cumulative_var = self.get_cumulative_variance()

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

            # Individual explained variance
            ax1.bar(range(1, len(explained_var) + 1), explained_var * 100,
                   color=sns.color_palette("husl", len(explained_var)))
            ax1.set_xlabel('Principal Component')
            ax1.set_ylabel('Explained Variance (%)')
            ax1.set_title('Individual Explained Variance')
            ax1.grid(True, alpha=0.3)

            # Cumulative explained variance
            ax2.plot(range(1, len(cumulative_var) + 1), cumulative_var * 100,
                    'o-', linewidth=2, markersize=6, color='darkblue')
            ax2.axhline(y=95, color='red', linestyle='--', alpha=0.7, label='95% threshold')
            ax2.set_xlabel('Number of Components')
            ax2.set_ylabel('Cumulative Explained Variance (%)')
            ax2.set_title('Cumulative Explained Variance')
            ax2.legend()
            ax2.grid(True, alpha=0.3)

            plt.tight_layout()

            if save_path:
                plt.savefig(save_path, dpi=150, bbox_inches='tight')
                self.logger.info(f"Variance explained plot saved to {save_path}")

            return fig

        except ImportError:
            self.logger.warning("matplotlib or seaborn not available for plotting")
            return None