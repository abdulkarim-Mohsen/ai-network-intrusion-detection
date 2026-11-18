"""Offline dashboard contract tests using only fictional aggregate counts."""

from __future__ import annotations

import json
from copy import deepcopy

import pytest

from nids.dashboard import (
    MAX_REPORT_BYTES,
    DashboardReportError,
    build_dashboard_snapshot,
    load_dashboard_snapshot,
)
from nids.models.evaluate import calculate_metrics


@pytest.fixture
def report():
    good = calculate_metrics(
        [0, 0, 0, 1, 1, 1], [0, 0, 1, 1, 1, 0],
        [0.1, 0.2, 0.8, 0.9, 0.7, 0.4],
    )
    worse = calculate_metrics(
        [0, 0, 0, 1, 1, 1], [1, 1, 1, 0, 0, 0],
        [0.8, 0.7, 0.6, 0.4, 0.3, 0.2],
    )
    return {
        "status": "evaluation_completed", "phase": 4,
        "dataset_authenticity_verified_by_code": False,
        "created_at_utc": "2026-11-18T15:00:00+00:00",
        "selected_model": "logistic_regression",
        "validation": {"logistic_regression": good, "random_forest": worse},
        "official_test_selected_model": good,
        "selection_protocol": {
            "metric": "validation_positive_class_f1",
            "test_models_evaluated": ["logistic_regression"],
            "test_predictions_or_metrics_before_selection": False,
        },
        "source_files_sha256": {"training.csv": "a" * 64, "testing.csv": "b" * 64},
    }


def test_valid_report_summary_contains_only_aggregate_information(report):
    snapshot = build_dashboard_snapshot(report)
    assert snapshot.selected_model == "logistic_regression"
    assert len(snapshot.validation_rows) == 2
    assert snapshot.test_count == 6
    assert snapshot.normal_count == 3 and snapshot.attack_count == 3
    assert snapshot.confusion_matrix == ((2, 1), (1, 2))
    assert snapshot.selected_test["false_positive_rate"] == pytest.approx(1 / 3)
    assert snapshot.hashes_recorded
    assert not hasattr(snapshot, "raw_rows")


def test_missing_report_is_not_fabricated(tmp_path):
    with pytest.raises(FileNotFoundError, match="No local evaluation.json"):
        load_dashboard_snapshot(tmp_path)


def test_load_real_json_aggregate_without_model_loading(tmp_path, report):
    (tmp_path / "evaluation.json").write_text(json.dumps(report), encoding="utf-8")
    snapshot = load_dashboard_snapshot(tmp_path)
    assert snapshot.test_count == 6


@pytest.mark.parametrize("change", [
    lambda r: r.update(status="not_finished"),
    lambda r: r.update(dataset_authenticity_verified_by_code=True),
    lambda r: r.update(selected_model="random_forest"),
    lambda r: r["validation"].pop("random_forest"),
    lambda r: r["selection_protocol"].update(test_models_evaluated=["logistic_regression", "random_forest"]),
    lambda r: r["selection_protocol"].update(test_predictions_or_metrics_before_selection=True),
    lambda r: r["official_test_selected_model"].update(sample_count=100),
    lambda r: r["official_test_selected_model"].update(confusion_matrix=[[0, 1], [1, -1]]),
    lambda r: r["official_test_selected_model"].update(false_positive_rate=0.99),
    lambda r: r["official_test_selected_model"].update(roc_auc=float("nan")),
    lambda r: r["official_test_selected_model"]["per_class"]["1"].update(support=500),
    lambda r: r["official_test_selected_model"]["per_class"]["1"].update(f1="not-a-metric"),
    lambda r: r["official_test_selected_model"]["per_class"]["1"].update(f1=0.12),
    lambda r: r.update(created_at_utc=4),
])
def test_unsupported_or_corrupt_reports_rejected(report, change):
    corrupted = deepcopy(report)
    change(corrupted)
    with pytest.raises(DashboardReportError):
        build_dashboard_snapshot(corrupted)


def test_large_report_rejected_without_parsing(tmp_path):
    (tmp_path / "evaluation.json").write_bytes(b" " * (MAX_REPORT_BYTES + 1))
    with pytest.raises(DashboardReportError, match="maximum"):
        load_dashboard_snapshot(tmp_path)


def test_non_json_or_non_object_rejected(tmp_path):
    path = tmp_path / "evaluation.json"
    path.write_text("not valid", encoding="utf-8")
    with pytest.raises(DashboardReportError):
        load_dashboard_snapshot(tmp_path)
    path.write_text("[]", encoding="utf-8")
    with pytest.raises(DashboardReportError):
        load_dashboard_snapshot(tmp_path)


def test_undefined_auc_preserved_as_missing_not_zero(report):
    # An all-normal held-out split makes AUC and FNR undefined.
    m = calculate_metrics([0, 0, 0], [0, 0, 1], [0.1, 0.2, 0.8])
    assert m["roc_auc"] is None
    report["official_test_selected_model"] = m
    snap = build_dashboard_snapshot(report)
    assert snap.selected_test["roc_auc"] is None
    assert snap.selected_test["false_negative_rate"] is None
    assert "undefined" in snap.roc_auc_note.lower()
