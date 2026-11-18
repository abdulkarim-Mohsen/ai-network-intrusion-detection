"""Fully synthetic samples: validate model creation without real network data."""

import json

import joblib
import numpy as np
import pandas as pd
import pytest

from nids.data.load import OfficialDataset, TEST_FILENAME, TRAIN_FILENAME
from nids.models.train import (
    TrainingConfig,
    save_training_run,
    sha256_file,
    train_baselines,
    train_from_directory,
)


def synthetic_frame(size=60, *, sentinel=0.0):
    """A fictional tabular fixture; never captured packets or actual connections."""
    if size % 2:
        raise ValueError("Expected even row count")
    k = np.arange(size)
    return pd.DataFrame({
        "id": k + 1,
        "proto": np.where(k % 2 == 0, "tcp", "udp"),
        "service": np.where(k % 3 == 0, "http", "dns"),
        "state": np.where(k % 2 == 0, "FIN", "INT"),
        "dur": (k % 11).astype(float) + sentinel,
        "sbytes": (k % 17).astype(float),
        "attack_cat": np.where(k % 2 == 0, "Normal", "Generic"),
        "label": k % 2,
    })


def fixture_dataset():
    return OfficialDataset(train=synthetic_frame(), test=synthetic_frame(20, sentinel=1e8))


def test_both_models_fit_with_isolated_preprocessors():
    run = train_baselines(fixture_dataset(), TrainingConfig(forest_trees=5, logistic_max_iter=150))
    assert set(run.models) == {"logistic_regression", "random_forest"}
    logit = run.models["logistic_regression"]
    forest = run.models["random_forest"]
    assert logit.named_steps["preprocess"] is not forest.named_steps["preprocess"]
    assert type(logit.named_steps["classifier"]).__name__ == "LogisticRegression"
    assert type(forest.named_steps["classifier"]).__name__ == "RandomForestClassifier"
    assert run.manifest["training_rows"] == 48
    assert run.manifest["validation_rows"] == 12
    assert run.manifest["official_test_rows"] == 20
    assert run.manifest["training_label_counts"] == {"0": 24, "1": 24}
    assert run.manifest["validation_label_counts"] == {"0": 6, "1": 6}
    assert run.manifest["official_test_used_in_training"] is False
    assert run.manifest["held_out_evaluation_performed"] is False
    assert run.manifest["measured_model_performance"] is None
    assert not {"id", "label", "attack_cat"}.intersection(run.manifest["feature_names"])
    assert {"numpy", "pandas", "scikit_learn", "python"}.issubset(run.manifest["environment"])


def test_repeated_training_with_seed_produces_identical_validation_predictions():
    dataset = fixture_dataset()
    config = TrainingConfig(seed=17, forest_trees=7, logistic_max_iter=200)
    run_a = train_baselines(dataset, config)
    run_b = train_baselines(dataset, config)
    X = synthetic_frame(8).drop(columns=["id", "attack_cat", "label"])
    for model_name in run_a.models:
        np.testing.assert_array_equal(
            run_a.models[model_name].predict(X), run_b.models[model_name].predict(X)
        )
        np.testing.assert_allclose(
            run_a.models[model_name].predict_proba(X),
            run_b.models[model_name].predict_proba(X),
        )


def test_validation_and_official_test_outliers_do_not_change_fitted_preprocessing():
    a = fixture_dataset()
    altered_test = a.test.copy()
    altered_test["dur"] = -1e12
    altered_test["label"] = 1 - altered_test["label"]
    config = TrainingConfig(forest_trees=3)
    first = train_baselines(a, config)
    second = train_baselines(OfficialDataset(train=a.train, test=altered_test), config)
    for name in first.models:
        p1 = first.models[name].named_steps["preprocess"]
        p2 = second.models[name].named_steps["preprocess"]
        np.testing.assert_array_equal(
            p1.named_transformers_["numeric"].named_steps["scale"].mean_,
            p2.named_transformers_["numeric"].named_steps["scale"].mean_,
        )
    assert first.manifest["training_label_counts"] == second.manifest["training_label_counts"]


def test_trained_pipelines_save_and_can_predict_from_trusted_local_artifacts(tmp_path):
    run = train_baselines(fixture_dataset(), TrainingConfig(forest_trees=3))
    saved = save_training_run(run, tmp_path / "models")
    assert set(saved) == {"logistic_regression", "random_forest", "manifest"}
    manifest = json.loads((tmp_path / "models" / "training_manifest.json").read_text())
    assert manifest["status"] == "fitted_models_without_evaluation"
    X = synthetic_frame(6).drop(columns=["id", "attack_cat", "label"])
    for name in ("logistic_regression", "random_forest"):
        restored = joblib.load(saved[name])  # trusted locally created test artifacts only
        assert restored.predict(X).shape == (6,)


def test_end_to_end_training_from_synthetic_csv_writes_hashes(tmp_path):
    data = tmp_path / "raw"
    data.mkdir()
    synthetic_frame().to_csv(data / TRAIN_FILENAME, index=False)
    synthetic_frame(20).to_csv(data / TEST_FILENAME, index=False)
    output = train_from_directory(
        data, tmp_path / "models", TrainingConfig(forest_trees=3)
    )
    manifest = json.loads((tmp_path / "models" / "training_manifest.json").read_text())
    assert output["status"] == "trained_no_evaluation"
    assert output["evaluated_on_official_test"] is False
    assert manifest["source_files_sha256"][TRAIN_FILENAME] == sha256_file(data / TRAIN_FILENAME)
    assert manifest["source_files_sha256"][TEST_FILENAME] == sha256_file(data / TEST_FILENAME)
    assert len(manifest["source_files_sha256"][TRAIN_FILENAME]) == 64


def test_missing_source_does_not_create_misleading_artifacts(tmp_path):
    with pytest.raises(FileNotFoundError, match="official UNSW"):
        train_from_directory(tmp_path, tmp_path / "models")
    assert not (tmp_path / "models").exists()


@pytest.mark.parametrize("kwargs", [
    {"validation_fraction": 0}, {"validation_fraction": 1},
    {"forest_trees": 0}, {"logistic_max_iter": -2},
    {"seed": -1},
])
def test_invalid_configuration_fails_fast(kwargs):
    with pytest.raises(ValueError):
        TrainingConfig(**kwargs)
