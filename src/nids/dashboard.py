"""Strict, read-only adapter from offline aggregate evaluation JSON to a UI.

No pickle/joblib deserialization, user-record rendering, or network operations.
The report filename is fixed and all presented numbers are validated as a
coherent binary-confusion-matrix summary before they are displayed.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

REPORT_FILENAME = "evaluation.json"
MAX_REPORT_BYTES = 2 * 1024 * 1024
MODEL_NAMES = ("logistic_regression", "random_forest")


class DashboardReportError(ValueError):
    """An existing results file is invalid or unsupported for display."""


@dataclass(frozen=True)
class DashboardSnapshot:
    """A validated aggregate view, without private row-level records."""

    selected_model: str
    generated_at: str
    validation_rows: tuple[dict[str, Any], ...]
    selected_test: dict[str, Any]
    confusion_matrix: tuple[tuple[int, int], tuple[int, int]]
    normal_count: int
    attack_count: int
    test_count: int
    roc_auc_note: str | None
    hashes_recorded: bool


def _object(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise DashboardReportError(f"{label} must be a JSON object")
    return value


def _integer(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise DashboardReportError(f"{label} must be a nonnegative integer")
    return value


def _rate(value: Any, label: str, *, optional: bool = False) -> float | None:
    if value is None and optional:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise DashboardReportError(f"{label} must be a numeric rate")
    value = float(value)
    if not math.isfinite(value) or not 0.0 <= value <= 1.0:
        raise DashboardReportError(f"{label} must be finite and in [0, 1]")
    return value


def _consistent(observed: float | None, expected: float | None, label: str) -> None:
    if (observed is None) != (expected is None):
        raise DashboardReportError(f"{label} disagrees with the confusion matrix")
    if observed is not None and expected is not None and not math.isclose(
        observed, expected, abs_tol=1e-9, rel_tol=1e-7
    ):
        raise DashboardReportError(f"{label} disagrees with the confusion matrix")


def _check_metrics(value: Any, label: str) -> dict[str, Any]:
    m = _object(value, label)
    raw_matrix = m.get("confusion_matrix")
    if not isinstance(raw_matrix, list) or len(raw_matrix) != 2 or any(
        not isinstance(row, list) or len(row) != 2 for row in raw_matrix
    ):
        raise DashboardReportError(f"{label}.confusion_matrix must be 2x2")
    tn, fp = [_integer(x, f"{label}.confusion_matrix") for x in raw_matrix[0]]
    fn, tp = [_integer(x, f"{label}.confusion_matrix") for x in raw_matrix[1]]
    count = _integer(m.get("sample_count"), f"{label}.sample_count")
    if count <= 0 or count != tn + fp + fn + tp:
        raise DashboardReportError(f"{label}.sample_count conflicts with confusion matrix")
    counts = _object(m.get("class_counts"), f"{label}.class_counts")
    if counts.get("0") != tn + fp or counts.get("1") != fn + tp:
        raise DashboardReportError(f"{label}.class_counts conflict with confusion matrix")
    classes = _object(m.get("per_class"), f"{label}.per_class")
    for cl, support in (("0", tn + fp), ("1", fn + tp)):
        row = _object(classes.get(cl), f"{label}.per_class.{cl}")
        if _integer(row.get("support"), f"{label}.per_class.{cl}.support") != support:
            raise DashboardReportError(f"{label}.per_class.{cl}.support conflicts with counts")
        precision_observed = _rate(row.get("precision"), f"{label}.per_class.{cl}.precision")
        recall_observed = _rate(row.get("recall"), f"{label}.per_class.{cl}.recall")
        f1_observed = _rate(row.get("f1"), f"{label}.per_class.{cl}.f1")
        true_pos, false_pos, false_neg = (tn, fn, fp) if cl == "0" else (tp, fp, fn)
        expected_precision = true_pos / (true_pos + false_pos) if true_pos + false_pos else 0.0
        expected_recall = true_pos / (true_pos + false_neg) if true_pos + false_neg else 0.0
        expected_f1 = (2 * expected_precision * expected_recall / (expected_precision + expected_recall)
                       if expected_precision + expected_recall else 0.0)
        for metric, actual, expected in (
            ("precision", precision_observed, expected_precision),
            ("recall", recall_observed, expected_recall),
            ("f1", f1_observed, expected_f1),
        ):
            _consistent(actual, expected, f"{label}.per_class.{cl}.{metric}")

    accuracy = _rate(m.get("accuracy"), f"{label}.accuracy")
    macro_f1 = _rate(m.get("macro_f1"), f"{label}.macro_f1")
    weighted_f1 = _rate(m.get("weighted_f1"), f"{label}.weighted_f1")
    fpr = _rate(m.get("false_positive_rate"), f"{label}.false_positive_rate", optional=True)
    fnr = _rate(m.get("false_negative_rate"), f"{label}.false_negative_rate", optional=True)
    auc = _rate(m.get("roc_auc"), f"{label}.roc_auc", optional=True)

    _consistent(accuracy, (tn + tp) / count, f"{label}.accuracy")
    _consistent(fpr, fp / (tn + fp) if tn + fp else None, f"{label}.false_positive_rate")
    _consistent(fnr, fn / (fn + tp) if fn + tp else None, f"{label}.false_negative_rate")
    _consistent(
        macro_f1,
        (float(classes["0"]["f1"]) + float(classes["1"]["f1"])) / 2,
        f"{label}.macro_f1",
    )
    _consistent(
        weighted_f1,
        (float(classes["0"]["f1"]) * (tn + fp) + float(classes["1"]["f1"]) * (fn + tp)) / count,
        f"{label}.weighted_f1",
    )
    if auc is not None and (tn + fp == 0 or fn + tp == 0):
        raise DashboardReportError(f"{label}.roc_auc is undefined for single-class data")

    return {
        "sample_count": count,
        "normal_count": tn + fp,
        "attack_count": fn + tp,
        "confusion_matrix": ((tn, fp), (fn, tp)),
        "accuracy": accuracy,
        "macro_f1": macro_f1,
        "weighted_f1": weighted_f1,
        "precision_attack": float(classes["1"]["precision"]),
        "recall_attack": float(classes["1"]["recall"]),
        "f1_attack": float(classes["1"]["f1"]),
        "false_positive_rate": fpr,
        "false_negative_rate": fnr,
        "roc_auc": auc,
    }


def build_dashboard_snapshot(report: Mapping[str, Any]) -> DashboardSnapshot:
    """Validate the evaluator's contract and extract safe, aggregate figures."""
    root = _object(report, "report")
    if root.get("status") != "evaluation_completed":
        raise DashboardReportError("Report is not a completed evaluation")
    if root.get("dataset_authenticity_verified_by_code") is not False:
        raise DashboardReportError("Unsupported dataset provenance flag")
    selected = root.get("selected_model")
    if selected not in MODEL_NAMES:
        raise DashboardReportError("Unknown selected model")
    validation = _object(root.get("validation"), "validation")
    if set(validation) != set(MODEL_NAMES):
        raise DashboardReportError("Expected validation results for both baseline models")
    by_name = {name: _check_metrics(validation[name], f"validation.{name}") for name in MODEL_NAMES}
    rows = tuple({"model": name, **by_name[name]} for name in MODEL_NAMES)
    winner = max(MODEL_NAMES, key=lambda name: by_name[name]["f1_attack"])
    if selected != winner:
        raise DashboardReportError("Selected model conflicts with validation F1 selection")
    protocol = _object(root.get("selection_protocol"), "selection_protocol")
    if protocol.get("metric") != "validation_positive_class_f1" or protocol.get(
        "test_models_evaluated"
    ) != [selected] or protocol.get("test_predictions_or_metrics_before_selection") is not False:
        raise DashboardReportError("Unsupported or inconsistent model-selection protocol")
    test = _check_metrics(root.get("official_test_selected_model"), "official_test_selected_model")
    generated = root.get("created_at_utc")
    if not isinstance(generated, str) or len(generated) > 100:
        raise DashboardReportError("Missing or malformed timestamp")
    note = root["official_test_selected_model"].get("roc_auc_note")
    if note is not None and (not isinstance(note, str) or len(note) > 200):
        raise DashboardReportError("Invalid ROC-AUC note")
    sha = root.get("source_files_sha256")
    hash_recorded = isinstance(sha, dict) and len(sha) == 2 and all(
        isinstance(v, str) and len(v) == 64 and all(c in "0123456789abcdefABCDEF" for c in v)
        for v in sha.values()
    )
    return DashboardSnapshot(
        selected_model=selected,
        generated_at=generated,
        validation_rows=rows,
        selected_test=test,
        confusion_matrix=test["confusion_matrix"],
        normal_count=test["normal_count"],
        attack_count=test["attack_count"],
        test_count=test["sample_count"],
        roc_auc_note=note,
        hashes_recorded=hash_recorded,
    )


def load_dashboard_snapshot(report_directory: Path | str) -> DashboardSnapshot:
    """Read only the local fixed-name aggregate JSON (max 2 MiB)."""
    source = Path(report_directory).expanduser().resolve() / REPORT_FILENAME
    if not source.is_file():
        raise FileNotFoundError(f"No local {REPORT_FILENAME} in {source.parent}")
    if source.stat().st_size > MAX_REPORT_BYTES:
        raise DashboardReportError("Report exceeds maximum supported size (2 MiB)")
    try:
        with source.open("r", encoding="utf-8") as handle:
            report = json.load(handle)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise DashboardReportError("Unable to read a valid UTF-8 JSON evaluation report") from exc
    return build_dashboard_snapshot(report)
