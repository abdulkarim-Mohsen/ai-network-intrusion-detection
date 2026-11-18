"""Render-path smoke tests using a fake Streamlit module, no web or server."""

from __future__ import annotations

import json
import runpy
import sys
from contextlib import nullcontext
from pathlib import Path
from unittest.mock import MagicMock

from nids.models.evaluate import calculate_metrics


APP = Path(__file__).resolve().parents[1] / "app" / "streamlit_app.py"


def fake_streamlit(monkeypatch):
    ui = MagicMock()
    ui.sidebar = ui
    ui.columns.side_effect = lambda n: (ui,) * n
    ui.tabs.return_value = tuple(nullcontext() for _ in range(4))
    monkeypatch.setitem(sys.modules, "streamlit", ui)
    return ui


def test_empty_state_does_not_claim_detection_results(monkeypatch, tmp_path):
    ui = fake_streamlit(monkeypatch)
    monkeypatch.setenv("NIDS_REPORT_DIR", str(tmp_path))
    runpy.run_path(str(APP), run_name="__main__")
    assert ui.info.called
    assert not ui.metric.called
    assert not ui.pyplot.called


def test_valid_report_renders_both_validation_and_test_panels(monkeypatch, tmp_path):
    ui = fake_streamlit(monkeypatch)
    monkeypatch.setenv("NIDS_REPORT_DIR", str(tmp_path))
    a = calculate_metrics([0, 0, 1, 1], [0, 0, 1, 1], [0.1, 0.2, 0.8, 0.9])
    b = calculate_metrics([0, 0, 1, 1], [1, 0, 0, 1], [0.8, 0.2, 0.3, 0.9])
    report = {
        "status": "evaluation_completed", "created_at_utc": "2026-11-18T15:00:00+00:00",
        "dataset_authenticity_verified_by_code": False,
        "selected_model": "logistic_regression",
        "validation": {"logistic_regression": a, "random_forest": b},
        "official_test_selected_model": a,
        "selection_protocol": {
            "metric": "validation_positive_class_f1",
            "test_models_evaluated": ["logistic_regression"],
            "test_predictions_or_metrics_before_selection": False,
        },
    }
    (tmp_path / "evaluation.json").write_text(json.dumps(report), encoding="utf-8")
    runpy.run_path(str(APP), run_name="__main__")
    assert ui.warning.called  # dataset provenance warning
    assert ui.dataframe.called
    assert ui.bar_chart.called
    assert ui.pyplot.called
    assert ui.metric.called
    assert not ui.image.called  # no real ROC PNG, even when AUC exists
