"""CLI evaluation contract exercised with synthetic CSVs only."""

import json
import numpy as np
import pandas as pd

from nids.cli import main
from nids.data.load import TRAIN_FILENAME, TEST_FILENAME


def test_cli_evaluate_writes_local_json_without_plots(tmp_path, capsys):
    k = np.arange(40)
    frame = pd.DataFrame({
        "id": k,
        "proto": np.where(k % 2 == 0, "tcp", "udp"),
        "service": np.where(k % 2 == 0, "http", "-"),
        "state": np.where(k % 2 == 0, "FIN", "INT"),
        "dur": k.astype(float),
        "label": k % 2,
        "attack_cat": np.where(k % 2 == 0, "Normal", "Generic"),
    })
    root = tmp_path / "raw"
    root.mkdir()
    frame.to_csv(root / TRAIN_FILENAME, index=False)
    frame.iloc[:16].to_csv(root / TEST_FILENAME, index=False)
    output = tmp_path / "reports"
    code = main([
        "evaluate", "--data-dir", str(root), "--output-dir", str(output),
        "--seed", "5", "--trees", "3", "--max-iter", "200", "--no-plots",
    ])
    assert code == 0
    reply = json.loads(capsys.readouterr().out)
    assert reply["status"] == "evaluation_completed"
    assert set(reply["validation_positive_f1"]) == {"logistic_regression", "random_forest"}
    assert (output / "evaluation.json").is_file()
    assert not (output / "confusion_matrix.png").exists()
    assert not (output / "roc_curve.png").exists()
