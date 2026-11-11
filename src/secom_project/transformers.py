"""Scikit-learn-compatible transformers for leakage-safe SECOM preprocessing."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

from secom_project.data_cleaning import CleaningConfig, fit_cleaning_plan


class SecomTrainingPreprocessor(BaseEstimator, TransformerMixin):
    """Sklearn-compatible wrapper around Phase 2 `fit_cleaning_plan()` fit on training rows only."""

    def __init__(
        self,
        missing_cutoff: float = 0.50,
        drop_constant: bool = True,
        near_constant_threshold: float | None = 0.99,
        add_missing_indicators: bool = False,
    ) -> None:
        self.missing_cutoff = missing_cutoff
        self.drop_constant = drop_constant
        self.near_constant_threshold = near_constant_threshold
        self.add_missing_indicators = add_missing_indicators

    def fit(self, X: pd.DataFrame, y: object = None) -> "SecomTrainingPreprocessor":
        del y  # strictly unsupervised; target labels never touch preprocessing
        df = self._to_dataframe(X)
        nc_thresh = self.near_constant_threshold if self.near_constant_threshold is not None else 1.01
        config = CleaningConfig(
            high_missing_threshold=self.missing_cutoff,
            near_constant_dominant_threshold=nc_thresh,
        )
        plan = fit_cleaning_plan(df, config=config)

        self.plan_ = plan
        self.input_features_ = list(df.columns)
        self.kept_features_ = list(plan.kept_features)
        self.removed_features_ = [c for c in df.columns if c not in set(plan.kept_features)]
        self.medians_ = dict(plan.imputation_medians)
        self.indicator_features_: list[str] = []
        if self.add_missing_indicators:
            miss_counts = df[self.kept_features_].isna().sum(axis=0)
            self.indicator_features_ = miss_counts[miss_counts > 0].index.tolist()
        return self

    def transform(self, X: pd.DataFrame) -> np.ndarray:
        df = self._to_dataframe(X)
        if df.empty:
            raise ValueError("Prediction input X cannot be empty.")
        missing_cols = [c for c in self.kept_features_ if c not in df.columns]
        if missing_cols:
            raise ValueError(
                f"Prediction input missing {len(missing_cols)} required sensor column(s), "
                f"starting with: {missing_cols[:5]}"
            )
        kept = df[self.kept_features_].copy()
        non_num = [c for c in kept.columns if not pd.api.types.is_numeric_dtype(kept[c])]
        if non_num:
            raise ValueError(f"Prediction input contains non-numeric column(s): {non_num[:5]}")
        kept = kept.replace([np.inf, -np.inf], np.nan)
        imputed = kept.fillna(self.medians_)
        if self.add_missing_indicators and self.indicator_features_:
            ind_df = kept[self.indicator_features_].isna().astype(np.float64)
            ind_df.columns = [f"{c}_ismissing" for c in self.indicator_features_]
            out = pd.concat([imputed, ind_df], axis=1)
        else:
            out = imputed
        return out.to_numpy(dtype=np.float64)

    def get_feature_names_out(self, input_features: object = None) -> np.ndarray:
        del input_features
        names = list(self.kept_features_) + [f"{c}_ismissing" for c in self.indicator_features_]
        return np.asarray(names, dtype=object)

    @staticmethod
    def _to_dataframe(X: object) -> pd.DataFrame:
        if isinstance(X, pd.DataFrame):
            return X.copy()
        try:
            arr = np.asarray(X, dtype=np.float64)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Prediction input could not be converted to float64 array: {exc}") from exc
        if arr.ndim != 2:
            raise ValueError(f"Prediction input array must be 2D, got {arr.ndim}D.")
        return pd.DataFrame(arr, columns=[f"sensor_{i:03d}" for i in range(arr.shape[1])])
