"""Unit tests focus on *not learning* preprocessing from validation/test."""

import numpy as np
import pandas as pd
import pytest

from nids.data.load import OfficialDataset
from nids.features.preprocess import build_preprocessor, partition_data, select_features


def frame(n=40):
    return pd.DataFrame({
        "id": range(n),
        "proto": ["tcp", "udp"] * (n // 2),
        "service": ["-", "dns"] * (n // 2),
        "state": ["FIN", "INT"] * (n // 2),
        "dur": [float(i) for i in range(n)],
        "sbytes": [float(i + 1) for i in range(n)],
        "attack_cat": ["Normal", "Exploits"] * (n // 2),
        "label": [0, 1] * (n // 2),
    })


def test_partition_uses_official_holdout_without_leakage():
    train = frame(40)
    test = frame(12)
    test["dur"] = 1e9
    parts = partition_data(OfficialDataset(train, test), seed=42)
    assert len(parts.X_train) + len(parts.X_valid) == 40
    assert len(parts.X_test) == 12
    assert (parts.X_test["dur"] == 1e9).all()
    assert set(parts.X_train.index).isdisjoint(parts.X_valid.index)
    assert not {"id", "label", "attack_cat"}.intersection(parts.features)
    assert parts.y_train.value_counts().to_dict() == {0: 16, 1: 16}
    assert parts.y_valid.value_counts().to_dict() == {0: 4, 1: 4}
    assert parts.features == partition_data(OfficialDataset(train, test), seed=42).features
    assert parts.X_train.index.equals(partition_data(OfficialDataset(train, test), seed=42).X_train.index)


def test_preprocessor_learns_training_values_only_and_handles_new_categories():
    train = pd.DataFrame({
        "dur": [0.0, 2.0, np.nan, 4.0],
        "proto": ["tcp", "udp", "tcp", "udp"],
        "service": ["http", "dns", "http", "dns"],
        "state": ["FIN", "FIN", "INT", "INT"],
    })
    holdout = pd.DataFrame({
        "dur": [1000.0, np.nan],
        "proto": ["new_protocol", "tcp"],
        "service": ["new_service", "http"],
        "state": ["new_state", "FIN"],
    })
    transformer = build_preprocessor(list(train.columns))
    fitted_train = transformer.fit_transform(train)
    train_mean = transformer.named_transformers_["numeric"].named_steps["scale"].mean_[0]
    assert train_mean == pytest.approx(2.0)  # median-imputed 0,2,2,4
    transformed_test = transformer.transform(holdout)
    assert transformed_test.shape[0] == 2
    assert fitted_train.shape[1] == transformed_test.shape[1]
    assert transformer.named_transformers_["numeric"].named_steps["scale"].mean_[0] == pytest.approx(train_mean)
    assert transformed_test[0, 0] > 100  # holdout outlier does not affect training mean
    assert np.isfinite(transformed_test).all()


def test_invalid_numeric_tokens_become_missing_for_imputation():
    sample = frame(4)
    sample["dur"] = ["1.5", "?", "inf", ""]
    sample["service"] = ["http", "", None, "-"]
    features = select_features(sample)
    assert features["dur"].isna().sum() == 3
    assert features["service"].isna().sum() == 2
    assert features.loc[3, "service"] == "-"


@pytest.mark.parametrize("columns", [["dur", "label", "proto"], ["dur", "attack_cat", "proto"], ["id", "proto", "dur"]])
def test_leakage_columns_rejected(columns):
    with pytest.raises(ValueError, match="cannot be features"):
        build_preprocessor(columns)


def test_validation_fraction_out_of_bounds():
    with pytest.raises(ValueError, match="validation_fraction"):
        partition_data(OfficialDataset(frame(40), frame(10)), validation_fraction=1)


def test_train_needs_both_binary_classes():
    sample = frame(40)
    sample["label"] = 0
    with pytest.raises(ValueError, match="at least two"):
        partition_data(OfficialDataset(sample, frame(10)))
