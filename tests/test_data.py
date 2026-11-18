"""Synthetic-only tests: no UNSW records are distributed in this repository."""

import pandas as pd
import pytest

from nids.data.load import (
    OfficialDataset,
    TEST_FILENAME,
    TRAIN_FILENAME,
    dataset_summary,
    load_official_split,
    validate_frame,
)


def synthetic_frame(count=20):
    return pd.DataFrame({
        "id": list(range(count)),
        "proto": ["tcp", "udp"] * (count // 2),
        "service": ["http", "-"] * (count // 2),
        "state": ["FIN", "CON"] * (count // 2),
        "dur": [float(k) for k in range(count)],
        "sbytes": [10 + k for k in range(count)],
        "attack_cat": ["Normal", "Generic"] * (count // 2),
        "label": [0, 1] * (count // 2),
    })


def test_load_official_files_preserves_source_splits(tmp_path):
    train, test = synthetic_frame(20), synthetic_frame(10)
    train.to_csv(tmp_path / TRAIN_FILENAME, index=False)
    test.loc[:, list(reversed(test.columns))].to_csv(tmp_path / TEST_FILENAME, index=False)
    ds = load_official_split(tmp_path)
    assert len(ds.train) == 20
    assert len(ds.test) == 10
    assert list(ds.train.columns) == list(ds.test.columns)
    assert dataset_summary(ds)["training_label_counts"] == {"0": 10, "1": 10}
    assert dataset_summary(ds)["any_model_trained"] is False


def test_missing_file_error_points_to_official_source(tmp_path):
    with pytest.raises(FileNotFoundError, match="official UNSW"):
        load_official_split(tmp_path)


@pytest.mark.parametrize("bad_target", [None, 2, -1, "unknown"])
def test_reject_invalid_binary_targets(bad_target):
    sample = synthetic_frame(4)
    sample["label"] = sample["label"].astype("object")
    sample.loc[0, "label"] = bad_target
    with pytest.raises(ValueError, match="label must contain"):
        validate_frame(sample, source="synthetic")


def test_reject_missing_categorical_field():
    with pytest.raises(ValueError, match="proto"):
        validate_frame(synthetic_frame(4).drop(columns=["proto"]), source="synthetic")


def test_reject_test_schema_mismatch(tmp_path):
    synthetic_frame(10).to_csv(tmp_path / TRAIN_FILENAME, index=False)
    synthetic_frame(10).drop(columns=["sbytes"]).to_csv(tmp_path / TEST_FILENAME, index=False)
    with pytest.raises(ValueError, match="schema mismatch"):
        load_official_split(tmp_path)
