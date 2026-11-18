"""CLI training behavior with tiny, synthetic CSV fixtures."""

import json

import numpy as np
import pandas as pd

from nids.cli import main
from nids.data.load import TRAIN_FILENAME, TEST_FILENAME


def test_train_cli_writes_local_artifacts_with_no_test_metrics(tmp_path, capsys):
    n = 40
    k = np.arange(n)
    sample = pd.DataFrame({
        "id": k,
        "proto": np.where(k % 2 == 0, "tcp", "udp"),
        "service": np.where(k % 2 == 0, "http", "-"),
        "state": np.where(k % 2 == 0, "FIN", "INT"),
        "dur": k.astype(float),
        "label": k % 2,
        "attack_cat": np.where(k % 2 == 0, "Normal", "Generic"),
    })
    data = tmp_path / "raw"
    data.mkdir()
    sample.to_csv(data / TRAIN_FILENAME, index=False)
    sample.iloc[:12].to_csv(data / TEST_FILENAME, index=False)
    output_dir = tmp_path / "models"
    assert main([
        "train", "--data-dir", str(data), "--output-dir", str(output_dir),
        "--seed", "24", "--trees", "4", "--max-iter", "400",
    ]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "trained_no_evaluation"
    assert output["evaluated_on_official_test"] is False
    assert (output_dir / "logistic_regression.joblib").is_file()
    assert (output_dir / "random_forest.joblib").is_file()
    manifest = json.loads((output_dir / "training_manifest.json").read_text())
    assert manifest["training_config"]["seed"] == 24
    assert manifest["official_test_rows"] == 12
    assert manifest["held_out_evaluation_performed"] is False
