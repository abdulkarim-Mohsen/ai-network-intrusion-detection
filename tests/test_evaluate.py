"""Evaluation checks use only synthetic, fictional tabular samples."""

import json

import numpy as np
import pandas as pd
import pytest

from nids.data.load import OfficialDataset, TEST_FILENAME, TRAIN_FILENAME
from nids.models.evaluate import (
    calculate_metrics,
    evaluate_baselines,
    evaluate_from_directory,
)
from nids.models.train import TrainingConfig


def sample_frame(n=60):
    k = np.arange(n)
    return pd.DataFrame({
        "id": k + 1,
        "proto": np.where(k % 2 == 0, "tcp", "udp"),
        "service": np.where(k % 3 == 0, "http", "dns"),
        "state": np.where(k % 2 == 0, "FIN", "INT"),
        "dur": (k % 13).astype(float),
        "sbytes": ((k * 7) % 19).astype(float),
        "attack_cat": np.where(k % 2 == 0, "Normal", "Generic"),
        "label": k % 2,
    })


def test_known_metrics_include_false_alarms_and_roc_auc():
    result = calculate_metrics(
        [0, 0, 1, 1], [0, 1, 0, 1], [0.1, 0.8, 0.4, 0.9]
    )
    assert result["confusion_matrix"] == [[1, 1], [1, 1]]
    assert result["false_positive_rate"] == pytest.approx(0.5)
    assert result["false_negative_rate"] == pytest.approx(0.5)
    assert result["per_class"]["1"]["precision"] == pytest.approx(0.5)
    assert result["per_class"]["1"]["recall"] == pytest.approx(0.5)
    assert result["per_class"]["1"]["f1"] == pytest.approx(0.5)
    assert result["roc_auc"] == pytest.approx(0.75)


def test_perfect_predictions_score_one():
    result = calculate_metrics([0, 1, 0, 1], [0, 1, 0, 1], [0.1, 0.9, 0.2, 0.8])
    assert result["false_positive_rate"] == 0
    assert result["false_negative_rate"] == 0
    assert result["macro_f1"] == 1
    assert result["roc_auc"] == 1


@pytest.mark.parametrize("labels,preds,scores,rate", [
    ([1, 1], [1, 0], [0.9, 0.3], None),
    ([0, 0], [0, 1], [0.1, 0.7], 0.5),
])
def test_single_class_roc_auc_undefined(labels, preds, scores, rate):
    result = calculate_metrics(labels, preds, scores)
    assert result["roc_auc"] is None
    assert "undefined" in result["roc_auc_note"].lower()
    assert result["false_positive_rate"] == rate


@pytest.mark.parametrize("truth,pred,scores", [
    ([], [], None),
    ([0, 1], [0], None),
    ([0, 2], [0, 1], None),
    ([0, 1], [0, 1], [0.1]),
    ([0, 1], [0, 1], [0.1, float("nan")]),
])
def test_invalid_inputs_rejected(truth, pred, scores):
    with pytest.raises(ValueError):
        calculate_metrics(truth, pred, scores)


def test_validation_selection_does_not_peek_at_test_labels():
    dataset = OfficialDataset(train=sample_frame(60), test=sample_frame(20))
    modified_test = dataset.test.copy()
    modified_test["label"] = 1 - modified_test["label"]
    config = TrainingConfig(seed=25, forest_trees=3, logistic_max_iter=200)
    initial, _, _ = evaluate_baselines(dataset, config)
    changed, _, _ = evaluate_baselines(
        OfficialDataset(train=dataset.train, test=modified_test), config
    )
    assert initial["selected_model"] == changed["selected_model"]
    assert initial["validation"] == changed["validation"]
    assert initial["selection_protocol"]["test_models_evaluated"] == [initial["selected_model"]]
    assert initial["source_data_type"].startswith("user-supplied")
    assert not initial["dataset_authenticity_verified_by_code"]


def test_full_offline_evaluation_writes_aggregate_report_and_figures(tmp_path):
    input_dir = tmp_path / "raw"
    input_dir.mkdir()
    sample_frame().to_csv(input_dir / TRAIN_FILENAME, index=False)
    sample_frame(20).to_csv(input_dir / TEST_FILENAME, index=False)
    output_dir = tmp_path / "reports"
    summary = evaluate_from_directory(
        input_dir, output_dir,
        TrainingConfig(seed=7, forest_trees=3, logistic_max_iter=200),
    )
    assert summary["status"] == "evaluation_completed"
    report = json.loads((output_dir / "evaluation.json").read_text(encoding="utf-8"))
    assert set(report["validation"]) == {"logistic_regression", "random_forest"}
    assert report["official_test_selected_model"]["sample_count"] == 20
    assert report["official_test_selected_model"]["roc_auc"] is not None
    assert (output_dir / "confusion_matrix.png").stat().st_size > 1000
    assert (output_dir / "roc_curve.png").stat().st_size > 1000
    assert report["source_files_sha256"][TRAIN_FILENAME]
    assert "prediction" not in report
    assert not (output_dir / "raw_predictions.csv").exists()
    assert not (output_dir / "logistic_regression.joblib").exists()


def test_missing_source_does_not_write_evaluation_results(tmp_path):
    with pytest.raises(FileNotFoundError):
        evaluate_from_directory(tmp_path, tmp_path / "reports")
    assert not (tmp_path / "reports").exists()
