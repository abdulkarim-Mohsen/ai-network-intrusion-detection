"""Leakage-aware feature selection, splitting, and *unfitted* transformers.

Importing/calling partition functions never fits statistics or an estimator.
Only fit the resulting scikit-learn transformer on X_train in Phase 3.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from nids.data.load import CATEGORICAL_FEATURES, LEAKAGE_COLUMNS, TARGET, OfficialDataset

DEFAULT_SEED = 42


@dataclass(frozen=True)
class DataPartitions:
    """Feature/target partitions. Official test records remain held out."""

    X_train: pd.DataFrame
    X_valid: pd.DataFrame
    X_test: pd.DataFrame
    y_train: pd.Series
    y_valid: pd.Series
    y_test: pd.Series

    @property
    def features(self) -> tuple[str, ...]:
        return tuple(self.X_train.columns)


def select_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Drop record IDs, the binary target, and attack-category ground truth.

    Explicit feature typing matches UNSW's supplied train/test CSV schema.
    Replace invalid numeric values and infinities with NaN for *later* imputation.
    """
    columns = [c for c in frame.columns if c.strip().lower() not in LEAKAGE_COLUMNS]
    if not columns:
        raise ValueError("No usable feature columns")
    if not set(CATEGORICAL_FEATURES).issubset(columns):
        raise ValueError("Required UNSW categorical features are missing")
    X = frame.loc[:, columns].copy()
    for name in X.columns:
        if name in CATEGORICAL_FEATURES:
            s = X[name].astype("object")
            # Missing tokens are not category labels; preserve genuine '-' values.
            s = s.replace(r"^\s*$", np.nan, regex=True)
            X[name] = s.where(pd.notna(s), np.nan)
        else:
            X[name] = pd.to_numeric(X[name], errors="coerce").replace([np.inf, -np.inf], np.nan)
    return X


def partition_data(
    dataset: OfficialDataset, *, validation_fraction: float = 0.2, seed: int = DEFAULT_SEED
) -> DataPartitions:
    """Stratify *only* the official training set into fit/validation folds.

    Never use official test rows to compute features, class balance, or fit statistics.
    No train/validation/test feature transformer is fitted here.
    """
    if not 0 < validation_fraction < 1:
        raise ValueError("validation_fraction must be strictly between 0 and 1")
    X_official_train = select_features(dataset.train)
    X_test = select_features(dataset.test)
    if list(X_official_train.columns) != list(X_test.columns):
        raise ValueError("Train/test feature schema differs")
    y_official_train = dataset.train[TARGET]
    if y_official_train.nunique() != 2 or y_official_train.value_counts().min() < 2:
        raise ValueError("Training partition must contain at least two rows per class")
    try:
        X_train, X_valid, y_train, y_valid = train_test_split(
            X_official_train,
            y_official_train,
            test_size=validation_fraction,
            random_state=seed,
            stratify=y_official_train,
        )
    except ValueError as exc:
        raise ValueError(f"Cannot form a stratified validation split: {exc}") from exc
    return DataPartitions(
        X_train=X_train,
        X_valid=X_valid,
        X_test=X_test,
        y_train=y_train,
        y_valid=y_valid,
        y_test=dataset.test[TARGET].copy(),
    )


def build_preprocessor(feature_columns: tuple[str, ...] | list[str]) -> ColumnTransformer:
    """Create a new *unfitted* preprocessing transformer for model pipelines.

    SimpleImputer and StandardScaler only learn from data passed to .fit().
    Unseen categories at validation/test time are ignored rather than refitted.
    """
    names = list(feature_columns)
    if len(names) != len(set(names)):
        raise ValueError("Duplicate feature names")
    if any(name.strip().lower() in LEAKAGE_COLUMNS for name in names):
        raise ValueError("Target, attack category, and record ID cannot be features")
    cat = [name for name in names if name in CATEGORICAL_FEATURES]
    num = [name for name in names if name not in CATEGORICAL_FEATURES]
    if not cat or not num:
        raise ValueError("Expect both categorical and numeric UNSW-NB15 features")
    numeric = Pipeline([
        ("impute", SimpleImputer(strategy="median", keep_empty_features=True)),
        ("scale", StandardScaler()),
    ])
    categorical = Pipeline([
        ("impute", SimpleImputer(strategy="most_frequent", keep_empty_features=True)),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])
    return ColumnTransformer(
        transformers=[("numeric", numeric, num), ("categorical", categorical, cat)],
        remainder="drop",
    )
