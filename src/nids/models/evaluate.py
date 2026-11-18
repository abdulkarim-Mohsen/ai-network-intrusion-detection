"""Offline, leakage-aware evaluation of the two trained UNSW-NB15 baselines.

Model selection uses *only* the validation split (positive-class F1).
The held-out provider test split is evaluated once, for the selected model.
No row-level predictions, network addresses, or raw data are written to disk.
"""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import pandas as pd
from sklearn.metrics import (
    confusion_matrix,
    precision_recall_fscore_support,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline

from nids.data.load import TEST_FILENAME, TRAIN_FILENAME, load_official_split
from nids.features.preprocess import DataPartitions, partition_data
from nids.models.train import TrainingConfig, sha256_file, train_baselines


LABELS = (0, 1)


def _positive_probabilities(model: Pipeline, X: pd.DataFrame) -> np.ndarray:
    """Return attack probabilities, using the estimator's actual class order."""
    if not hasattr(model, "predict_proba"):
        raise ValueError("Binary ROC-AUC requires an estimator with predict_proba")
    classes = list(model.classes_)
    if set(classes) != set(LABELS):
        raise ValueError("Expected classifier classes {0, 1}")
    scores = np.asarray(model.predict_proba(X)[:, classes.index(1)], dtype=float)
    if scores.ndim != 1 or len(scores) != len(X) or not np.isfinite(scores).all():
        raise ValueError("Classifier returned invalid probability scores")
    return scores


def calculate_metrics(
    y_true: pd.Series | np.ndarray | list[int],
    y_pred: pd.Series | np.ndarray | list[int],
    y_score: pd.Series | np.ndarray | list[float] | None = None,
) -> dict[str, Any]:
    """Compute binary metrics with explicit zero denominators and label order.

    Rows in the confusion matrix = true class [0, 1]; columns = predicted
    class [0, 1]. FPR = FP / (FP + TN) for attacks (label 1).
    """
    truth = np.asarray(y_true)
    predicted = np.asarray(y_pred)
    if truth.ndim != 1 or predicted.ndim != 1 or len(truth) != len(predicted):
        raise ValueError("Labels and predictions must be equal-length 1D arrays")
    if not len(truth):
        raise ValueError("Cannot evaluate an empty split")
    if not np.isin(truth, LABELS).all() or not np.isin(predicted, LABELS).all():
        raise ValueError("Binary evaluation requires labels/predictions in {0, 1}")

    matrix = confusion_matrix(truth, predicted, labels=LABELS)
    tn, fp, fn, tp = (int(x) for x in matrix.ravel())
    precision, recall, f1, support = precision_recall_fscore_support(
        truth, predicted, labels=LABELS, average=None, zero_division=0
    )
    results: dict[str, Any] = {
        "sample_count": int(len(truth)),
        "class_counts": {"0": int(tn + fp), "1": int(fn + tp)},
        "label_mapping": {"0": "normal", "1": "attack"},
        "confusion_matrix": matrix.astype(int).tolist(),
        "confusion_matrix_convention": "rows=true, columns=predicted; order=[0,1]",
        "true_negatives": tn,
        "false_positives": fp,
        "false_negatives": fn,
        "true_positives": tp,
        "accuracy": float((tp + tn) / len(truth)),
        "per_class": {
            str(label): {
                "precision": float(precision[idx]),
                "recall": float(recall[idx]),
                "f1": float(f1[idx]),
                "support": int(support[idx]),
            }
            for idx, label in enumerate(LABELS)
        },
        "macro_f1": float(np.mean(f1)),
        "weighted_f1": float(np.average(f1, weights=support)),
        "false_positive_rate": (float(fp / (tn + fp)) if (tn + fp) else None),
        "false_negative_rate": (float(fn / (fn + tp)) if (fn + tp) else None),
        "roc_auc": None,
        "roc_auc_note": "Not requested (no probability scores provided)",
    }
    if y_score is not None:
        scores = np.asarray(y_score, dtype=float)
        if scores.ndim != 1 or len(scores) != len(truth) or not np.isfinite(scores).all():
            raise ValueError("Probability scores must be finite and match row count")
        if np.unique(truth).size == 2:
            results["roc_auc"] = float(roc_auc_score(truth, scores))
            results["roc_auc_note"] = None
        else:
            results["roc_auc_note"] = "ROC-AUC undefined: the split has only one class"
    return results


def evaluate_model(model: Pipeline, X: pd.DataFrame, y: pd.Series) -> dict[str, Any]:
    """Evaluate one *already fitted* pipeline; never fit on evaluation data."""
    return calculate_metrics(y, model.predict(X), _positive_probabilities(model, X))


def evaluate_baselines(
    dataset,
    config: TrainingConfig = TrainingConfig(),
) -> tuple[dict[str, Any], Pipeline, DataPartitions]:
    """Select by validation F1 and evaluate selected model on held-out test.

    Returns only the chosen fitted model and split references for optional plots.
    Both models' validation metrics are recorded; only the selected model is
    allowed to see official test features after selection.
    """
    partitions = partition_data(
        dataset, seed=config.seed, validation_fraction=config.validation_fraction
    )
    run = train_baselines(dataset, config)
    validation = {
        name: evaluate_model(model, partitions.X_valid, partitions.y_valid)
        for name, model in run.models.items()
    }
    # Python dictionaries preserve insertion order. On a tie Logistic Regression
    # (the first model) wins deterministically, without looking at test labels.
    selected = max(validation, key=lambda name: validation[name]["per_class"]["1"]["f1"])
    chosen = run.models[selected]
    held_out = evaluate_model(chosen, partitions.X_test, partitions.y_test)
    report: dict[str, Any] = {
        "status": "evaluation_completed",
        "phase": 4,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset": "Local CSVs using UNSW-NB15 official split filenames",
        "dataset_authenticity_verified_by_code": False,
        "source_data_type": "user-supplied local files; verify provider provenance independently",
        "target": "label",
        "positive_class": 1,
        "class_mapping": {"0": "normal", "1": "attack"},
        "selection_protocol": {
            "metric": "validation_positive_class_f1",
            "selection_data": "stratified validation subset of provider training partition",
            "tie_break": "logistic_regression wins a tie",
            "test_predictions_or_metrics_before_selection": False,
            "test_models_evaluated": [selected],
            "threshold": "classifier.predict default decision rule",
        },
        "training_run": run.manifest,
        "validation": validation,
        "selected_model": selected,
        "official_test_selected_model": held_out,
        "limitations": [
            "Test scores are valid only for the files supplied by the user; filenames do not authenticate origin.",
            "A static academic split does not establish real-world deployment performance.",
            "Selecting or tuning further on these held-out scores would compromise an unbiased final evaluation.",
            "Class support and false-positive rate must accompany precision and recall.",
        ],
    }
    return report, chosen, partitions


def _write_json_atomically(path: Path, payload: dict[str, Any]) -> None:
    """Write a JSON report via replacement, never via a half-finished file."""
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=path.parent, mode="w", encoding="utf-8", suffix=".json.tmp", delete=False
        ) as f:
            temp_path = Path(f.name)
            json.dump(payload, f, indent=2, ensure_ascii=False, allow_nan=False)
            f.write("\n")
        os.replace(temp_path, path)
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


