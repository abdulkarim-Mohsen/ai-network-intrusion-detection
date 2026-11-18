"""Load and validate the *official pre-partitioned* UNSW-NB15 CSV files.

Never downloads data, joins train/test partitions, or fits transformations.
The provider's dataset license is independent from this project's MIT license.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

TRAIN_FILENAME = "UNSW_NB15_training-set.csv"
TEST_FILENAME = "UNSW_NB15_testing-set.csv"
TARGET = "label"
CATEGORICAL_FEATURES = ("proto", "service", "state")
LEAKAGE_COLUMNS = frozenset({"id", "attack_cat", TARGET})


@dataclass(frozen=True)
class OfficialDataset:
    """Original UNSW-designated training/test partitions, before any fitting."""

    train: pd.DataFrame
    test: pd.DataFrame


def validate_frame(frame: pd.DataFrame, *, source: str) -> pd.DataFrame:
    """Check required fields and require a non-missing binary target (0/1).

    Keep NaNs in predictors for later training-only imputation. Return a copy.
    """
    if frame.empty:
        raise ValueError(f"{source}: dataset is empty")
    if not frame.columns.is_unique:
        raise ValueError(f"{source}: duplicate columns")
    required = {TARGET, *CATEGORICAL_FEATURES}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"{source}: missing required columns: {', '.join(missing)}")
    labels = pd.to_numeric(frame[TARGET], errors="coerce")
    if labels.isna().any() or not labels.isin([0, 1]).all():
        raise ValueError(f"{source}: label must contain only non-missing 0 or 1")
    result = frame.copy()
    result[TARGET] = labels.astype("int64")
    return result


def load_official_split(directory: str | Path) -> OfficialDataset:
    """Read official CSVs from a *local* directory; never fetch from a URL.

    The official train/test boundary is preserved for downstream evaluation.
    """
    directory = Path(directory).expanduser()
    for filename in (TRAIN_FILENAME, TEST_FILENAME):
        if not (directory / filename).is_file():
            raise FileNotFoundError(
                f"Missing {filename} in {directory}. Download it from the "
                "official UNSW-NB15 research page for authorized academic use."
            )
    train = validate_frame(pd.read_csv(directory / TRAIN_FILENAME, low_memory=False), source=TRAIN_FILENAME)
    test = validate_frame(pd.read_csv(directory / TEST_FILENAME, low_memory=False), source=TEST_FILENAME)
    if set(train.columns) != set(test.columns):
        missing_test = sorted(set(train.columns) - set(test.columns))
        missing_train = sorted(set(test.columns) - set(train.columns))
        raise ValueError(
            "Official train/test schema mismatch; "
            f"missing from test: {missing_test}; missing from train: {missing_train}"
        )
    # Match column order without mixing records across the official split.
    return OfficialDataset(train=train, test=test.loc[:, train.columns].copy())


def dataset_summary(dataset: OfficialDataset) -> dict[str, object]:
    """Non-sensitive aggregate overview (no network identifiers or raw rows)."""
    return {
        "dataset": "UNSW-NB15",
        "source": "Official UNSW training/testing CSVs (local copies)",
        "official_train_rows": int(len(dataset.train)),
        "official_test_rows": int(len(dataset.test)),
        "training_label_counts": {str(k): int(v) for k, v in dataset.train[TARGET].value_counts().sort_index().items()},
        "test_label_counts": {str(k): int(v) for k, v in dataset.test[TARGET].value_counts().sort_index().items()},
        "column_count_including_target": int(dataset.train.shape[1]),
        "missing_training_cells": int(dataset.train.isna().sum().sum()),
        "missing_test_cells": int(dataset.test.isna().sum().sum()),
        "any_model_trained": False,
    }
