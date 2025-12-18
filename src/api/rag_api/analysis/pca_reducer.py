"""
PCA Reducer - Dimensionality reduction using Principal Component Analysis.

Provides tools for reducing embedding dimensions while preserving variance,
analyzing component importance, and transforming embeddings for visualization.
"""

import json
import numpy as np
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
from sklearn.decomposition import PCA
from datetime import datetime

from .logger import get_logger


class PCAReducer:
    """
    PCA-based dimensionality reduction for embeddings.

    Handles fitting PCA models, transforming embeddings to reduced dimensions,
    and analyzing explained variance and component importance.
    """

    def __init__(self, n_components: Optional[int] = None,
                 random_state: int = 42, logger=None):
        """
        Initialize PCA reducer.

        Args:
            n_components: Number of components to keep. If None, keep all components.
            random_state: Random state for reproducibility
            logger: Optional logger instance
        """
        self.n_components = n_components
        self.random_state = random_state
        self.pca = None
        self.is_fitted = False
        self.logger = logger or get_logger(__name__)

    def fit(self, embeddings: np.ndarray, n_components: Optional[int] = None) -> 'PCAReducer':
        """
        Fit PCA model on embeddings.

        Args:
            embeddings: Input embeddings array of shape (n_samples, n_features)
            n_components: Override number of components for this fit

        Returns:
            Self for method chaining
        """
        if embeddings.size == 0:
            raise ValueError("Cannot fit PCA on empty embeddings array")

        n_components_fit = n_components or self.n_components
        if n_components_fit is None:
            n_components_fit = min(embeddings.shape[0], embeddings.shape[1])

        self.logger.info(f"Fitting PCA with {n_components_fit} components on {embeddings.shape[0]} embeddings")

        try:
            self.pca = PCA(n_components=n_components_fit, random_state=self.random_state)
            self.pca.fit(embeddings)
            self.is_fitted = True

            explained_var = self.explained_variance_ratio()
            total_var = np.sum(explained_var)
            self.logger.info(".2%")

        except Exception as e:
            self.logger.error(f"PCA fitting failed: {e}")
            raise

        return self

    def transform(self, embeddings: np.ndarray) -> np.ndarray:
        """
        Transform embeddings to reduced dimensional space.

        Args:
            embeddings: Input embeddings to transform

        Returns:
            Transformed embeddings in reduced space

        Raises:
            RuntimeError: If PCA model is not fitted
        """
        if not self.is_fitted or self.pca is None:
            raise RuntimeError("PCA model must be fitted before transform")

        if embeddings.size == 0:
            return np.array([])

        self.logger.info(f"Transforming {embeddings.shape[0]} embeddings to {self.pca.n_components_}D space")

        try:
            transformed = self.pca.transform(embeddings)
            return transformed
        except Exception as e:
            self.logger.error(f"PCA transformation failed: {e}")
            raise

    def fit_transform(self, embeddings: np.ndarray,
                     n_components: Optional[int] = None) -> np.ndarray:
        """
        Fit PCA and transform embeddings in one step.

        Args:
            embeddings: Input embeddings
            n_components: Number of components to keep

        Returns:
            Transformed embeddings
        """
        return self.fit(embeddings, n_components).transform(embeddings)

    def explained_variance_ratio(self) -> np.ndarray:
        """
        Get explained variance ratio for each component.

        Returns:
            Array of explained variance ratios

        Raises:
            RuntimeError: If PCA model is not fitted
        """
        if not self.is_fitted or self.pca is None:
            raise RuntimeError("PCA model must be fitted to get explained variance")

        return self.pca.explained_variance_ratio_

    def explained_variance(self) -> np.ndarray:
        """
        Get explained variance for each component.

        Returns:
            Array of explained variances

        Raises:
            RuntimeError: If PCA model is not fitted
        """
        if not self.is_fitted or self.pca is None:
            raise RuntimeError("PCA model must be fitted to get explained variance")

        return self.pca.explained_variance_

    def cumulative_explained_variance(self) -> np.ndarray:
        """
        Get cumulative explained variance ratio.

        Returns:
            Array of cumulative explained variance ratios
        """
        explained_var = self.explained_variance_ratio()
        return np.cumsum(explained_var)

    def get_components(self) -> np.ndarray:
        """
        Get principal components (eigenvectors).

        Returns:
            Principal components array of shape (n_components, n_features)

        Raises:
            RuntimeError: If PCA model is not fitted
        """
        if not self.is_fitted or self.pca is None:
            raise RuntimeError("PCA model must be fitted to get components")

        return self.pca.components_

    def get_n_components_for_variance(self, target_variance: float = 0.95) -> int:
        """
        Find number of components needed to explain target variance.

        Args:
            target_variance: Target explained variance ratio (0-1)

        Returns:
            Number of components needed

        Raises:
            RuntimeError: If PCA model is not fitted
        """
        if not self.is_fitted:
            raise RuntimeError("PCA model must be fitted to analyze variance")

        cumulative_var = self.cumulative_explained_variance()
        n_components_needed = np.searchsorted(cumulative_var, target_variance) + 1

        # Ensure we don't exceed available components
        n_components_needed = min(n_components_needed, len(cumulative_var))

        return int(n_components_needed)

    def get_variance_analysis(self) -> Dict[str, Any]:
        """
        Get comprehensive variance analysis.

        Returns:
            Dictionary with variance analysis results

        Raises:
            RuntimeError: If PCA model is not fitted
        """
        if not self.is_fitted:
            raise RuntimeError("PCA model must be fitted for variance analysis")

        explained_var = self.explained_variance_ratio()
        cumulative_var = self.cumulative_explained_variance()

        # Find components for common variance thresholds
        thresholds = [0.8, 0.9, 0.95, 0.99]
        components_for_thresholds = {}

        for threshold in thresholds:
            n_comp = self.get_n_components_for_variance(threshold)
            components_for_thresholds[f"{int(threshold*100)}%"] = n_comp

        analysis = {
            'total_components': len(explained_var),
            'explained_variance_ratio': explained_var.tolist(),
            'cumulative_explained_variance': cumulative_var.tolist(),
            'components_for_variance_thresholds': components_for_thresholds,
            'variance_explained_by_top_components': {
                'first': explained_var[0] if len(explained_var) > 0 else 0,
                'first_3': np.sum(explained_var[:3]) if len(explained_var) >= 3 else np.sum(explained_var),
                'first_10': np.sum(explained_var[:10]) if len(explained_var) >= 10 else np.sum(explained_var),
                'first_50': np.sum(explained_var[:50]) if len(explained_var) >= 50 else np.sum(explained_var)
            },
            'analysis_timestamp': datetime.now().isoformat()
        }

        return analysis

    def reconstruct(self, reduced_embeddings: np.ndarray) -> np.ndarray:
        """
        Reconstruct original embeddings from reduced space.

        Args:
            reduced_embeddings: Embeddings in reduced space

        Returns:
            Reconstructed embeddings in original space

        Raises:
            RuntimeError: If PCA model is not fitted
        """
        if not self.is_fitted or self.pca is None:
            raise RuntimeError("PCA model must be fitted for reconstruction")

        try:
            reconstructed = self.pca.inverse_transform(reduced_embeddings)
            return reconstructed
        except Exception as e:
            self.logger.error(f"PCA reconstruction failed: {e}")
            raise

    def reconstruction_error(self, original_embeddings: np.ndarray,
                            reduced_embeddings: np.ndarray) -> float:
        """
        Calculate reconstruction error (MSE) between original and reconstructed embeddings.

        Args:
            original_embeddings: Original embeddings
            reduced_embeddings: Embeddings in reduced space

        Returns:
            Mean squared reconstruction error
        """
        reconstructed = self.reconstruct(reduced_embeddings)
        mse = np.mean((original_embeddings - reconstructed) ** 2)
        return float(mse)

    def save_model(self, filepath: str) -> None:
        """
        Save PCA model to file.

        Args:
            filepath: Path to save the model
        """
        if not self.is_fitted or self.pca is None:
            raise RuntimeError("Cannot save unfitted PCA model")

        save_path = Path(filepath)
        save_path.parent.mkdir(parents=True, exist_ok=True)

        model_data = {
            'pca_components': self.pca.components_.tolist(),
            'pca_explained_variance': self.pca.explained_variance_.tolist(),
            'pca_explained_variance_ratio': self.pca.explained_variance_ratio_.tolist(),
            'pca_singular_values': self.pca.singular_values_.tolist(),
            'pca_mean': self.pca.mean_.tolist(),
            'n_components': self.pca.n_components_,
            'n_features': self.pca.n_features_in_,
            'n_samples': self.pca.n_samples_,
            'random_state': self.random_state,
            'saved_timestamp': datetime.now().isoformat()
        }

        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(model_data, f, indent=2)

        self.logger.info(f"PCA model saved to {save_path.absolute()}")

    def load_model(self, filepath: str) -> 'PCAReducer':
        """
        Load PCA model from file.

        Args:
            filepath: Path to load the model from

        Returns:
            Self for method chaining
        """
        load_path = Path(filepath)
        if not load_path.exists():
            raise FileNotFoundError(f"PCA model file not found: {filepath}")

        with open(load_path, 'r', encoding='utf-8') as f:
            model_data = json.load(f)

        # Reconstruct PCA object
        from sklearn.decomposition import PCA
        self.pca = PCA(n_components=model_data['n_components'])
        self.pca.components_ = np.array(model_data['pca_components'])
        self.pca.explained_variance_ = np.array(model_data['pca_explained_variance'])
        self.pca.explained_variance_ratio_ = np.array(model_data['pca_explained_variance_ratio'])
        self.pca.singular_values_ = np.array(model_data['pca_singular_values'])
        self.pca.mean_ = np.array(model_data['pca_mean'])
        self.pca.n_features_in_ = model_data['n_features']
        self.pca.n_samples_ = model_data['n_samples']

        self.is_fitted = True
        self.random_state = model_data.get('random_state', 42)

        self.logger.info(f"PCA model loaded from {load_path.absolute()}")
        return self

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the fitted PCA model.

        Returns:
            Dictionary with model information

        Raises:
            RuntimeError: If PCA model is not fitted
        """
        if not self.is_fitted or self.pca is None:
            raise RuntimeError("PCA model must be fitted to get info")

        info = {
            'n_components': self.pca.n_components_,
            'n_features': self.pca.n_features_in_,
            'n_samples': self.pca.n_samples_,
            'explained_variance_ratio_sum': float(np.sum(self.pca.explained_variance_ratio_)),
            'random_state': self.random_state,
            'is_fitted': self.is_fitted
        }

        return info