def evaluate_from_directory(
    data_dir: str | Path,
    output_dir: str | Path,
    config: TrainingConfig = TrainingConfig(),
    *,
    make_plots: bool = True,
) -> dict[str, Any]:
    """Train, select and evaluate offline; save aggregate outputs only.

    Refit two models from trusted local CSVs rather than loading pickle/joblib.
    No files are created until the input and fitting/evaluation succeed.
    """
    input_dir = Path(data_dir).expanduser().resolve()
    dataset = load_official_split(input_dir)
    report, chosen, partitions = evaluate_baselines(dataset, config)
    report["source_files_sha256"] = {
        TRAIN_FILENAME: sha256_file(input_dir / TRAIN_FILENAME),
        TEST_FILENAME: sha256_file(input_dir / TEST_FILENAME),
    }
    destination = Path(output_dir).expanduser().resolve()
    destination.mkdir(parents=True, exist_ok=True)
    report_path = destination / "evaluation.json"
    _write_json_atomically(report_path, report)
    paths: dict[str, str] = {"metrics": str(report_path)}
    if make_plots:
        from nids.visualization.plots import plot_confusion_matrix, plot_roc_curve

        from sklearn.metrics import confusion_matrix as sklearn_cm

        predictions = chosen.predict(partitions.X_test)
        confusion_path = destination / "confusion_matrix.png"
        plot_confusion_matrix(
            sklearn_cm(partitions.y_test, predictions, labels=LABELS), confusion_path,
            title=f"Held-out test confusion matrix ({report['selected_model']})",
        )
        paths["confusion_matrix"] = str(confusion_path)
        if report["official_test_selected_model"]["roc_auc"] is not None:
            roc_path = destination / "roc_curve.png"
            plot_roc_curve(
                partitions.y_test,
                _positive_probabilities(chosen, partitions.X_test),
                roc_path,
                title=f"Held-out test ROC ({report['selected_model']})",
            )
            paths["roc_curve"] = str(roc_path)
        else:
            # An earlier run must not leave a stale ROC plot in the same output
            # directory when the current test set makes ROC undefined.
            (destination / "roc_curve.png").unlink(missing_ok=True)
    return {
        "status": report["status"],
        "selected_model": report["selected_model"],
        "validation_positive_f1": {
            name: values["per_class"]["1"]["f1"]
            for name, values in report["validation"].items()
        },
        "test_metrics_recorded_for": [report["selected_model"]],
        "report_paths": paths,
        "dataset_authenticity_verified_by_code": False,
    }
