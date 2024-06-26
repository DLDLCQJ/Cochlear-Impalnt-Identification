import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.decomposition import PCA
from sklearn.base import BaseEstimator, TransformerMixin
import typing
from textwrap import wrap

class ScalerPCA(BaseEstimator, TransformerMixin):
    def __init__(self, variance_threshold=0.95):
        self.variance_threshold = variance_threshold
        self.scaler = StandardScaler(with_std=False)
        self.pca = PCA()

    def fit(self, X, y=None):
        X_scaled = self.scaler.fit_transform(X)
        self.pca.fit(X_scaled)
        cumulative_variance = np.cumsum(self.pca.explained_variance_ratio_)
        self.n_components_ = np.argmax(cumulative_variance >= self.variance_threshold) + 1
        self.pca = PCA(n_components=self.n_components_)
        self.pca.fit(X_scaled)
        return self

    def transform(self, X, y=None):
        X_scaled = self.scaler.transform(X)
        X_pca = self.pca.transform(X_scaled)
        return X_pca
    
class Preprocessor:
    def __init__(self, preprocess: typing.Union[str, bool, None] = None,
                    **kwargs) -> None:
        from sklearn.pipeline import Pipeline

        preprocessor_classes = {
            'demean': StandardScaler(with_std=False),
            'demean_std': StandardScaler(with_std=True),
            'minmax': MinMaxScaler,
            'pca_auto': ScalerPCA(variance_threshold=0.95),
            'pca100': Pipeline([('scaler', StandardScaler(with_std=False)), ('pca', PCA(n_components=100))]),
            'pca10': Pipeline([('scaler', StandardScaler(with_std=False)), ('pca', PCA(n_components=10))]),
            None: None
        }

        if preprocess not in preprocessor_classes:
            raise ValueError(f'Preprocess setting {preprocess} does not exist in preprocessor_classes')

        self.unfitted_scaler = preprocessor_classes[preprocess]
        self.preprocess_name = preprocess

    def fit(self, A_raw: typing.Union[pd.DataFrame, np.ndarray] = None):
        if self.unfitted_scaler is not None:
            fitted_scaler = self.unfitted_scaler.fit(A_raw) 
        else:
            fitted_scaler = None

        return fitted_scaler

    def transform(self, scaler: typing.Union[StandardScaler, MinMaxScaler] = None,
                    A_raw: typing.Union[pd.DataFrame, np.ndarray] = None):
        if scaler is not None:
            A_scaled = scaler.transform(A_raw)

            if type(A_raw) == pd.DataFrame:
                if self.preprocess_name.startswith(
                        'pca'):  
                    A_scaled = pd.DataFrame(data=A_scaled, index=A_raw.index)
                else:
                    A_scaled = pd.DataFrame(A_scaled, index=A_raw.index, columns=A_raw.columns)

        else:
            A_scaled = A_raw

        return A_scaled
    
