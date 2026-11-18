"""Real evaluator-to-dashboard file integration using synthetic fixtures only."""

from __future__ import annotations

import numpy as np
import pandas as pd

from nids.dashboard import load_dashboard_snapshot
from nids.data.load import TEST_FILENAME, TRAIN_FILENAME
from nids.models.evaluate import evaluate_from_directory
from nids.models.train import TrainingConfig


def sample_frame(size: int) -> pd.DataFrame:
    k = np.arange(size)
    return pd.DataFrame({
        "id": k + 1,
        "proto": np.where(k % 2, "udp", "tcp"),
        "service": np.where(k % 3, "dns", "http"),
        "state": np.where(k % 2, "INT", "FIN"),
        "dur": (k % 11).astype(float),
        "sbytes": ((k * 7) % 13).astype(float),
        "attack_cat": np.where(k % 2, "Generic", "Normal"),
        "label": k % 2,
    })


def test_evaluate_then_display_contract_without_real_network_data(tmp_path):
    data = tmp_path / "raw"
    reports = tmp_path / "reports"
    data.mkdir()
    sample_frame(60).to_csv(data / TRAIN_FILENAME, index=False)
    sample_frame(20).to_csv(data / TEST_FILENAME, index=False)
    outcome = evaluate_from_directory(
        data, reports, TrainingConfig(seed=23, forest_trees=3, logistic_max_iter=200),
        make_plots=False,
    )
    view = load_dashboard_snapshot(reports)
    assert view.selected_model == outcome["selected_model"]
    assert view.test_count == 20
    assert len(view.validation_rows) == 2
    assert view.normal_count + view.attack_count == 20
    assert view.hashes_recorded
    assert not (reports / "roc_curve.png").exists()
